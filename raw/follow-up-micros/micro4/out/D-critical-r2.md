# Go Fractals CLI - Implementation Plan

A command-line tool generating ASCII art fractals (Sierpinski triangle, Mandelbrot set) using cobra for the CLI layer and pure-Go algorithm packages.

## Global Constraints

- Go 1.21+ (set `go 1.21` in `go.mod`)
- CLI dependency: `github.com/spf13/cobra` (only external dependency)
- Binary name: `fractals`
- Sierpinski defaults: `--size` 32, `--depth` 5, `--char` `*`
- Mandelbrot defaults: `--width` 80, `--height` 24, `--iterations` 100, `--char` gradient `" .:-=+*#%@"` (10 chars, space first)
- Invalid inputs must produce clear error messages (non-zero exit)
- Output goes to stdout, one row per line
- Module path: `github.com/example/fractals`

## File Structure

| File | Responsibility |
|------|---------------|
| `go.mod` | Module definition, Go version, cobra dependency |
| `internal/sierpinski/sierpinski.go` | Sierpinski triangle generation algorithm |
| `internal/sierpinski/sierpinski_test.go` | Tests for Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Mandelbrot set rendering algorithm |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for Mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command and help wiring |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand: flags → algorithm → stdout |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand: flags → algorithm → stdout |
| `internal/cli/root_test.go` | CLI integration tests via command execution |
| `cmd/fractals/main.go` | Entry point invoking cli.Execute() |

---

### Task 1: Module setup and Sierpinski algorithm

Establishes the module and delivers the first testable algorithm package. No cobra needed yet.

**Files:**
- `go.mod`
- `internal/sierpinski/sierpinski.go`
- `internal/sierpinski/sierpinski_test.go`

**Interfaces:**
- Produces: `func Generate(size, depth int, char rune) ([]string, error)` — returns the triangle as a slice of strings (one per row), or an error for invalid input.

The classic bit-trick for a Sierpinski triangle: a point `(row, col)` in a triangular grid is filled when `(row AND col) == 0`. We render `size` rows; row `r` has leading spaces to center it and `r+1` cells. The `depth` parameter limits recursion-equivalent detail; clamp effective rows to `min(size, 2^depth)`.

- [ ] Write failing test `TestGenerate_BasicShape` in `sierpinski_test.go`:

```go
package sierpinski

import "testing"

func TestGenerate_BasicShape(t *testing.T) {
	rows, err := Generate(4, 5, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 4 {
		t.Fatalf("expected 4 rows, got %d", len(rows))
	}
	// Top row has exactly one filled cell.
	got := countRune(rows[0], '*')
	if got != 1 {
		t.Errorf("row 0: expected 1 star, got %d in %q", got, rows[0])
	}
	// Bottom row of a 4-high Sierpinski is fully filled (4 stars).
	if c := countRune(rows[3], '*'); c != 4 {
		t.Errorf("row 3: expected 4 stars, got %d in %q", c, rows[3])
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

- [ ] Run `go mod init github.com/example/fractals` then `go test ./internal/sierpinski/` — expect compile failure (no `Generate`).
- [ ] Implement `Generate` in `sierpinski.go`:

```go
package sierpinski

import "fmt"

// Generate returns the Sierpinski triangle as a slice of strings, one per row.
// A cell (row, col) is filled when (row & col) == 0.
func Generate(size, depth int, char rune) ([]string, error) {
	if size < 1 {
		return nil, fmt.Errorf("size must be >= 1, got %d", size)
	}
	if depth < 0 {
		return nil, fmt.Errorf("depth must be >= 0, got %d", depth)
	}
	rows := size
	if max := 1 << depth; rows > max {
		rows = max
	}
	out := make([]string, rows)
	for r := 0; r < rows; r++ {
		line := make([]rune, 0, rows+r)
		// Leading spaces to center the triangle.
		for s := 0; s < rows-r-1; s++ {
			line = append(line, ' ')
		}
		for c := 0; c <= r; c++ {
			if r&c == 0 {
				line = append(line, char)
			} else {
				line = append(line, ' ')
			}
			if c < r {
				line = append(line, ' ')
			}
		}
		out[r] = string(line)
	}
	return out, nil
}
```

- [ ] Run `go test ./internal/sierpinski/` — expect PASS.
- [ ] Add failing test `TestGenerate_InvalidSize`:

```go
func TestGenerate_InvalidSize(t *testing.T) {
	if _, err := Generate(0, 5, '*'); err == nil {
		t.Error("expected error for size 0, got nil")
	}
	if _, err := Generate(4, -1, '*'); err == nil {
		t.Error("expected error for depth -1, got nil")
	}
}
```

- [ ] Run `go test ./internal/sierpinski/` — expect PASS (error paths already implemented).
- [ ] Commit: `git add -A && git commit -m "Add Sierpinski algorithm package"`

---

### Task 2: Mandelbrot algorithm

Delivers the second algorithm package independently.

**Files:**
- `internal/mandelbrot/mandelbrot.go`
- `internal/mandelbrot/mandelbrot_test.go`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `const Gradient = " .:-=+*#%@"` (exported, 10 runes)
  - `func Render(width, height, iterations int, char rune) ([]string, error)` — when `char == 0` use the gradient; otherwise fill escaped/in-set cells with `char`.

Map pixel `(px, py)` to complex plane: real ∈ [-2.5, 1.0], imag ∈ [-1.25, 1.25]. Iterate `z = z² + c` until `|z| > 2` or max iterations. Points that never escape (in-set) get the last gradient char (`@`) or `char`; escaped points map iteration count to a gradient index.

- [ ] Write failing test `TestRender_Dimensions`:

```go
package mandelbrot

import (
	"strings"
	"testing"
)

func TestRender_Dimensions(t *testing.T) {
	rows, err := Render(20, 10, 50, 0)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 10 {
		t.Fatalf("expected 10 rows, got %d", len(rows))
	}
	for i, r := range rows {
		if len([]rune(r)) != 20 {
			t.Errorf("row %d: expected width 20, got %d", i, len([]rune(r)))
		}
	}
}

func TestRender_InSetCenter(t *testing.T) {
	// The origin (-0.5, 0) is inside the set; center cells should be the
	// in-set character (last gradient rune).
	rows, err := Render(80, 24, 100, 0)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	center := rows[12]
	if !strings.ContainsRune(center, '@') {
		t.Errorf("expected in-set char '@' in center row, got %q", center)
	}
}

func TestRender_Invalid(t *testing.T) {
	if _, err := Render(0, 10, 50, 0); err == nil {
		t.Error("expected error for width 0")
	}
	if _, err := Render(20, 0, 50, 0); err == nil {
		t.Error("expected error for height 0")
	}
	if _, err := Render(20, 10, 0, 0); err == nil {
		t.Error("expected error for iterations 0")
	}
}
```

- [ ] Run `go test ./internal/mandelbrot/` — expect compile failure.
- [ ] Implement `mandelbrot.go`:

```go
package mandelbrot

import "fmt"

const Gradient = " .:-=+*#%@"

// Render returns the Mandelbrot set as a slice of strings, one per row.
// If char == 0, the gradient maps iteration count to a character.
// Otherwise char fills every in-set point and escaped points are blank.
func Render(width, height, iterations int, char rune) ([]string, error) {
	if width < 1 {
		return nil, fmt.Errorf("width must be >= 1, got %d", width)
	}
	if height < 1 {
		return nil, fmt.Errorf("height must be >= 1, got %d", height)
	}
	if iterations < 1 {
		return nil, fmt.Errorf("iterations must be >= 1, got %d", iterations)
	}

	const (
		minReal, maxReal = -2.5, 1.0
		minImag, maxImag = -1.25, 1.25
	)
	grad := []rune(Gradient)

	out := make([]string, height)
	for py := 0; py < height; py++ {
		cy := minImag + (maxImag-minImag)*float64(py)/float64(height-1)
		if height == 1 {
			cy = (minImag + maxImag) / 2
		}
		line := make([]rune, width)
		for px := 0; px < width; px++ {
			cx := minReal + (maxReal-minReal)*float64(px)/float64(width-1)
			if width == 1 {
				cx = (minReal + maxReal) / 2
			}
			n := escapeCount(cx, cy, iterations)
			line[px] = pickChar(n, iterations, char, grad)
		}
		out[py] = string(line)
	}
	return out, nil
}

func escapeCount(cx, cy float64, maxIter int) int {
	var zx, zy float64
	for i := 0; i < maxIter; i++ {
		zx, zy = zx*zx-zy*zy+cx, 2*zx*zy+cy
		if zx*zx+zy*zy > 4 {
			return i
		}
	}
	return maxIter
}

func pickChar(n, maxIter int, char rune, grad []rune) rune {
	inSet := n >= maxIter
	if char != 0 {
		if inSet {
			return char
		}
		return ' '
	}
	if inSet {
		return grad[len(grad)-1]
	}
	idx := n * (len(grad) - 1) / maxIter
	if idx >= len(grad) {
		idx = len(grad) - 1
	}
	return grad[idx]
}
```

- [ ] Run `go test ./internal/mandelbrot/` — expect PASS.
- [ ] Commit: `git add -A && git commit -m "Add Mandelbrot algorithm package"`

---

### Task 3: CLI root command and entry point

Wires cobra and the binary entry point. Delivers a runnable `fractals --help`.

**Files:**
- `go.mod` (cobra dependency added)
- `internal/cli/root.go`
- `internal/cli/root_test.go`
- `cmd/fractals/main.go`

**Interfaces:**
- Consumes: nothing yet (subcommands added in Tasks 4–5).
- Produces:
  - `func NewRootCmd() *cobra.Command` — builds the root command; tests construct it to inspect/execute.
  - `func Execute() error` — runs the root command; called by `main`.

- [ ] Add cobra: `go get github.com/spf13/cobra@latest` then `go mod tidy`. Expect `go.mod` to list cobra.
- [ ] Write failing test `TestRootHelp` in `root_test.go`:

```go
package cli

import (
	"bytes"
	"strings"
	"testing"
)

func TestRootHelp(t *testing.T) {
	cmd := NewRootCmd()
	var buf bytes.Buffer
	cmd.SetOut(&buf)
	cmd.SetArgs([]string{"--help"})
	if err := cmd.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "fractals") {
		t.Errorf("help should mention 'fractals', got: %q", out)
	}
}
```

- [ ] Run `go test ./internal/cli/` — expect compile failure (no `NewRootCmd`).
- [ ] Implement `root.go`:

```go
package cli

import "github.com/spf13/cobra"

// NewRootCmd builds the top-level fractals command.
func NewRootCmd() *cobra.Command {
	root := &cobra.Command{
		Use:   "fractals",
		Short: "Generate ASCII art fractals",
		Long:  "fractals generates ASCII art fractals (Sierpinski triangle, Mandelbrot set).",
	}
	return root
}

// Execute runs the root command.
func Execute() error {
	return NewRootCmd().Execute()
}
```

- [ ] Run `go test ./internal/cli/` — expect PASS.
- [ ] Implement `cmd/fractals/main.go`:

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

- [ ] Run `go run ./cmd/fractals --help` — expect usage text mentioning `fractals`.
- [ ] Commit: `git add -A && git commit -m "Add CLI root command and entry point"`

---

### Task 4: Sierpinski subcommand

Wires flags to the Sierpinski algorithm and registers the subcommand.

**Files:**
- `internal/cli/sierpinski.go`
- `internal/cli/root.go` (register subcommand)
- `internal/cli/root_test.go` (add subcommand test)

**Interfaces:**
- Consumes: `sierpinski.Generate(size, depth int, char rune) ([]string, error)`.
- Produces: `func newSierpinskiCmd() *cobra.Command`; registered onto root via `AddCommand`.

The `--char` flag is a string; convert to `rune` by taking the first rune, erroring if empty or multi-rune.

- [ ] Write failing test `TestSierpinskiCommand` in `root_test.go`:

```go
func TestSierpinskiCommand(t *testing.T) {
	cmd := NewRootCmd()
	var buf bytes.Buffer
	cmd.SetOut(&buf)
	cmd.SetArgs([]string{"sierpinski", "--size", "4", "--depth", "5", "--char", "#"})
	if err := cmd.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "#") {
		t.Errorf("expected '#' in output, got %q", out)
	}
	if strings.Contains(out, "*") {
		t.Errorf("did not expect default '*' when --char #, got %q", out)
	}
}

func TestSierpinskiInvalidChar(t *testing.T) {
	cmd := NewRootCmd()
	cmd.SetArgs([]string{"sierpinski", "--char", "ab"})
	if err := cmd.Execute(); err == nil {
		t.Error("expected error for multi-rune --char")
	}
}
```

- [ ] Run `go test ./internal/cli/` — expect compile/run failure (no `sierpinski` command).
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
		size    int
		depth   int
		charStr string
	)
	cmd := &cobra.Command{
		Use:   "sierpinski",
		Short: "Generate a Sierpinski triangle",
		RunE: func(cmd *cobra.Command, args []string) error {
			char, err := singleRune(charStr)
			if err != nil {
				return err
			}
			rows, err := sierpinski.Generate(size, depth, char)
			if err != nil {
				return err
			}
			for _, r := range rows {
				fmt.Fprintln(cmd.OutOrStdout(), r)
			}
			return nil
		},
	}
	cmd.Flags().IntVar(&size, "size", 32, "Width of the triangle base in characters")
	cmd.Flags().IntVar(&depth, "depth", 5, "Recursion depth")
	cmd.Flags().StringVar(&charStr, "char", "*", "Character to use for filled points")
	return cmd
}

// singleRune validates that s is exactly one rune and returns it.
func singleRune(s string) (rune, error) {
	rs := []rune(s)
	if len(rs) != 1 {
		return 0, fmt.Errorf("char must be a single character, got %q", s)
	}
	return rs[0], nil
}
```

- [ ] Register in `root.go`: add `root.AddCommand(newSierpinskiCmd())` before `return root`.
- [ ] Run `go test ./internal/cli/` — expect PASS.
- [ ] Run `go run ./cmd/fractals sierpinski --size 16` — expect a centered triangle of `*`.
- [ ] Commit: `git add -A && git commit -m "Add sierpinski subcommand"`

---

### Task 5: Mandelbrot subcommand

Wires flags to the Mandelbrot algorithm, including gradient-vs-char handling, and registers the subcommand.

**Files:**
- `internal/cli/mandelbrot.go`
- `internal/cli/root.go` (register subcommand)
- `internal/cli/root_test.go` (add subcommand test)

**Interfaces:**
- Consumes: `mandelbrot.Render(width, height, iterations int, char rune) ([]string, error)`; `singleRune` from Task 4.
- Produces: `func newMandelbrotCmd() *cobra.Command`; registered onto root.

When `--char` is not set by the user, pass `rune(0)` to trigger gradient mode. Use `cmd.Flags().Changed("char")` to detect this.

- [ ] Write failing test `TestMandelbrotCommand` in `root_test.go`:

```go
func TestMandelbrotCommand(t *testing.T) {
	cmd := NewRootCmd()
	var buf bytes.Buffer
	cmd.SetOut(&buf)
	cmd.SetArgs([]string{"mandelbrot", "--width", "20", "--height", "10", "--iterations", "50"})
	if err := cmd.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(buf.String(), "\n"), "\n")
	if len(lines) != 10 {
		t.Fatalf("expected 10 lines, got %d", len(lines))
	}
	if !strings.ContainsAny(buf.String(), "@%#") {
		t.Errorf("expected gradient chars in output, got %q", buf.String())
	}
}

func TestMandelbrotCustomChar(t *testing.T) {
	cmd := NewRootCmd()
	var buf bytes.Buffer
	cmd.SetOut(&buf)
	cmd.SetArgs([]string{"mandelbrot", "--width", "20", "--height", "10", "--char", "X"})
	if err := cmd.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(buf.String(), "X") {
		t.Errorf("expected 'X' in output, got %q", buf.String())
	}
}
```

- [ ] Run `go test ./internal/cli/` — expect compile/run failure (no `mandelbrot` command).
- [ ] Implement `internal/cli/mandelbrot.go`:

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
		charStr    string
	)
	cmd := &cobra.Command{
		Use:   "mandelbrot",
		Short: "Render the Mandelbrot set",
		RunE: func(cmd *cobra.Command, args []string) error {
			var char rune // 0 => gradient mode
			if cmd.Flags().Changed("char") {
				r, err := singleRune(charStr)
				if err != nil {
					return err
				}
				char = r
			}
			rows, err := mandelbrot.Render(width, height, iterations, char)
			if err != nil {
				return err
			}
			for _, r := range rows {
				fmt.Fprintln(cmd.OutOrStdout(), r)
			}
			return nil
		},
	}
	cmd.Flags().IntVar(&width, "width", 80, "Output width in characters")
	cmd.Flags().IntVar(&height, "height", 24, "Output height in characters")
	cmd.Flags().IntVar(&iterations, "iterations", 100, "Maximum iterations for escape calculation")
	cmd.Flags().StringVar(&charStr, "char", "", "Single character, or omit for gradient")
	return cmd
}
```

- [ ] Register in `root.go`: add `root.AddCommand(newMandelbrotCmd())`.
- [ ] Run `go test ./internal/cli/` — expect PASS.
- [ ] Run `go run ./cmd/fractals mandelbrot --width 80 --height 24` — expect a recognizable Mandelbrot rendering with gradient.
- [ ] Commit: `git add -A && git commit -m "Add mandelbrot subcommand"`

---

### Task 6: Full acceptance verification

No new behavior; confirm all acceptance criteria and build cleanly. Fold the build check and final tidy here.

**Files:** none modified (verification only; fix inline if any check fails).

- [ ] Run `go build ./...` — expect no output (success).
- [ ] Run `go vet ./...` — expect no output.
- [ ] Run `go test ./...` — expect all packages PASS.
- [ ] Run `go run ./cmd/fractals --help` — confirm criterion 1 (usage shown, lists `sierpinski` and `mandelbrot`).
- [ ] Run `go run ./cmd/fractals sierpinski` — confirm criterion 2 (recognizable triangle).
- [ ] Run `go run ./cmd/fractals mandelbrot` — confirm criterion 3 (recognizable set).
- [ ] Run `go run ./cmd/fractals sierpinski --size 0` — confirm criterion 6 (clear error, exit 1).
- [ ] Run `go run ./cmd/fractals mandelbrot --char xy` — confirm criterion 6 (clear error for multi-rune char).
- [ ] Commit (if any fixes applied): `git add -A && git commit -m "Acceptance fixes"`

---

## Self-Review

- **Spec coverage:** Two fractal types ✓ (Tasks 1–2, 4–5); all flags `--size/--depth/--char` (Task 4), `--width/--height/--iterations/--char` (Task 5) ✓; gradient default `" .:-=+*#%@"` ✓ (Task 2); help ✓ (Task 3); invalid-input errors ✓ (Tasks 1, 2, 4, 5); architecture file layout matches spec exactly ✓; Go 1.21+ and cobra ✓ (Global Constraints, Tasks 1, 3); all acceptance criteria mapped in Task 6 ✓.
- **Placeholder scan:** No TODOs or stubs; every function body is complete.
- **Type consistency:** `Generate(int, int, rune) ([]string, error)` and `Render(int, int, int, rune) ([]string, error)` match their consumer call sites in `sierpinski.go`/`mandelbrot.go` CLI files. `singleRune(string) (rune, error)` is defined once in Task 4 and reused in Task 5 (no duplication — DRY). `rune(0)` sentinel for gradient mode is consistent between `Render`'s `char == 0` check and the CLI's `Changed("char")` gate.
- **Module path:** `github.com/example/fractals` used consistently in `go.mod`, `main.go` import, and CLI imports.