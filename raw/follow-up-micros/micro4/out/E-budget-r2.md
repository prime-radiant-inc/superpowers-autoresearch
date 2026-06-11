# Go Fractals CLI - Implementation Plan

## Global Constraints

- Go 1.21+ (set `go 1.21` in `go.mod`)
- Dependency: `github.com/spf13/cobra` only
- Module path: `github.com/example/fractals`
- Sierpinski default char: `*`; Mandelbrot default gradient: `" .:-=+*#%@"` (10 chars, space first)
- All output to stdout, one row per line
- Invalid inputs (non-positive sizes/dimensions/depth/iterations) produce clear errors and non-zero exit

## File Structure

- `go.mod` — module + cobra dependency
- `internal/sierpinski/sierpinski.go` — `Render(size, depth int, char rune) ([]string, error)`
- `internal/sierpinski/sierpinski_test.go` — algorithm tests
- `internal/mandelbrot/mandelbrot.go` — `Render(width, height, iterations int, gradient []rune) ([]string, error)`
- `internal/mandelbrot/mandelbrot_test.go` — algorithm tests
- `internal/cli/root.go` — root cobra command
- `internal/cli/sierpinski.go` — sierpinski subcommand
- `internal/cli/mandelbrot.go` — mandelbrot subcommand
- `cmd/fractals/main.go` — entry point

---

### Task 1: Module setup

**Files:** `go.mod`

- [ ] Run `go mod init github.com/example/fractals`
- [ ] Edit `go.mod` to ensure `go 1.21`
- [ ] Run `go get github.com/spf13/cobra@latest`
- [ ] Verify: `go build ./...` → exits 0 (no packages yet, no error)
- [ ] Commit: `chore: init module with cobra`

**Interfaces:** Produces module `github.com/example/fractals` for all imports.

---

### Task 2: Sierpinski algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

The classic bit-trick: cell `(row, col)` is filled when `(row & col) == 0`. `size` rows produce a triangle; `depth` caps recursion by limiting rows to `min(size, 2^depth)`.

- [ ] Write failing test:

```go
package sierpinski

import "testing"

func TestRenderSmall(t *testing.T) {
	lines, err := Render(4, 2, '*')
	if err != nil {
		t.Fatal(err)
	}
	want := []string{"*", "* *", "*   *", "* * * *"}
	if len(lines) != len(want) {
		t.Fatalf("got %d lines, want %d", len(lines), len(want))
	}
	for i := range want {
		if lines[i] != want[i] {
			t.Errorf("line %d = %q, want %q", i, lines[i], want[i])
		}
	}
}

func TestRenderCustomChar(t *testing.T) {
	lines, _ := Render(2, 1, '#')
	if lines[1] != "# #" {
		t.Errorf("got %q, want %q", lines[1], "# #")
	}
}

func TestRenderInvalid(t *testing.T) {
	if _, err := Render(0, 5, '*'); err == nil {
		t.Error("expected error for size 0")
	}
	if _, err := Render(4, 0, '*'); err == nil {
		t.Error("expected error for depth 0")
	}
}
```

- [ ] Run `go test ./internal/sierpinski/` → FAIL (undefined: Render)
- [ ] Implement:

```go
package sierpinski

import "fmt"

// Render returns the Sierpinski triangle as rows of text.
// size is the number of rows; depth caps rows to 2^depth.
func Render(size, depth int, char rune) ([]string, error) {
	if size <= 0 {
		return nil, fmt.Errorf("size must be positive, got %d", size)
	}
	if depth <= 0 {
		return nil, fmt.Errorf("depth must be positive, got %d", depth)
	}
	rows := size
	if cap := 1 << depth; rows > cap {
		rows = cap
	}
	lines := make([]string, rows)
	for r := 0; r < rows; r++ {
		buf := make([]rune, 0, 2*r+1)
		for c := 0; c <= r; c++ {
			if r&c == 0 {
				buf = append(buf, char)
			} else {
				buf = append(buf, ' ')
			}
			if c < r {
				buf = append(buf, ' ')
			}
		}
		lines[r] = string(buf)
	}
	return lines, nil
}
```

- [ ] Run `go test ./internal/sierpinski/` → PASS
- [ ] Commit: `feat: sierpinski algorithm`

**Interfaces:** Consumes module path. Produces `sierpinski.Render(size, depth int, char rune) ([]string, error)`.

---

### Task 3: Mandelbrot algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

Map pixel `(x,y)` to complex plane (real −2.5..1.0, imag −1.0..1.0), iterate `z=z²+c`, pick gradient char by escape ratio.

- [ ] Write failing test:

```go
package mandelbrot

import (
	"strings"
	"testing"
)

func TestRenderDimensions(t *testing.T) {
	lines, err := Render(20, 10, 50, []rune(" .:-=+*#%@"))
	if err != nil {
		t.Fatal(err)
	}
	if len(lines) != 10 {
		t.Fatalf("got %d rows, want 10", len(lines))
	}
	for i, l := range lines {
		if len([]rune(l)) != 20 {
			t.Errorf("row %d width %d, want 20", i, len([]rune(l)))
		}
	}
}

func TestRenderCenterInSet(t *testing.T) {
	// Center of plane is inside the set -> last gradient char.
	lines, _ := Render(21, 11, 100, []rune(" .:-=+*#%@"))
	mid := []rune(lines[5])
	if mid[10] != '@' {
		t.Errorf("center = %q, want '@'", mid[10])
	}
}

func TestRenderSingleChar(t *testing.T) {
	lines, _ := Render(10, 5, 50, []rune{'#'})
	if strings.ContainsAny(lines[2], " .:-=+*%@") {
		t.Error("single-char gradient leaked other chars")
	}
}

func TestRenderInvalid(t *testing.T) {
	if _, err := Render(0, 10, 50, []rune("@")); err == nil {
		t.Error("expected error for width 0")
	}
	if _, err := Render(10, 0, 50, []rune("@")); err == nil {
		t.Error("expected error for height 0")
	}
	if _, err := Render(10, 10, 0, []rune("@")); err == nil {
		t.Error("expected error for iterations 0")
	}
	if _, err := Render(10, 10, 50, []rune{}); err == nil {
		t.Error("expected error for empty gradient")
	}
}
```

- [ ] Run `go test ./internal/mandelbrot/` → FAIL
- [ ] Implement:

```go
package mandelbrot

import "fmt"

// Render returns the Mandelbrot set as ASCII rows.
// gradient maps escape speed to characters; last char = in-set.
func Render(width, height, iterations int, gradient []rune) ([]string, error) {
	if width <= 0 {
		return nil, fmt.Errorf("width must be positive, got %d", width)
	}
	if height <= 0 {
		return nil, fmt.Errorf("height must be positive, got %d", height)
	}
	if iterations <= 0 {
		return nil, fmt.Errorf("iterations must be positive, got %d", iterations)
	}
	if len(gradient) == 0 {
		return nil, fmt.Errorf("gradient must not be empty")
	}
	const rMin, rMax, iMin, iMax = -2.5, 1.0, -1.0, 1.0
	last := len(gradient) - 1
	lines := make([]string, height)
	for py := 0; py < height; py++ {
		ci := iMin + (iMax-iMin)*float64(py)/float64(height-1+b2i(height == 1))
		row := make([]rune, width)
		for px := 0; px < width; px++ {
			cr := rMin + (rMax-rMin)*float64(px)/float64(width-1+b2i(width == 1))
			var zr, zi float64
			n := 0
			for ; n < iterations; n++ {
				zr2, zi2 := zr*zr, zi*zi
				if zr2+zi2 > 4 {
					break
				}
				zr, zi = zr2-zi2+cr, 2*zr*zi+ci
			}
			if n == iterations {
				row[px] = gradient[last]
			} else {
				idx := n * len(gradient) / iterations
				if idx > last {
					idx = last
				}
				row[px] = gradient[idx]
			}
		}
		lines[py] = string(row)
	}
	return lines, nil
}

func b2i(b bool) int {
	if b {
		return 1
	}
	return 0
}
```

- [ ] Run `go test ./internal/mandelbrot/` → PASS
- [ ] Commit: `feat: mandelbrot algorithm`

**Interfaces:** Produces `mandelbrot.Render(width, height, iterations int, gradient []rune) ([]string, error)`.

---

### Task 4: Root CLI command

**Files:** `internal/cli/root.go`, `cmd/fractals/main.go`

- [ ] Implement `internal/cli/root.go`:

```go
package cli

import "github.com/spf13/cobra"

// NewRootCmd builds the top-level fractals command.
func NewRootCmd() *cobra.Command {
	root := &cobra.Command{
		Use:   "fractals",
		Short: "Generate ASCII art fractals",
	}
	root.AddCommand(newSierpinskiCmd())
	root.AddCommand(newMandelbrotCmd())
	return root
}
```

- [ ] Implement `cmd/fractals/main.go`:

```go
package main

import (
	"os"

	"github.com/example/fractals/internal/cli"
)

func main() {
	if err := cli.NewRootCmd().Execute(); err != nil {
		os.Exit(1)
	}
}
```

- [ ] (subcommand files added in Tasks 5–6; build verified there)
- [ ] Commit: `feat: root cli command`

**Interfaces:** Consumes `sierpinski.Render`, `mandelbrot.Render`. Produces `cli.NewRootCmd() *cobra.Command`; expects `newSierpinskiCmd()` and `newMandelbrotCmd()` in package `cli`.

---

### Task 5: Sierpinski subcommand

**Files:** `internal/cli/sierpinski.go`

- [ ] Implement:

```go
package cli

import (
	"fmt"

	"github.com/example/fractals/internal/sierpinski"
	"github.com/spf13/cobra"
)

func newSierpinskiCmd() *cobra.Command {
	var size, depth int
	var char string
	cmd := &cobra.Command{
		Use:   "sierpinski",
		Short: "Generate a Sierpinski triangle",
		RunE: func(cmd *cobra.Command, _ []string) error {
			r := []rune(char)
			if len(r) != 1 {
				return fmt.Errorf("--char must be exactly one character, got %q", char)
			}
			lines, err := sierpinski.Render(size, depth, r[0])
			if err != nil {
				return err
			}
			for _, l := range lines {
				fmt.Fprintln(cmd.OutOrStdout(), l)
			}
			return nil
		},
	}
	cmd.Flags().IntVar(&size, "size", 32, "Width of the triangle base")
	cmd.Flags().IntVar(&depth, "depth", 5, "Recursion depth")
	cmd.Flags().StringVar(&char, "char", "*", "Character to use")
	return cmd
}
```

- [ ] Run `go build ./...` → exits 0
- [ ] Run `go run ./cmd/fractals sierpinski --size 4 --depth 2` → prints 4-row triangle
- [ ] Commit: `feat: sierpinski subcommand`

**Interfaces:** Consumes `sierpinski.Render`. Produces `newSierpinskiCmd() *cobra.Command`.

---

### Task 6: Mandelbrot subcommand

**Files:** `internal/cli/mandelbrot.go`

- [ ] Implement:

```go
package cli

import (
	"fmt"

	"github.com/example/fractals/internal/mandelbrot"
	"github.com/spf13/cobra"
)

func newMandelbrotCmd() *cobra.Command {
	var width, height, iterations int
	var char string
	cmd := &cobra.Command{
		Use:   "mandelbrot",
		Short: "Render the Mandelbrot set",
		RunE: func(cmd *cobra.Command, _ []string) error {
			gradient := []rune(" .:-=+*#%@")
			if char != "" {
				r := []rune(char)
				if len(r) != 1 {
					return fmt.Errorf("--char must be exactly one character, got %q", char)
				}
				gradient = r
			}
			lines, err := mandelbrot.Render(width, height, iterations, gradient)
			if err != nil {
				return err
			}
			for _, l := range lines {
				fmt.Fprintln(cmd.OutOrStdout(), l)
			}
			return nil
		},
	}
	cmd.Flags().IntVar(&width, "width", 80, "Output width")
	cmd.Flags().IntVar(&height, "height", 24, "Output height")
	cmd.Flags().IntVar(&iterations, "iterations", 100, "Max iterations")
	cmd.Flags().StringVar(&char, "char", "", "Single character (omit for gradient)")
	return cmd
}
```

- [ ] Run `go run ./cmd/fractals mandelbrot --width 40 --height 20` → prints recognizable set
- [ ] Run `go run ./cmd/fractals --help` → shows usage with both subcommands
- [ ] Run `go run ./cmd/fractals sierpinski --size 0` → error `size must be positive, got 0`, exit 1
- [ ] Commit: `feat: mandelbrot subcommand`

**Interfaces:** Consumes `mandelbrot.Render`. Produces `newMandelbrotCmd() *cobra.Command`.

---

### Task 7: End-to-end verification

**Files:** none (verification only)

- [ ] Run `go test ./...` → all PASS
- [ ] Run `go vet ./...` → no output
- [ ] Verify acceptance: `--help` (AC1), `sierpinski` triangle (AC2), `mandelbrot` set (AC3), flags (AC4), `--char '#'` on both (AC5), invalid input error (AC6), tests (AC7)
- [ ] Commit: `test: verify acceptance criteria`

**Interfaces:** Consumes the full binary.

---

## Self-Review

- **Spec coverage:** All flags, defaults, both commands, gradient string `" .:-=+*#%@"`, custom char, error handling, help, Go 1.21, cobra — covered (Tasks 2–7).
- **Placeholder scan:** No TODOs or stubs; all code blocks complete.
- **Type consistency:** `sierpinski.Render(int,int,rune)` and `mandelbrot.Render(int,int,int,[]rune)` signatures match between Interfaces blocks and callers in Tasks 5–6. `b2i` guards single-row/column division-by-zero. Single-char `--char` validated as exactly one rune in both subcommands.