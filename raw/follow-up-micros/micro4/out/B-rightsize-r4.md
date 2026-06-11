# Go Fractals CLI - Implementation Plan

## Overview

We're building a CLI tool that generates ASCII art fractals (Sierpinski triangle and Mandelbrot set). The work proceeds bottom-up: pure algorithm packages first (fully testable in isolation), then the CLI layer that wires them to cobra commands, then the entry point.

This plan assumes zero context. Follow steps in order. Each step is one action.

## File Structure

| File | Responsibility |
|------|----------------|
| `go.mod` | Module definition and dependencies |
| `internal/sierpinski/sierpinski.go` | Pure function generating Sierpinski triangle as `[]string` |
| `internal/sierpinski/sierpinski_test.go` | Tests for the Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure function generating Mandelbrot set as `[]string` |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for the Mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command + `Execute()` |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand: flag parsing, validation, output |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand: flag parsing, validation, output |
| `internal/cli/root_test.go` | Tests for root command help |
| `internal/cli/sierpinski_test.go` | Tests for sierpinski subcommand wiring/validation |
| `internal/cli/mandelbrot_test.go` | Tests for mandelbrot subcommand wiring/validation |
| `cmd/fractals/main.go` | Entry point calling `cli.Execute()` |

## Conventions

- Module path: `github.com/example/fractals`. (If you fork this, change consistently everywhere.)
- Algorithm packages are **pure**: they take parameters and return `([]string, error)`, never printing or touching `os.Args`.
- CLI commands write to a configurable `io.Writer` (cobra's `cmd.OutOrStdout()`) so output is testable.
- Validation lives in the CLI layer; algorithm functions assume valid input but defend against the cheap cases.

---

### Task 1: Project scaffolding and module setup

**Files:** `go.mod`, `cmd/fractals/main.go`

This task establishes a compiling, runnable skeleton so later tasks have something to build on. `main.go` is a thin placeholder that we replace its body in Task 6; we create it here only so the module builds.

- [ ] Create the project directory and initialize git:
  ```bash
  mkdir -p fractals && cd fractals
  git init
  ```
  Expected: `Initialized empty Git repository ...`

- [ ] Initialize the Go module:
  ```bash
  go mod init github.com/example/fractals
  ```
  Expected: `go: creating new go.mod: module github.com/example/fractals`

- [ ] Confirm Go version is 1.21 or newer:
  ```bash
  go version
  ```
  Expected: `go version go1.21` or higher.

- [ ] Add cobra as a dependency:
  ```bash
  go get github.com/spf13/cobra@latest
  ```
  Expected output ends with a line like `go: added github.com/spf13/cobra v1.x.x`.

- [ ] Create a placeholder entry point so the module compiles. Create `cmd/fractals/main.go`:
  ```go
  package main

  import "fmt"

  func main() {
  	fmt.Println("fractals: not yet implemented")
  }
  ```

- [ ] Add a `.gitignore`:
  ```bash
  cat > .gitignore <<'EOF'
  /fractals
  /dist/
  *.out
  EOF
  ```

- [ ] Verify the build:
  ```bash
  go build ./...
  ```
  Expected: no output, exit code 0.

- [ ] Run it to confirm it executes:
  ```bash
  go run ./cmd/fractals
  ```
  Expected: `fractals: not yet implemented`

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Scaffold Go module with cobra dependency"
  ```

---

### Task 2: Sierpinski algorithm package

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

Deliverable: a pure `Generate` function. We use the classic bitwise rule: in a rendered triangle, a cell at row `y`, column `x` is filled when `(x & y) == 0` (Sierpinski via Pascal's triangle mod 2). This gives a clean, well-defined output independent of floating point.

We map the spec flags onto this: `depth` determines the triangle's logical resolution — the triangle has `2^depth` rows. `size` controls the horizontal scaling of the base. We render `rows = 2^depth` lines; for each row `y` we print characters at the appropriate horizontal positions, indenting to form the triangular shape.

To keep output unambiguous and testable, define the rendering precisely:
- Number of rows = `2^depth`.
- For row `y` (0-indexed from the top), the row contains cells for `x` in `0..y`. Cell `x` is filled if `(x & (y)) == ... ` — we use `(x & (y)) == x`? No. Use the standard: filled when `(x & (y_from_bottom))`... To avoid ambiguity we pin the exact rule in the test below and implement to match.

We'll use this concrete rule (top row is a single point):
- Let `n = 2^depth`.
- For each `y` from `0` to `n-1`:
  - Leading spaces: `n - 1 - y`.
  - For `x` from `0` to `y`: emit `char` if `(x & (n-1-... ))`...

To remove all hand-waving, we fix the rule as: **fill cell `(x, y)` when `(x & y) == 0`**, with `x` in `0..y`. Each filled cell is followed by a space for visual spacing; unfilled cells are two spaces. Leading indent of `(n-1-y)` spaces centers each row. `size` scales horizontal repetition (each cell repeated `max(1, size/n)` times). The test encodes the exact expected strings so the implementation has a single correct target.

- [ ] Create the failing test file `internal/sierpinski/sierpinski_test.go`:
  ```go
  package sierpinski

  import (
  	"reflect"
  	"strings"
  	"testing"
  )

  func TestGenerateDepthZero(t *testing.T) {
  	// depth 0 => 2^0 = 1 row, a single filled cell.
  	got, err := Generate(1, 0, '*')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	want := []string{"*"}
  	if !reflect.DeepEqual(got, want) {
  		t.Fatalf("got %#v, want %#v", got, want)
  	}
  }

  func TestGenerateDepthTwo(t *testing.T) {
  	// depth 2 => 4 rows. Rule: cell (x,y) filled when (x & y) == 0,
  	// x in 0..y. Each row indented by (n-1-y) spaces, cells separated
  	// by single spaces, trailing whitespace trimmed.
  	got, err := Generate(4, 2, '*')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	// y=0: x=0 -> (0&0)==0 filled.            indent 3 => "   *"
  	// y=1: x=0 (0&1)==0 filled; x=1 (1&1)=1 empty. indent 2 => "  * "
  	//      trailing trimmed => "  *"
  	// y=2: x=0 filled; x=1 (1&2)=0 filled; x=2 (2&2)=2 empty.
  	//      indent 1 => " * * " -> trimmed " * *"
  	// y=3: x=0 filled; x=1 (1&3)=1 empty; x=2 (2&3)=2 empty; x=3 (3&3)=3 empty.
  	//      indent 0 => "*     " -> trimmed "*"
  	want := []string{
  		"   *",
  		"  *",
  		" * *",
  		"*",
  	}
  	if !reflect.DeepEqual(got, want) {
  		t.Fatalf("got:\n%s\nwant:\n%s",
  			strings.Join(got, "\n"), strings.Join(want, "\n"))
  	}
  }

  func TestGenerateCustomChar(t *testing.T) {
  	got, err := Generate(1, 0, '#')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if got[0] != "#" {
  		t.Fatalf("got %q, want %q", got[0], "#")
  	}
  }

  func TestGenerateRejectsNegativeDepth(t *testing.T) {
  	_, err := Generate(8, -1, '*')
  	if err == nil {
  		t.Fatal("expected error for negative depth, got nil")
  	}
  }

  func TestGenerateRejectsZeroSize(t *testing.T) {
  	_, err := Generate(0, 2, '*')
  	if err == nil {
  		t.Fatal("expected error for non-positive size, got nil")
  	}
  }
  ```

- [ ] Run the test to see it fail (compilation failure because `Generate` does not exist):
  ```bash
  go test ./internal/sierpinski/
  ```
  Expected: failure mentioning `undefined: Generate`.

- [ ] Create `internal/sierpinski/sierpinski.go` to make it pass:
  ```go
  // Package sierpinski generates Sierpinski triangles as ASCII art.
  package sierpinski

  import (
  	"fmt"
  	"strings"
  )

  // Generate returns the rows of a Sierpinski triangle.
  //
  // depth controls resolution: the triangle has 2^depth rows.
  // size is the intended base width in characters; it is currently used
  // only for validation and future horizontal scaling. char is the rune
  // used for filled cells.
  //
  // A cell at column x, row y (x in 0..y) is filled when (x & y) == 0.
  // Each row is left-indented to form the triangular shape and has
  // trailing whitespace trimmed.
  func Generate(size, depth int, char rune) ([]string, error) {
  	if size <= 0 {
  		return nil, fmt.Errorf("size must be positive, got %d", size)
  	}
  	if depth < 0 {
  		return nil, fmt.Errorf("depth must be non-negative, got %d", depth)
  	}

  	n := 1 << depth // 2^depth rows
  	rows := make([]string, 0, n)

  	for y := 0; y < n; y++ {
  		var b strings.Builder
  		// Leading indent to center the row within the triangle.
  		for i := 0; i < n-1-y; i++ {
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
  		rows = append(rows, strings.TrimRight(b.String(), " "))
  	}
  	return rows, nil
  }
  ```

- [ ] Run the test to see it pass:
  ```bash
  go test ./internal/sierpinski/
  ```
  Expected: `ok  github.com/example/fractals/internal/sierpinski`

- [ ] Vet the package:
  ```bash
  go vet ./internal/sierpinski/
  ```
  Expected: no output.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add sierpinski algorithm package"
  ```

---

### Task 3: Mandelbrot algorithm package

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

Deliverable: a pure `Generate` function rendering the Mandelbrot set over the standard view rectangle (real `-2.5..1.0`, imaginary `-1.0..1.0`). For each pixel we compute escape iterations and map to a character.

Mapping rule:
- If a custom `char` (non-zero rune) is provided: filled (in-set / high iteration) cells use that char, escaped cells use a space.
- If `char == 0` (gradient mode): map iteration count to the gradient `" .:-=+*#%@"`. Points that never escape map to the last gradient char `@`. Escaped points map proportionally: index = `iter * (len(gradient)-1) / maxIter`.

- [ ] Create the failing test file `internal/mandelbrot/mandelbrot_test.go`:
  ```go
  package mandelbrot

  import (
  	"strings"
  	"testing"
  )

  func TestGenerateDimensions(t *testing.T) {
  	rows, err := Generate(80, 24, 100, 0)
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 24 {
  		t.Fatalf("got %d rows, want 24", len(rows))
  	}
  	for i, r := range rows {
  		if len([]rune(r)) != 80 {
  			t.Fatalf("row %d has width %d, want 80", i, len([]rune(r)))
  		}
  	}
  }

  func TestGenerateGradientContainsSet(t *testing.T) {
  	// The center of the view (origin of complex plane, ~real 0, imag 0)
  	// is inside the set and must render as the densest gradient char '@'.
  	rows, err := Generate(80, 24, 100, 0)
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	joined := strings.Join(rows, "\n")
  	if !strings.ContainsRune(joined, '@') {
  		t.Fatalf("expected gradient output to contain '@' (in-set points)")
  	}
  	if !strings.ContainsRune(joined, ' ') {
  		t.Fatalf("expected gradient output to contain ' ' (escaped points)")
  	}
  }

  func TestGenerateCustomChar(t *testing.T) {
  	rows, err := Generate(40, 20, 100, '#')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	joined := strings.Join(rows, "")
  	// Custom-char mode uses only the char and spaces.
  	for _, r := range joined {
  		if r != '#' && r != ' ' {
  			t.Fatalf("unexpected rune %q in custom-char output", r)
  		}
  	}
  	if !strings.ContainsRune(strings.Join(rows, ""), '#') {
  		t.Fatalf("expected at least one '#' in output")
  	}
  }

  func TestGenerateRejectsBadWidth(t *testing.T) {
  	if _, err := Generate(0, 24, 100, 0); err == nil {
  		t.Fatal("expected error for non-positive width")
  	}
  }

  func TestGenerateRejectsBadHeight(t *testing.T) {
  	if _, err := Generate(80, 0, 100, 0); err == nil {
  		t.Fatal("expected error for non-positive height")
  	}
  }

  func TestGenerateRejectsBadIterations(t *testing.T) {
  	if _, err := Generate(80, 24, 0, 0); err == nil {
  		t.Fatal("expected error for non-positive iterations")
  	}
  }
  ```

- [ ] Run the test to see it fail:
  ```bash
  go test ./internal/mandelbrot/
  ```
  Expected: failure mentioning `undefined: Generate`.

- [ ] Create `internal/mandelbrot/mandelbrot.go`:
  ```go
  // Package mandelbrot renders the Mandelbrot set as ASCII art.
  package mandelbrot

  import (
  	"fmt"
  	"strings"
  )

  // gradient maps increasing density to increasingly heavy characters.
  const gradient = " .:-=+*#%@"

  // View bounds for the complex plane.
  const (
  	realMin = -2.5
  	realMax = 1.0
  	imagMin = -1.0
  	imagMax = 1.0
  )

  // Generate renders the Mandelbrot set into height rows of width runes.
  //
  // maxIter is the escape-iteration cap. If char is non-zero, in-set points
  // render as char and escaped points as spaces. If char is zero, output
  // uses the gradient " .:-=+*#%@".
  func Generate(width, height, maxIter int, char rune) ([]string, error) {
  	if width <= 0 {
  		return nil, fmt.Errorf("width must be positive, got %d", width)
  	}
  	if height <= 0 {
  		return nil, fmt.Errorf("height must be positive, got %d", height)
  	}
  	if maxIter <= 0 {
  		return nil, fmt.Errorf("iterations must be positive, got %d", maxIter)
  	}

  	rows := make([]string, 0, height)
  	for py := 0; py < height; py++ {
  		var b strings.Builder
  		ci := imagMin + (imagMax-imagMin)*float64(py)/float64(height-1)
  		if height == 1 {
  			ci = (imagMin + imagMax) / 2
  		}
  		for px := 0; px < width; px++ {
  			cr := realMin + (realMax-realMin)*float64(px)/float64(width-1)
  			if width == 1 {
  				cr = (realMin + realMax) / 2
  			}
  			iter := escape(cr, ci, maxIter)
  			b.WriteRune(cell(iter, maxIter, char))
  		}
  		rows = append(rows, b.String())
  	}
  	return rows, nil
  }

  // escape returns the number of iterations before the orbit of c escapes
  // the radius-2 disk, capped at maxIter.
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

  // cell maps an iteration count to a display rune.
  func cell(iter, maxIter int, char rune) rune {
  	inSet := iter >= maxIter
  	if char != 0 {
  		if inSet {
  			return char
  		}
  		return ' '
  	}
  	if inSet {
  		return rune(gradient[len(gradient)-1])
  	}
  	idx := iter * (len(gradient) - 1) / maxIter
  	if idx >= len(gradient) {
  		idx = len(gradient) - 1
  	}
  	return rune(gradient[idx])
  }
  ```

- [ ] Run the test to see it pass:
  ```bash
  go test ./internal/mandelbrot/
  ```
  Expected: `ok  github.com/example/fractals/internal/mandelbrot`

- [ ] Vet the package:
  ```bash
  go vet ./internal/mandelbrot/
  ```
  Expected: no output.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add mandelbrot algorithm package"
  ```

---

### Task 4: CLI root command

**Files:** `internal/cli/root.go`, `internal/cli/root_test.go`

Deliverable: a root cobra command with help text and an `Execute()` entry point. Subcommands are attached in later tasks via a shared `rootCmd`. We expose a helper to build a fresh command tree for testing so tests don't share global state.

- [ ] Create the failing test `internal/cli/root_test.go`:
  ```go
  package cli

  import (
  	"bytes"
  	"strings"
  	"testing"
  )

  func TestRootHelp(t *testing.T) {
  	cmd := NewRootCmd()
  	var out bytes.Buffer
  	cmd.SetOut(&out)
  	cmd.SetErr(&out)
  	cmd.SetArgs([]string{"--help"})
  	if err := cmd.Execute(); err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	got := out.String()
  	if !strings.Contains(got, "fractals") {
  		t.Fatalf("help output missing program name; got:\n%s", got)
  	}
  	if !strings.Contains(got, "Usage:") {
  		t.Fatalf("help output missing Usage section; got:\n%s", got)
  	}
  }

  func TestRootListsSubcommands(t *testing.T) {
  	cmd := NewRootCmd()
  	var out bytes.Buffer
  	cmd.SetOut(&out)
  	cmd.SetErr(&out)
  	cmd.SetArgs([]string{"--help"})
  	if err := cmd.Execute(); err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	got := out.String()
  	for _, sub := range []string{"sierpinski", "mandelbrot"} {
  		if !strings.Contains(got, sub) {
  			t.Fatalf("help output missing subcommand %q; got:\n%s", sub, got)
  		}
  	}
  }
  ```

- [ ] Run the test to see it fail:
  ```bash
  go test ./internal/cli/
  ```
  Expected: failure mentioning `undefined: NewRootCmd`.

- [ ] Create `internal/cli/root.go`:
  ```go
  // Package cli wires the fractal algorithms to cobra commands.
  package cli

  import (
  	"github.com/spf13/cobra"
  )

  // NewRootCmd builds the root command with all subcommands attached.
  // A fresh tree is returned each call so tests do not share state.
  func NewRootCmd() *cobra.Command {
  	root := &cobra.Command{
  		Use:   "fractals",
  		Short: "Generate ASCII art fractals",
  		Long: "fractals generates ASCII art fractals.\n\n" +
  			"Supported fractals: sierpinski, mandelbrot.",
  		SilenceUsage: true,
  	}
  	root.AddCommand(newSierpinskiCmd())
  	root.AddCommand(newMandelbrotCmd())
  	return root
  }

  // Execute runs the root command against os.Args and returns its error.
  func Execute() error {
  	return NewRootCmd().Execute()
  }
  ```

  > Note: `newSierpinskiCmd` and `newMandelbrotCmd` do not exist yet, so this will not compile until Tasks 5 and 6 add them. To keep this task independently green, add temporary stubs now and replace them in the next tasks.

- [ ] Add temporary stub commands at the bottom of `internal/cli/root.go` (these will be **moved into their own files and fleshed out** in Tasks 5 and 6):
  ```go
  // Temporary stubs replaced in later tasks.
  func newSierpinskiCmd() *cobra.Command {
  	return &cobra.Command{Use: "sierpinski", Short: "Generate a Sierpinski triangle"}
  }

  func newMandelbrotCmd() *cobra.Command {
  	return &cobra.Command{Use: "mandelbrot", Short: "Render the Mandelbrot set"}
  }
  ```

- [ ] Run the test to see it pass:
  ```bash
  go test ./internal/cli/
  ```
  Expected: `ok  github.com/example/fractals/internal/cli`

- [ ] Vet:
  ```bash
  go vet ./internal/cli/
  ```
  Expected: no output.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add CLI root command with subcommand stubs"
  ```

---

### Task 5: Sierpinski subcommand

**Files:** `internal/cli/sierpinski.go` (new), `internal/cli/root.go` (remove stub), `internal/cli/sierpinski_test.go` (new)

Deliverable: a working `sierpinski` subcommand with `--size`, `--depth`, `--char` flags that calls `sierpinski.Generate` and prints rows. Replaces the stub from Task 4.

- [ ] Remove the `newSierpinskiCmd` stub from `internal/cli/root.go`. Open the file and delete this block:
  ```go
  func newSierpinskiCmd() *cobra.Command {
  	return &cobra.Command{Use: "sierpinski", Short: "Generate a Sierpinski triangle"}
  }
  ```
  Leave the `newMandelbrotCmd` stub in place for now.

- [ ] Create the failing test `internal/cli/sierpinski_test.go`:
  ```go
  package cli

  import (
  	"bytes"
  	"strings"
  	"testing"
  )

  func runCmd(t *testing.T, args ...string) (string, error) {
  	t.Helper()
  	cmd := NewRootCmd()
  	var out bytes.Buffer
  	cmd.SetOut(&out)
  	cmd.SetErr(&out)
  	cmd.SetArgs(args)
  	err := cmd.Execute()
  	return out.String(), err
  }

  func TestSierpinskiDefault(t *testing.T) {
  	out, err := runCmd(t, "sierpinski", "--depth", "2", "--size", "4")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 4 {
  		t.Fatalf("expected 4 lines, got %d:\n%s", len(lines), out)
  	}
  	if !strings.Contains(out, "*") {
  		t.Fatalf("expected '*' in output:\n%s", out)
  	}
  }

  func TestSierpinskiCustomChar(t *testing.T) {
  	out, err := runCmd(t, "sierpinski", "--depth", "1", "--size", "2", "--char", "#")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(out, "#") {
  		t.Fatalf("expected '#' in output:\n%s", out)
  	}
  	if strings.Contains(out, "*") {
  		t.Fatalf("did not expect default '*' when custom char set:\n%s", out)
  	}
  }

  func TestSierpinskiRejectsMultiRuneChar(t *testing.T) {
  	_, err := runCmd(t, "sierpinski", "--char", "ab")
  	if err == nil {
  		t.Fatal("expected error for multi-rune --char")
  	}
  }

  func TestSierpinskiRejectsNegativeDepth(t *testing.T) {
  	_, err := runCmd(t, "sierpinski", "--depth", "-1")
  	if err == nil {
  		t.Fatal("expected error for negative depth")
  	}
  }
  ```

- [ ] Run the test to see it fail (the stub command ignores flags and prints nothing, so `TestSierpinskiDefault` fails on line count, and `newSierpinskiCmd` is now undefined after stub removal):
  ```bash
  go test ./internal/cli/
  ```
  Expected: failure mentioning `undefined: newSierpinskiCmd`.

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
  		size    int
  		depth   int
  		charStr string
  	)

  	cmd := &cobra.Command{
  		Use:   "sierpinski",
  		Short: "Generate a Sierpinski triangle",
  		Long:  "Generate a Sierpinski triangle using recursive subdivision.",
  		RunE: func(cmd *cobra.Command, args []string) error {
  			char, err := singleRune(charStr)
  			if err != nil {
  				return err
  			}
  			rows, err := sierpinski.Generate(size, depth, char)
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
  	cmd.Flags().StringVar(&charStr, "char", "*", "character to use for filled points")
  	return cmd
  }

  // singleRune validates that s is exactly one rune and returns it.
  func singleRune(s string) (rune, error) {
  	runes := []rune(s)
  	if len(runes) != 1 {
  		return 0, fmt.Errorf("--char must be exactly one character, got %q", s)
  	}
  	return runes[0], nil
  }
  ```

- [ ] Run the test to see it pass:
  ```bash
  go test ./internal/cli/
  ```
  Expected: `ok  github.com/example/fractals/internal/cli`

- [ ] Vet:
  ```bash
  go vet ./internal/cli/
  ```
  Expected: no output.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Implement sierpinski subcommand"
  ```

---

### Task 6: Mandelbrot subcommand and wired entry point

**Files:** `internal/cli/mandelbrot.go` (new), `internal/cli/root.go` (remove stub), `internal/cli/mandelbrot_test.go` (new), `cmd/fractals/main.go` (rewrite)

Deliverable: a working `mandelbrot` subcommand and a `main.go` that runs the real CLI. The `--char` flag is optional here: when unset, gradient mode is used (rune `0`); when set, it must be a single rune.

- [ ] Remove the `newMandelbrotCmd` stub from `internal/cli/root.go`. Delete this block:
  ```go
  func newMandelbrotCmd() *cobra.Command {
  	return &cobra.Command{Use: "mandelbrot", Short: "Render the Mandelbrot set"}
  }
  ```
  Also remove the now-orphaned comment line `// Temporary stubs replaced in later tasks.` if it remains.

- [ ] Create the failing test `internal/cli/mandelbrot_test.go`:
  ```go
  package cli

  import (
  	"strings"
  	"testing"
  )

  func TestMandelbrotDefaultDimensions(t *testing.T) {
  	out, err := runCmd(t, "mandelbrot", "--width", "40", "--height", "12")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 12 {
  		t.Fatalf("expected 12 lines, got %d:\n%s", len(lines), out)
  	}
  	for i, l := range lines {
  		if len([]rune(l)) != 40 {
  			t.Fatalf("line %d width %d, want 40", i, len([]rune(l)))
  		}
  	}
  }

  func TestMandelbrotGradientByDefault(t *testing.T) {
  	out, err := runCmd(t, "mandelbrot", "--width", "60", "--height", "20")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.ContainsRune(out, '@') {
  		t.Fatalf("expected gradient '@' in default output:\n%s", out)
  	}
  }

  func TestMandelbrotCustomChar(t *testing.T) {
  	out, err := runCmd(t, "mandelbrot", "--width", "40", "--height", "12", "--char", "#")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.ContainsRune(out, '#') {
  		t.Fatalf("expected '#' in custom output:\n%s", out)
  	}
  	if strings.ContainsRune(out, '@') {
  		t.Fatalf("did not expect gradient '@' with custom char:\n%s", out)
  	}
  }

  func TestMandelbrotRejectsMultiRuneChar(t *testing.T) {
  	_, err := runCmd(t, "mandelbrot", "--char", "ab")
  	if err == nil {
  		t.Fatal("expected error for multi-rune --char")
  	}
  }

  func TestMandelbrotRejectsZeroWidth(t *testing.T) {
  	_, err := runCmd(t, "mandelbrot", "--width", "0")
  	if err == nil {
  		t.Fatal("expected error for zero width")
  	}
  }
  ```

- [ ] Run the test to see it fail:
  ```bash
  go test ./internal/cli/
  ```
  Expected: failure mentioning `undefined: newMandelbrotCmd`.

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
  		charStr    string
  	)

  	cmd := &cobra.Command{
  		Use:   "mandelbrot",
  		Short: "Render the M