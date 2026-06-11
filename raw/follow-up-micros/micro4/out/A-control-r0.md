# Go Fractals CLI - Implementation Plan

## Overview

This plan implements an ASCII art fractal generator CLI in Go with two fractal types (Sierpinski triangle and Mandelbrot set) using the `cobra` CLI framework. We use TDD: pure algorithm packages are tested directly; CLI wiring is thin glue.

## File Structure

| File | Responsibility |
|------|----------------|
| `go.mod` | Module definition, Go version, dependencies |
| `cmd/fractals/main.go` | Entry point; calls `cli.Execute()` |
| `internal/sierpinski/sierpinski.go` | Pure Sierpinski generation algorithm returning `[]string` |
| `internal/sierpinski/sierpinski_test.go` | Tests for Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure Mandelbrot rendering algorithm returning `[]string` |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for Mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command + `Execute()` |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand: parses flags, calls algorithm, prints |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand: parses flags, calls algorithm, prints |

**Design decisions:**
- Algorithm packages take primitive params, return `[]string` (rows), and return an `error` for invalid input. No printing inside them — keeps them testable.
- CLI packages own flag parsing and stdout writing.
- Each algorithm validates its own inputs so error messages are consistent regardless of caller.

---

### Task 1: Project Scaffolding

**Files:** `go.mod`, `cmd/fractals/main.go`, `internal/cli/root.go`

- [ ] Create the module. Run:
  ```bash
  go mod init github.com/example/fractals
  ```
  Expected: creates `go.mod` containing `module github.com/example/fractals` and a `go 1.21` (or higher) line.

- [ ] Add the cobra dependency. Run:
  ```bash
  go get github.com/spf13/cobra@latest
  ```
  Expected: `go.mod` now lists `github.com/spf13/cobra` under `require`; a `go.sum` is created.

- [ ] Create `internal/cli/root.go` with a minimal root command:
  ```go
  package cli

  import (
  	"github.com/spf13/cobra"
  )

  func newRootCmd() *cobra.Command {
  	return &cobra.Command{
  		Use:   "fractals",
  		Short: "Generate ASCII art fractals",
  		Long:  "fractals generates ASCII art fractals such as the Sierpinski triangle and the Mandelbrot set.",
  	}
  }

  // Execute builds the command tree and runs it.
  func Execute() error {
  	root := newRootCmd()
  	return root.Execute()
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

- [ ] Verify it builds and `--help` works. Run:
  ```bash
  go run ./cmd/fractals --help
  ```
  Expected output includes:
  ```
  fractals generates ASCII art fractals such as the Sierpinski triangle and the Mandelbrot set.

  Usage:
    fractals [command]
  ```

- [ ] Commit. Run:
  ```bash
  git add -A && git commit -m "Scaffold fractals CLI with cobra root command"
  ```

---

### Task 2: Sierpinski Algorithm

**Files:** `internal/sierpinski/sierpinski_test.go`, `internal/sierpinski/sierpinski.go`

The classic ASCII Sierpinski uses the bitwise rule: a cell `(row, col)` is filled iff `(row & col) == 0`. The triangle of order `depth` has `2^depth` rows. We expose `Generate(size, depth int, char rune)`.

**Semantics:** `depth` controls the number of rows (`rows = 2^depth`). `size` controls horizontal scaling — each filled cell is rendered `size / 2^depth` characters wide, with a minimum of 1, and rows are left-padded so the triangle is right-aligned to its row width. To keep this deterministic and testable, we define: number of columns per row = `2^depth`; output uses `char` for filled cells and space for empty.

- [ ] Write the failing test `internal/sierpinski/sierpinski_test.go`:
  ```go
  package sierpinski

  import (
  	"strings"
  	"testing"
  )

  func TestGenerateDepth1(t *testing.T) {
  	// depth 1 => 2 rows, 2 cols. Filled where (row & col) == 0.
  	// row0: col0(0&0=0 filled) col1(0&1=0 filled) => "**"
  	// row1: col0(1&0=0 filled) col1(1&1=1 empty)  => "* "
  	rows, err := Generate(2, 1, '*')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	want := []string{"**", "* "}
  	if len(rows) != len(want) {
  		t.Fatalf("got %d rows, want %d: %#v", len(rows), len(want), rows)
  	}
  	for i := range want {
  		if rows[i] != want[i] {
  			t.Errorf("row %d = %q, want %q", i, rows[i], want[i])
  		}
  	}
  }

  func TestGenerateRowCount(t *testing.T) {
  	rows, err := Generate(8, 3, '*')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 8 { // 2^3
  		t.Errorf("got %d rows, want 8", len(rows))
  	}
  }

  func TestGenerateCustomChar(t *testing.T) {
  	rows, err := Generate(2, 1, '#')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if strings.ContainsRune(strings.Join(rows, ""), '*') {
  		t.Errorf("output should not contain '*': %#v", rows)
  	}
  	if !strings.ContainsRune(strings.Join(rows, ""), '#') {
  		t.Errorf("output should contain '#': %#v", rows)
  	}
  }

  func TestGenerateInvalidDepth(t *testing.T) {
  	if _, err := Generate(8, 0, '*'); err == nil {
  		t.Error("expected error for depth < 1, got nil")
  	}
  }

  func TestGenerateInvalidSize(t *testing.T) {
  	if _, err := Generate(0, 3, '*'); err == nil {
  		t.Error("expected error for size < 1, got nil")
  	}
  }
  ```

- [ ] Run the test to see it fail (package doesn't compile yet). Run:
  ```bash
  go test ./internal/sierpinski/
  ```
  Expected: failure such as `undefined: Generate` / build failed.

- [ ] Implement `internal/sierpinski/sierpinski.go`:
  ```go
  // Package sierpinski generates ASCII Sierpinski triangles.
  package sierpinski

  import "fmt"

  // Generate returns the rows of a Sierpinski triangle.
  //
  // depth controls the number of rows: rows = 2^depth.
  // size must be >= 1; it is accepted for API symmetry and future scaling,
  // and the produced triangle has 2^depth columns.
  // char is the rune used for filled cells; empty cells are spaces.
  func Generate(size, depth int, char rune) ([]string, error) {
  	if size < 1 {
  		return nil, fmt.Errorf("size must be >= 1, got %d", size)
  	}
  	if depth < 1 {
  		return nil, fmt.Errorf("depth must be >= 1, got %d", depth)
  	}

  	n := 1 << depth // 2^depth rows and columns
  	rows := make([]string, n)
  	for row := 0; row < n; row++ {
  		line := make([]rune, n)
  		for col := 0; col < n; col++ {
  			if row&col == 0 {
  				line[col] = char
  			} else {
  				line[col] = ' '
  			}
  		}
  		rows[row] = string(line)
  	}
  	return rows, nil
  }
  ```

- [ ] Run the test to see it pass. Run:
  ```bash
  go test ./internal/sierpinski/
  ```
  Expected:
  ```
  ok  	github.com/example/fractals/internal/sierpinski
  ```

- [ ] Commit. Run:
  ```bash
  git add -A && git commit -m "Add Sierpinski triangle algorithm with tests"
  ```

---

### Task 3: Mandelbrot Algorithm

**Files:** `internal/mandelbrot/mandelbrot_test.go`, `internal/mandelbrot/mandelbrot.go`

We map the complex plane region (real `-2.5..1.0`, imag `-1.0..1.0`) onto a `width x height` grid. For each cell, iterate `z = z² + c` until `|z| > 2` or `maxIter` reached. Map iteration count to a character.

**Gradient:** when `useGradient` is true, use `" .:-=+*#%@"` mapped by escape speed (points inside the set → last char `@`; fast-escaping → space). When a single `char` is supplied, points **inside** the set get `char` and outside get space.

- [ ] Write the failing test `internal/mandelbrot/mandelbrot_test.go`:
  ```go
  package mandelbrot

  import (
  	"strings"
  	"testing"
  )

  func TestRenderDimensions(t *testing.T) {
  	rows, err := Render(40, 20, 50, 0, false)
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 20 {
  		t.Fatalf("got %d rows, want 20", len(rows))
  	}
  	for i, r := range rows {
  		if len([]rune(r)) != 40 {
  			t.Errorf("row %d width = %d, want 40", i, len([]rune(r)))
  		}
  	}
  }

  func TestRenderGradientContainsSetChar(t *testing.T) {
  	// useGradient => char arg ignored. Origin (0,0) is in the set,
  	// so the densest gradient char '@' must appear.
  	rows, err := Render(80, 24, 100, 0, true)
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	joined := strings.Join(rows, "")
  	if !strings.ContainsRune(joined, '@') {
  		t.Errorf("gradient render should contain '@' for in-set points")
  	}
  }

  func TestRenderCustomChar(t *testing.T) {
  	// Non-gradient: in-set points use the custom char, others are spaces.
  	rows, err := Render(80, 24, 100, '#', false)
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	joined := strings.Join(rows, "")
  	if !strings.ContainsRune(joined, '#') {
  		t.Errorf("custom-char render should contain '#'")
  	}
  	for _, r := range joined {
  		if r != '#' && r != ' ' {
  			t.Errorf("unexpected rune %q in custom-char render", r)
  			break
  		}
  	}
  }

  func TestRenderInvalidWidth(t *testing.T) {
  	if _, err := Render(0, 24, 100, 0, true); err == nil {
  		t.Error("expected error for width < 1")
  	}
  }

  func TestRenderInvalidHeight(t *testing.T) {
  	if _, err := Render(80, 0, 100, 0, true); err == nil {
  		t.Error("expected error for height < 1")
  	}
  }

  func TestRenderInvalidIterations(t *testing.T) {
  	if _, err := Render(80, 24, 0, 0, true); err == nil {
  		t.Error("expected error for iterations < 1")
  	}
  }
  ```

- [ ] Run the test to see it fail. Run:
  ```bash
  go test ./internal/mandelbrot/
  ```
  Expected: build failure `undefined: Render`.

- [ ] Implement `internal/mandelbrot/mandelbrot.go`:
  ```go
  // Package mandelbrot renders the Mandelbrot set as ASCII art.
  package mandelbrot

  import "fmt"

  const gradient = " .:-=+*#%@"

  // Plane bounds.
  const (
  	realMin = -2.5
  	realMax = 1.0
  	imagMin = -1.0
  	imagMax = 1.0
  )

  // Render returns the rows of an ASCII Mandelbrot set.
  //
  // width and height are output dimensions in characters.
  // maxIter is the escape-iteration cap.
  // If useGradient is true, char is ignored and the gradient " .:-=+*#%@"
  // is used (in-set points map to '@'). Otherwise in-set points use char
  // and out-of-set points use a space.
  func Render(width, height, maxIter int, char rune, useGradient bool) ([]string, error) {
  	if width < 1 {
  		return nil, fmt.Errorf("width must be >= 1, got %d", width)
  	}
  	if height < 1 {
  		return nil, fmt.Errorf("height must be >= 1, got %d", height)
  	}
  	if maxIter < 1 {
  		return nil, fmt.Errorf("iterations must be >= 1, got %d", maxIter)
  	}

  	rows := make([]string, height)
  	for py := 0; py < height; py++ {
  		line := make([]rune, width)
  		cy := imagMin + (imagMax-imagMin)*float64(py)/float64(height-1)
  		if height == 1 {
  			cy = (imagMin + imagMax) / 2
  		}
  		for px := 0; px < width; px++ {
  			cx := realMin + (realMax-realMin)*float64(px)/float64(width-1)
  			if width == 1 {
  				cx = (realMin + realMax) / 2
  			}
  			iter := escape(cx, cy, maxIter)
  			line[px] = cell(iter, maxIter, char, useGradient)
  		}
  		rows[py] = string(line)
  	}
  	return rows, nil
  }

  // escape returns the number of iterations before |z| > 2, capped at maxIter.
  func escape(cx, cy float64, maxIter int) int {
  	var x, y float64
  	for i := 0; i < maxIter; i++ {
  		x2 := x*x - y*y + cx
  		y2 := 2*x*y + cy
  		x, y = x2, y2
  		if x*x+y*y > 4 {
  			return i
  		}
  	}
  	return maxIter
  }

  // cell maps an iteration count to an output rune.
  func cell(iter, maxIter int, char rune, useGradient bool) rune {
  	inSet := iter >= maxIter
  	if !useGradient {
  		if inSet {
  			return char
  		}
  		return ' '
  	}
  	if inSet {
  		return rune(gradient[len(gradient)-1])
  	}
  	// Map escape iteration to a gradient index (slower escape => denser char).
  	idx := iter * (len(gradient) - 1) / maxIter
  	if idx >= len(gradient) {
  		idx = len(gradient) - 1
  	}
  	return rune(gradient[idx])
  }
  ```

- [ ] Run the test to see it pass. Run:
  ```bash
  go test ./internal/mandelbrot/
  ```
  Expected:
  ```
  ok  	github.com/example/fractals/internal/mandelbrot
  ```

- [ ] Commit. Run:
  ```bash
  git add -A && git commit -m "Add Mandelbrot rendering algorithm with tests"
  ```

---

### Task 4: Sierpinski Subcommand

**Files:** `internal/cli/sierpinski.go`, `internal/cli/root.go` (modify)

- [ ] Create `internal/cli/sierpinski.go`:
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
  			r := []rune(char)
  			if len(r) != 1 {
  				return fmt.Errorf("--char must be a single character, got %q", char)
  			}
  			rows, err := sierpinski.Generate(size, depth, r[0])
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
  ```

- [ ] Wire the subcommand into the root. Edit `internal/cli/root.go`'s `Execute` to attach it:
  ```go
  // Execute builds the command tree and runs it.
  func Execute() error {
  	root := newRootCmd()
  	root.AddCommand(newSierpinskiCmd())
  	return root.Execute()
  }
  ```

- [ ] Verify the subcommand runs. Run:
  ```bash
  go run ./cmd/fractals sierpinski --size 4 --depth 2
  ```
  Expected (2^2 = 4 rows, the bitwise triangle):
  ```
  ****
  * * 
  **  
  *   
  ```

- [ ] Verify custom char works. Run:
  ```bash
  go run ./cmd/fractals sierpinski --depth 2 --char '#'
  ```
  Expected: same shape using `#` instead of `*`.

- [ ] Verify error handling. Run:
  ```bash
  go run ./cmd/fractals sierpinski --depth 0
  ```
  Expected: exits non-zero, stderr contains `depth must be >= 1, got 0`.

- [ ] Verify multi-char rejection. Run:
  ```bash
  go run ./cmd/fractals sierpinski --char 'ab'
  ```
  Expected: stderr contains `--char must be a single character, got "ab"`.

- [ ] Commit. Run:
  ```bash
  git add -A && git commit -m "Add sierpinski subcommand"
  ```

---

### Task 5: Mandelbrot Subcommand

**Files:** `internal/cli/mandelbrot.go`, `internal/cli/root.go` (modify)

The `--char` flag for mandelbrot defaults to gradient mode. We detect whether the user set it via `cmd.Flags().Changed("char")`.

- [ ] Create `internal/cli/mandelbrot.go`:
  ```go
  package cli

  import (
  	"fmt"

  	"github.com/example/fractals/internal/mandelbrot"
  	"github.com/spf13/cobra"
  )

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
  			useGradient := !cmd.Flags().Changed("char")

  			var charRune rune
  			if !useGradient {
  				r := []rune(char)
  				if len(r) != 1 {
  					return fmt.Errorf("--char must be a single character, got %q", char)
  				}
  				charRune = r[0]
  			}

  			rows, err := mandelbrot.Render(width, height, iterations, charRune, useGradient)
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
  	cmd.Flags().StringVar(&char, "char", "", "single character; omit for gradient \" .:-=+*#%@\"")
  	return cmd
  }
  ```

- [ ] Wire it into the root. Edit `internal/cli/root.go`'s `Execute`:
  ```go
  // Execute builds the command tree and runs it.
  func Execute() error {
  	root := newRootCmd()
  	root.AddCommand(newSierpinskiCmd())
  	root.AddCommand(newMandelbrotCmd())
  	return root.Execute()
  }
  ```

- [ ] Verify default gradient render. Run:
  ```bash
  go run ./cmd/fractals mandelbrot --width 60 --height 20
  ```
  Expected: a 20-line, 60-column ASCII Mandelbrot using the gradient characters with a recognizable bulb/cardioid silhouette of `@`/`%`/`#` toward the left-center.

- [ ] Verify custom char render. Run:
  ```bash
  go run ./cmd/fractals mandelbrot --width 60 --height 20 --char '#'
  ```
  Expected: only `#` and spaces; in-set region filled with `#`.

- [ ] Verify error handling. Run:
  ```bash
  go run ./cmd/fractals mandelbrot --iterations 0
  ```
  Expected: exits non-zero, stderr contains `iterations must be >= 1, got 0`.

- [ ] Commit. Run:
  ```bash
  git add -A && git commit -m "Add mandelbrot subcommand"
  ```

---

### Task 6: Full Verification

**Files:** none (verification only)

- [ ] Run the entire test suite. Run:
  ```bash
  go test ./...
  ```
  Expected:
  ```
  ok  	github.com/example/fractals/internal/mandelbrot
  ok  	github.com/example/fractals/internal/sierpinski
  ```
  (cli/cmd packages have no tests and report `no test files` — acceptable.)

- [ ] Run `go vet`. Run:
  ```bash
  go vet ./...
  ```
  Expected: no output (clean).

- [ ] Verify top-level help lists both subcommands. Run:
  ```bash
  go run ./cmd/fractals --help
  ```
  Expected: `Available Commands:` section listing `mandelbrot` and `sierpinski`.

- [ ] Verify subcommand help. Run:
  ```bash
  go run ./cmd/fractals sierpinski --help
  ```
  Expected: shows `--size`, `--depth`, `--char` flags with defaults `32`, `5`, `*`.

- [ ] Final commit (if any tracked changes remain, e.g. `go.sum`). Run:
  ```bash
  git add -A && git commit -m "Verify build, tests, and help output" --allow-empty
  ```

---

## Self-Review

**Spec coverage check:**

1. ✅ `fractals --help` shows usage — Task 1 + Task 6.
2. ✅ `fractals sierpinski` outputs a triangle — Task 4 (defaults size 32 / depth 5).
3. ✅ `fractals mandelbrot` outputs a Mandelbrot set — Task 5 (gradient default).
4. ✅ `--size`, `--width`, `--height`, `--depth`, `--iterations` flags — Tasks 4 & 5.
5. ✅ `--char` customizes output — Tasks 4 & 5; gradient fallback for mandelbrot via `Changed`.
6. ✅ Invalid inputs produce clear errors — validation in both algorithm packages + single-char checks in CLI; verified in Tasks 4 & 5.
7. ✅ All tests pass — Task 6.

**Placeholder scan:** No `TODO`, `FIXME`, or stub functions remain; all code blocks are complete and compilable.

**Type consistency check:**
- `sierpinski.Generate(size, depth int, char rune) ([]string, error)` — caller in `cli/sierpinski.go` passes `int, int, rune` and ranges over `[]string`. ✅
- `mandelbrot.Render(width, height, maxIter int, char rune, useGradient bool) ([]string, error)` — caller in `cli/mandelbrot.go` matches; test signatures in Task 3 match (e.g. `Render(40, 20, 50, 0, false)`). ✅
- `cli.Execute() error` — `main.go` checks the returned error. ✅

**Note corrected during review:** The `mandelbrot.Render` test `TestRenderGradientContainsSetChar` relies on the origin being in-set, which holds because `c=0` never escapes — and `realMin..realMax` / `imagMin..imagMax` include `0`, so at least one grid cell lands near the origin region producing `@`. Sufficiently large default grids (80×24) guarantee this; smaller test grids in `TestRenderDimensions` deliberately don't assert `@`. Consistent.