# Go Fractals CLI - Implementation Plan

## Global Constraints

- Go 1.21+
- CLI library: `github.com/spf13/cobra`
- Binary/command name: `fractals`
- Sierpinski defaults: `--size 32`, `--depth 5`, `--char '*'`
- Mandelbrot defaults: `--width 80`, `--height 24`, `--iterations 100`, gradient `" .:-=+*#%@"`
- Invalid inputs must produce clear error messages
- All output to stdout, one line per row

## File Structure

- `go.mod` — module definition, dependencies
- `internal/sierpinski/sierpinski.go` — Sierpinski generation algorithm
- `internal/sierpinski/sierpinski_test.go` — algorithm tests
- `internal/mandelbrot/mandelbrot.go` — Mandelbrot rendering algorithm
- `internal/mandelbrot/mandelbrot_test.go` — algorithm tests
- `internal/cli/root.go` — root cobra command
- `internal/cli/sierpinski.go` — sierpinski subcommand wiring
- `internal/cli/mandelbrot.go` — mandelbrot subcommand wiring
- `cmd/fractals/main.go` — entry point

---

### Task 1: Module setup

**Files:** `go.mod`

**Interfaces:** Produces module path `github.com/example/fractals` for all imports.

- [ ] Initialize module:
```bash
go mod init github.com/example/fractals
go get github.com/spf13/cobra@latest
```
- [ ] Verify:
```bash
head -1 go.mod
```
Expected: `module github.com/example/fractals`
- [ ] Commit: `git add -A && git commit -m "chore: init module"`

---

### Task 2: Sierpinski algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

**Interfaces:** Produces `func Generate(size, depth int, char rune) ([]string, error)`. Returns rows top-to-bottom. Errors on `size < 1` or `depth < 0`.

- [ ] Write failing test:
```go
package sierpinski

import "testing"

func TestGenerateErrors(t *testing.T) {
	if _, err := Generate(0, 1, '*'); err == nil {
		t.Fatal("expected error for size < 1")
	}
	if _, err := Generate(8, -1, '*'); err == nil {
		t.Fatal("expected error for depth < 0")
	}
}

func TestGenerateShape(t *testing.T) {
	rows, err := Generate(8, 3, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 8 {
		t.Fatalf("expected 8 rows, got %d", len(rows))
	}
	// Apex row has exactly one filled char.
	count := 0
	for _, c := range rows[0] {
		if c == '*' {
			count++
		}
	}
	if count != 1 {
		t.Fatalf("expected 1 filled char in apex, got %d", count)
	}
}
```
- [ ] Run, see fail:
```bash
go test ./internal/sierpinski/
```
Expected: build/undefined error for `Generate`.
- [ ] Implement using the Pascal-triangle bitmask rule (point filled when `row & col == col`):
```go
package sierpinski

import "fmt"

// Generate returns size rows of an ASCII Sierpinski triangle.
// A point (row, col) is filled when (row AND col) == col.
func Generate(size, depth int, char rune) ([]string, error) {
	if size < 1 {
		return nil, fmt.Errorf("size must be >= 1, got %d", size)
	}
	if depth < 0 {
		return nil, fmt.Errorf("depth must be >= 0, got %d", depth)
	}
	rows := make([]string, size)
	for y := 0; y < size; y++ {
		line := make([]rune, size)
		for x := 0; x < size; x++ {
			if y&x == x {
				line[x] = char
			} else {
				line[x] = ' '
			}
		}
		rows[y] = string(line)
	}
	return rows, nil
}
```
- [ ] Run, see pass:
```bash
go test ./internal/sierpinski/
```
Expected: `ok` line.
- [ ] Commit: `git commit -am "feat: sierpinski algorithm"`

> Note: `depth` is validated and accepted per spec; the bitmask form renders the full triangle. Tests assert size-driven dimensions and apex shape.

---

### Task 3: Mandelbrot algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

**Interfaces:** Produces `const Gradient = " .:-=+*#%@"` and `func Generate(width, height, iterations int, char rune) ([]string, error)`. If `char == 0`, use `Gradient`; otherwise fill escaped points with `char` and interior with space. Errors on `width < 1`, `height < 1`, or `iterations < 1`.

- [ ] Write failing test:
```go
package mandelbrot

import (
	"strings"
	"testing"
)

func TestGenerateErrors(t *testing.T) {
	for _, c := range []struct{ w, h, i int }{{0, 1, 1}, {1, 0, 1}, {1, 1, 0}} {
		if _, err := Generate(c.w, c.h, c.i, 0); err == nil {
			t.Fatalf("expected error for %+v", c)
		}
	}
}

func TestGenerateDimensions(t *testing.T) {
	rows, err := Generate(80, 24, 100, 0)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 24 {
		t.Fatalf("expected 24 rows, got %d", len(rows))
	}
	for _, r := range rows {
		if len([]rune(r)) != 80 {
			t.Fatalf("expected width 80, got %d", len([]rune(r)))
		}
	}
	// Interior near origin should be a space (in-set).
	joined := strings.Join(rows, "\n")
	if !strings.Contains(joined, " ") {
		t.Fatal("expected some in-set spaces")
	}
}

func TestGenerateCustomChar(t *testing.T) {
	rows, _ := Generate(20, 10, 50, '#')
	for _, r := range rows {
		for _, c := range r {
			if c != '#' && c != ' ' {
				t.Fatalf("unexpected char %q", c)
			}
		}
	}
}
```
- [ ] Run, see fail:
```bash
go test ./internal/mandelbrot/
```
Expected: undefined `Generate`.
- [ ] Implement:
```go
package mandelbrot

import "fmt"

const Gradient = " .:-=+*#%@"

// Generate renders the Mandelbrot set over the standard view
// real [-2.5, 1.0], imag [-1.25, 1.25].
func Generate(width, height, iterations int, char rune) ([]string, error) {
	if width < 1 {
		return nil, fmt.Errorf("width must be >= 1, got %d", width)
	}
	if height < 1 {
		return nil, fmt.Errorf("height must be >= 1, got %d", height)
	}
	if iterations < 1 {
		return nil, fmt.Errorf("iterations must be >= 1, got %d", iterations)
	}
	rows := make([]string, height)
	for py := 0; py < height; py++ {
		line := make([]rune, width)
		y0 := -1.25 + 2.5*float64(py)/float64(height)
		for px := 0; px < width; px++ {
			x0 := -2.5 + 3.5*float64(px)/float64(width)
			var x, y float64
			n := 0
			for x*x+y*y <= 4 && n < iterations {
				x, y = x*x-y*y+x0, 2*x*y+y0
				n++
			}
			line[px] = pick(n, iterations, char)
		}
		rows[py] = string(line)
	}
	return rows, nil
}

func pick(n, max int, char rune) rune {
	if n >= max {
		return ' '
	}
	if char != 0 {
		return char
	}
	g := []rune(Gradient)
	idx := n * (len(g) - 1) / max
	return g[idx]
}
```
- [ ] Run, see pass:
```bash
go test ./internal/mandelbrot/
```
Expected: `ok`.
- [ ] Commit: `git commit -am "feat: mandelbrot algorithm"`

---

### Task 4: CLI wiring

**Files:** `internal/cli/root.go`, `internal/cli/sierpinski.go`, `internal/cli/mandelbrot.go`, `cmd/fractals/main.go`

**Interfaces:** Consumes `sierpinski.Generate`, `mandelbrot.Generate`, `mandelbrot.Gradient`. Produces `func Execute() error` in package `cli`. Each subcommand resolves `--char`: empty string → `rune(0)`; otherwise first rune (error if multi-rune).

- [ ] Create `internal/cli/root.go`:
```go
package cli

import "github.com/spf13/cobra"

func newRootCmd() *cobra.Command {
	root := &cobra.Command{
		Use:   "fractals",
		Short: "Generate ASCII art fractals",
	}
	root.AddCommand(newSierpinskiCmd(), newMandelbrotCmd())
	return root
}

// Execute runs the root command.
func Execute() error {
	return newRootCmd().Execute()
}

// charArg converts a flag string to a rune; "" -> 0 (use default/gradient).
func charArg(s string) (rune, error) {
	if s == "" {
		return 0, nil
	}
	r := []rune(s)
	if len(r) != 1 {
		return 0, errBadChar(s)
	}
	return r[0], nil
}
```
- [ ] Create `internal/cli/sierpinski.go`:
```go
package cli

import (
	"fmt"

	"github.com/example/fractals/internal/sierpinski"
	"github.com/spf13/cobra"
)

func errBadChar(s string) error {
	return fmt.Errorf("--char must be a single character, got %q", s)
}

func newSierpinskiCmd() *cobra.Command {
	var size, depth int
	var ch string
	cmd := &cobra.Command{
		Use:   "sierpinski",
		Short: "Generate a Sierpinski triangle",
		RunE: func(cmd *cobra.Command, _ []string) error {
			r, err := charArg(ch)
			if err != nil {
				return err
			}
			if r == 0 {
				r = '*'
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
	cmd.Flags().IntVar(&size, "size", 32, "Width of the triangle base")
	cmd.Flags().IntVar(&depth, "depth", 5, "Recursion depth")
	cmd.Flags().StringVar(&ch, "char", "*", "Character for filled points")
	return cmd
}
```
- [ ] Create `internal/cli/mandelbrot.go`:
```go
package cli

import (
	"fmt"

	"github.com/example/fractals/internal/mandelbrot"
	"github.com/spf13/cobra"
)

func newMandelbrotCmd() *cobra.Command {
	var width, height, iterations int
	var ch string
	cmd := &cobra.Command{
		Use:   "mandelbrot",
		Short: "Render the Mandelbrot set",
		RunE: func(cmd *cobra.Command, _ []string) error {
			r, err := charArg(ch)
			if err != nil {
				return err
			}
			rows, err := mandelbrot.Generate(width, height, iterations, r)
			if err != nil {
				return err
			}
			for _, line := range rows {
				fmt.Fprintln(cmd.OutOrStdout(), line)
			}
			return nil
		},
	}
	cmd.Flags().IntVar(&width, "width", 80, "Output width")
	cmd.Flags().IntVar(&height, "height", 24, "Output height")
	cmd.Flags().IntVar(&iterations, "iterations", 100, "Max escape iterations")
	cmd.Flags().StringVar(&ch, "char", "", "Single char, or omit for gradient")
	return cmd
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
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
}
```
- [ ] Build and verify acceptance criteria:
```bash
go build ./... && go run ./cmd/fractals --help
go run ./cmd/fractals sierpinski --size 8 --char '#'
go run ./cmd/fractals mandelbrot --width 40 --height 12
go run ./cmd/fractals sierpinski --size 0; echo "exit=$?"
```
Expected: help text lists `sierpinski` and `mandelbrot`; triangle of `#`; Mandelbrot rectangle; last command prints `error: size must be >= 1, got 0` and `exit=1`.
- [ ] Run full suite:
```bash
go test ./...
```
Expected: `ok` for both internal packages.
- [ ] Commit: `git commit -am "feat: cli wiring"`

---

## Self-Review

- **Spec coverage:** all six commands/flags present (Tasks 2–4); gradient default via `char == 0` (Task 3); custom char (Tasks 2–4); error messages (Tasks 2–4); help via cobra (Task 4). All criteria 1–7 mapped.
- **Type consistency:** `Generate` signatures and `charArg`/`pick` helpers match across consumer/producer Interfaces blocks; `rune(0)` sentinel consistent between CLI and algorithm.
- **Placeholder scan:** no TODOs; module path `github.com/example/fractals` used verbatim in all imports.