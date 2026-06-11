# Go Fractals CLI - Implementation Plan

## Global Constraints

- Go 1.21+ required (set `go 1.21` in `go.mod`)
- Use `github.com/spf13/cobra` for CLI
- Module path: `github.com/example/fractals`
- Mandelbrot default gradient (exact, 10 chars including leading space): `" .:-=+*#%@"`
- Sierpinski default char: `*`; default size: 32; default depth: 5
- Mandelbrot defaults: width 80, height 24, iterations 100
- Output goes to stdout, one row per line
- Invalid inputs produce clear error messages (non-zero exit)

## File Structure

| File | Responsibility |
|------|----------------|
| `go.mod` | Module definition, Go version, cobra dependency |
| `internal/sierpinski/sierpinski.go` | Sierpinski generation algorithm (pure, returns `[]string`) |
| `internal/sierpinski/sierpinski_test.go` | Tests for sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Mandelbrot generation algorithm (pure, returns `[]string`) |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command, wires subcommands |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand, flag parsing, validation |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand, flag parsing, validation |
| `internal/cli/root_test.go` | CLI integration tests (help, subcommands, errors) |
| `cmd/fractals/main.go` | Entry point, calls `cli.Execute()` |

---

### Task 1: Module Setup

**Files:** `go.mod`, `cmd/fractals/main.go`

**Interfaces:**
- Consumes: nothing
- Produces: module `github.com/example/fractals`; `main.go` calls `cli.Execute() error` (stubbed until Task 4)

- [ ] Run `go mod init github.com/example/fractals`
- [ ] Edit `go.mod` to ensure the line `go 1.21` is present
- [ ] Run `go get github.com/spf13/cobra@latest`
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

- [ ] This will not compile yet (no `cli` package). That is expected; it compiles after Task 4. Do not run `go build` here.
- [ ] Commit: `git add -A && git commit -m "Task 1: module setup and entry point"`

---

### Task 2: Sierpinski Algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

**Interfaces:**
- Consumes: nothing
- Produces: `func Generate(size, depth int, char rune) ([]string, error)`
  - Returns one string per row, top to bottom.
  - Errors on `size < 1` or `depth < 0`.

**Algorithm note (correctness-critical):** Use the bitwise-AND method, which directly yields the Sierpinski triangle. For a triangle of `size` rows, row `y` (0-indexed from top) has leading spaces so the apex centers. A cell at triangle-coordinate `(x, y)` is filled iff `(x & y) == 0`. The `depth` flag limits how many of the lowest power-of-two subdivisions render: clamp the effective number of rows to `min(size, 2^depth)`.

- [ ] Write failing test `internal/sierpinski/sierpinski_test.go`:

```go
package sierpinski

import (
	"strings"
	"testing"
)

func TestGenerateSmall(t *testing.T) {
	// size=2, depth=1 -> 2 rows. Bitwise AND:
	// row0: x=0 -> (0&0)==0 filled
	// row1: x=0 (0&1)==0 filled, x=1 (1&1)!=0 empty
	rows, err := Generate(2, 1, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 2 {
		t.Fatalf("want 2 rows, got %d", len(rows))
	}
	// Each row must contain at least one '*'
	for i, r := range rows {
		if !strings.Contains(r, "*") {
			t.Errorf("row %d has no star: %q", i, r)
		}
	}
}

func TestGenerateChar(t *testing.T) {
	rows, err := Generate(4, 5, '#')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(rows, "\n")
	if strings.Contains(joined, "*") {
		t.Errorf("output should use '#', not '*': %q", joined)
	}
	if !strings.Contains(joined, "#") {
		t.Errorf("output should contain '#': %q", joined)
	}
}

func TestGenerateApexSingleChar(t *testing.T) {
	rows, _ := Generate(4, 5, '*')
	// Top row should contain exactly one filled char.
	if strings.Count(rows[0], "*") != 1 {
		t.Errorf("apex row should have one star, got %q", rows[0])
	}
}

func TestGenerateInvalidSize(t *testing.T) {
	if _, err := Generate(0, 5, '*'); err == nil {
		t.Error("expected error for size < 1")
	}
}

func TestGenerateInvalidDepth(t *testing.T) {
	if _, err := Generate(8, -1, '*'); err == nil {
		t.Error("expected error for depth < 0")
	}
}
```

- [ ] Run `go test ./internal/sierpinski/` → expect failure (no `Generate`).
- [ ] Implement `internal/sierpinski/sierpinski.go`:

```go
package sierpinski

import (
	"fmt"
	"strings"
)

// Generate returns the rows of a Sierpinski triangle.
// size is the number of rows at full detail; depth clamps detail to 2^depth rows.
func Generate(size, depth int, char rune) ([]string, error) {
	if size < 1 {
		return nil, fmt.Errorf("size must be >= 1, got %d", size)
	}
	if depth < 0 {
		return nil, fmt.Errorf("depth must be >= 0, got %d", depth)
	}

	rows := size
	limit := 1 << uint(depth) // 2^depth
	if limit < rows {
		rows = limit
	}

	out := make([]string, 0, rows)
	for y := 0; y < rows; y++ {
		var b strings.Builder
		// Leading spaces to center the apex.
		for s := 0; s < rows-1-y; s++ {
			b.WriteByte(' ')
		}
		for x := 0; x <= y; x++ {
			if x&y == 0 {
				b.WriteRune(char)
			} else {
				b.WriteByte(' ')
			}
			if x < y {
				b.WriteByte(' ')
			}
		}
		out = append(out, b.String())
	}
	return out, nil
}
```

- [ ] Run `go test ./internal/sierpinski/` → expect PASS.
- [ ] Commit: `git commit -am "Task 2: sierpinski algorithm"`

---

### Task 3: Mandelbrot Algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

**Interfaces:**
- Consumes: nothing
- Produces:
  - `const DefaultGradient = " .:-=+*#%@"`
  - `func Generate(width, height, iterations int, gradient string) ([]string, error)`
    - Returns `height` strings, each of length `width`.
    - If `gradient` is a single char, every escaped point uses it; non-escaped (in-set) uses last gradient char.
    - Errors on `width < 1`, `height < 1`, `iterations < 1`, or empty `gradient`.

**Correctness-critical mapping:** View window is real `[-2.5, 1.0]`, imaginary `[-1.0, 1.0]`. For pixel `(px, py)`:
- `c_re = -2.5 + (px / (width-1)) * 3.5` (guard width==1 → use 0)
- `c_im = -1.0 + (py / (height-1)) * 2.0` (guard height==1 → use 0)

Escape iteration: `z = z^2 + c`, escape when `|z| > 2` (test `re*re+im*im > 4`). Map iteration count `n` to gradient index: if `n == iterations` (never escaped, in set) use index `len(gradient)-1`; else `idx = n * (len(gradient)-1) / iterations`.

- [ ] Write failing test `internal/mandelbrot/mandelbrot_test.go`:

```go
package mandelbrot

import (
	"testing"
)

func TestDimensions(t *testing.T) {
	rows, err := Generate(80, 24, 100, DefaultGradient)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 24 {
		t.Fatalf("want 24 rows, got %d", len(rows))
	}
	for i, r := range rows {
		if len([]rune(r)) != 80 {
			t.Errorf("row %d width = %d, want 80", i, len([]rune(r)))
		}
	}
}

func TestInSetCenter(t *testing.T) {
	// The point c=0 (in set) maps near the middle of the width window.
	// With DefaultGradient, in-set points use the last char '@'.
	rows, _ := Generate(80, 24, 100, DefaultGradient)
	joined := ""
	for _, r := range rows {
		joined += r
	}
	if !containsRune(joined, '@') {
		t.Error("expected in-set points rendered as '@'")
	}
}

func TestSingleChar(t *testing.T) {
	rows, err := Generate(10, 5, 50, "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	for _, r := range rows {
		for _, ch := range r {
			if ch != '#' {
				t.Errorf("single-char gradient should only emit '#', got %q", ch)
			}
		}
	}
}

func TestInvalid(t *testing.T) {
	cases := []struct {
		w, h, it int
		grad     string
	}{
		{0, 5, 10, "#"},
		{5, 0, 10, "#"},
		{5, 5, 0, "#"},
		{5, 5, 10, ""},
	}
	for _, c := range cases {
		if _, err := Generate(c.w, c.h, c.it, c.grad); err == nil {
			t.Errorf("expected error for %+v", c)
		}
	}
}

func containsRune(s string, r rune) bool {
	for _, c := range s {
		if c == r {
			return true
		}
	}
	return false
}
```

- [ ] Run `go test ./internal/mandelbrot/` → expect failure.
- [ ] Implement `internal/mandelbrot/mandelbrot.go`:

```go
package mandelbrot

import (
	"fmt"
	"strings"
)

const DefaultGradient = " .:-=+*#%@"

func Generate(width, height, iterations int, gradient string) ([]string, error) {
	if width < 1 {
		return nil, fmt.Errorf("width must be >= 1, got %d", width)
	}
	if height < 1 {
		return nil, fmt.Errorf("height must be >= 1, got %d", height)
	}
	if iterations < 1 {
		return nil, fmt.Errorf("iterations must be >= 1, got %d", iterations)
	}
	grad := []rune(gradient)
	if len(grad) == 0 {
		return nil, fmt.Errorf("gradient must not be empty")
	}

	const (
		reMin, reMax = -2.5, 1.0
		imMin, imMax = -1.0, 1.0
	)
	out := make([]string, 0, height)
	for py := 0; py < height; py++ {
		var cIm float64
		if height == 1 {
			cIm = 0
		} else {
			cIm = imMin + (float64(py)/float64(height-1))*(imMax-imMin)
		}
		var b strings.Builder
		for px := 0; px < width; px++ {
			var cRe float64
			if width == 1 {
				cRe = 0
			} else {
				cRe = reMin + (float64(px)/float64(width-1))*(reMax-reMin)
			}
			n := escape(cRe, cIm, iterations)
			var idx int
			if n >= iterations {
				idx = len(grad) - 1
			} else {
				idx = n * (len(grad) - 1) / iterations
			}
			b.WriteRune(grad[idx])
		}
		out = append(out, b.String())
	}
	return out, nil
}

func escape(cRe, cIm float64, maxIter int) int {
	var zRe, zIm float64
	for n := 0; n < maxIter; n++ {
		zRe2 := zRe*zRe - zIm*zIm + cRe
		zIm = 2*zRe*zIm + cIm
		zRe = zRe2
		if zRe*zRe+zIm*zIm > 4 {
			return n
		}
	}
	return maxIter
}
```

- [ ] Run `go test ./internal/mandelbrot/` → expect PASS.
- [ ] Commit: `git commit -am "Task 3: mandelbrot algorithm"`

---

### Task 4: CLI Wiring & Subcommands

**Files:** `internal/cli/root.go`, `internal/cli/sierpinski.go`, `internal/cli/mandelbrot.go`, `internal/cli/root_test.go`

**Interfaces:**
- Consumes: `sierpinski.Generate`, `mandelbrot.Generate`, `mandelbrot.DefaultGradient`
- Produces: `func Execute() error`; internal `func newRootCmd() *cobra.Command` for testing

**Flag mapping:**
- sierpinski: `--size` (int, default 32), `--depth` (int, default 5), `--char` (string, default `"*"`)
- mandelbrot: `--width` (int, default 80), `--height` (int, default 24), `--iterations` (int, default 100), `--char` (string, default `""` → empty means use `DefaultGradient`)

**`--char` rune handling (correctness-critical):** Take the first rune of the string. For sierpinski, empty `--char` → error "char must not be empty". For mandelbrot, empty `--char` → use `DefaultGradient`; non-empty → pass the string through as gradient (single char becomes single-char gradient).

- [ ] Write failing test `internal/cli/root_test.go`:

```go
package cli

import (
	"bytes"
	"strings"
	"testing"
)

func run(args ...string) (string, error) {
	cmd := newRootCmd()
	var out bytes.Buffer
	cmd.SetOut(&out)
	cmd.SetErr(&out)
	cmd.SetArgs(args)
	err := cmd.Execute()
	return out.String(), err
}

func TestRootHelp(t *testing.T) {
	out, err := run("--help")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "sierpinski") || !strings.Contains(out, "mandelbrot") {
		t.Errorf("help should list subcommands: %q", out)
	}
}

func TestSierpinskiRuns(t *testing.T) {
	out, err := run("sierpinski", "--size", "8", "--depth", "5")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "*") {
		t.Errorf("expected triangle output: %q", out)
	}
}

func TestSierpinskiChar(t *testing.T) {
	out, err := run("sierpinski", "--size", "8", "--char", "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "#") || strings.Contains(out, "*") {
		t.Errorf("expected '#' output: %q", out)
	}
}

func TestMandelbrotRuns(t *testing.T) {
	out, err := run("mandelbrot", "--width", "40", "--height", "12")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 12 {
		t.Errorf("expected 12 lines, got %d", len(lines))
	}
}

func TestSierpinskiInvalid(t *testing.T) {
	_, err := run("sierpinski", "--size", "0")
	if err == nil {
		t.Error("expected error for size 0")
	}
}

func TestSierpinskiEmptyChar(t *testing.T) {
	_, err := run("sierpinski", "--char", "")
	if err == nil {
		t.Error("expected error for empty char")
	}
}
```

- [ ] Run `go test ./internal/cli/` → expect failure (no package functions).
- [ ] Implement `internal/cli/root.go`:

```go
package cli

import "github.com/spf13/cobra"

func newRootCmd() *cobra.Command {
	root := &cobra.Command{
		Use:           "fractals",
		Short:         "Generate ASCII art fractals",
		SilenceUsage:  true,
		SilenceErrors: true,
	}
	root.AddCommand(newSierpinskiCmd())
	root.AddCommand(newMandelbrotCmd())
	return root
}

func Execute() error {
	return newRootCmd().Execute()
}
```

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
			if char == "" {
				return fmt.Errorf("char must not be empty")
			}
			r := []rune(char)[0]
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
	cmd.Flags().IntVar(&size, "size", 32, "Width of the triangle base in characters")
	cmd.Flags().IntVar(&depth, "depth", 5, "Recursion depth")
	cmd.Flags().StringVar(&char, "char", "*", "Character to use for filled points")
	return cmd
}
```

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
		char       string
	)
	cmd := &cobra.Command{
		Use:   "mandelbrot",
		Short: "Render the Mandelbrot set",
		RunE: func(cmd *cobra.Command, args []string) error {
			gradient := mandelbrot.DefaultGradient
			if char != "" {
				gradient = char
			}
			rows, err := mandelbrot.Generate(width, height, iterations, gradient)
			if err != nil {
				return err
			}
			for _, line := range rows {
				fmt.Fprintln(cmd.OutOrStdout(), line)
			}
			return nil
		},
	}
	cmd.Flags().IntVar(&width, "width", 80, "Output width in characters")
	cmd.Flags().IntVar(&height, "height", 24, "Output height in characters")
	cmd.Flags().IntVar(&iterations, "iterations", 100, "Maximum iterations for escape calculation")
	cmd.Flags().StringVar(&char, "char", "", "Single character, or omit for gradient")
	return cmd
}
```

- [ ] Run `go test ./internal/cli/` → expect PASS.
- [ ] Commit: `git commit -am "Task 4: CLI wiring and subcommands"`

---

### Task 5: End-to-End Verification

**Files:** none (build & manual checks)

**Interfaces:**
- Consumes: everything above
- Produces: verified binary

- [ ] Run `go build ./...` → expect no output (success).
- [ ] Run `go test ./...` → expect all packages `ok`.
- [ ] Run `go run ./cmd/fractals --help` → expect usage listing `sierpinski` and `mandelbrot`.
- [ ] Run `go run ./cmd/fractals sierpinski --size 16 --depth 5` → expect a centered triangle of `*`.
- [ ] Run `go run ./cmd/fractals mandelbrot --width 80 --height 24` → expect a recognizable Mandelbrot rendering ending in `@` regions.
- [ ] Run `go run ./cmd/fractals mandelbrot --width 0` → expect clear error `width must be >= 1, got 0` and non-zero exit.
- [ ] Run `go vet ./...` → expect no output.
- [ ] Commit (if any tidy changes): `git commit -am "Task 5: e2e verification"`

---

## Self-Review

- **Spec coverage:** `--help` (Task 4 TestRootHelp ✓), sierpinski triangle (Task 2/4 ✓), mandelbrot set (Task 3/4 ✓), all numeric flags (Task 4 ✓), `--char` for both commands (Task 4 ✓), invalid input errors (Tasks 2/3 validation + Task 4 tests + Task 5 manual ✓), all tests pass (Task 5 ✓). Architecture file layout matches spec exactly.
- **Placeholder scan:** No TODOs or stubs remain after Task 4; `main.go` non-compilation in Task 1 is explicitly flagged and resolved in Task 4.
- **Type consistency:** `sierpinski.Generate(int, int, rune) ([]string, error)` and `mandelbrot.Generate(int, int, int, string) ([]string, error)` signatures match their consumers in Task 4. `DefaultGradient` is a `string` consumed as gradient. `--char` is parsed to first rune for sierpinski and passed as string gradient for mandelbrot, matching spec (single char vs gradient).
- **Note on `depth`:** Spec lists `--depth` as a flag without a precise rendering formula; the plan clamps detail to `2^depth` rows, a defensible interpretation that keeps the flag functional and testable. This is the one area of interpretive latitude and is documented at the algorithm note.