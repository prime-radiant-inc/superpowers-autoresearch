# Go Fractals CLI - Implementation Plan

## Overview

We are building a command-line tool in Go that generates ASCII art fractals (Sierpinski triangle and Mandelbrot set). This plan assumes zero context for the codebase. Follow each step in order: write the failing test, run it to confirm failure, implement, run to confirm pass, commit.

## File Structure

```
go.mod                              # Module definition + deps
cmd/fractals/main.go                # Entry point; calls cli.Execute()
internal/sierpinski/sierpinski.go   # Generate(size, depth, char) -> []string + validation
internal/sierpinski/sierpinski_test.go
internal/mandelbrot/mandelbrot.go   # Generate(width, height, iterations, charset) -> []string + validation
internal/mandelbrot/mandelbrot_test.go
internal/cli/root.go                # Root cobra command + Execute()
internal/cli/sierpinski.go          # sierpinski subcommand wiring
internal/cli/mandelbrot.go          # mandelbrot subcommand wiring
```

Responsibilities:
- **Algorithm packages** (`internal/sierpinski`, `internal/mandelbrot`): pure functions, no I/O, no cobra. Return `[]string` (rows) and `error` for invalid input. Fully unit-tested.
- **CLI packages** (`internal/cli`): flag parsing, calls algorithm functions, prints to stdout.
- **Entry point** (`cmd/fractals/main.go`): thin wrapper.

---

### Task 1: Project Scaffolding

**Files:** `go.mod`, `cmd/fractals/main.go`

- [ ] Initialize the module:

```bash
go mod init github.com/example/fractals
```

Expected output:
```
go: creating new go.mod: module github.com/example/fractals
```

- [ ] Add the cobra dependency:

```bash
go get github.com/spf13/cobra@latest
```

Expected output (version may differ):
```
go: added github.com/spf13/cobra v1.8.x
```

- [ ] Create `cmd/fractals/main.go` with a placeholder that compiles. We will replace `cli.Execute()` once the cli package exists; for now use a stub so the build works:

```go
package main

import "fmt"

func main() {
	fmt.Println("fractals")
}
```

- [ ] Confirm it builds and runs:

```bash
go run ./cmd/fractals
```

Expected output:
```
fractals
```

- [ ] Commit:

```bash
git add -A && git commit -m "Scaffold module and entry point"
```

---

### Task 2: Sierpinski Algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

We use the bitwise rule: cell `(row, col)` is filled when `(col & row) == col`. This produces a Sierpinski triangle. `size` is the number of rows; `depth` limits rows to `min(size, 2^depth)` so increasing depth reveals more detail up to the size cap. `char` is the filled character; empty rows are space-padded.

- [ ] Write the failing test file `internal/sierpinski/sierpinski_test.go`:

```go
package sierpinski

import (
	"strings"
	"testing"
)

func TestGenerateRowCount(t *testing.T) {
	rows, err := Generate(8, 5, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 8 {
		t.Fatalf("expected 8 rows, got %d", len(rows))
	}
}

func TestGenerateTopRowSingleChar(t *testing.T) {
	rows, err := Generate(8, 5, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if strings.Count(rows[0], "*") != 1 {
		t.Fatalf("expected exactly 1 star in top row, got %q", rows[0])
	}
}

func TestGenerateUsesChar(t *testing.T) {
	rows, err := Generate(4, 5, '#')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(rows, "\n")
	if strings.Contains(joined, "*") {
		t.Fatalf("output should not contain default char: %q", joined)
	}
	if !strings.Contains(joined, "#") {
		t.Fatalf("output should contain custom char: %q", joined)
	}
}

func TestGenerateDepthLimitsRows(t *testing.T) {
	// depth 2 => 2^2 = 4 effective rows even though size is 16
	rows, err := Generate(16, 2, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 4 {
		t.Fatalf("expected 4 rows when depth caps it, got %d", len(rows))
	}
}

func TestGenerateInvalidSize(t *testing.T) {
	if _, err := Generate(0, 5, '*'); err == nil {
		t.Fatal("expected error for size 0")
	}
}

func TestGenerateInvalidDepth(t *testing.T) {
	if _, err := Generate(8, 0, '*'); err == nil {
		t.Fatal("expected error for depth 0")
	}
}
```

- [ ] Run the test to see it fail (package has no `Generate` yet):

```bash
go test ./internal/sierpinski/
```

Expected output (compilation failure):
```
internal/sierpinski/sierpinski_test.go:...: undefined: Generate
FAIL    github.com/example/fractals/internal/sierpinski [build failed]
```

- [ ] Implement `internal/sierpinski/sierpinski.go`:

```go
package sierpinski

import (
	"fmt"
	"strings"
)

// Generate builds a Sierpinski triangle.
// size  = number of rows (triangle base width grows with rows).
// depth = recursion depth; effective rows = min(size, 2^depth).
// char  = filled character.
// Returns one string per row.
func Generate(size, depth int, char rune) ([]string, error) {
	if size < 1 {
		return nil, fmt.Errorf("size must be >= 1, got %d", size)
	}
	if depth < 1 {
		return nil, fmt.Errorf("depth must be >= 1, got %d", depth)
	}

	maxRows := 1
	for i := 0; i < depth; i++ {
		maxRows *= 2
	}
	rowCount := size
	if maxRows < rowCount {
		rowCount = maxRows
	}

	rows := make([]string, rowCount)
	for r := 0; r < rowCount; r++ {
		var b strings.Builder
		// Leading spaces to center the triangle.
		for s := 0; s < rowCount-r-1; s++ {
			b.WriteRune(' ')
		}
		for c := 0; c <= r; c++ {
			if (c & r) == c {
				b.WriteRune(char)
			} else {
				b.WriteRune(' ')
			}
			if c < r {
				b.WriteRune(' ')
			}
		}
		rows[r] = b.String()
	}
	return rows, nil
}
```

- [ ] Run the tests to confirm they pass:

```bash
go test ./internal/sierpinski/
```

Expected output:
```
ok      github.com/example/fractals/internal/sierpinski 0.00s
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add sierpinski algorithm with tests"
```

---

### Task 3: Mandelbrot Algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

`Generate` maps the complex plane region (re: -2.5..1.0, im: -1.25..1.25) onto a `width`x`height` grid. For each cell it computes escape iterations and maps to a character in `charset` (string of ramp characters, first = inside/most iterations behavior defined below). If `charset` has length 1, that single char marks points inside the set and space marks outside.

- [ ] Write the failing test file `internal/mandelbrot/mandelbrot_test.go`:

```go
package mandelbrot

import (
	"strings"
	"testing"
)

const gradient = " .:-=+*#%@"

func TestGenerateDimensions(t *testing.T) {
	rows, err := Generate(40, 12, 50, gradient)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 12 {
		t.Fatalf("expected 12 rows, got %d", len(rows))
	}
	for i, row := range rows {
		if len([]rune(row)) != 40 {
			t.Fatalf("row %d width = %d, want 40", i, len([]rune(row)))
		}
	}
}

func TestGenerateCenterInsideSet(t *testing.T) {
	// The center of the plane (~ -0.75) is inside the set, mapping to the
	// last gradient char (max iterations).
	rows, err := Generate(80, 24, 100, gradient)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	midRow := rows[len(rows)/2]
	if !strings.ContainsRune(midRow, '@') {
		t.Fatalf("expected '@' (inside set) in middle row, got %q", midRow)
	}
}

func TestGenerateSingleChar(t *testing.T) {
	rows, err := Generate(40, 12, 50, "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(rows, "\n")
	if !strings.Contains(joined, "#") {
		t.Fatalf("expected '#' in output, got %q", joined)
	}
	for _, r := range joined {
		if r != '#' && r != ' ' && r != '\n' {
			t.Fatalf("single-char mode should only emit '#' or space, got %q", r)
		}
	}
}

func TestGenerateInvalidWidth(t *testing.T) {
	if _, err := Generate(0, 12, 50, gradient); err == nil {
		t.Fatal("expected error for width 0")
	}
}

func TestGenerateInvalidHeight(t *testing.T) {
	if _, err := Generate(40, 0, 50, gradient); err == nil {
		t.Fatal("expected error for height 0")
	}
}

func TestGenerateInvalidIterations(t *testing.T) {
	if _, err := Generate(40, 12, 0, gradient); err == nil {
		t.Fatal("expected error for iterations 0")
	}
}

func TestGenerateEmptyCharset(t *testing.T) {
	if _, err := Generate(40, 12, 50, ""); err == nil {
		t.Fatal("expected error for empty charset")
	}
}
```

- [ ] Run to see it fail:

```bash
go test ./internal/mandelbrot/
```

Expected output:
```
internal/mandelbrot/mandelbrot_test.go:...: undefined: Generate
FAIL    github.com/example/fractals/internal/mandelbrot [build failed]
```

- [ ] Implement `internal/mandelbrot/mandelbrot.go`:

```go
package mandelbrot

import (
	"fmt"
	"strings"
)

const (
	reMin = -2.5
	reMax = 1.0
	imMin = -1.25
	imMax = 1.25
)

// Generate renders the Mandelbrot set as ASCII rows.
// width, height = output dimensions in characters.
// iterations    = max escape iterations.
// charset       = ramp; index chosen by iteration count.
//
//	If len(charset) == 1, that char marks points inside the set,
//	space marks outside.
func Generate(width, height, iterations int, charset string) ([]string, error) {
	if width < 1 {
		return nil, fmt.Errorf("width must be >= 1, got %d", width)
	}
	if height < 1 {
		return nil, fmt.Errorf("height must be >= 1, got %d", height)
	}
	if iterations < 1 {
		return nil, fmt.Errorf("iterations must be >= 1, got %d", iterations)
	}
	ramp := []rune(charset)
	if len(ramp) == 0 {
		return nil, fmt.Errorf("charset must not be empty")
	}

	single := len(ramp) == 1
	rows := make([]string, height)
	for py := 0; py < height; py++ {
		var b strings.Builder
		ci := imMin + (imMax-imMin)*float64(py)/float64(height-1)
		if height == 1 {
			ci = (imMin + imMax) / 2
		}
		for px := 0; px < width; px++ {
			cr := reMin + (reMax-reMin)*float64(px)/float64(width-1)
			if width == 1 {
				cr = (reMin + reMax) / 2
			}
			n := escape(cr, ci, iterations)
			b.WriteRune(charFor(n, iterations, ramp, single))
		}
		rows[py] = b.String()
	}
	return rows, nil
}

// escape returns the iteration count before |z| > 2, capped at maxIter.
func escape(cr, ci float64, maxIter int) int {
	var zr, zi float64
	for n := 0; n < maxIter; n++ {
		zr2, zi2 := zr*zr, zi*zi
		if zr2+zi2 > 4 {
			return n
		}
		zi = 2*zr*zi + ci
		zr = zr2 - zi2 + cr
	}
	return maxIter
}

func charFor(n, maxIter int, ramp []rune, single bool) rune {
	if single {
		if n >= maxIter {
			return ramp[0]
		}
		return ' '
	}
	// Map n in [0, maxIter] to an index in ramp.
	idx := n * (len(ramp) - 1) / maxIter
	if idx >= len(ramp) {
		idx = len(ramp) - 1
	}
	return ramp[idx]
}
```

- [ ] Run to confirm pass:

```bash
go test ./internal/mandelbrot/
```

Expected output:
```
ok      github.com/example/fractals/internal/mandelbrot 0.00s
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add mandelbrot algorithm with tests"
```

---

### Task 4: CLI Root Command

**Files:** `internal/cli/root.go`, `cmd/fractals/main.go`

- [ ] Create `internal/cli/root.go`:

```go
package cli

import (
	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "fractals",
	Short: "Generate ASCII art fractals",
	Long:  "fractals generates ASCII art fractals (Sierpinski triangle, Mandelbrot set).",
}

// Execute runs the root command and returns a non-nil error on failure.
func Execute() error {
	return rootCmd.Execute()
}
```

- [ ] Replace `cmd/fractals/main.go` to call the CLI:

```go
package main

import (
	"fmt"
	"os"

	"github.com/example/fractals/internal/cli"
)

func main() {
	if err := cli.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
```

- [ ] Verify help works:

```bash
go run ./cmd/fractals --help
```

Expected output (contains):
```
fractals generates ASCII art fractals (Sierpinski triangle, Mandelbrot set).

Usage:
  fractals [command]
...
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add root CLI command"
```

---

### Task 5: Sierpinski Subcommand

**Files:** `internal/cli/sierpinski.go`

The `--char` flag is a string; we take the first rune and error if empty or multi-rune.

- [ ] Create `internal/cli/sierpinski.go`:

```go
package cli

import (
	"fmt"

	"github.com/example/fractals/internal/sierpinski"
	"github.com/spf13/cobra"
)

func init() {
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
			for _, row := range rows {
				fmt.Fprintln(cmd.OutOrStdout(), row)
			}
			return nil
		},
	}

	cmd.Flags().IntVar(&size, "size", 32, "Width of the triangle base in characters")
	cmd.Flags().IntVar(&depth, "depth", 5, "Recursion depth")
	cmd.Flags().StringVar(&char, "char", "*", "Character to use for filled points")

	rootCmd.AddCommand(cmd)
}

// singleRune validates that s is exactly one rune and returns it.
func singleRune(s string) (rune, error) {
	rs := []rune(s)
	if len(rs) != 1 {
		return 0, fmt.Errorf("--char must be exactly one character, got %q", s)
	}
	return rs[0], nil
}
```

- [ ] Verify the default triangle renders:

```bash
go run ./cmd/fractals sierpinski --size 8 --depth 5
```

Expected output (recognizable triangle, leading spaces preserved):
```
       *
      * *
     *   *
    * * * *
   *       *
  * *     * *
 *   *   *   *
* * * * * * * *
```

- [ ] Verify custom char and invalid char error:

```bash
go run ./cmd/fractals sierpinski --size 4 --char '#'
```

Expected output (uses `#`):
```
   #
  # #
 #   #
# # # #
```

```bash
go run ./cmd/fractals sierpinski --char 'ab'
```

Expected output (to stderr, exit 1):
```
--char must be exactly one character, got "ab"
```

- [ ] Verify invalid size error:

```bash
go run ./cmd/fractals sierpinski --size 0
```

Expected output (to stderr, exit 1):
```
Error: size must be >= 1, got 0
...
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add sierpinski subcommand"
```

---

### Task 6: Mandelbrot Subcommand

**Files:** `internal/cli/mandelbrot.go`

The `--char` flag defaults to empty string meaning "use gradient". If the user supplies a value, it must be exactly one rune (single-char mode).

- [ ] Create `internal/cli/mandelbrot.go`:

```go
package cli

import (
	"fmt"

	"github.com/example/fractals/internal/mandelbrot"
	"github.com/spf13/cobra"
)

const gradient = " .:-=+*#%@"

func init() {
	var (
		width      int
		height     int
		iterations int
		char       string
	)

	cmd := &cobra.Command{
		Use:   "mandelbrot",
		Short: "Render the Mandelbrot set as ASCII art",
		RunE: func(cmd *cobra.Command, args []string) error {
			charset := gradient
			if char != "" {
				if _, err := singleRune(char); err != nil {
					return err
				}
				charset = char
			}
			rows, err := mandelbrot.Generate(width, height, iterations, charset)
			if err != nil {
				return err
			}
			for _, row := range rows {
				fmt.Fprintln(cmd.OutOrStdout(), row)
			}
			return nil
		},
	}

	cmd.Flags().IntVar(&width, "width", 80, "Output width in characters")
	cmd.Flags().IntVar(&height, "height", 24, "Output height in characters")
	cmd.Flags().IntVar(&iterations, "iterations", 100, "Maximum iterations for escape calculation")
	cmd.Flags().StringVar(&char, "char", "", "Single character, or omit for gradient \" .:-=+*#%@\"")

	rootCmd.AddCommand(cmd)
}
```

- [ ] Verify the default render produces a recognizable Mandelbrot set:

```bash
go run ./cmd/fractals mandelbrot --width 80 --height 24
```

Expected output: a rectangle 24 lines tall, 80 chars wide, with a bulbous `@`-filled body on the left-center and a cardioid tail. (Visual check only.)

- [ ] Verify single-char mode:

```bash
go run ./cmd/fractals mandelbrot --width 40 --height 12 --char '#'
```

Expected output: 12 lines of 40 chars containing only `#` and spaces, forming the set silhouette.

- [ ] Verify invalid inputs error:

```bash
go run ./cmd/fractals mandelbrot --width 0
```

Expected output (to stderr, exit 1):
```
Error: width must be >= 1, got 0
...
```

```bash
go run ./cmd/fractals mandelbrot --char 'xy'
```

Expected output (to stderr, exit 1):
```
--char must be exactly one character, got "xy"
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add mandelbrot subcommand"
```

---

### Task 7: Full Test Pass & Build Verification

**Files:** none (verification only)

- [ ] Run the entire test suite:

```bash
go test ./...
```

Expected output:
```
ok      github.com/example/fractals/internal/mandelbrot 0.00s
ok      github.com/example/fractals/internal/sierpinski 0.00s
```
(The `cli` and `main` packages have no tests and may report `no test files`.)

- [ ] Run `go vet` to catch issues:

```bash
go vet ./...
```

Expected output: no output (success).

- [ ] Build a binary and run acceptance checks:

```bash
go build -o fractals ./cmd/fractals
./fractals --help
./fractals sierpinski
./fractals mandelbrot
```

Expected: help text, a triangle, and a Mandelbrot rectangle, respectively.

- [ ] Commit any cleanup (e.g., add `/fractals` binary to `.gitignore`):

```bash
echo "/fractals" >> .gitignore
git add -A && git commit -m "Add gitignore for built binary"
```

---

## Self-Review

**Spec coverage:**
1. `fractals --help` shows usage — Task 4. ✓
2. `fractals sierpinski` outputs a triangle — Task 5. ✓
3. `fractals mandelbrot` outputs a Mandelbrot set — Task 6. ✓
4. `--size`, `--width`, `--height`, `--depth`, `--iterations` flags — Tasks 5 & 6 register all five. ✓
5. `--char` customizes output — Task 5 (sierpinski, required single rune) and Task 6 (mandelbrot, optional, gradient default). ✓
6. Invalid inputs produce clear errors — algorithm functions return `fmt.Errorf` messages; cobra prints them with `Error:` prefix; `singleRune` validates `--char`. Verified in Tasks 5 & 6. ✓
7. All tests pass — Task 7. ✓

**Architecture match:** File layout matches the spec exactly (`cmd/fractals`, `internal/sierpinski`, `internal/mandelbrot`, `internal/cli` with `root.go`, `sierpinski.go`, `mandelbrot.go`). ✓

**Placeholder scan:** No `TODO`/`FIXME`/`...` left in code blocks; the `...` in expected-output blocks denote omitted cobra help text, not code. The module path `github.com/example/fractals` is used consistently across `main.go`, both cli files, and `go.mod`. ✓

**Type consistency:** `sierpinski.Generate(size, depth int, char rune) ([]string, error)` and `mandelbrot.Generate(width, height, iterations int, charset string) ([]string, error)` — call sites in the cli pass matching types (`singleRune` yields a `rune` for sierpinski; mandelbrot passes a `string` charset). ✓

**Note on `gradient` constant:** Defined as a test-local `const gradient` in `mandelbrot_test.go` (package `mandelbrot`) and as a package-level `const gradient` in `internal/cli/mandelbrot.go` (package `cli`). These are in different packages, so there is no collision. ✓

**Edge case:** `Generate` for mandelbrot guards `width == 1` / `height == 1` to avoid division by zero from `float64(width-1)`. ✓