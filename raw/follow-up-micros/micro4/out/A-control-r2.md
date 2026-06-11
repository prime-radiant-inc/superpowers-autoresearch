# Go Fractals CLI - Implementation Plan

## Overview

This plan implements a command-line tool that generates ASCII art fractals (Sierpinski triangle and Mandelbrot set). We use TDD throughout: write a failing test, see it fail, implement, see it pass, commit.

The codebase starts empty. You will create a Go module, two pure algorithm packages (`sierpinski`, `mandelbrot`), a CLI package using cobra, and a `main.go` entry point.

## File Structure

| File | Responsibility |
|------|----------------|
| `go.mod` | Module definition, Go version, dependencies |
| `internal/sierpinski/sierpinski.go` | Pure function generating Sierpinski triangle as `[]string` |
| `internal/sierpinski/sierpinski_test.go` | Tests for Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure function generating Mandelbrot set as `[]string` |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for Mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command, help, version |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand: flag parsing, validation, calls algorithm |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand: flag parsing, validation, calls algorithm |
| `cmd/fractals/main.go` | Entry point: calls `cli.Execute()` |

### Design Decisions (read before starting)

- **Algorithm packages are pure**: they take primitives, return `[]string` (one entry per row), and never print or call `os.Exit`. This makes them trivially testable.
- **CLI packages handle I/O and validation**: they parse flags, validate ranges, write to an `io.Writer`, and return errors. Cobra prints errors.
- **`char` semantics**:
  - Sierpinski default `*`. A filled point uses `char`; empty point uses a space.
  - Mandelbrot default is the gradient `" .:-=+*#%@"`. If `--char` is supplied, every "in-set-ish" cell uses that single char based on a threshold; cells that escape immediately are spaces. (See Task 3 for exact mapping.)

---

### Task 1: Project Scaffold

**Files:** `go.mod`, `cmd/fractals/main.go`, `internal/cli/root.go`

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

Expected: output lines ending with `go: added github.com/spf13/cobra v1.x.x` (exact patch version may vary).

- [ ] Create `internal/cli/root.go` with a minimal root command:

```go
package cli

import (
	"github.com/spf13/cobra"
)

// rootCmd is the base command when called without any subcommands.
var rootCmd = &cobra.Command{
	Use:   "fractals",
	Short: "Generate ASCII art fractals",
	Long:  "fractals generates ASCII art fractals such as the Sierpinski triangle and the Mandelbrot set.",
}

// Execute runs the root command and returns any error encountered.
func Execute() error {
	return rootCmd.Execute()
}
```

- [ ] Create `cmd/fractals/main.go`:

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

- [ ] Tidy and verify it builds:

```bash
go mod tidy && go build ./...
```

Expected: no output, exit code 0.

- [ ] Verify the help works:

```bash
go run ./cmd/fractals --help
```

Expected output contains:
```
fractals generates ASCII art fractals such as the Sierpinski triangle and the Mandelbrot set.

Usage:
  fractals [command]
```

- [ ] Commit:

```bash
git add -A && git commit -m "Scaffold fractals CLI module with root command"
```

---

### Task 2: Sierpinski Algorithm Package

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

We use the classic bitwise property: cell `(row, col)` is filled when `(row & col) == 0` for a triangle of height `size`. `depth` controls how many recursive subdivisions are visible by capping the effective resolution: the rendered triangle has `2^depth` rows, then is scaled to `size`. To keep this simple and testable, we render `rows = min(size, 2^depth)` rows, each row `r` having `2*r+1` relevant positions centered in a field of width `size`.

The function signature:

```go
func Generate(size, depth int, char rune) []string
```

Each returned string is one row, left-padded with spaces so the triangle is centered.

- [ ] Write the failing test `internal/sierpinski/sierpinski_test.go`:

```go
package sierpinski

import (
	"strings"
	"testing"
)

func TestGenerateRowCount(t *testing.T) {
	rows := Generate(8, 5, '*')
	if len(rows) != 8 {
		t.Fatalf("expected 8 rows, got %d", len(rows))
	}
}

func TestGenerateDepthCapsRows(t *testing.T) {
	// 2^2 = 4, which is less than size 16, so we expect 4 rows.
	rows := Generate(16, 2, '*')
	if len(rows) != 4 {
		t.Fatalf("expected 4 rows (capped by depth), got %d", len(rows))
	}
}

func TestGenerateTopRowSingleChar(t *testing.T) {
	rows := Generate(8, 5, '*')
	if strings.Count(rows[0], "*") != 1 {
		t.Fatalf("expected exactly 1 star in top row, got %q", rows[0])
	}
}

func TestGenerateUsesCustomChar(t *testing.T) {
	rows := Generate(4, 5, '#')
	joined := strings.Join(rows, "\n")
	if strings.Contains(joined, "*") {
		t.Fatalf("output should not contain '*' when char is '#': %q", joined)
	}
	if !strings.Contains(joined, "#") {
		t.Fatalf("output should contain '#': %q", joined)
	}
}

func TestGenerateLastRowAllFilled(t *testing.T) {
	// For a power-of-two size, the bottom row of the (row & col)==0 triangle
	// alternates, but the first and last filled positions are always set.
	rows := Generate(8, 5, '*')
	last := rows[len(rows)-1]
	if !strings.Contains(last, "*") {
		t.Fatalf("expected last row to contain stars, got %q", last)
	}
}
```

- [ ] Run the test to see it fail (no implementation yet):

```bash
go test ./internal/sierpinski/
```

Expected: compilation failure such as `undefined: Generate`.

- [ ] Implement `internal/sierpinski/sierpinski.go`:

```go
// Package sierpinski generates Sierpinski triangles as ASCII art.
package sierpinski

import "strings"

// Generate returns the rows of a Sierpinski triangle.
//
// size is the maximum number of rows (and the width of the centering field).
// depth caps the resolution: at most 2^depth rows are produced.
// char is the rune used for filled cells; empty cells are spaces.
//
// A cell (row, col) is filled when (row & col) == 0, the classic bitwise
// Sierpinski property.
func Generate(size, depth int, char rune) []string {
	rows := size
	if max := 1 << depth; max < rows {
		rows = max
	}
	if rows < 1 {
		rows = 1
	}

	out := make([]string, 0, rows)
	for r := 0; r < rows; r++ {
		var b strings.Builder
		// Left padding to center the triangle.
		for p := 0; p < rows-1-r; p++ {
			b.WriteRune(' ')
		}
		for c := 0; c <= r; c++ {
			if r&c == 0 {
				b.WriteRune(char)
			} else {
				b.WriteRune(' ')
			}
			if c < r {
				b.WriteRune(' ')
			}
		}
		out = append(out, b.String())
	}
	return out
}
```

- [ ] Run the test to see it pass:

```bash
go test ./internal/sierpinski/
```

Expected:
```
ok  	github.com/example/fractals/internal/sierpinski	0.00s
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add sierpinski algorithm package with tests"
```

---

### Task 3: Mandelbrot Algorithm Package

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

The function signature:

```go
func Generate(width, height, iterations int, gradient []rune) []string
```

For each cell we map pixel coordinates to the complex plane (real range `-2.5..1.0`, imaginary range `-1.0..1.0`), run the escape-time iteration, then map iteration count to a gradient rune. Points that never escape (in the set) use the **last** gradient rune.

Mapping iteration count `n` (0..iterations) to a gradient index:
- If `n == iterations` (never escaped): use `gradient[len(gradient)-1]`.
- Else: `idx = n * (len(gradient)-1) / iterations`, clamped to `[0, len-1]`.

The CLI passes either the default gradient `[]rune(" .:-=+*#%@")` or, for a custom `--char`, a two-rune gradient `[]rune{' ', char}` so escaped cells are spaces and in-set cells are `char`.

- [ ] Write the failing test `internal/mandelbrot/mandelbrot_test.go`:

```go
package mandelbrot

import (
	"strings"
	"testing"
)

var defaultGradient = []rune(" .:-=+*#%@")

func TestGenerateDimensions(t *testing.T) {
	rows := Generate(80, 24, 100, defaultGradient)
	if len(rows) != 24 {
		t.Fatalf("expected 24 rows, got %d", len(rows))
	}
	for i, r := range rows {
		if len([]rune(r)) != 80 {
			t.Fatalf("row %d: expected width 80, got %d", i, len([]rune(r)))
		}
	}
}

func TestGenerateCenterIsInSet(t *testing.T) {
	// The point near (-0.5, 0) is inside the set and should map to the
	// last gradient rune.
	rows := Generate(80, 24, 100, defaultGradient)
	mid := rows[len(rows)/2]
	last := defaultGradient[len(defaultGradient)-1]
	if !strings.ContainsRune(mid, last) {
		t.Fatalf("expected middle row to contain in-set rune %q, got %q", last, mid)
	}
}

func TestGenerateCornerEscapes(t *testing.T) {
	// Top-left corner maps near (-2.5, -1.0), which escapes quickly and
	// should be the first gradient rune (space).
	rows := Generate(80, 24, 100, defaultGradient)
	first := []rune(rows[0])[0]
	if first != defaultGradient[0] {
		t.Fatalf("expected top-left rune %q, got %q", defaultGradient[0], first)
	}
}

func TestGenerateCustomTwoRuneGradient(t *testing.T) {
	rows := Generate(40, 20, 100, []rune{' ', '#'})
	joined := strings.Join(rows, "\n")
	if !strings.Contains(joined, "#") {
		t.Fatalf("expected output to contain '#': %q", joined)
	}
	for _, r := range joined {
		if r != ' ' && r != '#' && r != '\n' {
			t.Fatalf("unexpected rune %q in output", r)
		}
	}
}
```

- [ ] Run the test to see it fail:

```bash
go test ./internal/mandelbrot/
```

Expected: `undefined: Generate`.

- [ ] Implement `internal/mandelbrot/mandelbrot.go`:

```go
// Package mandelbrot renders the Mandelbrot set as ASCII art.
package mandelbrot

import "strings"

const (
	realMin = -2.5
	realMax = 1.0
	imagMin = -1.0
	imagMax = 1.0
)

// Generate returns the rows of the Mandelbrot set rendered as ASCII art.
//
// width and height are the output dimensions in characters.
// iterations is the maximum escape-time iteration count.
// gradient maps iteration counts to runes; index 0 is "escaped immediately"
// and the final index is "in the set".
func Generate(width, height, iterations int, gradient []rune) []string {
	if len(gradient) == 0 {
		gradient = []rune{' '}
	}
	maxIdx := len(gradient) - 1

	out := make([]string, 0, height)
	for py := 0; py < height; py++ {
		var b strings.Builder
		imag := imagMin + (imagMax-imagMin)*float64(py)/float64(height-1)
		for px := 0; px < width; px++ {
			real := realMin + (realMax-realMin)*float64(px)/float64(width-1)
			n := escape(real, imag, iterations)

			var idx int
			if n >= iterations {
				idx = maxIdx
			} else {
				idx = n * maxIdx / iterations
				if idx < 0 {
					idx = 0
				}
				if idx > maxIdx {
					idx = maxIdx
				}
			}
			b.WriteRune(gradient[idx])
		}
		out = append(out, b.String())
	}
	return out
}

// escape returns the number of iterations before the point (cRe, cIm)
// escapes the radius-2 circle, capped at maxIter.
func escape(cRe, cIm float64, maxIter int) int {
	var zRe, zIm float64
	for n := 0; n < maxIter; n++ {
		zRe2 := zRe*zRe - zIm*zIm + cRe
		zIm2 := 2*zRe*zIm + cIm
		zRe, zIm = zRe2, zIm2
		if zRe*zRe+zIm*zIm > 4.0 {
			return n
		}
	}
	return maxIter
}
```

Note: when `width` or `height` is `1`, the divisor `width-1`/`height-1` is `0`. The CLI validation in Task 5 enforces a minimum of `2`, so this is safe. Tests use values ≥ 2.

- [ ] Run the test to see it pass:

```bash
go test ./internal/mandelbrot/
```

Expected:
```
ok  	github.com/example/fractals/internal/mandelbrot	0.00s
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add mandelbrot algorithm package with tests"
```

---

### Task 4: Sierpinski CLI Subcommand

**Files:** `internal/cli/sierpinski.go`, `internal/cli/sierpinski_test.go`

The subcommand parses flags, validates them, calls `sierpinski.Generate`, and writes rows to the command's configured output writer (`cmd.OutOrStdout()`), which makes it testable.

The `--char` flag is a string; we take the first rune. Empty string is an error.

- [ ] Write the failing test `internal/cli/sierpinski_test.go`:

```go
package cli

import (
	"bytes"
	"strings"
	"testing"
)

func TestSierpinskiCommandOutputsTriangle(t *testing.T) {
	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"sierpinski", "--size", "8", "--depth", "5"})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	out := buf.String()
	if strings.Count(out, "*") < 1 {
		t.Fatalf("expected stars in output, got %q", out)
	}
	if !strings.Contains(out, "\n") {
		t.Fatalf("expected multiple lines, got %q", out)
	}
}

func TestSierpinskiCommandCustomChar(t *testing.T) {
	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"sierpinski", "--size", "4", "--char", "#"})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(buf.String(), "#") {
		t.Fatalf("expected '#' in output, got %q", buf.String())
	}
}

func TestSierpinskiCommandRejectsNegativeSize(t *testing.T) {
	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"sierpinski", "--size", "-1"})

	err := rootCmd.Execute()
	if err == nil {
		t.Fatal("expected error for negative size, got nil")
	}
	if !strings.Contains(err.Error(), "size") {
		t.Fatalf("expected error mentioning size, got %v", err)
	}
}

func TestSierpinskiCommandRejectsEmptyChar(t *testing.T) {
	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"sierpinski", "--char", ""})

	err := rootCmd.Execute()
	if err == nil {
		t.Fatal("expected error for empty char, got nil")
	}
	if !strings.Contains(err.Error(), "char") {
		t.Fatalf("expected error mentioning char, got %v", err)
	}
}
```

- [ ] Run the test to see it fail:

```bash
go test ./internal/cli/
```

Expected: failure such as `unknown command "sierpinski"` causing `rootCmd.Execute()` to return an error in the first test, or a non-nil error where none is expected.

- [ ] Implement `internal/cli/sierpinski.go`:

```go
package cli

import (
	"fmt"

	"github.com/example/fractals/internal/sierpinski"
	"github.com/spf13/cobra"
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
			if size < 1 {
				return fmt.Errorf("size must be >= 1, got %d", size)
			}
			if depth < 1 {
				return fmt.Errorf("depth must be >= 1, got %d", depth)
			}
			if char == "" {
				return fmt.Errorf("char must be a single character, got empty string")
			}
			r := []rune(char)[0]

			rows := sierpinski.Generate(size, depth, r)
			out := cmd.OutOrStdout()
			for _, row := range rows {
				fmt.Fprintln(out, row)
			}
			return nil
		},
	}

	cmd.Flags().IntVar(&size, "size", 32, "width of the triangle base in characters")
	cmd.Flags().IntVar(&depth, "depth", 5, "recursion depth")
	cmd.Flags().StringVar(&char, "char", "*", "character to use for filled points")
	return cmd
}

func init() {
	rootCmd.AddCommand(newSierpinskiCmd())
}
```

- [ ] Run the test to see it pass:

```bash
go test ./internal/cli/
```

Expected:
```
ok  	github.com/example/fractals/internal/cli	0.0XXs
```

- [ ] Manually verify output looks like a triangle:

```bash
go run ./cmd/fractals sierpinski --size 16 --depth 5
```

Expected: a centered triangular pattern of `*` characters, 16 (or fewer, capped by depth) rows.

- [ ] Commit:

```bash
git add -A && git commit -m "Add sierpinski CLI subcommand with validation and tests"
```

---

### Task 5: Mandelbrot CLI Subcommand

**Files:** `internal/cli/mandelbrot.go`, `internal/cli/mandelbrot_test.go`

The `--char` flag here is special: cobra cannot distinguish "default gradient" from "user passed a value" via a plain default string, so we use `cmd.Flags().Changed("char")` to decide. If the user passed `--char`, build a two-rune gradient `{' ', char}`; otherwise use the default gradient.

- [ ] Write the failing test `internal/cli/mandelbrot_test.go`:

```go
package cli

import (
	"bytes"
	"strings"
	"testing"
)

func TestMandelbrotCommandDimensions(t *testing.T) {
	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"mandelbrot", "--width", "40", "--height", "10", "--iterations", "50"})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(buf.String(), "\n"), "\n")
	if len(lines) != 10 {
		t.Fatalf("expected 10 lines, got %d", len(lines))
	}
	for i, ln := range lines {
		if len([]rune(ln)) != 40 {
			t.Fatalf("line %d: expected width 40, got %d", i, len([]rune(ln)))
		}
	}
}

func TestMandelbrotCommandCustomChar(t *testing.T) {
	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"mandelbrot", "--width", "40", "--height", "10", "--char", "#"})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "#") {
		t.Fatalf("expected '#' in output, got %q", out)
	}
	for _, r := range out {
		if r != ' ' && r != '#' && r != '\n' {
			t.Fatalf("unexpected rune %q with custom char", r)
		}
	}
}

func TestMandelbrotCommandRejectsTooSmallWidth(t *testing.T) {
	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"mandelbrot", "--width", "1"})

	err := rootCmd.Execute()
	if err == nil {
		t.Fatal("expected error for width 1, got nil")
	}
	if !strings.Contains(err.Error(), "width") {
		t.Fatalf("expected error mentioning width, got %v", err)
	}
}

func TestMandelbrotCommandRejectsEmptyChar(t *testing.T) {
	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"mandelbrot", "--char", ""})

	err := rootCmd.Execute()
	if err == nil {
		t.Fatal("expected error for empty char, got nil")
	}
	if !strings.Contains(err.Error(), "char") {
		t.Fatalf("expected error mentioning char, got %v", err)
	}
}
```

- [ ] Run the test to see it fail:

```bash
go test ./internal/cli/
```

Expected: failure due to `unknown command "mandelbrot"`.

- [ ] Implement `internal/cli/mandelbrot.go`:

```go
package cli

import (
	"fmt"

	"github.com/example/fractals/internal/mandelbrot"
	"github.com/spf13/cobra"
)

var defaultGradient = []rune(" .:-=+*#%@")

func newMandelbrotCmd() *cobra.Command {
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
			if width < 2 {
				return fmt.Errorf("width must be >= 2, got %d", width)
			}
			if height < 2 {
				return fmt.Errorf("height must be >= 2, got %d", height)
			}
			if iterations < 1 {
				return fmt.Errorf("iterations must be >= 1, got %d", iterations)
			}

			gradient := defaultGradient
			if cmd.Flags().Changed("char") {
				if char == "" {
					return fmt.Errorf("char must be a single character, got empty string")
				}
				gradient = []rune{' ', []rune(char)[0]}
			}

			rows := mandelbrot.Generate(width, height, iterations, gradient)
			out := cmd.OutOrStdout()
			for _, row := range rows {
				fmt.Fprintln(out, row)
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

func init() {
	rootCmd.AddCommand(newMandelbrotCmd())
}
```

- [ ] Run the test to see it pass:

```bash
go test ./internal/cli/
```

Expected:
```
ok  	github.com/example/fractals/internal/cli	0.0XXs
```

- [ ] Manually verify output looks like a Mandelbrot set:

```bash
go run ./cmd/fractals mandelbrot --width 80 --height 24
```

Expected: a recognizable bulbous Mandelbrot shape with gradient characters densest near the set boundary.

- [ ] Commit:

```bash
git add -A && git commit -m "Add mandelbrot CLI subcommand with validation and tests"
```

---

### Task 6: Final Integration Verification

**Files:** none (verification only)

- [ ] Run the full test suite:

```bash
go test ./...
```

Expected:
```
ok  	github.com/example/fractals/internal/cli	0.0XXs
ok  	github.com/example/fractals/internal/mandelbrot	0.0XXs
ok  	github.com/example/fractals/internal/sierpinski	0.0XXs
```
(plus a `no test files` line for `cmd/fractals` — acceptable.)

- [ ] Run `go vet`:

```bash
go vet ./...
```

Expected: no output, exit code 0.

- [ ] Verify root help (Acceptance Criterion 1):

```bash
go run ./cmd/fractals --help
```

Expected: shows usage with `sierpinski` and `mandelbrot` listed under "Available Commands".

- [ ] Verify subcommand help:

```bash
go run ./cmd/fractals sierpinski --help
```

Expected: shows `--size`, `--depth`, `--char` flags with defaults.

- [ ] Verify an invalid input produces a clear error (Acceptance Criterion 6):

```bash
go run ./cmd/fractals mandelbrot --width 1
```

Expected stderr:
```
width must be >= 2, got 1
```
Exit code 1.

- [ ] Build the binary:

```bash
go build -o fractals ./cmd/fractals && ./fractals sierpinski --size 16
```

Expected: a triangle prints; the `fractals` binary exists.

- [ ] Add `fractals` (the built binary) to `.gitignore` and commit:

```bash
echo "/fractals" > .gitignore
git add -A && git commit -m "Add .gitignore for built binary"
```

---

## Self-Review

**Spec coverage check:**

| Acceptance Criterion | Covered by |
|----------------------|-----------|
| 1. `--help` shows usage | Task 1 + Task 6 |
| 2. `sierpinski` outputs triangle | Task 4 test + Task 6 manual |
| 3. `mandelbrot` outputs set | Task 5 test + Task 6 manual |
| 4. size/width/height/depth/iterations flags work | Task 4 & 5 tests |
| 5. `--char` customizes output | Task 4 & 5 custom-char tests |
| 6. Invalid inputs → clear errors | Task 4 & 5 rejection tests + Task 6 |
| 7. All tests pass | Task 6 `go test ./...` |

All commands from the spec's Usage section are exercised: `sierpinski --size --depth`, `mandelbrot --width --height --iterations`, `sierpinski --char`, `--help`, `sierpinski --help`.

**Placeholder scan:** No `TODO`, `FIXME`, or stub functions remain. All code blocks are complete and compilable.

**Type consistency check:**
- `sierpinski.Generate(size, depth int, char rune) []string` — called with `(size, depth, r)` where `r` is `[]rune(char)[0]` (a `rune`). ✓
- `mandelbrot.Generate(width, height, iterations int, gradient []rune) []string` — called with `(width, height, iterations, gradient)` where `gradient` is `[]rune`. ✓
- `cli.Execute() error` — called in `main.go` and assigned to `err`. ✓

**Edge case check:** Mandelbrot divides by `width-1` and `height-1`; CLI validation enforces `>= 2`, and all tests use values `>= 2`. The algorithm package's own tests also use `>= 2`. ✓ Sierpinski guards against `rows < 1`. ✓

**Module path consistency:** All imports use `github.com/example/fractals/...` matching the `go mod init` path. If you choose a different module path, update all import statements accordingly.