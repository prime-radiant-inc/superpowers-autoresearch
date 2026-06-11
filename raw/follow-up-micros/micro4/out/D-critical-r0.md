# Go Fractals CLI - Implementation Plan

## Global Constraints

- Go 1.21+ required (set in `go.mod`)
- Use `github.com/spf13/cobra` for CLI
- Module path: `github.com/example/fractals`
- Default sierpinski: `--size 32`, `--depth 5`, `--char '*'`
- Default mandelbrot: `--width 80`, `--height 24`, `--iterations 100`, gradient `" .:-=+*#%@"`
- Invalid inputs produce clear error messages (non-zero exit, message to stderr)
- All output goes to stdout, one line per row

## File Structure

| File | Responsibility |
|------|----------------|
| `go.mod` | Module definition, Go version, cobra dependency |
| `internal/sierpinski/sierpinski.go` | Sierpinski generation algorithm returning `[]string` |
| `internal/sierpinski/sierpinski_test.go` | Tests for sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Mandelbrot generation algorithm returning `[]string` |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command, help wiring |
| `internal/cli/sierpinski.go` | Sierpinski subcommand, flag parsing |
| `internal/cli/mandelbrot.go` | Mandelbrot subcommand, flag parsing |
| `internal/cli/sierpinski_test.go` | Sierpinski command flag/validation tests |
| `internal/cli/mandelbrot_test.go` | Mandelbrot command flag/validation tests |
| `cmd/fractals/main.go` | Entry point calling `cli.Execute()` |

---

### Task 1: Module setup and Sierpinski algorithm

**Files:** `go.mod`, `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

**Interfaces:**
- Produces: `func Generate(size, depth int, char rune) ([]string, error)` — returns one string per row; errors on `size < 1` or `depth < 0`.

The Sierpinski algorithm uses the bitwise property: a cell at row `r`, column `c` (in triangle coordinates) is filled when `(r & c) == 0`. We render `size` rows; each row `r` has leading spaces for alignment and fills column `c` where `(c & (r-c)) == 0` produces the classic triangle. Use the standard approach below.

- [ ] Create `go.mod`:
  ```
  go mod init github.com/example/fractals
  ```
  Then edit `go.mod` to ensure `go 1.21`.

- [ ] Write failing test `internal/sierpinski/sierpinski_test.go`:
  ```go
  package sierpinski

  import (
  	"strings"
  	"testing"
  )

  func TestGenerateSmallTriangle(t *testing.T) {
  	rows, err := Generate(4, 5, '*')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 4 {
  		t.Fatalf("expected 4 rows, got %d", len(rows))
  	}
  	// Top row has exactly one filled cell.
  	if strings.Count(rows[0], "*") != 1 {
  		t.Errorf("top row should have 1 star, got %q", rows[0])
  	}
  	// Bottom row is fully filled across its width.
  	if strings.Count(rows[3], "*") != 4 {
  		t.Errorf("bottom row should have 4 stars, got %q", rows[3])
  	}
  }

  func TestGenerateCustomChar(t *testing.T) {
  	rows, _ := Generate(2, 1, '#')
  	joined := strings.Join(rows, "\n")
  	if strings.Contains(joined, "*") {
  		t.Errorf("output should not contain default char: %q", joined)
  	}
  	if !strings.Contains(joined, "#") {
  		t.Errorf("output should contain custom char: %q", joined)
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

- [ ] Run the test, expect compile failure (no `Generate`):
  ```
  go test ./internal/sierpinski/
  ```
  Expected: `undefined: Generate`.

- [ ] Implement `internal/sierpinski/sierpinski.go`:
  ```go
  package sierpinski

  import "fmt"

  // Generate returns size rows forming a Sierpinski triangle.
  // A cell at row r, column c is filled when (c & (r-c)) == 0,
  // which yields the classic bitwise Sierpinski pattern.
  func Generate(size, depth int, char rune) ([]string, error) {
  	if size < 1 {
  		return nil, fmt.Errorf("size must be at least 1, got %d", size)
  	}
  	if depth < 0 {
  		return nil, fmt.Errorf("depth must be non-negative, got %d", depth)
  	}

  	rows := make([]string, size)
  	for r := 0; r < size; r++ {
  		line := make([]rune, 0, size)
  		// Leading spaces center the triangle.
  		for s := 0; s < size-1-r; s++ {
  			line = append(line, ' ')
  		}
  		for c := 0; c <= r; c++ {
  			if (c & (r - c)) == 0 {
  				line = append(line, char)
  			} else {
  				line = append(line, ' ')
  			}
  		}
  		rows[r] = string(line)
  	}
  	return rows, nil
  }
  ```
  Note: `depth` is accepted and validated per spec; the bitwise method renders the full triangle for the given `size`.

- [ ] Run the test, expect pass:
  ```
  go test ./internal/sierpinski/
  ```
  Expected: `ok  github.com/example/fractals/internal/sierpinski`.

- [ ] Commit:
  ```
  git add go.mod internal/sierpinski && git commit -m "Add sierpinski algorithm"
  ```

---

### Task 2: Mandelbrot algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `const DefaultGradient = " .:-=+*#%@"`
  - `func Generate(width, height, iterations int, char rune) ([]string, error)` — when `char == 0`, use the gradient mapped by iteration count; otherwise use the single char for in-set points and space for escaped points. Errors on `width < 1`, `height < 1`, or `iterations < 1`.

The escape calculation maps pixel `(px, py)` to complex plane: real in `[-2.5, 1.0]`, imag in `[-1.0, 1.0]`. Iterate `z = z² + c` until `|z| > 2` or max iterations. Gradient index = `iter * (len(gradient)-1) / iterations`; points that never escape (`iter == iterations`) get the last gradient char.

- [ ] Write failing test `internal/mandelbrot/mandelbrot_test.go`:
  ```go
  package mandelbrot

  import (
  	"strings"
  	"testing"
  )

  func TestGenerateDimensions(t *testing.T) {
  	rows, err := Generate(20, 10, 50, 0)
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 10 {
  		t.Fatalf("expected 10 rows, got %d", len(rows))
  	}
  	for i, row := range rows {
  		if len([]rune(row)) != 20 {
  			t.Errorf("row %d width = %d, want 20", i, len([]rune(row)))
  		}
  	}
  }

  func TestGenerateGradientContainsSetChar(t *testing.T) {
  	// The center region is inside the set -> last gradient char '@'.
  	rows, _ := Generate(80, 24, 100, 0)
  	joined := strings.Join(rows, "\n")
  	if !strings.Contains(joined, "@") {
  		t.Errorf("expected in-set char '@' in output")
  	}
  }

  func TestGenerateCustomChar(t *testing.T) {
  	rows, _ := Generate(80, 24, 100, '#')
  	joined := strings.Join(rows, "\n")
  	if !strings.Contains(joined, "#") {
  		t.Errorf("expected custom char '#' in output")
  	}
  	if strings.Contains(joined, "@") {
  		t.Errorf("custom char mode should not contain gradient chars")
  	}
  }

  func TestGenerateInvalid(t *testing.T) {
  	cases := []struct{ w, h, it int }{{0, 10, 50}, {10, 0, 50}, {10, 10, 0}}
  	for _, c := range cases {
  		if _, err := Generate(c.w, c.h, c.it, 0); err == nil {
  			t.Errorf("expected error for %+v", c)
  		}
  	}
  }
  ```

- [ ] Run the test, expect compile failure:
  ```
  go test ./internal/mandelbrot/
  ```
  Expected: `undefined: Generate`.

- [ ] Implement `internal/mandelbrot/mandelbrot.go`:
  ```go
  package mandelbrot

  import "fmt"

  const DefaultGradient = " .:-=+*#%@"

  // Generate renders the Mandelbrot set as width x height rows.
  // If char == 0, iteration counts are mapped onto DefaultGradient.
  // Otherwise char marks in-set points and space marks escaped points.
  func Generate(width, height, iterations int, char rune) ([]string, error) {
  	if width < 1 {
  		return nil, fmt.Errorf("width must be at least 1, got %d", width)
  	}
  	if height < 1 {
  		return nil, fmt.Errorf("height must be at least 1, got %d", height)
  	}
  	if iterations < 1 {
  		return nil, fmt.Errorf("iterations must be at least 1, got %d", iterations)
  	}

  	const (
  		minRe, maxRe = -2.5, 1.0
  		minIm, maxIm = -1.0, 1.0
  	)
  	gradient := []rune(DefaultGradient)

  	rows := make([]string, height)
  	for py := 0; py < height; py++ {
  		cIm := minIm + (maxIm-minIm)*float64(py)/float64(height-1)
  		if height == 1 {
  			cIm = (minIm + maxIm) / 2
  		}
  		line := make([]rune, width)
  		for px := 0; px < width; px++ {
  			cRe := minRe + (maxRe-minRe)*float64(px)/float64(width-1)
  			if width == 1 {
  				cRe = (minRe + maxRe) / 2
  			}
  			iter := escape(cRe, cIm, iterations)

  			if char != 0 {
  				if iter == iterations {
  					line[px] = char
  				} else {
  					line[px] = ' '
  				}
  				continue
  			}
  			idx := iter * (len(gradient) - 1) / iterations
  			line[px] = gradient[idx]
  		}
  		rows[py] = string(line)
  	}
  	return rows, nil
  }

  func escape(cRe, cIm float64, maxIter int) int {
  	var zRe, zIm float64
  	for i := 0; i < maxIter; i++ {
  		zRe2, zIm2 := zRe*zRe, zIm*zIm
  		if zRe2+zIm2 > 4.0 {
  			return i
  		}
  		zIm = 2*zRe*zIm + cIm
  		zRe = zRe2 - zIm2 + cRe
  	}
  	return maxIter
  }
  ```

- [ ] Run the test, expect pass:
  ```
  go test ./internal/mandelbrot/
  ```
  Expected: `ok  github.com/example/fractals/internal/mandelbrot`.

- [ ] Commit:
  ```
  git add internal/mandelbrot && git commit -m "Add mandelbrot algorithm"
  ```

---

### Task 3: CLI root command and entry point

**Files:** `internal/cli/root.go`, `cmd/fractals/main.go`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `func NewRootCmd() *cobra.Command` — returns root command named `fractals` with short/long descriptions; subcommands added by later tasks via `rootCmd.AddCommand(...)`.
  - `func Execute() error` — builds root cmd (with subcommands wired in) and runs it.

- [ ] Add cobra dependency:
  ```
  go get github.com/spf13/cobra@latest
  ```
  Expected: `go.mod` gains `require github.com/spf13/cobra`.

- [ ] Implement `internal/cli/root.go`:
  ```go
  package cli

  import "github.com/spf13/cobra"

  // NewRootCmd builds the root fractals command without subcommands.
  func NewRootCmd() *cobra.Command {
  	return &cobra.Command{
  		Use:   "fractals",
  		Short: "Generate ASCII art fractals",
  		Long:  "fractals generates ASCII art fractals (Sierpinski triangle and Mandelbrot set).",
  	}
  }

  // Execute wires all subcommands and runs the CLI.
  func Execute() error {
  	root := NewRootCmd()
  	root.AddCommand(newSierpinskiCmd())
  	root.AddCommand(newMandelbrotCmd())
  	return root.Execute()
  }
  ```
  Note: `newSierpinskiCmd` and `newMandelbrotCmd` are defined in Tasks 4 and 5. This file will not compile standalone until those exist; build verification happens in Task 5.

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

- [ ] Commit (compilation completes after Task 5; commit scaffolding now):
  ```
  git add go.mod go.sum internal/cli/root.go cmd/fractals/main.go && git commit -m "Add CLI root command and entry point"
  ```

---

### Task 4: Sierpinski subcommand

**Files:** `internal/cli/sierpinski.go`, `internal/cli/sierpinski_test.go`

**Interfaces:**
- Consumes: `sierpinski.Generate(size, depth int, char rune) ([]string, error)`.
- Produces: `func newSierpinskiCmd() *cobra.Command` — subcommand `sierpinski` with flags `--size` (int, default 32), `--depth` (int, default 5), `--char` (string, default `"*"`); prints rows to the command's stdout.

The `--char` flag is a string; validate it is exactly one rune. Write to `cmd.OutOrStdout()` so tests can capture output.

- [ ] Write failing test `internal/cli/sierpinski_test.go`:
  ```go
  package cli

  import (
  	"bytes"
  	"strings"
  	"testing"
  )

  func runCmd(args ...string) (string, error) {
  	root := NewRootCmd()
  	root.AddCommand(newSierpinskiCmd())
  	root.AddCommand(newMandelbrotCmd())
  	var out bytes.Buffer
  	root.SetOut(&out)
  	root.SetErr(&out)
  	root.SetArgs(args)
  	err := root.Execute()
  	return out.String(), err
  }

  func TestSierpinskiDefault(t *testing.T) {
  	out, err := runCmd("sierpinski")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if strings.Count(out, "*") < 1 {
  		t.Errorf("expected stars in output")
  	}
  	if len(strings.Split(strings.TrimRight(out, "\n"), "\n")) != 32 {
  		t.Errorf("expected 32 rows by default")
  	}
  }

  func TestSierpinskiCustomChar(t *testing.T) {
  	out, err := runCmd("sierpinski", "--size", "8", "--char", "#")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(out, "#") {
  		t.Errorf("expected custom char in output")
  	}
  }

  func TestSierpinskiInvalidChar(t *testing.T) {
  	_, err := runCmd("sierpinski", "--char", "ab")
  	if err == nil {
  		t.Error("expected error for multi-char --char")
  	}
  }

  func TestSierpinskiInvalidSize(t *testing.T) {
  	_, err := runCmd("sierpinski", "--size", "0")
  	if err == nil {
  		t.Error("expected error for size 0")
  	}
  }
  ```

- [ ] Run the test, expect compile failure (`newSierpinskiCmd` / `newMandelbrotCmd` undefined):
  ```
  go test ./internal/cli/
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
  			runes := []rune(char)
  			if len(runes) != 1 {
  				return fmt.Errorf("--char must be a single character, got %q", char)
  			}
  			rows, err := sierpinski.Generate(size, depth, runes[0])
  			if err != nil {
  				return err
  			}
  			for _, row := range rows {
  				fmt.Fprintln(cmd.OutOrStdout(), row)
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

- [ ] The CLI test file references `newMandelbrotCmd` (Task 5). Add a temporary stub at the bottom of `internal/cli/sierpinski.go` ONLY if needed to compile in isolation — skip; instead run sierpinski-package algorithm tests now and defer CLI test run to Task 5 where both commands exist:
  ```
  go build ./internal/sierpinski/ ./internal/mandelbrot/
  ```
  Expected: no output (success).

- [ ] Commit:
  ```
  git add internal/cli/sierpinski.go internal/cli/sierpinski_test.go && git commit -m "Add sierpinski subcommand"
  ```

---

### Task 5: Mandelbrot subcommand and full integration

**Files:** `internal/cli/mandelbrot.go`, `internal/cli/mandelbrot_test.go`

**Interfaces:**
- Consumes: `mandelbrot.Generate(width, height, iterations int, char rune) ([]string, error)`, `mandelbrot.DefaultGradient`.
- Produces: `func newMandelbrotCmd() *cobra.Command` — subcommand `mandelbrot` with flags `--width` (int, default 80), `--height` (int, default 24), `--iterations` (int, default 100), `--char` (string, default `""` meaning gradient). When `--char` is empty, pass `rune(0)` to `Generate`; otherwise validate single rune.

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
  		Short: "Render the Mandelbrot set as ASCII art",
  		RunE: func(cmd *cobra.Command, args []string) error {
  			var ch rune // 0 means gradient
  			if char != "" {
  				runes := []rune(char)
  				if len(runes) != 1 {
  					return fmt.Errorf("--char must be a single character, got %q", char)
  				}
  				ch = runes[0]
  			}
  			rows, err := mandelbrot.Generate(width, height, iterations, ch)
  			if err != nil {
  				return err
  			}
  			for _, row := range rows {
  				fmt.Fprintln(cmd.OutOrStdout(), row)
  			}
  			return nil
  		},
  	}
  	cmd.Flags().IntVar(&width, "width", 80, "output width in characters")
  	cmd.Flags().IntVar(&height, "height", 24, "output height in characters")
  	cmd.Flags().IntVar(&iterations, "iterations", 100, "maximum iterations for escape calculation")
  	cmd.Flags().StringVar(&char, "char", "", "single character, or omit for gradient \""+mandelbrot.DefaultGradient+"\"")
  	return cmd
  }
  ```

- [ ] Write `internal/cli/mandelbrot_test.go`:
  ```go
  package cli

  import (
  	"strings"
  	"testing"
  )

  func TestMandelbrotDefault(t *testing.T) {
  	out, err := runCmd("mandelbrot")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 24 {
  		t.Errorf("expected 24 rows, got %d", len(lines))
  	}
  	if !strings.Contains(out, "@") {
  		t.Errorf("expected gradient in-set char '@'")
  	}
  }

  func TestMandelbrotCustomChar(t *testing.T) {
  	out, err := runCmd("mandelbrot", "--char", "#")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(out, "#") {
  		t.Errorf("expected custom char in output")
  	}
  }

  func TestMandelbrotInvalidWidth(t *testing.T) {
  	_, err := runCmd("mandelbrot", "--width", "0")
  	if err == nil {
  		t.Error("expected error for width 0")
  	}
  }

  func TestMandelbrotInvalidChar(t *testing.T) {
  	_, err := runCmd("mandelbrot", "--char", "ab")
  	if err == nil {
  		t.Error("expected error for multi-char --char")
  	}
  }
  ```

- [ ] Run the full CLI test suite, expect pass (both subcommands now exist):
  ```
  go test ./internal/cli/
  ```
  Expected: `ok  github.com/example/fractals/internal/cli`.

- [ ] Run all tests:
  ```
  go test ./...
  ```
  Expected: `ok` for `internal/sierpinski`, `internal/mandelbrot`, `internal/cli`.

- [ ] Tidy and build the binary:
  ```
  go mod tidy && go build -o fractals ./cmd/fractals
  ```
  Expected: no output; `fractals` binary created.

- [ ] Manual acceptance checks:
  ```
  ./fractals --help
  ./fractals sierpinski --size 16 --char '#'
  ./fractals mandelbrot --width 80 --height 24
  ```
  Expected: help lists `sierpinski` and `mandelbrot`; triangle of `#`; recognizable Mandelbrot set with gradient.

- [ ] Commit:
  ```
  git add internal/cli/mandelbrot.go internal/cli/mandelbrot_test.go go.mod go.sum && git commit -m "Add mandelbrot subcommand and complete integration"
  ```

---

## Self-Review

- **Spec coverage:** `--help` (Task 3 root + cobra auto), sierpinski triangle (Tasks 1, 4), mandelbrot set (Tasks 2, 5), all flags `--size/--width/--height/--depth/--iterations` (Tasks 4, 5), `--char` customization including gradient default (Tasks 2, 5), clear error messages for invalid inputs (validation in Tasks 1, 2, 4, 5), all tests pass (Task 5 `go test ./...`). ✓
- **Architecture match:** All files from spec's tree are present and assigned. ✓
- **Type consistency:** `Generate` signatures match between algorithm tasks and consuming CLI tasks; `char rune`, with `rune(0)` sentinel for mandelbrot gradient mode consistently documented. ✓
- **Placeholder scan:** No TODOs or unfilled placeholders; module path `github.com/example/fractals` used uniformly. ✓
- **Ordering note:** Task 3's `Execute()` references commands defined in Tasks 4–5, so first full compile/build occurs in Task 5; this is called out explicitly to avoid a reviewer expecting a green build mid-Task 3. ✓