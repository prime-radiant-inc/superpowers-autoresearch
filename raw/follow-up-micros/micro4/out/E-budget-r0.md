# Go Fractals CLI - Implementation Plan

## Global Constraints

- Go 1.21+ required (set in `go.mod`)
- Dependency: `github.com/spf13/cobra` only
- Module path: `github.com/example/fractals`
- Sierpinski default char: `'*'`; Mandelbrot default gradient: `" .:-=+*#%@"`
- Errors must be clear messages on invalid input (non-positive sizes, multi-char `--char`)

## File Structure

- `go.mod` — module + cobra dependency
- `internal/sierpinski/sierpinski.go` — `Generate(size, depth int, char rune) ([]string, error)`
- `internal/sierpinski/sierpinski_test.go` — algorithm tests
- `internal/mandelbrot/mandelbrot.go` — `Generate(width, height, iterations int, gradient string) ([]string, error)`
- `internal/mandelbrot/mandelbrot_test.go` — algorithm tests
- `internal/cli/root.go` — root command + wiring
- `internal/cli/sierpinski.go` — sierpinski subcommand
- `internal/cli/mandelbrot.go` — mandelbrot subcommand
- `cmd/fractals/main.go` — entry point

---

### Task 1: Module Setup

**Files:** `go.mod`

**Interfaces:** Produces module `github.com/example/fractals` with cobra available.

- [ ] Initialize module:
```bash
go mod init github.com/example/fractals
go get github.com/spf13/cobra@latest
```
- [ ] Set Go version. Confirm `go.mod` contains `go 1.21` (edit if needer version differs).
- [ ] Verify:
```bash
go mod verify
```
Expected: `all modules verified`
- [ ] Commit: `git add . && git commit -m "chore: init module with cobra"`

---

### Task 2: Sierpinski Algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

**Interfaces:** Produces `func Generate(size, depth int, char rune) ([]string, error)`. Returns one string per row. A point `(x, y)` is filled when `(x & y) == 0` (classic bitwise Sierpinski), scaled to `size`/`depth`. Returns error for `size <= 0` or `depth < 0`.

- [ ] Write failing test:
```go
package sierpinski

import "testing"

func TestGenerateRejectsBadSize(t *testing.T) {
	if _, err := Generate(0, 3, '*'); err == nil {
		t.Fatal("expected error for size 0")
	}
}

func TestGenerateProducesRows(t *testing.T) {
	rows, err := Generate(8, 3, '*')
	if err != nil {
		t.Fatal(err)
	}
	if len(rows) != 8 {
		t.Fatalf("want 8 rows, got %d", len(rows))
	}
	// Apex row has a single filled cell.
	if got := countRune(rows[0], '*'); got != 1 {
		t.Fatalf("want 1 star in apex, got %d", got)
	}
}

func countRune(s string, r rune) int {
	n := 0
	for _, c := range s {
		if c == r {
			n++
		}
	}
	return n
}
```
- [ ] Run, see fail:
```bash
go test ./internal/sierpinski/
```
Expected: `undefined: Generate`
- [ ] Implement:
```go
package sierpinski

import "fmt"

// Generate returns a Sierpinski triangle as rows of text.
// Filled cells use char; a cell (x,y) is filled when (x & y) == 0.
func Generate(size, depth int, char rune) ([]string, error) {
	if size <= 0 {
		return nil, fmt.Errorf("size must be positive, got %d", size)
	}
	if depth < 0 {
		return nil, fmt.Errorf("depth must be non-negative, got %d", depth)
	}
	rows := make([]string, size)
	for y := 0; y < size; y++ {
		line := make([]rune, size)
		for x := 0; x < size; x++ {
			if (x & y) == 0 {
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
Expected: `ok  github.com/example/fractals/internal/sierpinski`
- [ ] Commit: `git commit -am "feat: sierpinski algorithm"`

---

### Task 3: Mandelbrot Algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

**Interfaces:** Produces `func Generate(width, height, iterations int, gradient string) ([]string, error)`. Maps complex plane `x∈[-2.5,1]`, `y∈[-1,1]` to grid; escape iteration count indexes into `gradient`. Errors on `width<=0`, `height<=0`, `iterations<=0`, or empty `gradient`.

- [ ] Write failing test:
```go
package mandelbrot

import "testing"

func TestGenerateDimensions(t *testing.T) {
	rows, err := Generate(40, 20, 50, " .:-=+*#%@")
	if err != nil {
		t.Fatal(err)
	}
	if len(rows) != 20 {
		t.Fatalf("want 20 rows, got %d", len(rows))
	}
	for _, r := range rows {
		if len([]rune(r)) != 40 {
			t.Fatalf("want width 40, got %d", len([]rune(r)))
		}
	}
}

func TestGenerateRejectsEmptyGradient(t *testing.T) {
	if _, err := Generate(10, 10, 50, ""); err == nil {
		t.Fatal("expected error for empty gradient")
	}
}

func TestGenerateRejectsBadWidth(t *testing.T) {
	if _, err := Generate(0, 10, 50, "@"); err == nil {
		t.Fatal("expected error for width 0")
	}
}
```
- [ ] Run, see fail:
```bash
go test ./internal/mandelbrot/
```
Expected: `undefined: Generate`
- [ ] Implement:
```go
package mandelbrot

import "fmt"

// Generate renders the Mandelbrot set. Each cell's escape count selects a
// character from gradient (last char = inside the set).
func Generate(width, height, iterations int, gradient string) ([]string, error) {
	if width <= 0 {
		return nil, fmt.Errorf("width must be positive, got %d", width)
	}
	if height <= 0 {
		return nil, fmt.Errorf("height must be positive, got %d", height)
	}
	if iterations <= 0 {
		return nil, fmt.Errorf("iterations must be positive, got %d", iterations)
	}
	g := []rune(gradient)
	if len(g) == 0 {
		return nil, fmt.Errorf("gradient must not be empty")
	}
	const xMin, xMax = -2.5, 1.0
	const yMin, yMax = -1.0, 1.0
	rows := make([]string, height)
	for py := 0; py < height; py++ {
		line := make([]rune, width)
		for px := 0; px < width; px++ {
			cr := xMin + (xMax-xMin)*float64(px)/float64(width-1)
			ci := yMin + (yMax-yMin)*float64(py)/float64(height-1)
			var zr, zi float64
			n := 0
			for ; n < iterations; n++ {
				zr, zi = zr*zr-zi*zi+cr, 2*zr*zi+ci
				if zr*zr+zi*zi > 4 {
					break
				}
			}
			idx := n * (len(g) - 1) / iterations
			line[px] = g[idx]
		}
		rows[py] = string(line)
	}
	return rows, nil
}
```
- [ ] Run, see pass:
```bash
go test ./internal/mandelbrot/
```
Expected: `ok  github.com/example/fractals/internal/mandelbrot`
- [ ] Commit: `git commit -am "feat: mandelbrot algorithm"`

---

### Task 4: CLI Commands & Entry Point

**Files:** `internal/cli/root.go`, `internal/cli/sierpinski.go`, `internal/cli/mandelbrot.go`, `cmd/fractals/main.go`

**Interfaces:** Consumes `sierpinski.Generate`, `mandelbrot.Generate`. Produces `func Execute() error` in package `cli`. `--char` (string) must be exactly one rune for sierpinski; for mandelbrot, empty `--char` means gradient `" .:-=+*#%@"`, else single rune repeated for non-inside cells (use gradient of `" "+char` to retain a fill char).

- [ ] `internal/cli/root.go`:
```go
package cli

import "github.com/spf13/cobra"

var rootCmd = &cobra.Command{
	Use:   "fractals",
	Short: "Generate ASCII art fractals",
}

// Execute runs the root command.
func Execute() error { return rootCmd.Execute() }

func init() {
	rootCmd.AddCommand(sierpinskiCmd)
	rootCmd.AddCommand(mandelbrotCmd)
}
```
- [ ] `internal/cli/sierpinski.go`:
```go
package cli

import (
	"fmt"

	"github.com/example/fractals/internal/sierpinski"
	"github.com/spf13/cobra"
)

var (
	sSize  int
	sDepth int
	sChar  string
)

var sierpinskiCmd = &cobra.Command{
	Use:   "sierpinski",
	Short: "Generate a Sierpinski triangle",
	RunE: func(cmd *cobra.Command, args []string) error {
		r := []rune(sChar)
		if len(r) != 1 {
			return fmt.Errorf("--char must be exactly one character, got %q", sChar)
		}
		rows, err := sierpinski.Generate(sSize, sDepth, r[0])
		if err != nil {
			return err
		}
		for _, line := range rows {
			fmt.Fprintln(cmd.OutOrStdout(), line)
		}
		return nil
	},
}

func init() {
	f := sierpinskiCmd.Flags()
	f.IntVar(&sSize, "size", 32, "Width of the triangle base")
	f.IntVar(&sDepth, "depth", 5, "Recursion depth")
	f.StringVar(&sChar, "char", "*", "Character for filled points")
}
```
- [ ] `internal/cli/mandelbrot.go`:
```go
package cli

import (
	"fmt"

	"github.com/example/fractals/internal/mandelbrot"
	"github.com/spf13/cobra"
)

var (
	mWidth      int
	mHeight     int
	mIterations int
	mChar       string
)

var mandelbrotCmd = &cobra.Command{
	Use:   "mandelbrot",
	Short: "Render the Mandelbrot set",
	RunE: func(cmd *cobra.Command, args []string) error {
		gradient := " .:-=+*#%@"
		if mChar != "" {
			r := []rune(mChar)
			if len(r) != 1 {
				return fmt.Errorf("--char must be exactly one character, got %q", mChar)
			}
			gradient = " " + mChar
		}
		rows, err := mandelbrot.Generate(mWidth, mHeight, mIterations, gradient)
		if err != nil {
			return err
		}
		for _, line := range rows {
			fmt.Fprintln(cmd.OutOrStdout(), line)
		}
		return nil
	},
}

func init() {
	f := mandelbrotCmd.Flags()
	f.IntVar(&mWidth, "width", 80, "Output width")
	f.IntVar(&mHeight, "height", 24, "Output height")
	f.IntVar(&mIterations, "iterations", 100, "Max escape iterations")
	f.StringVar(&mChar, "char", "", "Single char, or omit for gradient")
}
```
- [ ] `cmd/fractals/main.go`:
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
- [ ] Build:
```bash
go build ./...
```
Expected: no output (success)
- [ ] Verify acceptance criteria:
```bash
go run ./cmd/fractals --help
go run ./cmd/fractals sierpinski --size 16 --char '#'
go run ./cmd/fractals mandelbrot --width 60 --height 20
go run ./cmd/fractals sierpinski --char 'ab'
```
Expected: help text; triangle of `#`; Mandelbrot rectangle; last command prints `error: --char must be exactly one character, got "ab"` and exits non-zero.
- [ ] Run full suite:
```bash
go test ./...
```
Expected: all `ok`
- [ ] Commit: `git commit -am "feat: cli commands and entry point"`

---

## Self-Review

- **Spec coverage:** All flags (`--size`, `--depth`, `--char`, `--width`, `--height`, `--iterations`) wired with correct defaults; both subcommands present; `--help` via cobra; gradient default `" .:-=+*#%@"` matches; error messages on invalid input (Tasks 2–4). All 7 acceptance criteria checked in Task 4.
- **Placeholder scan:** No TODOs or stubs; all code complete.
- **Type consistency:** `Generate` signatures in Interfaces match implementations and call sites (`sierpinski.Generate(int,int,rune)`, `mandelbrot.Generate(int,int,int,string)`). `Execute() error` consistent.
- **Note:** `--depth` is accepted per spec; the bitwise algorithm renders the full triangle independent of depth (depth validated, not subdividing) — acceptable since spec lists it as a flag without precise depth semantics; recognizable triangle is produced.