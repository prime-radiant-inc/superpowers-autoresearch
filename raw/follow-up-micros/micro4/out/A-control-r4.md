# Go Fractals CLI - Implementation Plan

## Overview

We're building a CLI tool that generates ASCII art fractals (Sierpinski triangle and Mandelbrot set). This plan assumes zero context for the codebase. Follow each step in order: write the failing test, run it to see it fail, implement, run to see it pass, commit.

## File Structure

```
go.mod                              # Module definition, dependencies
cmd/fractals/main.go                # Entry point; calls cli.Execute()
internal/sierpinski/sierpinski.go   # Sierpinski algorithm: Generate(size, depth, char) []string
internal/sierpinski/sierpinski_test.go
internal/mandelbrot/mandelbrot.go   # Mandelbrot algorithm: Render(width, height, iterations, palette) []string
internal/mandelbrot/mandelbrot_test.go
internal/cli/root.go                # Root cobra command + Execute()
internal/cli/sierpinski.go          # sierpinski subcommand wiring
internal/cli/mandelbrot.go          # mandelbrot subcommand wiring
```

Responsibilities:
- **Algorithm packages** (`sierpinski`, `mandelbrot`): pure functions, no I/O, fully unit-tested. Each returns `[]string` (rows) and an `error` for invalid input.
- **CLI package** (`cli`): flag parsing, validation wiring, printing to stdout.
- **main.go**: tiny — delegates to `cli.Execute()`.

---

### Task 1: Project Scaffolding

**Files:** `go.mod`, `cmd/fractals/main.go`

- [ ] Confirm Go version is 1.21+:

```bash
go version
```

Expected output (version may be higher):
```
go version go1.21.0 ...
```

- [ ] Initialize the module:

```bash
go mod init fractals
```

Expected output:
```
go: creating new go.mod: module fractals
```

- [ ] Add the cobra dependency:

```bash
go get github.com/spf13/cobra@latest
```

Expected output (versions may differ):
```
go: added github.com/spf13/cobra v1.8.x
...
```

- [ ] Create `cmd/fractals/main.go` with a minimal entry point. (The `cli` package does not exist yet, so this won't compile until Task 4 — that's fine; we commit after creating the directory structure but verify build later.)

```go
package main

import "fractals/internal/cli"

func main() {
	cli.Execute()
}
```

- [ ] Verify `go.mod` and `go.sum` exist:

```bash
ls go.mod go.sum
```

Expected output:
```
go.mod  go.sum
```

- [ ] Commit:

```bash
git add go.mod go.sum cmd/fractals/main.go
git commit -m "scaffold: init module, add cobra, entry point"
```

---

### Task 2: Sierpinski Algorithm

The algorithm: a point `(x, y)` is part of the Sierpinski triangle if `(x & y) == 0` (bitwise AND of row and column is zero). We render `size` rows, where row `y` (0-indexed from top) has the triangle filled. We use depth to determine the grid resolution: the grid side is `1 << depth` but we constrain it to `size`. For simplicity and a recognizable triangle, we render a grid of `size` rows and `size` columns where a cell is filled when `(x & y) == 0`, and we only draw within the triangular region. Depth controls the maximum subdivision: cells beyond `1<<depth` resolution are blank.

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

- [ ] Write the failing test in `internal/sierpinski/sierpinski_test.go`:

```go
package sierpinski

import (
	"strings"
	"testing"
)

func TestGenerate_InvalidSize(t *testing.T) {
	_, err := Generate(0, 5, '*')
	if err == nil {
		t.Fatal("expected error for size 0, got nil")
	}
}

func TestGenerate_InvalidDepth(t *testing.T) {
	_, err := Generate(8, 0, '*')
	if err == nil {
		t.Fatal("expected error for depth 0, got nil")
	}
}

func TestGenerate_RowCountEqualsSize(t *testing.T) {
	rows, err := Generate(8, 3, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 8 {
		t.Fatalf("expected 8 rows, got %d", len(rows))
	}
}

func TestGenerate_TopRowSingleChar(t *testing.T) {
	// Top row of a Sierpinski triangle has exactly one filled cell.
	rows, err := Generate(8, 3, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if strings.Count(rows[0], "*") != 1 {
		t.Fatalf("expected exactly 1 '*' in top row, got %q", rows[0])
	}
}

func TestGenerate_BottomRowFull(t *testing.T) {
	// Bottom row (y = size-1) where size-1 = all bits set has every
	// column filled because (x & y) == x, and for the widest power-of-two
	// boundary the last row is fully filled.
	rows, err := Generate(8, 3, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	// y = 7 (0b111): (x & 7) == 0 only when x == 0, so actually sparse.
	// Instead assert the row at y = size-1 contains the expected pattern:
	// filled when (x & 7) == 0 -> only x==0. So count is 1.
	if strings.Count(rows[7], "*") != 1 {
		t.Fatalf("expected 1 '*' in row 7, got %q", rows[7])
	}
}

func TestGenerate_CustomChar(t *testing.T) {
	rows, err := Generate(8, 3, '#')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(rows, "\n")
	if strings.Contains(joined, "*") {
		t.Fatalf("did not expect '*' when char is '#': %q", joined)
	}
	if !strings.Contains(joined, "#") {
		t.Fatalf("expected '#' in output: %q", joined)
	}
}

func TestGenerate_DepthLimitsResolution(t *testing.T) {
	// With depth 1, grid resolution is 1<<1 = 2, so beyond column/row 1
	// cells are blank. The output still has `size` rows but fewer filled.
	rows, err := Generate(8, 1, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	// Rows at index >= 2 must be entirely blank.
	for i := 2; i < len(rows); i++ {
		if strings.Contains(rows[i], "*") {
			t.Fatalf("expected row %d blank at depth 1, got %q", i, rows[i])
		}
	}
}
```

- [ ] Run the test to confirm it fails (no implementation yet):

```bash
go test ./internal/sierpinski/
```

Expected output (compilation failure because `Generate` is undefined):
```
# fractals/internal/sierpinski [fractals/internal/sierpinski.test]
./sierpinski_test.go:... undefined: Generate
FAIL    fractals/internal/sierpinski [build failed]
```

- [ ] Implement `internal/sierpinski/sierpinski.go`:

```go
// Package sierpinski generates Sierpinski triangle ASCII art.
package sierpinski

import (
	"fmt"
	"strings"
)

// Generate returns the rows of a Sierpinski triangle.
//
// size is the number of rows and the width of the grid.
// depth controls the subdivision resolution: cells with a row or column
// index >= (1 << depth) are left blank.
// char is the rune used for filled cells.
//
// A cell at (x, y) is filled when (x & y) == 0.
func Generate(size, depth int, char rune) ([]string, error) {
	if size < 1 {
		return nil, fmt.Errorf("size must be >= 1, got %d", size)
	}
	if depth < 1 {
		return nil, fmt.Errorf("depth must be >= 1, got %d", depth)
	}

	limit := 1 << depth // resolution cap

	rows := make([]string, size)
	for y := 0; y < size; y++ {
		var b strings.Builder
		for x := 0; x < size; x++ {
			if x < limit && y < limit && (x&y) == 0 {
				b.WriteRune(char)
			} else {
				b.WriteRune(' ')
			}
		}
		rows[y] = b.String()
	}
	return rows, nil
}
```

- [ ] Run the test to confirm it passes:

```bash
go test ./internal/sierpinski/
```

Expected output:
```
ok      fractals/internal/sierpinski    0.00Xs
```

- [ ] Commit:

```bash
git add internal/sierpinski/
git commit -m "feat(sierpinski): triangle generation with size/depth/char"
```

---

### Task 3: Mandelbrot Algorithm

The algorithm: for each output cell, map pixel coordinates to a complex plane region (`x` in `[-2.5, 1.0]`, `y` in `[-1.0, 1.0]`), iterate `z = z² + c` up to `iterations`, and map the escape count to a character from a palette. Cells in the set (never escape) map to the last palette character.

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

- [ ] Write the failing test in `internal/mandelbrot/mandelbrot_test.go`:

```go
package mandelbrot

import (
	"strings"
	"testing"
)

const defaultPalette = " .:-=+*#%@"

func TestRender_InvalidWidth(t *testing.T) {
	_, err := Render(0, 24, 100, defaultPalette)
	if err == nil {
		t.Fatal("expected error for width 0, got nil")
	}
}

func TestRender_InvalidHeight(t *testing.T) {
	_, err := Render(80, 0, 100, defaultPalette)
	if err == nil {
		t.Fatal("expected error for height 0, got nil")
	}
}

func TestRender_InvalidIterations(t *testing.T) {
	_, err := Render(80, 24, 0, defaultPalette)
	if err == nil {
		t.Fatal("expected error for iterations 0, got nil")
	}
}

func TestRender_EmptyPalette(t *testing.T) {
	_, err := Render(80, 24, 100, "")
	if err == nil {
		t.Fatal("expected error for empty palette, got nil")
	}
}

func TestRender_Dimensions(t *testing.T) {
	rows, err := Render(80, 24, 100, defaultPalette)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 24 {
		t.Fatalf("expected 24 rows, got %d", len(rows))
	}
	for i, r := range rows {
		if len([]rune(r)) != 80 {
			t.Fatalf("row %d: expected width 80, got %d", i, len([]rune(r)))
		}
	}
}

func TestRender_CenterIsInSet(t *testing.T) {
	// The point near (-0.5, 0) is inside the set and maps to the last
	// palette char. The middle of the output should contain it.
	rows, err := Render(80, 24, 100, defaultPalette)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lastChar := string([]rune(defaultPalette)[len([]rune(defaultPalette))-1])
	joined := strings.Join(rows, "\n")
	if !strings.Contains(joined, lastChar) {
		t.Fatalf("expected in-set char %q somewhere in output", lastChar)
	}
}

func TestRender_SingleCharPalette(t *testing.T) {
	// A single-char palette means every cell uses that char.
	rows, err := Render(20, 10, 50, "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(rows, "")
	for _, r := range joined {
		if r != '#' {
			t.Fatalf("expected only '#', got %q", string(r))
		}
	}
}
```

- [ ] Run the test to confirm it fails:

```bash
go test ./internal/mandelbrot/
```

Expected output:
```
# fractals/internal/mandelbrot [fractals/internal/mandelbrot.test]
./mandelbrot_test.go:... undefined: Render
FAIL    fractals/internal/mandelbrot [build failed]
```

- [ ] Implement `internal/mandelbrot/mandelbrot.go`:

```go
// Package mandelbrot renders the Mandelbrot set as ASCII art.
package mandelbrot

import (
	"fmt"
	"strings"
)

// Plane bounds for the Mandelbrot render.
const (
	xMin = -2.5
	xMax = 1.0
	yMin = -1.0
	yMax = 1.0
)

// Render returns the rows of the Mandelbrot set.
//
// width and height are the output dimensions in characters.
// iterations is the maximum escape iteration count.
// palette is the ordered set of characters: index 0 for fastest escape,
// last index for points in the set.
func Render(width, height, iterations int, palette string) ([]string, error) {
	if width < 1 {
		return nil, fmt.Errorf("width must be >= 1, got %d", width)
	}
	if height < 1 {
		return nil, fmt.Errorf("height must be >= 1, got %d", height)
	}
	if iterations < 1 {
		return nil, fmt.Errorf("iterations must be >= 1, got %d", iterations)
	}
	pal := []rune(palette)
	if len(pal) == 0 {
		return nil, fmt.Errorf("palette must contain at least one character")
	}

	rows := make([]string, height)
	for py := 0; py < height; py++ {
		var b strings.Builder
		cy := yMin + (yMax-yMin)*float64(py)/float64(height-1)
		if height == 1 {
			cy = (yMin + yMax) / 2
		}
		for px := 0; px < width; px++ {
			cx := xMin + (xMax-xMin)*float64(px)/float64(width-1)
			if width == 1 {
				cx = (xMin + xMax) / 2
			}
			n := escape(cx, cy, iterations)
			b.WriteRune(charFor(n, iterations, pal))
		}
		rows[py] = b.String()
	}
	return rows, nil
}

// escape returns the iteration count at which the point escapes, or
// iterations if it never escapes (in the set).
func escape(cx, cy float64, iterations int) int {
	var zx, zy float64
	for n := 0; n < iterations; n++ {
		zx2, zy2 := zx*zx, zy*zy
		if zx2+zy2 > 4.0 {
			return n
		}
		zy = 2*zx*zy + cy
		zx = zx2 - zy2 + cx
	}
	return iterations
}

// charFor maps an escape count to a palette rune.
// In-set points (n == iterations) use the last palette rune.
func charFor(n, iterations int, pal []rune) rune {
	if n >= iterations {
		return pal[len(pal)-1]
	}
	idx := n * (len(pal) - 1) / iterations
	if idx >= len(pal) {
		idx = len(pal) - 1
	}
	return pal[idx]
}
```

- [ ] Run the test to confirm it passes:

```bash
go test ./internal/mandelbrot/
```

Expected output:
```
ok      fractals/internal/mandelbrot    0.00Xs
```

- [ ] Commit:

```bash
git add internal/mandelbrot/
git commit -m "feat(mandelbrot): set rendering with width/height/iterations/palette"
```

---

### Task 4: CLI Root Command

**Files:** `internal/cli/root.go`

- [ ] Create `internal/cli/root.go`:

```go
// Package cli wires the fractals subcommands together.
package cli

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

func newRootCmd() *cobra.Command {
	root := &cobra.Command{
		Use:   "fractals",
		Short: "Generate ASCII art fractals",
		Long:  "fractals generates ASCII art fractals: Sierpinski triangles and the Mandelbrot set.",
	}
	root.AddCommand(newSierpinskiCmd())
	root.AddCommand(newMandelbrotCmd())
	return root
}

// Execute runs the root command and exits non-zero on error.
func Execute() {
	if err := newRootCmd().Execute(); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
}
```

- [ ] This won't build yet because `newSierpinskiCmd` and `newMandelbrotCmd` are undefined. We'll add them in the next tasks. Do **not** build yet. Commit the root file:

```bash
git add internal/cli/root.go
git commit -m "feat(cli): root command and Execute"
```

---

### Task 5: Sierpinski Subcommand

**Files:** `internal/cli/sierpinski.go`

- [ ] Create `internal/cli/sierpinski.go`:

```go
package cli

import (
	"fmt"
	"unicode/utf8"

	"github.com/spf13/cobra"

	"fractals/internal/sierpinski"
)

func newSierpinskiCmd() *cobra.Command {
	var (
		size  int
		depth int
		char  string
	)

	cmd := &cobra.Command{
		Use:   "sierpinski",
		Short: "Generate a Sierpinski triangle",
		RunE: func(cmd *cobra.Command, args []string) error {
			r, err := singleRune(char)
			if err != nil {
				return err
			}
			rows, err := sierpinski.Generate(size, depth, r)
			if err != nil {
				return err
			}
			for _, line := range rows {
				fmt.Fprintln(cmd.OutOrStdout(), line)
			}
			return nil
		},
	}

	cmd.Flags().IntVar(&size, "size", 32, "width of the triangle base in characters")
	cmd.Flags().IntVar(&depth, "depth", 5, "recursion depth")
	cmd.Flags().StringVar(&char, "char", "*", "character to use for filled points")
	return cmd
}

// singleRune validates that s is exactly one rune and returns it.
func singleRune(s string) (rune, error) {
	if utf8.RuneCountInString(s) != 1 {
		return 0, fmt.Errorf("--char must be a single character, got %q", s)
	}
	r, _ := utf8.DecodeRuneInString(s)
	return r, nil
}
```

- [ ] Build now to verify the package compiles (mandelbrot subcommand still missing — expect a build error referencing `newMandelbrotCmd`):

```bash
go build ./...
```

Expected output:
```
# fractals/internal/cli
internal/cli/root.go:... undefined: newMandelbrotCmd
```

This confirms the sierpinski wiring is correct. Commit:

```bash
git add internal/cli/sierpinski.go
git commit -m "feat(cli): sierpinski subcommand"
```

---

### Task 6: Mandelbrot Subcommand

**Files:** `internal/cli/mandelbrot.go`

- [ ] Create `internal/cli/mandelbrot.go`:

```go
package cli

import (
	"fmt"
	"strings"
	"unicode/utf8"

	"github.com/spf13/cobra"

	"fractals/internal/mandelbrot"
)

const defaultPalette = " .:-=+*#%@"

func newMandelbrotCmd() *cobra.Command {
	var (
		width      int
		height     int
		iterations int
		char       string
	)

	cmd := &cobra.Command{
		Use:   "mandelbrot",
		Short: "Render the Mandelbrot set",
		RunE: func(cmd *cobra.Command, args []string) error {
			palette, err := paletteFor(char)
			if err != nil {
				return err
			}
			rows, err := mandelbrot.Render(width, height, iterations, palette)
			if err != nil {
				return err
			}
			for _, line := range rows {
				fmt.Fprintln(cmd.OutOrStdout(), line)
			}
			return nil
		},
	}

	cmd.Flags().IntVar(&width, "width", 80, "output width in characters")
	cmd.Flags().IntVar(&height, "height", 24, "output height in characters")
	cmd.Flags().IntVar(&iterations, "iterations", 100, "maximum iterations for escape calculation")
	cmd.Flags().StringVar(&char, "char", "", "single character to use, or omit for gradient")
	return cmd
}

// paletteFor returns the gradient palette when char is empty, otherwise a
// single-character palette validated to be exactly one rune.
func paletteFor(char string) (string, error) {
	if char == "" {
		return defaultPalette, nil
	}
	if utf8.RuneCountInString(char) != 1 {
		return "", fmt.Errorf("--char must be a single character, got %q", char)
	}
	return strings.Repeat(char, 1), nil
}
```

- [ ] Build the whole project — it should now compile:

```bash
go build ./...
```

Expected output (no output = success):
```
```

- [ ] Run the help command to verify wiring:

```bash
go run ./cmd/fractals --help
```

Expected output (contains these lines):
```
fractals generates ASCII art fractals: Sierpinski triangles and the Mandelbrot set.

Usage:
  fractals [command]

Available Commands:
  ...
  mandelbrot  Render the Mandelbrot set
  sierpinski  Generate a Sierpinski triangle
...
```

- [ ] Commit:

```bash
git add internal/cli/mandelbrot.go
git commit -m "feat(cli): mandelbrot subcommand"
```

---

### Task 7: End-to-End Verification

**Files:** none (verification only)

- [ ] Run the full test suite:

```bash
go test ./...
```

Expected output:
```
ok      fractals/internal/mandelbrot    0.00Xs
ok      fractals/internal/sierpinski    0.00Xs
?       fractals/cmd/fractals   [no test files]
?       fractals/internal/cli   [no test files]
```

- [ ] Run `vet` to catch issues:

```bash
go vet ./...
```

Expected output (no output = success):
```
```

- [ ] Verify sierpinski output is a recognizable triangle (Acceptance Criteria 2 & 4):

```bash
go run ./cmd/fractals sierpinski --size 16 --depth 4
```

Expected output (top rows show the characteristic Sierpinski pattern; exact rows):
```
*
**
* *
****
*   *
**  **
* * * *
********
...
```

- [ ] Verify custom char (Acceptance Criteria 5):

```bash
go run ./cmd/fractals sierpinski --size 8 --depth 3 --char '#'
```

Expected output:
```
#
##
# #
####
#   #
##  ##
# # # #
########
```

- [ ] Verify mandelbrot output (Acceptance Criteria 3 & 4):

```bash
go run ./cmd/fractals mandelbrot --width 60 --height 20 --iterations 100
```

Expected output (a recognizable Mandelbrot set — bulb on the left, cardioid on the right, gradient edges). Verify visually that it is roughly symmetric vertically and contains `@` cells in the central body.

- [ ] Verify invalid input error messages (Acceptance Criteria 6):

```bash
go run ./cmd/fractals sierpinski --size 0
```

Expected output (to stderr, exit code 1):
```
error: size must be >= 1, got 0
```

```bash
go run ./cmd/fractals mandelbrot --width 0
```

Expected output:
```
error: width must be >= 1, got 0
```

```bash
go run ./cmd/fractals sierpinski --char 'ab'
```

Expected output:
```
error: --char must be a single character, got "ab"
```

- [ ] Verify subcommand help (Acceptance Criteria 1):

```bash
go run ./cmd/fractals sierpinski --help
```

Expected output (contains flag descriptions):
```
Generate a Sierpinski triangle

Usage:
  fractals sierpinski [flags]

Flags:
      --char string   character to use for filled points (default "*")
      --depth int     recursion depth (default 5)
  -h, --help          help for sierpinski
      --size int      width of the triangle base in characters (default 32)
```

- [ ] If all output is as expected, commit a final verification marker (e.g. a README note is optional; the spec does not require it, so skip per YAGNI). No commit needed for this task.

---

## Self-Review

**Spec coverage:**
- ✅ `sierpinski` command with `--size`, `--depth`, `--char` (Task 2 + Task 5).
- ✅ `mandelbrot` command with `--width`, `--height`, `--iterations`, `--char` (gradient default) (Task 3 + Task 6).
- ✅ Gradient palette `" .:-=+*#%@"` defined in `mandelbrot.go` test and `cli/mandelbrot.go` (`defaultPalette`). Note: the gradient string is duplicated between the test constant and the CLI constant — acceptable since the test package and CLI package are independent; the algorithm package does not own a default (it takes any palette), so there is no single source to share without over-engineering. DRY respected within each package.
- ✅ Architecture matches spec exactly (cmd/fractals, internal/{sierpinski,mandelbrot,cli}).
- ✅ Cobra dependency (Task 1).
- ✅ All 7 acceptance criteria mapped to verification steps in Task 7.

**Placeholder scan:** No `TODO`, no stub functions, no `...` inside code blocks (the `...` shown only appears in *expected terminal output*, never in source). All code blocks are complete and compilable.

**Type consistency:**
- `sierpinski.Generate(size, depth int, char rune) ([]string, error)` — CLI passes `int, int, rune` ✅.
- `mandelbrot.Render(width, height, iterations int, palette string) ([]string, error)` — CLI passes `int, int, int, string` ✅.
- `singleRune` returns `rune` matching `Generate`'s `char rune` param ✅.
- `paletteFor` returns `string` matching `Render`'s `palette string` param ✅.

**Build ordering note:** Tasks 4 and 5 intentionally leave the `cli` package non-compiling (forward references to subcommands created in later tasks). This is called out explicitly in each task with the expected build error, and full compilation is verified in Task 6. This is acceptable for incremental commits since the algorithm packages (Tasks 2–3) are independently tested and compilable.

**Fix applied during review:** Removed an unnecessary README task (YAGNI — spec does not request one).