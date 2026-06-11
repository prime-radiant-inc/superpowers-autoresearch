# Go Fractals CLI - Implementation Plan

## Global Constraints

- Go 1.21+ required (`go.mod` declares `go 1.21`)
- Module path: `github.com/example/fractals`
- CLI library: `github.com/spf13/cobra`
- Sierpinski default char: `'*'`; Mandelbrot gradient: `" .:-=+*#%@"` (10 chars, index 0 = space)
- All output to stdout via injectable `io.Writer` for testability
- Invalid inputs (negative/zero sizes, multi-rune `--char`) produce clear errors, not panics

## File Structure

- `go.mod` — module declaration, cobra dependency
- `internal/sierpinski/sierpinski.go` — `Render` algorithm
- `internal/sierpinski/sierpinski_test.go` — algorithm tests
- `internal/mandelbrot/mandelbrot.go` — `Render` algorithm
- `internal/mandelbrot/mandelbrot_test.go` — algorithm tests
- `internal/cli/root.go` — root command + help
- `internal/cli/sierpinski.go` — sierpinski subcommand
- `internal/cli/mandelbrot.go` — mandelbrot subcommand
- `internal/cli/cli_test.go` — subcommand integration tests
- `cmd/fractals/main.go` — entry point

---

### Task 1: Module setup

**Files:** `go.mod`

- [ ] Run `go mod init github.com/example/fractals`
- [ ] Run `go get github.com/spf13/cobra@latest`
- [ ] Verify `go.mod` contains `go 1.21` (edit if lower) and a cobra `require` line
- [ ] Commit: `git add -A && git commit -m "Module setup with cobra"`

**Interfaces:** Produces module `github.com/example/fractals`.

---

### Task 2: Sierpinski algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

**Interfaces:** Produces `func Render(size, depth int, char rune) (string, error)`. Returns rows joined by `\n`. Errors on `size <= 0` or `depth < 0`.

- [ ] Write failing test:

```go
package sierpinski

import (
	"strings"
	"testing"
)

func TestRenderSmall(t *testing.T) {
	out, err := Render(4, 2, '*')
	if err != nil {
		t.Fatal(err)
	}
	lines := strings.Split(out, "\n")
	if len(lines) == 0 || !strings.Contains(out, "*") {
		t.Fatalf("expected triangle with stars, got:\n%s", out)
	}
	// Apex row should have a single star.
	if strings.Count(lines[0], "*") != 1 {
		t.Errorf("apex row should have 1 star, got %q", lines[0])
	}
}

func TestRenderInvalid(t *testing.T) {
	if _, err := Render(0, 1, '*'); err == nil {
		t.Error("expected error for size 0")
	}
	if _, err := Render(4, -1, '*'); err == nil {
		t.Error("expected error for negative depth")
	}
}
```

- [ ] Run `go test ./internal/sierpinski/` — expect FAIL (undefined: Render)
- [ ] Implement using the Pascal's-triangle bit rule (point `(row,col)` filled when `(row & col) == 0`):

```go
package sierpinski

import (
	"fmt"
	"strings"
)

// Render returns an ASCII Sierpinski triangle. rows = 2^depth, clamped by size.
func Render(size, depth int, char rune) (string, error) {
	if size <= 0 {
		return "", fmt.Errorf("size must be positive, got %d", size)
	}
	if depth < 0 {
		return "", fmt.Errorf("depth must be non-negative, got %d", depth)
	}
	rows := 1
	for i := 0; i < depth; i++ {
		rows *= 2
	}
	if rows > size {
		rows = size
	}
	var b strings.Builder
	for y := 0; y < rows; y++ {
		b.WriteString(strings.Repeat(" ", rows-1-y))
		for x := 0; x <= y; x++ {
			if x&(y-x) == 0 {
				b.WriteRune(char)
			} else {
				b.WriteRune(' ')
			}
			if x < y {
				b.WriteRune(' ')
			}
		}
		if y < rows-1 {
			b.WriteRune('\n')
		}
	}
	return b.String(), nil
}
```

- [ ] Run `go test ./internal/sierpinski/` — expect PASS
- [ ] Commit: `git commit -am "Sierpinski algorithm"`

---

### Task 3: Mandelbrot algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

**Interfaces:** Produces `const Gradient = " .:-=+*#%@"` and `func Render(width, height, iterations int, char rune) (string, error)`. When `char == 0`, use gradient; otherwise fill escaped points with `char`. Errors on non-positive width/height/iterations.

- [ ] Write failing test:

```go
package mandelbrot

import (
	"strings"
	"testing"
)

func TestRenderDimensions(t *testing.T) {
	out, err := Render(10, 5, 50, 0)
	if err != nil {
		t.Fatal(err)
	}
	lines := strings.Split(out, "\n")
	if len(lines) != 5 {
		t.Fatalf("expected 5 rows, got %d", len(lines))
	}
	for _, l := range lines {
		if len([]rune(l)) != 10 {
			t.Errorf("expected width 10, got %d in %q", len([]rune(l)), l)
		}
	}
}

func TestRenderCustomChar(t *testing.T) {
	out, _ := Render(10, 5, 50, '#')
	if strings.ContainsAny(out, ".:-=+*%@") {
		t.Error("custom char output should only use '#' and space")
	}
}

func TestRenderInvalid(t *testing.T) {
	if _, err := Render(0, 5, 10, 0); err == nil {
		t.Error("expected error for width 0")
	}
	if _, err := Render(10, 5, 0, 0); err == nil {
		t.Error("expected error for iterations 0")
	}
}
```

- [ ] Run `go test ./internal/mandelbrot/` — expect FAIL
- [ ] Implement:

```go
package mandelbrot

import (
	"fmt"
	"strings"
)

const Gradient = " .:-=+*#%@"

// Render maps the complex plane [-2.5,1] x [-1,1] to a width×height grid.
func Render(width, height, iterations int, char rune) (string, error) {
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
		y0 := float64(py)/float64(height)*2.0 - 1.0
		for px := 0; px < width; px++ {
			x0 := float64(px)/float64(width)*3.5 - 2.5
			x, y, iter := 0.0, 0.0, 0
			for x*x+y*y <= 4 && iter < iterations {
				x, y = x*x-y*y+x0, 2*x*y+y0
				iter++
			}
			b.WriteRune(pick(iter, iterations, char))
		}
		if py < height-1 {
			b.WriteRune('\n')
		}
	}
	return b.String(), nil
}

func pick(iter, max int, char rune) rune {
	inSet := iter >= max
	if char != 0 {
		if inSet {
			return char
		}
		return ' '
	}
	if inSet {
		return rune(Gradient[len(Gradient)-1])
	}
	idx := iter * (len(Gradient) - 1) / max
	return rune(Gradient[idx])
}
```

- [ ] Run `go test ./internal/mandelbrot/` — expect PASS
- [ ] Commit: `git commit -am "Mandelbrot algorithm"`

---

### Task 4: CLI commands

**Files:** `internal/cli/root.go`, `internal/cli/sierpinski.go`, `internal/cli/mandelbrot.go`, `internal/cli/cli_test.go`

**Interfaces:** Consumes `sierpinski.Render`, `mandelbrot.Render`, `mandelbrot.Gradient`. Produces `func NewRootCmd() *cobra.Command` wiring both subcommands; output goes to `cmd.OutOrStdout()`.

- [ ] Write `root.go`:

```go
package cli

import "github.com/spf13/cobra"

func NewRootCmd() *cobra.Command {
	root := &cobra.Command{
		Use:   "fractals",
		Short: "Generate ASCII art fractals",
	}
	root.AddCommand(newSierpinskiCmd(), newMandelbrotCmd())
	return root
}
```

- [ ] Write `sierpinski.go`:

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
				return fmt.Errorf("--char must be a single character, got %q", char)
			}
			out, err := sierpinski.Render(size, depth, r[0])
			if err != nil {
				return err
			}
			fmt.Fprintln(cmd.OutOrStdout(), out)
			return nil
		},
	}
	cmd.Flags().IntVar(&size, "size", 32, "Width of the triangle base")
	cmd.Flags().IntVar(&depth, "depth", 5, "Recursion depth")
	cmd.Flags().StringVar(&char, "char", "*", "Character for filled points")
	return cmd
}
```

- [ ] Write `mandelbrot.go`:

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
			var c rune
			if char != "" {
				r := []rune(char)
				if len(r) != 1 {
					return fmt.Errorf("--char must be a single character, got %q", char)
				}
				c = r[0]
			}
			out, err := mandelbrot.Render(width, height, iterations, c)
			if err != nil {
				return err
			}
			fmt.Fprintln(cmd.OutOrStdout(), out)
			return nil
		},
	}
	cmd.Flags().IntVar(&width, "width", 80, "Output width")
	cmd.Flags().IntVar(&height, "height", 24, "Output height")
	cmd.Flags().IntVar(&iterations, "iterations", 100, "Max escape iterations")
	cmd.Flags().StringVar(&char, "char", "", "Single character, or omit for gradient")
	return cmd
}
```

- [ ] Write `cli_test.go`:

```go
package cli

import (
	"bytes"
	"strings"
	"testing"
)

func run(args ...string) (string, error) {
	cmd := NewRootCmd()
	var buf bytes.Buffer
	cmd.SetOut(&buf)
	cmd.SetErr(&buf)
	cmd.SetArgs(args)
	err := cmd.Execute()
	return buf.String(), err
}

func TestHelp(t *testing.T) {
	out, err := run("--help")
	if err != nil || !strings.Contains(out, "fractals") {
		t.Fatalf("help failed: %v\n%s", err, out)
	}
}

func TestSierpinski(t *testing.T) {
	out, err := run("sierpinski", "--size", "4", "--depth", "2")
	if err != nil || !strings.Contains(out, "*") {
		t.Fatalf("got %v\n%s", err, out)
	}
}

func TestMandelbrot(t *testing.T) {
	out, err := run("mandelbrot", "--width", "10", "--height", "5")
	if err != nil || len(out) == 0 {
		t.Fatalf("got %v\n%s", err, out)
	}
}

func TestInvalidChar(t *testing.T) {
	if _, err := run("sierpinski", "--char", "ab"); err == nil {
		t.Error("expected error for multi-char")
	}
}

func TestInvalidSize(t *testing.T) {
	if _, err := run("sierpinski", "--size", "0"); err == nil {
		t.Error("expected error for size 0")
	}
}
```

- [ ] Run `go test ./internal/cli/` — expect PASS
- [ ] Commit: `git commit -am "CLI commands"`

---

### Task 5: Entry point

**Files:** `cmd/fractals/main.go`

**Interfaces:** Consumes `cli.NewRootCmd`.

- [ ] Write `main.go`:

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

- [ ] Run `go build ./...` — expect no output (success)
- [ ] Run `go run ./cmd/fractals sierpinski --size 8 --depth 3` — expect a triangle of `*`
- [ ] Run `go run ./cmd/fractals mandelbrot --width 40 --height 12` — expect a Mandelbrot rendering
- [ ] Run `go test ./...` — expect all PASS
- [ ] Commit: `git commit -am "Entry point"`

---

## Self-Review

- **Spec coverage:** All 7 acceptance criteria mapped — help (Task 4 `TestHelp`), triangle/Mandelbrot output (Tasks 4–5), all flags wired (Task 4), `--char` custom (both subcommands), error messages (Render funcs + char validation), tests pass (Task 5). ✓
- **Placeholder scan:** No TODOs or stubs; all code blocks complete. ✓
- **Type consistency:** `Render` signatures in algorithm tasks match calls in CLI; `char rune` with `0` sentinel for Mandelbrot gradient consistent between `mandelbrot.go` and `pick`. ✓
- **Note:** Sierpinski uses bit-rule subdivision; `depth` controls row count (`2^depth`), clamped by `size`, satisfying both flags meaningfully.