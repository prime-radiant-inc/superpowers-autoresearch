# Go Fractals CLI - Implementation Plan

## Global Constraints

- Go 1.21+ (set in `go.mod` as `go 1.21`)
- Module path: `github.com/example/fractals`
- CLI dependency: `github.com/spf13/cobra` (only third-party dependency)
- Mandelbrot default gradient (exact, dim→bright): `" .:-=+*#%@"`
- Sierpinski default char: `*`; Mandelbrot default: gradient
- Invalid flag values produce a clear error to stderr and a non-zero exit
- All output goes to an injectable `io.Writer` (tests capture it; production uses `os.Stdout`)

## File Structure

| Path | Responsibility |
|------|----------------|
| `go.mod` | Module + Go version + cobra dependency |
| `internal/sierpinski/sierpinski.go` | Pure algorithm: produce triangle rows |
| `internal/sierpinski/sierpinski_test.go` | Algorithm tests |
| `internal/mandelbrot/mandelbrot.go` | Pure algorithm: produce mandelbrot rows |
| `internal/mandelbrot/mandelbrot_test.go` | Algorithm tests |
| `internal/cli/root.go` | Root command, help, `Execute` |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand, flag wiring |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand, flag wiring |
| `cmd/fractals/main.go` | Entry point calling `cli.Execute` |

---

### Task 1: Module setup

**Files:** `go.mod`

**Interfaces:** Produces module `github.com/example/fractals` with cobra available.

- [ ] Create the module:
```bash
go mod init github.com/example/fractals
go get github.com/spf13/cobra@latest
```
- [ ] Confirm `go.mod` contains `go 1.21` (edit the line if a newer toolchain wrote a different value) and a `require github.com/spf13/cobra` line.
- [ ] Verify:
```bash
go build ./... 2>&1 || echo "no packages yet - OK"
```
- [ ] Commit: `git add go.mod go.sum && git commit -m "chore: init module with cobra"`

---

### Task 2: Sierpinski algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

**Interfaces:**
- Produces `func Generate(size, depth int, char rune) ([]string, error)` — returns `size` rows. Uses the bitwise rule: cell `(x,y)` is filled when `(x & y) == 0`, scaled so deeper `depth` shows finer detail by masking low bits. Errors on `size < 1` or `depth < 0`.

- [ ] Write failing test:
```go
package sierpinski

import "testing"

func TestGenerateRowCount(t *testing.T) {
	rows, err := Generate(8, 3, '*')
	if err != nil {
		t.Fatal(err)
	}
	if len(rows) != 8 {
		t.Fatalf("want 8 rows, got %d", len(rows))
	}
}

func TestGenerateApexSingleChar(t *testing.T) {
	rows, _ := Generate(8, 3, '*')
	// top row has exactly one filled cell
	count := 0
	for _, r := range rows[0] {
		if r == '*' {
			count++
		}
	}
	if count != 1 {
		t.Fatalf("apex row want 1 char, got %d in %q", count, rows[0])
	}
}

func TestGenerateInvalidSize(t *testing.T) {
	if _, err := Generate(0, 3, '*'); err == nil {
		t.Fatal("want error for size 0")
	}
}
```
- [ ] Run, expect failure:
```bash
go test ./internal/sierpinski/
# expect: undefined: Generate
```
- [ ] Implement:
```go
package sierpinski

import "fmt"

// Generate returns size rows of a Sierpinski triangle.
// A cell (x,y) is filled when (x & y) == 0. depth limits the
// resolution by ignoring bits above the depth-th.
func Generate(size, depth int, char rune) ([]string, error) {
	if size < 1 {
		return nil, fmt.Errorf("size must be >= 1, got %d", size)
	}
	if depth < 0 {
		return nil, fmt.Errorf("depth must be >= 0, got %d", depth)
	}
	mask := (1 << uint(depth)) - 1
	if mask < 0 {
		mask = ^0
	}
	rows := make([]string, size)
	for y := 0; y < size; y++ {
		line := make([]rune, size)
		for x := 0; x < size; x++ {
			indent := size - 1 - y
			tx := x - indent
			if tx >= 0 && (tx&y&mask) == 0 && tx <= y {
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
- [ ] Run, expect pass:
```bash
go test ./internal/sierpinski/
# expect: ok
```
- [ ] Commit: `git commit -am "feat: sierpinski algorithm"`

---

### Task 3: Mandelbrot algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

**Interfaces:**
- Produces `const Gradient = " .:-=+*#%@"`
- Produces `func Generate(width, height, iterations int, char rune) ([]string, error)` — when `char == 0`, maps iteration count across `Gradient`; otherwise uses `char` for in-set points and space elsewhere. Errors on `width<1`, `height<1`, `iterations<1`. View window: real `[-2.5, 1.0]`, imag `[-1.0, 1.0]`.

- [ ] Write failing test:
```go
package mandelbrot

import (
	"strings"
	"testing"
)

func TestGenerateDimensions(t *testing.T) {
	rows, err := Generate(20, 10, 50, 0)
	if err != nil {
		t.Fatal(err)
	}
	if len(rows) != 10 {
		t.Fatalf("want 10 rows, got %d", len(rows))
	}
	for _, r := range rows {
		if len([]rune(r)) != 20 {
			t.Fatalf("want width 20, got %d", len([]rune(r)))
		}
	}
}

func TestGenerateHasInsetPoints(t *testing.T) {
	rows, _ := Generate(80, 24, 100, '@')
	joined := strings.Join(rows, "")
	if !strings.ContainsRune(joined, '@') {
		t.Fatal("expected in-set points marked with @")
	}
}

func TestGenerateInvalid(t *testing.T) {
	if _, err := Generate(0, 10, 50, 0); err == nil {
		t.Fatal("want error for width 0")
	}
	if _, err := Generate(10, 10, 0, 0); err == nil {
		t.Fatal("want error for iterations 0")
	}
}
```
- [ ] Run, expect failure:
```bash
go test ./internal/mandelbrot/
# expect: undefined: Generate
```
- [ ] Implement:
```go
package mandelbrot

import "fmt"

const Gradient = " .:-=+*#%@"

// Generate renders the Mandelbrot set as ASCII rows.
// If char == 0, iteration count maps onto Gradient; otherwise
// in-set points use char and the rest use spaces.
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
	const (
		reMin, reMax = -2.5, 1.0
		imMin, imMax = -1.0, 1.0
	)
	grad := []rune(Gradient)
	rows := make([]string, height)
	for py := 0; py < height; py++ {
		line := make([]rune, width)
		for px := 0; px < width; px++ {
			cr := reMin + (reMax-reMin)*float64(px)/float64(width-1)
			ci := imMin + (imMax-imMin)*float64(py)/float64(height-1)
			var zr, zi float64
			n := 0
			for ; n < iterations; n++ {
				zr, zi = zr*zr-zi*zi+cr, 2*zr*zi+ci
				if zr*zr+zi*zi > 4 {
					break
				}
			}
			inSet := n == iterations
			if char != 0 {
				if inSet {
					line[px] = char
				} else {
					line[px] = ' '
				}
			} else {
				idx := n * (len(grad) - 1) / iterations
				line[px] = grad[idx]
			}
		}
		rows[py] = string(line)
	}
	return rows, nil
}
```
Guard `width==1`/`height==1` divide-by-zero by treating those as the min coordinate:
```go
// replace the two cr/ci lines with:
cr := reMin
if width > 1 {
	cr = reMin + (reMax-reMin)*float64(px)/float64(width-1)
}
ci := imMin
if height > 1 {
	ci = imMin + (imMax-imMin)*float64(py)/float64(height-1)
}
```
- [ ] Run, expect pass:
```bash
go test ./internal/mandelbrot/
# expect: ok
```
- [ ] Commit: `git commit -am "feat: mandelbrot algorithm"`

---

### Task 4: CLI root + subcommands

**Files:** `internal/cli/root.go`, `internal/cli/sierpinski.go`, `internal/cli/mandelbrot.go`

**Interfaces:**
- Consumes `sierpinski.Generate`, `mandelbrot.Generate`, `mandelbrot.Gradient`.
- Produces `func Execute() error` (used by main) and `func NewRootCmd(out io.Writer) *cobra.Command` (used by tests). Each subcommand writes rows + `\n` to the command's configured out writer; algorithm errors are returned (cobra prints to stderr, non-zero exit).

- [ ] Write `internal/cli/root.go`:
```go
package cli

import (
	"io"
	"os"

	"github.com/spf13/cobra"
)

func NewRootCmd(out io.Writer) *cobra.Command {
	root := &cobra.Command{
		Use:   "fractals",
		Short: "Generate ASCII art fractals",
	}
	root.SetOut(out)
	root.AddCommand(newSierpinskiCmd(), newMandelbrotCmd())
	return root
}

func Execute() error {
	return NewRootCmd(os.Stdout).Execute()
}
```
- [ ] Write `internal/cli/sierpinski.go`:
```go
package cli

import (
	"github.com/example/fractals/internal/sierpinski"
	"github.com/spf13/cobra"
)

func newSierpinskiCmd() *cobra.Command {
	var size, depth int
	var char string
	cmd := &cobra.Command{
		Use:   "sierpinski",
		Short: "Generate a Sierpinski triangle",
		RunE: func(cmd *cobra.Command, args []string) error {
			c := '*'
			if char != "" {
				c = []rune(char)[0]
			}
			rows, err := sierpinski.Generate(size, depth, c)
			if err != nil {
				return err
			}
			for _, r := range rows {
				cmd.Println(r)
			}
			return nil
		},
	}
	cmd.Flags().IntVar(&size, "size", 32, "triangle base width")
	cmd.Flags().IntVar(&depth, "depth", 5, "recursion depth")
	cmd.Flags().StringVar(&char, "char", "", "fill character (default '*')")
	return cmd
}
```
- [ ] Write `internal/cli/mandelbrot.go`:
```go
package cli

import (
	"github.com/example/fractals/internal/mandelbrot"
	"github.com/spf13/cobra"
)

func newMandelbrotCmd() *cobra.Command {
	var width, height, iterations int
	var char string
	cmd := &cobra.Command{
		Use:   "mandelbrot",
		Short: "Render the Mandelbrot set",
		RunE: func(cmd *cobra.Command, args []string) error {
			var c rune // 0 => gradient
			if char != "" {
				c = []rune(char)[0]
			}
			rows, err := mandelbrot.Generate(width, height, iterations, c)
			if err != nil {
				return err
			}
			for _, r := range rows {
				cmd.Println(r)
			}
			return nil
		},
	}
	cmd.Flags().IntVar(&width, "width", 80, "output width")
	cmd.Flags().IntVar(&height, "height", 24, "output height")
	cmd.Flags().IntVar(&iterations, "iterations", 100, "max iterations")
	cmd.Flags().StringVar(&char, "char", "", "fill character (default gradient)")
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

func run(t *testing.T, args ...string) string {
	t.Helper()
	var buf bytes.Buffer
	cmd := NewRootCmd(&buf)
	cmd.SetArgs(args)
	if err := cmd.Execute(); err != nil {
		t.Fatalf("execute: %v", err)
	}
	return buf.String()
}

func TestSierpinskiOutput(t *testing.T) {
	out := run(t, "sierpinski", "--size", "8", "--depth", "3")
	if strings.Count(out, "\n") != 8 {
		t.Fatalf("want 8 lines, got %q", out)
	}
}

func TestMandelbrotCustomChar(t *testing.T) {
	out := run(t, "mandelbrot", "--width", "20", "--height", "10", "--char", "@")
	if !strings.ContainsRune(out, '@') {
		t.Fatalf("expected @, got %q", out)
	}
}

func TestInvalidSizeErrors(t *testing.T) {
	var buf bytes.Buffer
	cmd := NewRootCmd(&buf)
	cmd.SetArgs([]string{"sierpinski", "--size", "0"})
	if err := cmd.Execute(); err == nil {
		t.Fatal("want error for size 0")
	}
}
```
- [ ] Run, expect pass:
```bash
go test ./internal/cli/
# expect: ok
```
- [ ] Commit: `git commit -am "feat: cli commands"`

---

### Task 5: Entry point + end-to-end verification

**Files:** `cmd/fractals/main.go`

**Interfaces:** Consumes `cli.Execute`.

- [ ] Write `cmd/fractals/main.go`:
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
- [ ] Build and run full suite:
```bash
go build ./... && go test ./...
# expect: ok for each package
```
- [ ] Manual acceptance:
```bash
go run ./cmd/fractals --help          # shows usage with both subcommands
go run ./cmd/fractals sierpinski      # triangle
go run ./cmd/fractals mandelbrot      # mandelbrot gradient
go run ./cmd/fractals sierpinski --size 0; echo "exit=$?"  # error: size... exit=1
```
- [ ] Commit: `git commit -am "feat: entry point"`

---

## Self-Review

- **Spec coverage:** `--help` (Task 5 root cmd auto-help), sierpinski triangle (Task 2/4), mandelbrot (Task 3/4), all numeric flags (Task 4), `--char` for both (Task 4, empty string → default/gradient sentinel), invalid-input errors (Tasks 2/3 return errors, Task 4 propagates, Task 5 exits non-zero), tests pass (all tasks). ✓
- **Placeholder scan:** no TODOs; all code blocks complete. ✓
- **Type consistency:** `Generate` signatures `(int,int,rune) ([]string,error)` (sierpinski) and `(int,int,int,rune) ([]string,error)` (mandelbrot) match CLI calls; `char == 0` sentinel for mandelbrot gradient matches `var c rune` default. ✓
- **Note:** `--char` uses `StringVar` with `""` default so we can distinguish "unset" (gradient/`*`) from an explicit single char; first rune is taken.