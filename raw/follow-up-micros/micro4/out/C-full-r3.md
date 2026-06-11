# Go Fractals CLI - Implementation Plan

## Global Constraints

- Go 1.21+ required (`go.mod` declares `go 1.21`)
- CLI dependency: `github.com/spf13/cobra` (only third-party dependency)
- Module path: `github.com/example/fractals`
- Sierpinski default char: `*`; default size: `32`; default depth: `5`
- Mandelbrot default width: `80`; default height: `24`; default iterations: `100`
- Mandelbrot default gradient (when `--char` omitted): `" .:-=+*#%@"` (10 chars, space first)
- Invalid inputs must produce clear error messages and a non-zero exit code
- Algorithm packages (`internal/sierpinski`, `internal/mandelbrot`) must have zero dependency on cobra or stdin/stdout — they return `string` or `[]string`

## File Structure

| Path | Responsibility |
|------|----------------|
| `go.mod` | Module declaration, Go version, cobra dependency |
| `internal/sierpinski/sierpinski.go` | Pure Sierpinski generation algorithm |
| `internal/sierpinski/sierpinski_test.go` | Tests for Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure Mandelbrot rendering algorithm |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for Mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command, help, command assembly |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand: flag parsing → algorithm → stdout |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand: flag parsing → algorithm → stdout |
| `internal/cli/cli_test.go` | Integration tests exercising commands via cobra |
| `cmd/fractals/main.go` | Entry point: calls `cli.Execute()` |

---

### Task 1: Module setup and Sierpinski algorithm

**Files:**
- `go.mod`
- `internal/sierpinski/sierpinski.go`
- `internal/sierpinski/sierpinski_test.go`

**Interfaces:**
- Produces: `func Generate(size, depth int, char rune) ([]string, error)` in package `sierpinski`. Returns one string per row (no trailing newline on rows). Returns an error if `size < 1` or `depth < 0`.

The algorithm: a point `(x, y)` is filled when `(x & y) == 0` (the classic bitwise Sierpinski rule). `depth` bounds the bit-width considered: only the low `depth` bits of `x` and `y` participate, so the visible structure has `2^depth` resolution. We render `size` rows; row `y` (0-based from top) has `y+1` leading characters of content, left-aligned. For each row `y` and column `x` in `[0, y]`, the cell is filled if `((y & x) & mask) == 0` where `mask = (1 << depth) - 1`.

- [ ] Create `go.mod`:
```bash
mkdir -p cmd/fractals internal/sierpinski internal/mandelbrot internal/cli
cat > go.mod <<'EOF'
module github.com/example/fractals

go 1.21
EOF
```

- [ ] Write the failing test `internal/sierpinski/sierpinski_test.go`:
```go
package sierpinski

import (
	"strings"
	"testing"
)

func TestGenerateSmall(t *testing.T) {
	rows, err := Generate(4, 5, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 4 {
		t.Fatalf("expected 4 rows, got %d", len(rows))
	}
	// Row 0: y=0 -> only x=0, (0&0)==0 filled
	if rows[0] != "*" {
		t.Errorf("row 0 = %q, want %q", rows[0], "*")
	}
	// Row 1: y=1 -> x=0:(1&0)=0 filled, x=1:(1&1)=1 empty
	if rows[1] != "* " {
		t.Errorf("row 1 = %q, want %q", rows[1], "* ")
	}
	// Row 2: y=2 -> x=0:(2&0)=0*, x=1:(2&1)=0*, x=2:(2&2)=2 space
	if rows[2] != "** " {
		t.Errorf("row 2 = %q, want %q", rows[2], "** ")
	}
	// Row 3: y=3 -> x=0:0*, x=1:(3&1)=1sp, x=2:(3&2)=2sp, x=3:(3&3)=3sp
	if rows[3] != "*   " {
		t.Errorf("row 3 = %q, want %q", rows[3], "*   ")
	}
}

func TestGenerateCustomChar(t *testing.T) {
	rows, err := Generate(2, 5, '#')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(rows[0], "#") {
		t.Errorf("expected '#' in output, got %q", rows[0])
	}
}

func TestGenerateInvalidSize(t *testing.T) {
	if _, err := Generate(0, 5, '*'); err == nil {
		t.Error("expected error for size 0")
	}
}

func TestGenerateInvalidDepth(t *testing.T) {
	if _, err := Generate(4, -1, '*'); err == nil {
		t.Error("expected error for negative depth")
	}
}
```

- [ ] Run the test, expect failure (no `Generate`):
```bash
go test ./internal/sierpinski/
```
Expected: `undefined: Generate` build failure.

- [ ] Implement `internal/sierpinski/sierpinski.go`:
```go
// Package sierpinski generates Sierpinski triangles as ASCII rows.
package sierpinski

import "fmt"

// Generate returns size rows representing a Sierpinski triangle.
// A cell (x, y) is filled when the low depth bits of (x & y) are zero.
// char is used for filled cells; spaces fill the rest of each row.
func Generate(size, depth int, char rune) ([]string, error) {
	if size < 1 {
		return nil, fmt.Errorf("size must be at least 1, got %d", size)
	}
	if depth < 0 {
		return nil, fmt.Errorf("depth must be non-negative, got %d", depth)
	}

	mask := (1 << depth) - 1
	rows := make([]string, size)
	for y := 0; y < size; y++ {
		line := make([]rune, y+1)
		for x := 0; x <= y; x++ {
			if (y&x)&mask == 0 {
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

- [ ] Run the test, expect pass:
```bash
go test ./internal/sierpinski/
```
Expected: `ok  	github.com/example/fractals/internal/sierpinski`

- [ ] Commit:
```bash
git add go.mod internal/sierpinski/
git commit -m "Add module setup and Sierpinski algorithm"
```

---

### Task 2: Mandelbrot algorithm

**Files:**
- `internal/mandelbrot/mandelbrot.go`
- `internal/mandelbrot/mandelbrot_test.go`

**Interfaces:**
- Produces: `func Render(width, height, iterations int, gradient string) ([]string, error)` in package `mandelbrot`. Returns `height` strings each of length `width`. `gradient` must be non-empty; each cell maps its escape iteration count onto a character in `gradient`. Returns an error if `width < 1`, `height < 1`, `iterations < 1`, or `gradient == ""`.
- `DefaultGradient` constant `= " .:-=+*#%@"`.

Mapping: viewport is the complex plane region real `[-2.5, 1.0]`, imaginary `[-1.0, 1.0]`. For each pixel compute escape iteration `n` (0..iterations). Points that never escape (`n == iterations`) map to the **last** gradient char (densest). Otherwise index `= n * (len(gradient)-1) / iterations`.

- [ ] Write the failing test `internal/mandelbrot/mandelbrot_test.go`:
```go
package mandelbrot

import "testing"

func TestRenderDimensions(t *testing.T) {
	rows, err := Render(20, 10, 50, DefaultGradient)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 10 {
		t.Fatalf("expected 10 rows, got %d", len(rows))
	}
	for i, r := range rows {
		if len([]rune(r)) != 20 {
			t.Errorf("row %d width = %d, want 20", i, len([]rune(r)))
		}
	}
}

func TestRenderInsideSetIsDensest(t *testing.T) {
	// The origin (0,0) is inside the set; with this viewport the center
	// rows should contain the densest (last) gradient character.
	rows, err := Render(80, 24, 100, DefaultGradient)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	last := DefaultGradient[len(DefaultGradient)-1]
	found := false
	for _, r := range rows {
		for _, c := range r {
			if byte(c) == last {
				found = true
			}
		}
	}
	if !found {
		t.Errorf("expected densest char %q somewhere in output", string(last))
	}
}

func TestRenderSingleChar(t *testing.T) {
	rows, err := Render(10, 5, 50, "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	for _, r := range rows {
		for _, c := range r {
			if c != '#' {
				t.Errorf("expected only '#', got %q", string(c))
			}
		}
	}
}

func TestRenderInvalid(t *testing.T) {
	cases := []struct {
		name                          string
		w, h, it                      int
		grad                          string
	}{
		{"width", 0, 5, 10, "#"},
		{"height", 5, 0, 10, "#"},
		{"iterations", 5, 5, 0, "#"},
		{"gradient", 5, 5, 10, ""},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if _, err := Render(c.w, c.h, c.it, c.grad); err == nil {
				t.Errorf("expected error for %s", c.name)
			}
		})
	}
}
```

- [ ] Run the test, expect failure:
```bash
go test ./internal/mandelbrot/
```
Expected: `undefined: Render` / `undefined: DefaultGradient`.

- [ ] Implement `internal/mandelbrot/mandelbrot.go`:
```go
// Package mandelbrot renders the Mandelbrot set as ASCII rows.
package mandelbrot

import "fmt"

// DefaultGradient maps low-to-high iteration density to characters.
const DefaultGradient = " .:-=+*#%@"

const (
	realMin = -2.5
	realMax = 1.0
	imagMin = -1.0
	imagMax = 1.0
)

// Render returns height rows each width characters wide. Each cell's escape
// iteration count is mapped onto gradient; non-escaping points use the last
// gradient character.
func Render(width, height, iterations int, gradient string) ([]string, error) {
	if width < 1 {
		return nil, fmt.Errorf("width must be at least 1, got %d", width)
	}
	if height < 1 {
		return nil, fmt.Errorf("height must be at least 1, got %d", height)
	}
	if iterations < 1 {
		return nil, fmt.Errorf("iterations must be at least 1, got %d", iterations)
	}
	if gradient == "" {
		return nil, fmt.Errorf("gradient must not be empty")
	}

	grad := []rune(gradient)
	rows := make([]string, height)
	for py := 0; py < height; py++ {
		ci := imagMin + (imagMax-imagMin)*float64(py)/float64(height-zeroGuard(height))
		line := make([]rune, width)
		for px := 0; px < width; px++ {
			cr := realMin + (realMax-realMin)*float64(px)/float64(width-zeroGuard(width))
			n := escape(cr, ci, iterations)
			var idx int
			if n >= iterations {
				idx = len(grad) - 1
			} else {
				idx = n * (len(grad) - 1) / iterations
			}
			line[px] = grad[idx]
		}
		rows[py] = string(line)
	}
	return rows, nil
}

// zeroGuard returns 1 when n > 1 so division spans the full viewport, and 0
// when n == 1 to avoid dividing by zero (single row/col maps to the start).
func zeroGuard(n int) int {
	if n > 1 {
		return 1
	}
	return 0
}

func escape(cr, ci float64, maxIter int) int {
	var zr, zi float64
	for n := 0; n < maxIter; n++ {
		if zr*zr+zi*zi > 4.0 {
			return n
		}
		zr, zi = zr*zr-zi*zi+cr, 2*zr*zi+ci
	}
	return maxIter
}
```

- [ ] Run the test, expect pass:
```bash
go test ./internal/mandelbrot/
```
Expected: `ok  	github.com/example/fractals/internal/mandelbrot`

- [ ] Commit:
```bash
git add internal/mandelbrot/
git commit -m "Add Mandelbrot rendering algorithm"
```

---

### Task 3: CLI wiring with cobra

**Files:**
- `internal/cli/root.go`
- `internal/cli/sierpinski.go`
- `internal/cli/mandelbrot.go`
- `internal/cli/cli_test.go`
- `cmd/fractals/main.go`
- `go.mod`, `go.sum` (updated by `go get`)

**Interfaces:**
- Consumes: `sierpinski.Generate(size, depth int, char rune) ([]string, error)`, `mandelbrot.Render(width, height, iterations int, gradient string) ([]string, error)`, `mandelbrot.DefaultGradient`.
- Produces: `func Execute() error` in package `cli` (used by `main`). Internal helper `func newRootCmd() *cobra.Command` assembling subcommands; output is written to the command's configured `OutOrStdout()` so tests can capture it.
- `--char` parsing: a string flag; the first rune is used for Sierpinski. For Mandelbrot, if `--char` is set and non-empty, the whole string is used as a single-char gradient (first rune repeated semantics: pass the string; if it is one rune the algorithm fills with it); if `--char` is unset, `mandelbrot.DefaultGradient` is used.

- [ ] Add cobra dependency:
```bash
go get github.com/spf13/cobra@latest
```
Expected: `go.sum` created, `go.mod` now lists `github.com/spf13/cobra`.

- [ ] Write `internal/cli/root.go`:
```go
// Package cli wires the fractals command-line interface.
package cli

import "github.com/spf13/cobra"

func newRootCmd() *cobra.Command {
	root := &cobra.Command{
		Use:   "fractals",
		Short: "Generate ASCII art fractals",
		Long:  "fractals generates ASCII art fractals (Sierpinski triangle and Mandelbrot set).",
	}
	root.AddCommand(newSierpinskiCmd())
	root.AddCommand(newMandelbrotCmd())
	return root
}

// Execute runs the root command against os.Args.
func Execute() error {
	return newRootCmd().Execute()
}
```

- [ ] Write `internal/cli/sierpinski.go`:
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
			runes := []rune(char)
			if len(runes) == 0 {
				return fmt.Errorf("--char must not be empty")
			}
			rows, err := sierpinski.Generate(size, depth, runes[0])
			if err != nil {
				return err
			}
			for _, r := range rows {
				fmt.Fprintln(cmd.OutOrStdout(), r)
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

- [ ] Write `internal/cli/mandelbrot.go`:
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
			gradient := mandelbrot.DefaultGradient
			if cmd.Flags().Changed("char") {
				if char == "" {
					return fmt.Errorf("--char must not be empty")
				}
				gradient = char
			}
			rows, err := mandelbrot.Render(width, height, iterations, gradient)
			if err != nil {
				return err
			}
			for _, r := range rows {
				fmt.Fprintln(cmd.OutOrStdout(), r)
			}
			return nil
		},
	}
	cmd.Flags().IntVar(&width, "width", 80, "output width in characters")
	cmd.Flags().IntVar(&height, "height", 24, "output height in characters")
	cmd.Flags().IntVar(&iterations, "iterations", 100, "maximum iterations for escape calculation")
	cmd.Flags().StringVar(&char, "char", "", "single character, or omit for gradient")
	return cmd
}
```

- [ ] Write `internal/cli/cli_test.go`:
```go
package cli

import (
	"bytes"
	"strings"
	"testing"
)

func runCmd(t *testing.T, args ...string) (string, error) {
	t.Helper()
	cmd := newRootCmd()
	var out bytes.Buffer
	cmd.SetOut(&out)
	cmd.SetErr(&out)
	cmd.SetArgs(args)
	err := cmd.Execute()
	return out.String(), err
}

func TestHelp(t *testing.T) {
	out, err := runCmd(t, "--help")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "fractals") {
		t.Errorf("help missing program name: %q", out)
	}
	if !strings.Contains(out, "sierpinski") || !strings.Contains(out, "mandelbrot") {
		t.Errorf("help missing subcommands: %q", out)
	}
}

func TestSierpinskiOutput(t *testing.T) {
	out, err := runCmd(t, "sierpinski", "--size", "4", "--depth", "5")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 4 {
		t.Fatalf("expected 4 lines, got %d: %q", len(lines), out)
	}
	if lines[0] != "*" {
		t.Errorf("first line = %q, want %q", lines[0], "*")
	}
}

func TestSierpinskiCustomChar(t *testing.T) {
	out, err := runCmd(t, "sierpinski", "--size", "2", "--char", "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "#") {
		t.Errorf("expected '#' in output: %q", out)
	}
}

func TestMandelbrotOutput(t *testing.T) {
	out, err := runCmd(t, "mandelbrot", "--width", "20", "--height", "8", "--iterations", "50")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 8 {
		t.Fatalf("expected 8 lines, got %d: %q", len(lines), out)
	}
	if len([]rune(lines[0])) != 20 {
		t.Errorf("line width = %d, want 20", len([]rune(lines[0])))
	}
}

func TestMandelbrotCustomChar(t *testing.T) {
	out, err := runCmd(t, "mandelbrot", "--width", "10", "--height", "4", "--char", "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	body := strings.ReplaceAll(strings.TrimRight(out, "\n"), "\n", "")
	for _, c := range body {
		if c != '#' {
			t.Errorf("expected only '#', got %q", string(c))
		}
	}
}

func TestSierpinskiInvalidSize(t *testing.T) {
	_, err := runCmd(t, "sierpinski", "--size", "0")
	if err == nil {
		t.Error("expected error for size 0")
	}
}

func TestMandelbrotInvalidIterations(t *testing.T) {
	_, err := runCmd(t, "mandelbrot", "--iterations", "0")
	if err == nil {
		t.Error("expected error for iterations 0")
	}
}
```

- [ ] Write `cmd/fractals/main.go`:
```go
package main

import (
	"os"

	"github.com/example/fractals/internal/cli"
)

func main() {
	if err := cli.Execute(); err != nil {
		os.Exit(1)
	}
}
```

- [ ] Tidy modules and run the full test suite:
```bash
go mod tidy
go test ./...
```
Expected: `ok` for `internal/cli`, `internal/mandelbrot`, `internal/sierpinski`; `cmd/fractals` reports `no test files`.

- [ ] Build and smoke-test the binary:
```bash
go build -o /tmp/fractals ./cmd/fractals
/tmp/fractals --help
/tmp/fractals sierpinski --size 16 --depth 5
/tmp/fractals mandelbrot --width 40 --height 12 --iterations 50
/tmp/fractals sierpinski --size 0; echo "exit=$?"
```
Expected: help text lists `sierpinski` and `mandelbrot`; triangle and Mandelbrot render; last command prints `Error: size must be at least 1, got 0` and `exit=1`.

- [ ] Commit:
```bash
git add cmd/ internal/cli/ go.mod go.sum
git commit -m "Add cobra CLI, subcommands, and entry point"
```

---

## Self-Review

- **Acceptance criteria coverage:**
  1. `--help` → `TestHelp` + smoke test ✓
  2. recognizable triangle → `TestSierpinskiOutput` + `TestGenerateSmall` ✓
  3. recognizable Mandelbrot → `TestMandelbrotOutput` + `TestRenderInsideSetIsDensest` ✓
  4. size/width/height/depth/iterations flags → all exercised in `cli_test.go` ✓
  5. `--char` customization → `TestSierpinskiCustomChar`, `TestMandelbrotCustomChar` ✓
  6. invalid input errors → `TestSierpinskiInvalidSize`, `TestMandelbrotInvalidIterations`, algorithm-level invalid tests, smoke test exit code ✓
  7. all tests pass → `go test ./...` ✓

- **Placeholder scan:** no TODOs, no stub functions; every function fully implemented.

- **Type consistency:** `sierpinski.Generate(int, int, rune) ([]string, error)` and `mandelbrot.Render(int, int, int, string) ([]string, error)` are referenced identically in the Interfaces blocks and call sites in `internal/cli`. `mandelbrot.DefaultGradient` is a `string` constant used consistently. `cli.Execute() error` matches `main.go` usage.

- **Constraint check:** defaults (`size 32`, `depth 5`, char `*`; `width 80`, `height 24`, `iterations 100`; gradient `" .:-=+*#%@"`) are wired verbatim in the cobra flag definitions and constant. Module path `github.com/example/fractals` is used in all imports. Algorithm packages import no cobra and perform no I/O.

- **Edge note:** `zeroGuard` prevents division-by-zero when `width` or `height` equals 1, since validation only rejects values `< 1`.