# Go Fractals CLI - Implementation Plan

## Overview

We're building a CLI tool that generates ASCII art fractals (Sierpinski triangle and Mandelbrot set). The architecture cleanly separates pure algorithm logic (`internal/sierpinski`, `internal/mandelbrot`) from CLI wiring (`internal/cli`) and the entry point (`cmd/fractals`).

The algorithm packages return strings (the rendered fractal) and never touch stdout or flags directly — this makes them trivially testable. The CLI packages handle flag parsing, validation, and printing.

We use TDD throughout: write a failing test, see it fail, implement, see it pass, commit.

## File Structure

| File | Responsibility |
|------|----------------|
| `go.mod` | Module definition, Go version, dependencies |
| `internal/sierpinski/sierpinski.go` | Pure function: generate Sierpinski triangle as a string |
| `internal/sierpinski/sierpinski_test.go` | Tests for the Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure function: generate Mandelbrot set as a string |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for the Mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command, wires subcommands, help text |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand: flags, validation, calls algorithm, prints |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand: flags, validation, calls algorithm, prints |
| `internal/cli/root_test.go` | Tests for CLI behavior (help, subcommand execution, validation errors) |
| `cmd/fractals/main.go` | Entry point: calls `cli.Execute()` |

## Conventions

- Module path: `github.com/example/fractals` (adjust if you have a real repo path, but use this consistently).
- Algorithm functions return `(string, error)` where validation can fail, or `string` where it cannot.
- CLI validation lives in the subcommand `RunE` functions; algorithm functions assume valid input but still guard against panics.

---

### Task 1: Project Setup

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
...
```

- [ ] Verify `go.mod` declares Go 1.21 or later. Open `go.mod` and confirm the `go` directive. If it shows a lower version, set it:

```bash
go mod edit -go=1.21
```

- [ ] Create `cmd/fractals/main.go` as a temporary stub so the project compiles (we'll wire `cli.Execute()` in Task 5):

```go
package main

import "fmt"

func main() {
	fmt.Println("fractals: not yet implemented")
}
```

- [ ] Verify it builds and runs:

```bash
go run ./cmd/fractals
```

Expected output:
```
fractals: not yet implemented
```

- [ ] Commit:

```bash
git init && git add -A && git commit -m "Project setup: go module, cobra dependency, main stub"
```

---

### Task 2: Sierpinski Algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

The algorithm uses the well-known bitwise trick: a cell at row `r`, column `c` is filled if `(r & c) == 0`. This produces a Sierpinski triangle of side `n` for an `n`-row grid. We render `size` rows, indenting each row so the triangle is centered/left-aligned consistently. We use the bit-trick over rows `0..size-1`, printing the `char` where `(row & col) == 0` and a space otherwise. `depth` limits how many rows of detail are rendered: effective rows = `min(size, 2^depth)`.

- [ ] Write the failing test. Create `internal/sierpinski/sierpinski_test.go`:

```go
package sierpinski

import (
	"strings"
	"testing"
)

func TestGenerate_SmallTriangle(t *testing.T) {
	out, err := Generate(4, 5, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	// Rows of a size-4 Sierpinski via (r&c)==0:
	// row0: cols 0,1,2,3 all filled
	// row1: cols where (1&c)==0 -> 0,2
	// row2: cols where (2&c)==0 -> 0,1
	// row3: cols where (3&c)==0 -> 0
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 4 {
		t.Fatalf("expected 4 lines, got %d: %q", len(lines), lines)
	}
	if strings.Count(lines[0], "*") != 4 {
		t.Errorf("row 0 should have 4 stars, got %q", lines[0])
	}
	if strings.Count(lines[1], "*") != 2 {
		t.Errorf("row 1 should have 2 stars, got %q", lines[1])
	}
	if strings.Count(lines[3], "*") != 1 {
		t.Errorf("row 3 should have 1 star, got %q", lines[3])
	}
}

func TestGenerate_CustomChar(t *testing.T) {
	out, err := Generate(2, 1, '#')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "#") {
		t.Errorf("expected output to contain '#', got %q", out)
	}
	if strings.Contains(out, "*") {
		t.Errorf("expected no '*' when char is '#', got %q", out)
	}
}

func TestGenerate_DepthLimitsRows(t *testing.T) {
	// depth 1 -> 2^1 = 2 rows even though size is 8
	out, err := Generate(8, 1, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 2 {
		t.Errorf("expected depth to cap rows at 2, got %d lines", len(lines))
	}
}

func TestGenerate_InvalidSize(t *testing.T) {
	if _, err := Generate(0, 5, '*'); err == nil {
		t.Error("expected error for size 0")
	}
	if _, err := Generate(-1, 5, '*'); err == nil {
		t.Error("expected error for negative size")
	}
}

func TestGenerate_InvalidDepth(t *testing.T) {
	if _, err := Generate(8, 0, '*'); err == nil {
		t.Error("expected error for depth 0")
	}
}
```

- [ ] Run the test to confirm it fails (no implementation yet):

```bash
go test ./internal/sierpinski/
```

Expected output (compilation failure because `Generate` is undefined):
```
# github.com/example/fractals/internal/sierpinski [...]
./sierpinski_test.go:... undefined: Generate
FAIL    github.com/example/fractals/internal/sierpinski [build failed]
```

- [ ] Implement the algorithm. Create `internal/sierpinski/sierpinski.go`:

```go
// Package sierpinski generates ASCII Sierpinski triangles.
package sierpinski

import (
	"fmt"
	"strings"
)

// Generate returns a Sierpinski triangle as a string.
//
// size is the number of rows when not limited by depth.
// depth caps the rendered rows to 2^depth.
// char is the rune used for filled cells; spaces are used elsewhere.
func Generate(size, depth int, char rune) (string, error) {
	if size <= 0 {
		return "", fmt.Errorf("size must be positive, got %d", size)
	}
	if depth <= 0 {
		return "", fmt.Errorf("depth must be positive, got %d", depth)
	}

	rows := size
	if limit := 1 << depth; limit < rows {
		rows = limit
	}

	var b strings.Builder
	for r := 0; r < rows; r++ {
		// Indent so the triangle leans into a pyramid shape.
		b.WriteString(strings.Repeat(" ", rows-r-1))
		for c := 0; c <= r; c++ {
			if r&c == 0 {
				b.WriteRune(char)
			} else {
				b.WriteByte(' ')
			}
			if c < r {
				b.WriteByte(' ')
			}
		}
		b.WriteByte('\n')
	}
	return b.String(), nil
}
```

- [ ] Run the test to confirm it passes:

```bash
go test ./internal/sierpinski/
```

Expected output:
```
ok      github.com/example/fractals/internal/sierpinski 0.00Xs
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add sierpinski algorithm with tests"
```

---

### Task 3: Mandelbrot Algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

We map a fixed region of the complex plane (real `-2.5..1.0`, imaginary `-1.0..1.0`) onto a `width × height` grid. For each cell we iterate `z = z² + c` up to `iterations`, counting escape time. Escape time maps to a character. If a custom `char` is provided (non-zero rune), points inside the set use `char` and escaped points use a space. With the default gradient `" .:-=+*#%@"`, escape count maps across the ramp.

- [ ] Write the failing test. Create `internal/mandelbrot/mandelbrot_test.go`:

```go
package mandelbrot

import (
	"strings"
	"testing"
)

func TestGenerate_Dimensions(t *testing.T) {
	out, err := Generate(20, 10, 50, 0) // 0 char = gradient
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 10 {
		t.Fatalf("expected 10 lines, got %d", len(lines))
	}
	for i, line := range lines {
		if len([]rune(line)) != 20 {
			t.Errorf("line %d expected width 20, got %d: %q", i, len([]rune(line)), line)
		}
	}
}

func TestGenerate_ContainsSetPoints(t *testing.T) {
	// The center-left region around (-0.5, 0) is inside the set, so with the
	// gradient the densest char '@' should appear somewhere.
	out, err := Generate(80, 24, 100, 0)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "@") {
		t.Errorf("expected interior points rendered as '@', got:\n%s", out)
	}
	// And there should be escaped (space) points too.
	if !strings.Contains(out, " ") {
		t.Errorf("expected some escaped points rendered as space")
	}
}

func TestGenerate_CustomChar(t *testing.T) {
	out, err := Generate(40, 20, 100, '#')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	// With a custom char, output contains only that char and spaces.
	for _, r := range out {
		if r != '#' && r != ' ' && r != '\n' {
			t.Errorf("unexpected rune %q in custom-char output", r)
		}
	}
	if !strings.Contains(out, "#") {
		t.Errorf("expected interior points rendered as '#'")
	}
}

func TestGenerate_InvalidInputs(t *testing.T) {
	if _, err := Generate(0, 10, 50, 0); err == nil {
		t.Error("expected error for width 0")
	}
	if _, err := Generate(10, 0, 50, 0); err == nil {
		t.Error("expected error for height 0")
	}
	if _, err := Generate(10, 10, 0, 0); err == nil {
		t.Error("expected error for iterations 0")
	}
}
```

- [ ] Run the test to confirm it fails:

```bash
go test ./internal/mandelbrot/
```

Expected output:
```
# github.com/example/fractals/internal/mandelbrot [...]
./mandelbrot_test.go:... undefined: Generate
FAIL    github.com/example/fractals/internal/mandelbrot [build failed]
```

- [ ] Implement the algorithm. Create `internal/mandelbrot/mandelbrot.go`:

```go
// Package mandelbrot renders the Mandelbrot set as ASCII art.
package mandelbrot

import (
	"fmt"
	"strings"
)

// gradient maps escape counts (low to high "inside-ness") onto characters.
const gradient = " .:-=+*#%@"

// Region of the complex plane to render.
const (
	realMin = -2.5
	realMax = 1.0
	imagMin = -1.0
	imagMax = 1.0
)

// Generate renders the Mandelbrot set as a string of height lines,
// each width characters wide.
//
// iterations is the escape-time limit.
// If char is 0, a gradient is used; otherwise interior points use char
// and escaped points use a space.
func Generate(width, height, iterations int, char rune) (string, error) {
	if width <= 0 {
		return "", fmt.Errorf("width must be positive, got %d", width)
	}
	if height <= 0 {
		return "", fmt.Errorf("height must be positive, got %d", height)
	}
	if iterations <= 0 {
		return "", fmt.Errorf("iterations must be positive, got %d", iterations)
	}

	var b strings.Builder
	for py := 0; py < height; py++ {
		ci := imagMin + (imagMax-imagMin)*float64(py)/float64(height-1)
		if height == 1 {
			ci = (imagMin + imagMax) / 2
		}
		for px := 0; px < width; px++ {
			cr := realMin + (realMax-realMin)*float64(px)/float64(width-1)
			if width == 1 {
				cr = (realMin + realMax) / 2
			}
			n := escapeCount(cr, ci, iterations)
			b.WriteRune(cell(n, iterations, char))
		}
		b.WriteByte('\n')
	}
	return b.String(), nil
}

// escapeCount returns the iteration at which z escapes, or iterations if it
// stays bounded (i.e. the point is considered inside the set).
func escapeCount(cr, ci float64, iterations int) int {
	var zr, zi float64
	for n := 0; n < iterations; n++ {
		zr2, zi2 := zr*zr, zi*zi
		if zr2+zi2 > 4.0 {
			return n
		}
		zi = 2*zr*zi + ci
		zr = zr2 - zi2 + cr
	}
	return iterations
}

// cell maps an escape count to a rune.
func cell(n, iterations int, char rune) rune {
	inside := n >= iterations
	if char != 0 {
		if inside {
			return char
		}
		return ' '
	}
	if inside {
		return rune(gradient[len(gradient)-1])
	}
	// Map escape count onto gradient[0 .. len-2].
	idx := n * (len(gradient) - 1) / iterations
	if idx > len(gradient)-2 {
		idx = len(gradient) - 2
	}
	return rune(gradient[idx])
}
```

- [ ] Run the test to confirm it passes:

```bash
go test ./internal/mandelbrot/
```

Expected output:
```
ok      github.com/example/fractals/internal/mandelbrot 0.00Xs
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add mandelbrot algorithm with tests"
```

---

### Task 4: CLI Commands

**Files:** `internal/cli/root.go`, `internal/cli/sierpinski.go`, `internal/cli/mandelbrot.go`, `internal/cli/root_test.go`

We build cobra commands. The root command holds no logic beyond help and registering subcommands. Each subcommand defines flags, validates by delegating to the algorithm (which returns errors), and prints to the command's configured output stream (so tests can capture it).

The `--char` flag is a string. Empty string means "use default" (gradient for mandelbrot, `*` for sierpinski). A multi-rune string is a validation error. We convert to `rune` before passing to the algorithm.

- [ ] Write the failing test. Create `internal/cli/root_test.go`:

```go
package cli

import (
	"bytes"
	"strings"
	"testing"
)

// execute runs the root command with the given args, capturing stdout/stderr.
func execute(args ...string) (string, error) {
	cmd := NewRootCmd()
	buf := &bytes.Buffer{}
	cmd.SetOut(buf)
	cmd.SetErr(buf)
	cmd.SetArgs(args)
	err := cmd.Execute()
	return buf.String(), err
}

func TestRootHelp(t *testing.T) {
	out, err := execute("--help")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "sierpinski") || !strings.Contains(out, "mandelbrot") {
		t.Errorf("help should list subcommands, got:\n%s", out)
	}
}

func TestSierpinskiDefault(t *testing.T) {
	out, err := execute("sierpinski")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "*") {
		t.Errorf("expected default sierpinski to contain '*', got:\n%s", out)
	}
}

func TestSierpinskiFlags(t *testing.T) {
	out, err := execute("sierpinski", "--size", "4", "--depth", "5", "--char", "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "#") {
		t.Errorf("expected custom char '#', got:\n%s", out)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 4 {
		t.Errorf("expected 4 rows for size 4, got %d", len(lines))
	}
}

func TestSierpinskiInvalidChar(t *testing.T) {
	_, err := execute("sierpinski", "--char", "ab")
	if err == nil {
		t.Error("expected error for multi-rune char")
	}
}

func TestSierpinskiInvalidSize(t *testing.T) {
	_, err := execute("sierpinski", "--size", "0")
	if err == nil {
		t.Error("expected error for size 0")
	}
}

func TestMandelbrotDefault(t *testing.T) {
	out, err := execute("mandelbrot", "--width", "40", "--height", "12")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 12 {
		t.Errorf("expected 12 rows, got %d", len(lines))
	}
}

func TestMandelbrotCustomChar(t *testing.T) {
	out, err := execute("mandelbrot", "--width", "40", "--height", "12", "--char", "@")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	for _, r := range out {
		if r != '@' && r != ' ' && r != '\n' {
			t.Errorf("unexpected rune %q with custom char", r)
		}
	}
}

func TestMandelbrotInvalidWidth(t *testing.T) {
	_, err := execute("mandelbrot", "--width", "0")
	if err == nil {
		t.Error("expected error for width 0")
	}
}
```

- [ ] Run the test to confirm it fails:

```bash
go test ./internal/cli/
```

Expected output:
```
# github.com/example/fractals/internal/cli [...]
./root_test.go:... undefined: NewRootCmd
FAIL    github.com/example/fractals/internal/cli [build failed]
```

- [ ] Implement the root command. Create `internal/cli/root.go`:

```go
// Package cli wires up the fractals command-line interface.
package cli

import (
	"fmt"

	"github.com/spf13/cobra"
)

// NewRootCmd builds the root command with all subcommands registered.
func NewRootCmd() *cobra.Command {
	root := &cobra.Command{
		Use:   "fractals",
		Short: "Generate ASCII art fractals",
		Long:  "fractals generates ASCII art fractals: Sierpinski triangles and the Mandelbrot set.",
	}
	root.AddCommand(newSierpinskiCmd())
	root.AddCommand(newMandelbrotCmd())
	return root
}

// Execute runs the root command. Called from main.
func Execute() error {
	if err := NewRootCmd().Execute(); err != nil {
		return fmt.Errorf("fractals: %w", err)
	}
	return nil
}

// parseChar converts a --char flag value into a rune.
// An empty string yields 0 (meaning "use default"). A value longer than one
// rune is an error.
func parseChar(s string) (rune, error) {
	if s == "" {
		return 0, nil
	}
	runes := []rune(s)
	if len(runes) != 1 {
		return 0, fmt.Errorf("--char must be a single character, got %q", s)
	}
	return runes[0], nil
}
```

- [ ] Implement the sierpinski subcommand. Create `internal/cli/sierpinski.go`:

```go
package cli

import (
	"github.com/example/fractals/internal/sierpinski"
	"github.com/spf13/cobra"
)

func newSierpinskiCmd() *cobra.Command {
	var (
		size     int
		depth    int
		charFlag string
	)

	cmd := &cobra.Command{
		Use:   "sierpinski",
		Short: "Generate a Sierpinski triangle",
		RunE: func(cmd *cobra.Command, args []string) error {
			char, err := parseChar(charFlag)
			if err != nil {
				return err
			}
			if char == 0 {
				char = '*'
			}
			out, err := sierpinski.Generate(size, depth, char)
			if err != nil {
				return err
			}
			cmd.Print(out)
			return nil
		},
	}

	cmd.Flags().IntVar(&size, "size", 32, "width of the triangle base in characters")
	cmd.Flags().IntVar(&depth, "depth", 5, "recursion depth")
	cmd.Flags().StringVar(&charFlag, "char", "", "character to use for filled points (default '*')")
	return cmd
}
```

- [ ] Implement the mandelbrot subcommand. Create `internal/cli/mandelbrot.go`:

```go
package cli

import (
	"github.com/example/fractals/internal/mandelbrot"
	"github.com/spf13/cobra"
)

func newMandelbrotCmd() *cobra.Command {
	var (
		width      int
		height     int
		iterations int
		charFlag   string
	)

	cmd := &cobra.Command{
		Use:   "mandelbrot",
		Short: "Render the Mandelbrot set as ASCII art",
		RunE: func(cmd *cobra.Command, args []string) error {
			char, err := parseChar(charFlag)
			if err != nil {
				return err
			}
			// char == 0 tells the algorithm to use the gradient.
			out, err := mandelbrot.Generate(width, height, iterations, char)
			if err != nil {
				return err
			}
			cmd.Print(out)
			return nil
		},
	}

	cmd.Flags().IntVar(&width, "width", 80, "output width in characters")
	cmd.Flags().IntVar(&height, "height", 24, "output height in characters")
	cmd.Flags().IntVar(&iterations, "iterations", 100, "maximum iterations for escape calculation")
	cmd.Flags().StringVar(&charFlag, "char", "", "single character, or omit for gradient \" .:-=+*#%@\"")
	return cmd
}
```

- [ ] Run the test to confirm it passes:

```bash
go test ./internal/cli/
```

Expected output:
```
ok      github.com/example/fractals/internal/cli 0.00Xs
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add CLI root and subcommands with tests"
```

---

### Task 5: Wire Entry Point

**Files:** `cmd/fractals/main.go`

Replace the stub with the real entry point that calls `cli.Execute()` and exits non-zero on error.

- [ ] Replace the contents of `cmd/fractals/main.go`:

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

- [ ] Verify the full build:

```bash
go build ./...
```

Expected output: no output (success).

- [ ] Run the help acceptance check (Acceptance Criterion 1):

```bash
go run ./cmd/fractals --help
```

Expected output (abridged) includes:
```
fractals generates ASCII art fractals: Sierpinski triangles and the Mandelbrot set.

Usage:
  fractals [command]

Available Commands:
  ...
  mandelbrot  Render the Mandelbrot set as ASCII art
  sierpinski  Generate a Sierpinski triangle
...
```

- [ ] Run the sierpinski acceptance check (Acceptance Criterion 2):

```bash
go run ./cmd/fractals sierpinski --size 16 --depth 4
```

Expected: a left-leaning triangle of `*` characters, 16 rows (capped to 2^4=16), e.g. the first row indented furthest and the bottom row widest.

- [ ] Run the mandelbrot acceptance check (Acceptance Criterion 3):

```bash
go run ./cmd/fractals mandelbrot --width 80 --height 24
```

Expected: an 80×24 block of gradient characters showing the recognizable bulb-and-disc Mandelbrot shape with `@` in the interior.

- [ ] Verify an invalid input produces a clear error (Acceptance Criterion 6):

```bash
go run ./cmd/fractals sierpinski --size 0
```

Expected output on stderr and non-zero exit:
```
fractals: size must be positive, got 0
```

- [ ] Verify invalid char:

```bash
go run ./cmd/fractals mandelbrot --char ab
```

Expected:
```
fractals: --char must be a single character, got "ab"
```

- [ ] Commit:

```bash
git add -A && git commit -m "Wire main entry point to cli.Execute"
```

---

### Task 6: Final Verification

**Files:** none (verification only)

- [ ] Run the entire test suite:

```bash
go test ./...
```

Expected output:
```
ok      github.com/example/fractals/internal/cli ...
ok      github.com/example/fractals/internal/mandelbrot ...
ok      github.com/example/fractals/internal/sierpinski ...
```
(and `cmd/fractals` reports `no test files`, which is fine)

- [ ] Run `go vet` to catch issues:

```bash
go vet ./...
```

Expected output: no output (success).

- [ ] Confirm `go.mod` is tidy:

```bash
go mod tidy
git diff --exit-code go.mod go.sum
```

Expected: no diff (exit code 0). If there is a diff, commit it:

```bash
git add -A && git commit -m "Tidy go.mod/go.sum"
```

---

## Self-Review

**Spec coverage check:**

1. ✅ `fractals --help` shows usage — Task 5 verification + `TestRootHelp`.
2. ✅ `fractals sierpinski` outputs a recognizable triangle — Task 5 + `TestSierpinskiDefault`.
3. ✅ `fractals mandelbrot` outputs a recognizable Mandelbrot set — Task 5 + `TestMandelbrotDefault`, `TestGenerate_ContainsSetPoints`.
4. ✅ `--size`, `--width`, `--height`, `--depth`, `--iterations` flags work — defined in Task 4 subcommands; defaults match spec (size 32, depth 5, width 80, height 24, iterations 100).
5. ✅ `--char` customizes output — `parseChar` + `TestSierpinskiFlags`, `TestMandelbrotCustomChar`. Empty `--char` defaults to `*` (sierpinski) / gradient (mandelbrot).
6. ✅ Invalid inputs produce clear errors — validation in algorithm packages, surfaced via `RunE`; covered by `TestSierpinskiInvalidSize`, `TestMandelbrotInvalidWidth`, `TestSierpinskiInvalidChar`, and Task 5 manual checks.
7. ✅ All tests pass — Task 6.

**Architecture match:** File layout matches the spec exactly (`cmd/fractals/main.go`, `internal/{sierpinski,mandelbrot,cli}/...`).

**Placeholder scan:** No `TODO`, no stubbed function bodies remain after Task 5 (the Task 1 stub is fully replaced). Module path `github.com/example/fractals` is used consistently across imports in `cli/sierpinski.go`, `cli/mandelbrot.go`, and `cmd/fractals/main.go`.

**Type consistency:** Algorithm `Generate` signatures are `(int, int, rune) (string, error)` (sierpinski) and `(int, int, int, rune) (string, error)` (mandelbrot); CLI passes `int` flags and a `rune` from `parseChar`. The gradient default is signaled by `char == 0`, handled in `mandelbrot.cell`. Consistent throughout.

**Note on default gradient char:** the spec's default mandelbrot gradient `" .:-=+*#%@"` is embedded as the `gradient` constant and used when `--char` is omitted (rune 0), matching the documented flag help text.