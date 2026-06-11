# Go Fractals CLI - Implementation Plan

## Global Constraints

- Go 1.21+ required (set `go 1.21` in `go.mod`)
- CLI library: `github.com/spf13/cobra` (only external dependency)
- Binary name: `fractals`
- Sierpinski default char: `'*'`
- Mandelbrot gradient (when `--char` omitted): `" .:-=+*#%@"` (10 characters, index 0 = space)
- All output goes to stdout; errors to stderr with non-zero exit code
- Module path: `github.com/example/fractals`

## File Structure

| Path | Responsibility |
|------|----------------|
| `go.mod` | Module definition, Go version, cobra dependency |
| `internal/sierpinski/sierpinski.go` | Sierpinski triangle generation algorithm |
| `internal/sierpinski/sierpinski_test.go` | Tests for sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Mandelbrot set rendering algorithm |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command, help wiring, `Execute()` |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand, flag parsing, validation |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand, flag parsing, validation |
| `internal/cli/sierpinski_test.go` | Tests for sierpinski command (flags, validation, output) |
| `internal/cli/mandelbrot_test.go` | Tests for mandelbrot command (flags, validation, output) |
| `cmd/fractals/main.go` | Entry point calling `cli.Execute()` |

---

### Task 1: Project scaffolding

**Files:** `go.mod`, `cmd/fractals/main.go`, `internal/cli/root.go`

**Interfaces:**
- Produces: `cli.Execute() error` — runs the root command, returns error on failure.
- Produces: `cli.RootCmd *cobra.Command` — root command other subcommands attach to via `RootCmd.AddCommand(...)`.

- [ ] Create the module:
  ```bash
  go mod init github.com/example/fractals
  ```
  Expected: creates `go.mod` containing `module github.com/example/fractals` and `go 1.21` (or higher). If the Go version line is higher than `1.21`, leave it.

- [ ] Add cobra dependency:
  ```bash
  go get github.com/spf13/cobra@latest
  ```
  Expected: `go.mod` now lists `github.com/spf13/cobra` under `require`; a `go.sum` is created.

- [ ] Create `internal/cli/root.go`:
  ```go
  package cli

  import "github.com/spf13/cobra"

  // RootCmd is the base command. Subcommands attach to it.
  var RootCmd = &cobra.Command{
  	Use:   "fractals",
  	Short: "Generate ASCII art fractals",
  	Long:  "fractals generates ASCII art fractals such as Sierpinski triangles and the Mandelbrot set.",
  }

  // Execute runs the root command.
  func Execute() error {
  	return RootCmd.Execute()
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

- [ ] Tidy and build:
  ```bash
  go mod tidy && go build ./...
  ```
  Expected: no output, exit code 0.

- [ ] Verify help works:
  ```bash
  go run ./cmd/fractals --help
  ```
  Expected: output includes `fractals generates ASCII art fractals` and a `Usage:` line.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Scaffold fractals CLI with cobra root command"
  ```

---

### Task 2: Sierpinski algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

**Interfaces:**
- Produces: `sierpinski.Generate(size, depth int, char rune) ([]string, error)` — returns one string per row of the triangle (top row first). Returns an error if `size < 1` or `depth < 0`.

Algorithm note: Use the bitwise-AND rule. A cell at row `r`, column `c` (within a triangular grid of `size` rows) is filled when `(r & c) == 0`. The `depth` parameter limits how many subdivision levels render: rows beyond `2^depth` are clipped to at most `size` rows, i.e. effective rows = `min(size, 1<<depth)`. Each row `r` is left-padded with `size-1-r` spaces and contains `r+1` cells separated by single spaces; filled cells use `char`, empty cells use space.

- [ ] Create failing test `internal/sierpinski/sierpinski_test.go`:
  ```go
  package sierpinski

  import (
  	"strings"
  	"testing"
  )

  func TestGenerateDepth0SingleRow(t *testing.T) {
  	rows, err := Generate(32, 0, '*')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 1 {
  		t.Fatalf("depth 0 should produce 1 row, got %d", len(rows))
  	}
  	if strings.TrimSpace(rows[0]) != "*" {
  		t.Errorf("first row should be a single star, got %q", rows[0])
  	}
  }

  func TestGenerateTriangleShape(t *testing.T) {
  	rows, err := Generate(4, 5, '*')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 4 {
  		t.Fatalf("size 4 should produce 4 rows, got %d", len(rows))
  	}
  	// Row 0 has 1 cell, row 3 has 4 cells. (r & c)==0 rule:
  	// row 3: c=0..3 -> (3&0)=0*,(3&1)=1 space,(3&2)=2 space,(3&3)=3 space
  	got := strings.ReplaceAll(rows[3], " ", "")
  	if got != "*" {
  		t.Errorf("row 3 should have exactly one star, got %q (line %q)", got, rows[3])
  	}
  }

  func TestGenerateCustomChar(t *testing.T) {
  	rows, err := Generate(8, 5, '#')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(rows[0], "#") {
  		t.Errorf("expected custom char '#' in output, got %q", rows[0])
  	}
  	if strings.Contains(rows[0], "*") {
  		t.Errorf("did not expect default '*' when custom char given, got %q", rows[0])
  	}
  }

  func TestGenerateDepthClipsRows(t *testing.T) {
  	// depth 2 -> 1<<2 = 4 effective rows even though size is 16
  	rows, err := Generate(16, 2, '*')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 4 {
  		t.Fatalf("depth 2 should clip to 4 rows, got %d", len(rows))
  	}
  }

  func TestGenerateInvalidSize(t *testing.T) {
  	if _, err := Generate(0, 5, '*'); err == nil {
  		t.Error("expected error for size 0")
  	}
  }

  func TestGenerateInvalidDepth(t *testing.T) {
  	if _, err := Generate(8, -1, '*'); err == nil {
  		t.Error("expected error for negative depth")
  	}
  }
  ```

- [ ] Run to see it fail:
  ```bash
  go test ./internal/sierpinski/
  ```
  Expected: build failure (`undefined: Generate`).

- [ ] Implement `internal/sierpinski/sierpinski.go`:
  ```go
  package sierpinski

  import (
  	"fmt"
  	"strings"
  )

  // Generate builds a Sierpinski triangle. It returns one string per row,
  // top row first. char is used for filled cells.
  func Generate(size, depth int, char rune) ([]string, error) {
  	if size < 1 {
  		return nil, fmt.Errorf("size must be at least 1, got %d", size)
  	}
  	if depth < 0 {
  		return nil, fmt.Errorf("depth must be non-negative, got %d", depth)
  	}

  	effRows := size
  	if limit := 1 << uint(depth); limit < effRows {
  		effRows = limit
  	}

  	rows := make([]string, 0, effRows)
  	for r := 0; r < effRows; r++ {
  		var b strings.Builder
  		// Left padding so the triangle is centered.
  		b.WriteString(strings.Repeat(" ", effRows-1-r))
  		for c := 0; c <= r; c++ {
  			if r&c == 0 {
  				b.WriteRune(char)
  			} else {
  				b.WriteByte(' ')
  			}
  			if c < r {
  				b.WriteByte(' ')
  			}
  		}
  		rows = append(rows, b.String())
  	}
  	return rows, nil
  }
  ```

- [ ] Run to see it pass:
  ```bash
  go test ./internal/sierpinski/
  ```
  Expected: `ok  	github.com/example/fractals/internal/sierpinski`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add sierpinski triangle algorithm"
  ```

---

### Task 3: Mandelbrot algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

**Interfaces:**
- Produces: `mandelbrot.Gradient` — exported `string` constant equal to `" .:-=+*#%@"`.
- Produces: `mandelbrot.Render(width, height, iterations int, char *rune) ([]string, error)` — returns `height` strings each of length `width`. If `char` is non-nil, every set point uses that rune and escaped points use space. If `char` is nil, an iteration-count-to-gradient mapping is used. Returns an error if `width < 1`, `height < 1`, or `iterations < 1`.

Algorithm note: Map column `x` (0..width-1) to real axis `[-2.5, 1.0]` and row `y` (0..height-1) to imaginary axis `[-1.0, 1.0]`. For each point iterate `z = z^2 + c` until `|z| > 2` or `iterations` reached. With nil char, pick gradient index `iter * (len(Gradient)-1) / iterations`; points that never escape (iter == iterations) use the last gradient char (`@`). With a non-nil char, never-escaped points use that char, escaped points use space.

- [ ] Create failing test `internal/mandelbrot/mandelbrot_test.go`:
  ```go
  package mandelbrot

  import (
  	"strings"
  	"testing"
  )

  func TestRenderDimensions(t *testing.T) {
  	rows, err := Render(80, 24, 100, nil)
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 24 {
  		t.Fatalf("expected 24 rows, got %d", len(rows))
  	}
  	for i, row := range rows {
  		if len([]rune(row)) != 80 {
  			t.Errorf("row %d width = %d, want 80", i, len([]rune(row)))
  		}
  	}
  }

  func TestRenderGradientContainsBody(t *testing.T) {
  	rows, err := Render(80, 24, 100, nil)
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	joined := strings.Join(rows, "\n")
  	// The set body (never escapes) maps to '@', the last gradient char.
  	if !strings.Contains(joined, "@") {
  		t.Error("expected '@' for in-set points in gradient mode")
  	}
  }

  func TestRenderCustomChar(t *testing.T) {
  	c := '#'
  	rows, err := Render(40, 20, 50, &c)
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	joined := strings.Join(rows, "\n")
  	if !strings.Contains(joined, "#") {
  		t.Error("expected custom char '#' for in-set points")
  	}
  	if strings.ContainsAny(joined, ".:-=+*%@") {
  		t.Error("custom char mode should not emit gradient chars")
  	}
  }

  func TestRenderInvalidWidth(t *testing.T) {
  	if _, err := Render(0, 24, 100, nil); err == nil {
  		t.Error("expected error for width 0")
  	}
  }

  func TestRenderInvalidHeight(t *testing.T) {
  	if _, err := Render(80, 0, 100, nil); err == nil {
  		t.Error("expected error for height 0")
  	}
  }

  func TestRenderInvalidIterations(t *testing.T) {
  	if _, err := Render(80, 24, 0, nil); err == nil {
  		t.Error("expected error for iterations 0")
  	}
  }

  func TestGradientValue(t *testing.T) {
  	if Gradient != " .:-=+*#%@" {
  		t.Errorf("Gradient = %q, want %q", Gradient, " .:-=+*#%@")
  	}
  }
  ```

- [ ] Run to see it fail:
  ```bash
  go test ./internal/mandelbrot/
  ```
  Expected: build failure (`undefined: Render`, `undefined: Gradient`).

- [ ] Implement `internal/mandelbrot/mandelbrot.go`:
  ```go
  package mandelbrot

  import (
  	"fmt"
  	"strings"
  )

  // Gradient maps low-to-high iteration counts to characters. Index 0 is space.
  const Gradient = " .:-=+*#%@"

  const (
  	realMin = -2.5
  	realMax = 1.0
  	imagMin = -1.0
  	imagMax = 1.0
  )

  // Render produces the Mandelbrot set as ASCII art. If char is non-nil, in-set
  // points use that rune and escaped points use space. If char is nil, iteration
  // counts map onto Gradient.
  func Render(width, height, iterations int, char *rune) ([]string, error) {
  	if width < 1 {
  		return nil, fmt.Errorf("width must be at least 1, got %d", width)
  	}
  	if height < 1 {
  		return nil, fmt.Errorf("height must be at least 1, got %d", height)
  	}
  	if iterations < 1 {
  		return nil, fmt.Errorf("iterations must be at least 1, got %d", iterations)
  	}

  	gr := []rune(Gradient)
  	rows := make([]string, 0, height)
  	for y := 0; y < height; y++ {
  		ci := imagMin + (imagMax-imagMin)*float64(y)/float64(height-1)
  		if height == 1 {
  			ci = imagMin
  		}
  		var b strings.Builder
  		for x := 0; x < width; x++ {
  			cr := realMin + (realMax-realMin)*float64(x)/float64(width-1)
  			if width == 1 {
  				cr = realMin
  			}
  			iter := escape(cr, ci, iterations)
  			if char != nil {
  				if iter == iterations {
  					b.WriteRune(*char)
  				} else {
  					b.WriteByte(' ')
  				}
  				continue
  			}
  			idx := iter * (len(gr) - 1) / iterations
  			if idx >= len(gr) {
  				idx = len(gr) - 1
  			}
  			b.WriteRune(gr[idx])
  		}
  		rows = append(rows, b.String())
  	}
  	return rows, nil
  }

  // escape returns the iteration count at which z = z^2 + c escapes |z| > 2,
  // or maxIter if it never escapes.
  func escape(cr, ci float64, maxIter int) int {
  	var zr, zi float64
  	for i := 0; i < maxIter; i++ {
  		zr2, zi2 := zr*zr, zi*zi
  		if zr2+zi2 > 4.0 {
  			return i
  		}
  		zi = 2*zr*zi + ci
  		zr = zr2 - zi2 + cr
  	}
  	return maxIter
  }
  ```

- [ ] Run to see it pass:
  ```bash
  go test ./internal/mandelbrot/
  ```
  Expected: `ok  	github.com/example/fractals/internal/mandelbrot`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add mandelbrot set rendering algorithm"
  ```

---

### Task 4: Sierpinski subcommand

**Files:** `internal/cli/sierpinski.go`, `internal/cli/sierpinski_test.go`

**Interfaces:**
- Consumes: `cli.RootCmd` (Task 1), `sierpinski.Generate(size, depth int, char rune) ([]string, error)` (Task 2).
- Produces: `cli.newSierpinskiCmd() *cobra.Command` — builds the subcommand. Registered onto `RootCmd` via `init()`.

Flag/char note: `--char` is a `string` flag defaulting to `"*"`. Convert to a rune by taking the first rune of the string; if the string is empty, return an error. Write each row plus a trailing newline to the command's configured out writer (`cmd.OutOrStdout()`) so tests can capture it.

- [ ] Create failing test `internal/cli/sierpinski_test.go`:
  ```go
  package cli

  import (
  	"bytes"
  	"strings"
  	"testing"
  )

  func runCmd(args ...string) (string, error) {
  	var out bytes.Buffer
  	RootCmd.SetOut(&out)
  	RootCmd.SetErr(&out)
  	RootCmd.SetArgs(args)
  	err := RootCmd.Execute()
  	return out.String(), err
  }

  func TestSierpinskiDefault(t *testing.T) {
  	out, err := runCmd("sierpinski", "--size", "8", "--depth", "5")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(out, "*") {
  		t.Errorf("expected stars in output, got %q", out)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 8 {
  		t.Errorf("expected 8 lines, got %d", len(lines))
  	}
  }

  func TestSierpinskiCustomChar(t *testing.T) {
  	out, err := runCmd("sierpinski", "--size", "8", "--char", "#")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(out, "#") {
  		t.Errorf("expected '#' in output, got %q", out)
  	}
  }

  func TestSierpinskiEmptyCharErrors(t *testing.T) {
  	_, err := runCmd("sierpinski", "--char", "")
  	if err == nil {
  		t.Error("expected error for empty --char")
  	}
  }

  func TestSierpinskiInvalidSize(t *testing.T) {
  	_, err := runCmd("sierpinski", "--size", "0")
  	if err == nil {
  		t.Error("expected error for size 0")
  	}
  }
  ```

- [ ] Run to see it fail:
  ```bash
  go test ./internal/cli/
  ```
  Expected: build failure or failing tests (no `sierpinski` command registered).

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
  			r, err := firstRune(char)
  			if err != nil {
  				return err
  			}
  			rows, err := sierpinski.Generate(size, depth, r)
  			if err != nil {
  				return err
  			}
  			for _, row := range rows {
  				fmt.Fprintln(cmd.OutOrStdout(), row)
  			}
  			return nil
  		},
  	}
  	cmd.Flags().IntVar(&size, "size", 32, "Width of the triangle base in characters")
  	cmd.Flags().IntVar(&depth, "depth", 5, "Recursion depth")
  	cmd.Flags().StringVar(&char, "char", "*", "Character to use for filled points")
  	return cmd
  }

  // firstRune returns the first rune of s, or an error if s is empty.
  func firstRune(s string) (rune, error) {
  	if s == "" {
  		return 0, fmt.Errorf("char must not be empty")
  	}
  	return []rune(s)[0], nil
  }

  func init() {
  	RootCmd.AddCommand(newSierpinskiCmd())
  }
  ```

- [ ] Run to see it pass:
  ```bash
  go test ./internal/cli/
  ```
  Expected: `ok  	github.com/example/fractals/internal/cli`.

- [ ] Verify end-to-end:
  ```bash
  go run ./cmd/fractals sierpinski --size 16 --depth 5
  ```
  Expected: a centered triangle of `*` characters, 16 lines tall.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add sierpinski subcommand"
  ```

---

### Task 5: Mandelbrot subcommand

**Files:** `internal/cli/mandelbrot.go`, `internal/cli/mandelbrot_test.go`

**Interfaces:**
- Consumes: `cli.RootCmd` (Task 1), `cli.firstRune(s string) (rune, error)` (Task 4), `mandelbrot.Render(width, height, iterations int, char *rune) ([]string, error)` (Task 3).
- Produces: `cli.newMandelbrotCmd() *cobra.Command` — registered onto `RootCmd` via `init()`.

Char note: `--char` defaults to empty string meaning gradient mode (pass `nil` to `Render`). If the user supplies a non-empty `--char`, convert via `firstRune` and pass a `*rune`. Detect whether the flag was set using `cmd.Flags().Changed("char")`.

- [ ] Create failing test `internal/cli/mandelbrot_test.go`:
  ```go
  package cli

  import (
  	"strings"
  	"testing"
  )

  func TestMandelbrotDefault(t *testing.T) {
  	out, err := runCmd("mandelbrot", "--width", "40", "--height", "12", "--iterations", "50")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 12 {
  		t.Fatalf("expected 12 lines, got %d", len(lines))
  	}
  	for i, line := range lines {
  		if len([]rune(line)) != 40 {
  			t.Errorf("line %d width = %d, want 40", i, len([]rune(line)))
  		}
  	}
  }

  func TestMandelbrotGradientChars(t *testing.T) {
  	out, err := runCmd("mandelbrot", "--width", "80", "--height", "24")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(out, "@") {
  		t.Errorf("expected '@' for in-set points, got:\n%s", out)
  	}
  }

  func TestMandelbrotCustomChar(t *testing.T) {
  	out, err := runCmd("mandelbrot", "--width", "40", "--height", "12", "--char", "#")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(out, "#") {
  		t.Errorf("expected '#' in output, got:\n%s", out)
  	}
  	if strings.ContainsAny(out, ".:-=+*%@") {
  		t.Errorf("custom char mode should not emit gradient chars, got:\n%s", out)
  	}
  }

  func TestMandelbrotInvalidIterations(t *testing.T) {
  	_, err := runCmd("mandelbrot", "--iterations", "0")
  	if err == nil {
  		t.Error("expected error for iterations 0")
  	}
  }

  func TestMandelbrotEmptyCharErrors(t *testing.T) {
  	_, err := runCmd("mandelbrot", "--char", "")
  	if err == nil {
  		t.Error("expected error for explicitly empty --char")
  	}
  }
  ```

  Note: `runCmd` is defined in `sierpinski_test.go` (same package `cli`); do not redeclare it.

- [ ] Run to see it fail:
  ```bash
  go test ./internal/cli/
  ```
  Expected: failing tests (no `mandelbrot` command registered).

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
  			var charPtr *rune
  			if cmd.Flags().Changed("char") {
  				r, err := firstRune(char)
  				if err != nil {
  					return err
  				}
  				charPtr = &r
  			}
  			rows, err := mandelbrot.Render(width, height, iterations, charPtr)
  			if err != nil {
  				return err
  			}
  			for _, row := range rows {
  				fmt.Fprintln(cmd.OutOrStdout(), row)
  			}
  			return nil
  		},
  	}
  	cmd.Flags().IntVar(&width, "width", 80, "Output width in characters")
  	cmd.Flags().IntVar(&height, "height", 24, "Output height in characters")
  	cmd.Flags().IntVar(&iterations, "iterations", 100, "Maximum iterations for escape calculation")
  	cmd.Flags().StringVar(&char, "char", "", "Single character, or omit for gradient \" .:-=+*#%@\"")
  	return cmd
  }

  func init() {
  	RootCmd.AddCommand(newMandelbrotCmd())
  }
  ```

- [ ] Run to see it pass:
  ```bash
  go test ./internal/cli/
  ```
  Expected: `ok  	github.com/example/fractals/internal/cli`.

- [ ] Verify end-to-end:
  ```bash
  go run ./cmd/fractals mandelbrot --width 80 --height 24
  ```
  Expected: a recognizable Mandelbrot set rendered with the gradient, including `@` in the body.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add mandelbrot subcommand"
  ```

---

### Task 6: Full acceptance verification

**Files:** none (verification only)

**Interfaces:** Consumes the fully assembled binary from Tasks 1–5.

- [ ] Run the full test suite:
  ```bash
  go test ./...
  ```
  Expected: `ok` for `internal/sierpinski`, `internal/mandelbrot`, and `internal/cli`; no failures.

- [ ] Build the binary:
  ```bash
  go build -o fractals ./cmd/fractals
  ```
  Expected: produces an executable `fractals`, exit code 0.

- [ ] Acceptance 1 — root help:
  ```bash
  ./fractals --help
  ```
  Expected: shows `Usage:`, and lists `sierpinski` and `mandelbrot` under available commands.

- [ ] Acceptance — subcommand help:
  ```bash
  ./fractals sierpinski --help
  ```
  Expected: lists `--size`, `--depth`, `--char` flags with defaults.

- [ ] Acceptance 2 — default sierpinski:
  ```bash
  ./fractals sierpinski
  ```
  Expected: a recognizable triangle of `*`.

- [ ] Acceptance 3 — default mandelbrot:
  ```bash
  ./fractals mandelbrot
  ```
  Expected: a recognizable Mandelbrot set.

- [ ] Acceptance 6 — invalid input error:
  ```bash
  ./fractals sierpinski --size 0; echo "exit=$?"
  ```
  Expected: clear error message containing `size must be at least 1` on stderr and `exit=1`.

- [ ] Clean up the local binary (not committed):
  ```bash
  rm -f fractals
  ```

- [ ] Commit any remaining changes (e.g. updated `go.sum`):
  ```bash
  git add -A && git commit -m "Finalize fractals CLI" --allow-empty
  ```

---

## Self-Review

**Spec coverage:**
- Two fractal types (sierpinski, mandelbrot): Tasks 2/4 and 3/5. ✓
- Flags `--size`, `--depth`, `--char` (sierpinski): Task 4. ✓
- Flags `--width`, `--height`, `--iterations`, `--char` (mandelbrot): Task 5. ✓
- Gradient `" .:-=+*#%@"` verbatim: Task 3 constant + test. ✓
- `--char` omitted → gradient (mandelbrot): handled via `Flags().Changed("char")`, Task 5. ✓
- Help (`--help`, subcommand `--help`): cobra-provided, verified Task 6. ✓
- Clear errors for invalid input: validation in algorithm packages, surfaced via `RunE` + `main.go` stderr/exit-1. ✓
- All tests pass: Tasks 2,3,4,5 unit tests + Task 6 suite. ✓
- Architecture file layout matches spec exactly (cmd/fractals, internal/{sierpinski,mandelbrot,cli}). ✓
- Go 1.21+ and cobra dependency: Task 1. ✓

**Placeholder scan:** No `TODO`, `FIXME`, or stub bodies remain; all code blocks are complete.

**Type consistency:** `Generate(int, int, rune) ([]string, error)` and `Render(int, int, int, *rune) ([]string, error)` signatures in the Interfaces blocks match their implementations and call sites. `firstRune(string) (rune, error)` defined once in Task 4 and consumed in Task 5. `RootCmd`/`Execute` signatures consistent across `main.go` and `root.go`.

**Note on `--char` semantics divergence:** For sierpinski, an empty `--char` is an error (default is `*`, so empty only occurs if user explicitly passes `--char ""`). For mandelbrot, an unset `--char` means gradient mode while an explicitly empty `--char ""` is an error — this matches the spec's "omit for gradient" wording and is verified by `TestMandelbrotEmptyCharErrors` and `TestMandelbrotGradientChars`.