# Go Fractals CLI - Implementation Plan

## Global Constraints

- Go 1.21+ required (set in `go.mod` as `go 1.21`)
- CLI library: `github.com/spf13/cobra` (only third-party dependency)
- Module path: `github.com/example/fractals`
- Binary name: `fractals`
- Sierpinski default char: `'*'`
- Mandelbrot default gradient: `" .:-=+*#%@"` (10 chars, index 0 = least iterations escaped / in-set, index 9 = escaped fastest — see Task 3 for exact mapping)
- All output to stdout, one row per line, each line terminated by `\n`
- Invalid inputs produce clear error messages and a non-zero exit code

## File Structure

| File | Responsibility |
|------|----------------|
| `go.mod` | Module definition, Go version, cobra dependency |
| `internal/sierpinski/sierpinski.go` | Pure Sierpinski triangle generation algorithm |
| `internal/sierpinski/sierpinski_test.go` | Tests for Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure Mandelbrot rendering algorithm |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for Mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command + help wiring + Execute |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand: flag parsing, validation, calls algorithm |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand: flag parsing, validation, calls algorithm |
| `internal/cli/root_test.go` | Tests for CLI wiring, flags, validation, output |
| `cmd/fractals/main.go` | Entry point; calls `cli.Execute()` |

---

### Task 1: Project scaffolding and module setup

**Files:** `go.mod`, `cmd/fractals/main.go`

**Interfaces:**
- Consumes: nothing.
- Produces: module `github.com/example/fractals`; `main.go` calls `cli.Execute()` (defined in Task 4). For this task `main.go` will temporarily print a placeholder so it compiles standalone; Task 4 replaces the body.

Steps:

- [ ] Initialize the module:
  ```bash
  go mod init github.com/example/fractals
  ```
  Expected output:
  ```
  go: creating new go.mod: module github.com/example/fractals
  ```

- [ ] Edit `go.mod` to pin the Go version. It should read exactly:
  ```
  module github.com/example/fractals

  go 1.21
  ```

- [ ] Create `cmd/fractals/main.go` with a temporary body (replaced in Task 4):
  ```go
  package main

  import "fmt"

  func main() {
  	fmt.Println("fractals: not yet wired")
  }
  ```

- [ ] Verify it builds and runs:
  ```bash
  go build ./... && go run ./cmd/fractals
  ```
  Expected output:
  ```
  fractals: not yet wired
  ```

- [ ] Commit:
  ```bash
  git add go.mod cmd/fractals/main.go && git commit -m "Scaffold module and entry point"
  ```

---

### Task 2: Sierpinski algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

**Interfaces:**
- Consumes: nothing.
- Produces:
  ```go
  // Generate returns the Sierpinski triangle as a slice of strings (one per row).
  // size is the width of the triangle base in characters (>= 1).
  // depth is the recursion depth (>= 0).
  // char is the rune printed at filled points.
  // Returns an error if size < 1 or depth < 0.
  func Generate(size, depth int, char rune) ([]string, error)
  ```
  Algorithm: a point (row r, col c) within a triangle of height `size` is filled when, using the bitwise rule limited by depth, `(xBit & yBit) == 0` for the relevant bits. We use the classic bitwise AND rule: cell `(r, c)` is filled if `(c & (size-1-r... ))`. To keep it deterministic and testable, use the rule below.

Steps:

- [ ] Write the failing test file `internal/sierpinski/sierpinski_test.go`:
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
  	// Bitwise Sierpinski: cell (r,c) filled when (c & r) == 0.
  	// Row 0: c=0,1,2,3 -> (c&0)==0 always -> all filled.
  	if rows[0] != "****" {
  		t.Errorf("row 0 = %q, want %q", rows[0], "****")
  	}
  	// Row 1: r=1 -> c&1==0 for c=0,2 -> filled at 0,2.
  	if rows[1] != "* * " {
  		t.Errorf("row 1 = %q, want %q", rows[1], "* * ")
  	}
  	// Row 3: r=3 -> c&3==0 only for c=0.
  	if rows[3] != "*   " {
  		t.Errorf("row 3 = %q, want %q", rows[3], "*   ")
  	}
  }

  func TestGenerateCustomChar(t *testing.T) {
  	rows, err := Generate(2, 1, '#')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(rows[0], "#") {
  		t.Errorf("expected '#' in output, got %q", rows[0])
  	}
  	if strings.Contains(rows[0], "*") {
  		t.Errorf("did not expect '*' in output, got %q", rows[0])
  	}
  }

  func TestGenerateInvalidSize(t *testing.T) {
  	if _, err := Generate(0, 5, '*'); err == nil {
  		t.Error("expected error for size 0, got nil")
  	}
  }

  func TestGenerateInvalidDepth(t *testing.T) {
  	if _, err := Generate(4, -1, '*'); err == nil {
  		t.Error("expected error for depth -1, got nil")
  	}
  }
  ```

- [ ] Run it to see it fail (no implementation yet):
  ```bash
  go test ./internal/sierpinski/
  ```
  Expected: compile error / `undefined: Generate`.

- [ ] Implement `internal/sierpinski/sierpinski.go`:
  ```go
  // Package sierpinski generates Sierpinski triangles as ASCII art.
  package sierpinski

  import (
  	"errors"
  	"strings"
  )

  // Generate returns the Sierpinski triangle as a slice of strings (one per row).
  //
  // size is the width of the triangle base in characters (must be >= 1).
  // depth bounds the recursion; it limits the number of low-order bits considered.
  // char is the rune printed at filled points; unfilled points are spaces.
  func Generate(size, depth int, char rune) ([]string, error) {
  	if size < 1 {
  		return nil, errors.New("size must be at least 1")
  	}
  	if depth < 0 {
  		return nil, errors.New("depth must be at least 0")
  	}

  	// mask limits the bits considered to `depth` low-order bits.
  	// depth 0 -> mask 0 -> every cell filled (single solid triangle).
  	mask := (1 << uint(depth)) - 1

  	rows := make([]string, size)
  	for r := 0; r < size; r++ {
  		var b strings.Builder
  		b.Grow(size)
  		for c := 0; c < size; c++ {
  			if ((c & r) & mask) == 0 {
  				b.WriteRune(char)
  			} else {
  				b.WriteRune(' ')
  			}
  		}
  		rows[r] = b.String()
  	}
  	return rows, nil
  }
  ```

- [ ] Run the tests to see them pass:
  ```bash
  go test ./internal/sierpinski/
  ```
  Expected output:
  ```
  ok  	github.com/example/fractals/internal/sierpinski	0.00s
  ```

- [ ] Commit:
  ```bash
  git add internal/sierpinski && git commit -m "Add Sierpinski algorithm"
  ```

---

### Task 3: Mandelbrot algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

**Interfaces:**
- Consumes: nothing.
- Produces:
  ```go
  // DefaultGradient is the character ramp used when no single char is given.
  const DefaultGradient = " .:-=+*#%@"

  // Generate renders the Mandelbrot set as a slice of strings (one per row).
  // width, height are output dimensions in characters (each >= 1).
  // iterations is the escape iteration cap (>= 1).
  // gradient maps iteration counts to characters; must be non-empty.
  //   A point still in the set after `iterations` maps to gradient[0].
  //   A point that escapes immediately maps to gradient[last].
  // Returns an error if width<1, height<1, iterations<1, or gradient empty.
  func Generate(width, height, iterations int, gradient string) ([]string, error)
  ```
  Note: the CLI passes a single repeated char as a 1-rune gradient string; the algorithm needs no special single-char branch.

Steps:

- [ ] Write the failing test file `internal/mandelbrot/mandelbrot_test.go`:
  ```go
  package mandelbrot

  import "testing"

  func TestGenerateDimensions(t *testing.T) {
  	rows, err := Generate(20, 10, 50, DefaultGradient)
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

  func TestGenerateCenterInSet(t *testing.T) {
  	// The point near (-0.5, 0) is in the set and maps to gradient[0] (space).
  	rows, err := Generate(80, 24, 100, DefaultGradient)
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	// Center cell should be in-set -> gradient[0] which is ' '.
  	center := []rune(rows[12])[40]
  	if center != ' ' {
  		t.Errorf("center cell = %q, want ' ' (in-set)", center)
  	}
  }

  func TestGenerateSingleCharGradient(t *testing.T) {
  	rows, err := Generate(10, 5, 50, "#")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	for _, row := range rows {
  		for _, ch := range row {
  			if ch != '#' {
  				t.Fatalf("expected only '#', got %q", ch)
  			}
  		}
  	}
  }

  func TestGenerateInvalidWidth(t *testing.T) {
  	if _, err := Generate(0, 10, 50, DefaultGradient); err == nil {
  		t.Error("expected error for width 0")
  	}
  }

  func TestGenerateInvalidIterations(t *testing.T) {
  	if _, err := Generate(10, 10, 0, DefaultGradient); err == nil {
  		t.Error("expected error for iterations 0")
  	}
  }

  func TestGenerateEmptyGradient(t *testing.T) {
  	if _, err := Generate(10, 10, 50, ""); err == nil {
  		t.Error("expected error for empty gradient")
  	}
  }
  ```

- [ ] Run it to see it fail:
  ```bash
  go test ./internal/mandelbrot/
  ```
  Expected: `undefined: Generate` / `undefined: DefaultGradient`.

- [ ] Implement `internal/mandelbrot/mandelbrot.go`:
  ```go
  // Package mandelbrot renders the Mandelbrot set as ASCII art.
  package mandelbrot

  import (
  	"errors"
  	"strings"
  )

  // DefaultGradient is the character ramp used when no single char is given.
  // Index 0 represents points in the set; the last index represents fast escape.
  const DefaultGradient = " .:-=+*#%@"

  // Viewport bounds covering the classic Mandelbrot view.
  const (
  	minRe = -2.5
  	maxRe = 1.0
  	minIm = -1.25
  	maxIm = 1.25
  )

  // Generate renders the Mandelbrot set as a slice of strings (one per row).
  func Generate(width, height, iterations int, gradient string) ([]string, error) {
  	if width < 1 {
  		return nil, errors.New("width must be at least 1")
  	}
  	if height < 1 {
  		return nil, errors.New("height must be at least 1")
  	}
  	if iterations < 1 {
  		return nil, errors.New("iterations must be at least 1")
  	}
  	if len(gradient) == 0 {
  		return nil, errors.New("gradient must be non-empty")
  	}

  	ramp := []rune(gradient)
  	rows := make([]string, height)

  	for y := 0; y < height; y++ {
  		var b strings.Builder
  		b.Grow(width)
  		ci := minIm + (maxIm-minIm)*float64(y)/float64(height-1)
  		if height == 1 {
  			ci = (minIm + maxIm) / 2
  		}
  		for x := 0; x < width; x++ {
  			cr := minRe + (maxRe-minRe)*float64(x)/float64(width-1)
  			if width == 1 {
  				cr = (minRe + maxRe) / 2
  			}
  			n := escape(cr, ci, iterations)
  			b.WriteRune(rampChar(ramp, n, iterations))
  		}
  		rows[y] = b.String()
  	}
  	return rows, nil
  }

  // escape returns the iteration count at which z escapes |z|>2, or iterations
  // if it never escapes within the cap.
  func escape(cr, ci float64, iterations int) int {
  	var zr, zi float64
  	for n := 0; n < iterations; n++ {
  		zr2, zi2 := zr*zr, zi*zi
  		if zr2+zi2 > 4 {
  			return n
  		}
  		zi = 2*zr*zi + ci
  		zr = zr2 - zi2 + cr
  	}
  	return iterations
  }

  // rampChar maps an escape count to a gradient rune.
  // n == iterations (in-set) -> ramp[0]; faster escape -> later ramp entries.
  func rampChar(ramp []rune, n, iterations int) rune {
  	if n >= iterations {
  		return ramp[0]
  	}
  	// Map n in [0, iterations) to ramp index in [len-1 .. 1].
  	// Fast escape (small n) -> high index; slow escape -> low index.
  	idx := len(ramp) - 1 - (n*(len(ramp)-1))/iterations
  	if idx < 0 {
  		idx = 0
  	}
  	if idx > len(ramp)-1 {
  		idx = len(ramp) - 1
  	}
  	return ramp[idx]
  }
  ```

- [ ] Run the tests to see them pass:
  ```bash
  go test ./internal/mandelbrot/
  ```
  Expected output:
  ```
  ok  	github.com/example/fractals/internal/mandelbrot	0.00s
  ```

- [ ] Commit:
  ```bash
  git add internal/mandelbrot && git commit -m "Add Mandelbrot algorithm"
  ```

---

### Task 4: CLI wiring (root + subcommands)

**Files:** `internal/cli/root.go`, `internal/cli/sierpinski.go`, `internal/cli/mandelbrot.go`, `internal/cli/root_test.go`, `cmd/fractals/main.go` (rewrite)

**Interfaces:**
- Consumes:
  - `sierpinski.Generate(size, depth int, char rune) ([]string, error)`
  - `mandelbrot.Generate(width, height, iterations int, gradient string) ([]string, error)`
  - `mandelbrot.DefaultGradient` (string constant)
- Produces:
  ```go
  // Execute runs the root command against os.Args; returns process exit error.
  func Execute() error

  // NewRootCmd builds the root *cobra.Command with subcommands attached.
  // Output is written to the command's configured out/err writers, enabling tests.
  func NewRootCmd() *cobra.Command
  ```

Steps:

- [ ] Add the cobra dependency:
  ```bash
  go get github.com/spf13/cobra@latest
  ```
  Expected: `go.mod`/`go.sum` updated; output mentions `github.com/spf13/cobra`.

- [ ] Write the failing test file `internal/cli/root_test.go`:
  ```go
  package cli

  import (
  	"bytes"
  	"strings"
  	"testing"
  )

  // run executes the root command with args and captures stdout+stderr.
  func run(args ...string) (string, error) {
  	cmd := NewRootCmd()
  	var out bytes.Buffer
  	cmd.SetOut(&out)
  	cmd.SetErr(&out)
  	cmd.SetArgs(args)
  	err := cmd.Execute()
  	return out.String(), err
  }

  func TestHelp(t *testing.T) {
  	out, err := run("--help")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(out, "sierpinski") || !strings.Contains(out, "mandelbrot") {
  		t.Errorf("help missing subcommands: %q", out)
  	}
  }

  func TestSierpinskiDefault(t *testing.T) {
  	out, err := run("sierpinski")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 32 {
  		t.Errorf("expected 32 rows, got %d", len(lines))
  	}
  	if !strings.Contains(out, "*") {
  		t.Errorf("expected '*' in output")
  	}
  }

  func TestSierpinskiFlags(t *testing.T) {
  	out, err := run("sierpinski", "--size", "8", "--depth", "3", "--char", "#")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 8 {
  		t.Errorf("expected 8 rows, got %d", len(lines))
  	}
  	if strings.Contains(out, "*") {
  		t.Errorf("did not expect '*', got %q", out)
  	}
  	if !strings.Contains(out, "#") {
  		t.Errorf("expected '#'")
  	}
  }

  func TestSierpinskiInvalidSize(t *testing.T) {
  	_, err := run("sierpinski", "--size", "0")
  	if err == nil {
  		t.Error("expected error for size 0")
  	}
  }

  func TestSierpinskiInvalidChar(t *testing.T) {
  	_, err := run("sierpinski", "--char", "ab")
  	if err == nil {
  		t.Error("expected error for multi-rune char")
  	}
  }

  func TestMandelbrotDefault(t *testing.T) {
  	out, err := run("mandelbrot")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 24 {
  		t.Errorf("expected 24 rows, got %d", len(lines))
  	}
  	if len([]rune(lines[0])) != 80 {
  		t.Errorf("expected width 80, got %d", len([]rune(lines[0])))
  	}
  }

  func TestMandelbrotFlags(t *testing.T) {
  	out, err := run("mandelbrot", "--width", "40", "--height", "12", "--iterations", "50", "--char", "@")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 12 {
  		t.Errorf("expected 12 rows, got %d", len(lines))
  	}
  	if len([]rune(lines[0])) != 40 {
  		t.Errorf("expected width 40, got %d", len([]rune(lines[0])))
  	}
  	for _, ch := range lines[0] {
  		if ch != '@' {
  			t.Fatalf("expected only '@', got %q", ch)
  		}
  	}
  }

  func TestMandelbrotInvalidWidth(t *testing.T) {
  	_, err := run("mandelbrot", "--width", "0")
  	if err == nil {
  		t.Error("expected error for width 0")
  	}
  }
  ```

- [ ] Run it to see it fail:
  ```bash
  go test ./internal/cli/
  ```
  Expected: `undefined: NewRootCmd`.

- [ ] Implement `internal/cli/root.go`:
  ```go
  // Package cli wires the fractals command-line interface.
  package cli

  import (
  	"github.com/spf13/cobra"
  )

  // NewRootCmd builds the root command with all subcommands attached.
  func NewRootCmd() *cobra.Command {
  	root := &cobra.Command{
  		Use:           "fractals",
  		Short:         "Generate ASCII art fractals",
  		Long:          "fractals generates ASCII art fractals (Sierpinski triangle, Mandelbrot set).",
  		SilenceUsage:  true,
  		SilenceErrors: true,
  	}
  	root.AddCommand(newSierpinskiCmd())
  	root.AddCommand(newMandelbrotCmd())
  	return root
  }

  // Execute runs the root command against os.Args.
  func Execute() error {
  	return NewRootCmd().Execute()
  }
  ```

- [ ] Implement `internal/cli/sierpinski.go`:
  ```go
  package cli

  import (
  	"errors"
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
  			r, err := singleRune(char)
  			if err != nil {
  				return err
  			}
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

  // singleRune validates that s is exactly one rune and returns it.
  func singleRune(s string) (rune, error) {
  	runes := []rune(s)
  	if len(runes) != 1 {
  		return 0, errors.New("--char must be exactly one character")
  	}
  	return runes[0], nil
  }
  ```

- [ ] Implement `internal/cli/mandelbrot.go`:
  ```go
  package cli

  import (
  	"fmt"
  	"strings"

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
  				r, err := singleRune(char)
  				if err != nil {
  					return err
  				}
  				gradient = string(r)
  			}
  			rows, err := mandelbrot.Generate(width, height, iterations, gradient)
  			if err != nil {
  				return err
  			}
  			fmt.Fprint(cmd.OutOrStdout(), strings.Join(rows, "\n"))
  			fmt.Fprintln(cmd.OutOrStdout())
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

- [ ] Rewrite `cmd/fractals/main.go`:
  ```go
  package main

  import (
  	"fmt"
  	"os"

  	"github.com/example/fractals/internal/cli"
  )

  func main() {
  	if err := cli.Execute(); err != nil {
  		fmt.Fprintln(os.Stderr, "Error:", err)
  		os.Exit(1)
  	}
  }
  ```

- [ ] Run the CLI tests to see them pass:
  ```bash
  go test ./internal/cli/
  ```
  Expected output:
  ```
  ok  	github.com/example/fractals/internal/cli	0.0Xs
  ```

- [ ] Tidy modules:
  ```bash
  go mod tidy
  ```
  Expected: no errors; `go.sum` populated.

- [ ] Commit:
  ```bash
  git add go.mod go.sum internal/cli cmd/fractals/main.go && git commit -m "Wire CLI with cobra subcommands"
  ```

---

### Task 5: Full build, smoke test, and acceptance verification

**Files:** none changed (verification only).

**Interfaces:**
- Consumes: `cli.Execute` via the built binary.
- Produces: nothing.

Steps:

- [ ] Run the entire test suite:
  ```bash
  go test ./...
  ```
  Expected output (three `ok` lines):
  ```
  ok  	github.com/example/fractals/internal/cli	0.0Xs
  ok  	github.com/example/fractals/internal/mandelbrot	0.0Xs
  ok  	github.com/example/fractals/internal/sierpinski	0.0Xs
  ```

- [ ] Build the binary:
  ```bash
  go build -o fractals ./cmd/fractals
  ```
  Expected: no output, `fractals` binary created.

- [ ] Acceptance 1 — help:
  ```bash
  ./fractals --help
  ```
  Expected: usage text listing `sierpinski` and `mandelbrot`.

- [ ] Acceptance 2 — default Sierpinski triangle:
  ```bash
  ./fractals sierpinski
  ```
  Expected: 32 rows of a recognizable triangle of `*` characters.

- [ ] Acceptance 3 — default Mandelbrot:
  ```bash
  ./fractals mandelbrot
  ```
  Expected: 80×24 block with an in-set void (spaces) surrounded by gradient characters.

- [ ] Acceptance 5 — custom char:
  ```bash
  ./fractals sierpinski --size 16 --char '#'
  ```
  Expected: 16-row triangle drawn with `#`.

- [ ] Acceptance 6 — invalid input exits non-zero with a clear message:
  ```bash
  ./fractals sierpinski --size 0; echo "exit=$?"
  ```
  Expected:
  ```
  Error: size must be at least 1
  exit=1
  ```

- [ ] Subcommand help:
  ```bash
  ./fractals sierpinski --help
  ```
  Expected: lists `--size`, `--depth`, `--char` flags with defaults.

- [ ] Remove the build artifact (avoid committing a binary):
  ```bash
  rm -f fractals
  ```

- [ ] Commit any housekeeping (e.g., a `.gitignore` if you add one) — otherwise nothing to commit. To add a `.gitignore`:
  ```bash
  printf '/fractals\n' > .gitignore
  git add .gitignore && git commit -m "Ignore built binary"
  ```

---

## Self-Review

**Spec coverage:**
- Two fractal types — Tasks 2, 3. ✓
- `sierpinski` flags `--size`/`--depth`/`--char` with defaults 32/5/`*` — Task 4 `sierpinski.go`. ✓
- `mandelbrot` flags `--width`/`--height`/`--iterations`/`--char` with defaults 80/24/100/gradient — Task 4 `mandelbrot.go`. ✓
- Gradient `" .:-=+*#%@"` — Task 3 `DefaultGradient`. ✓
- `--help` for root and subcommands — cobra built-in; tested in Task 4, verified Task 5. ✓
- Invalid inputs → clear errors + non-zero exit — algorithms return errors; `main.go` prints `Error:` and exits 1; tested Tasks 2–4, verified Task 5. ✓
- Architecture file layout matches spec exactly. ✓ (Added `root_test.go` for CLI tests — consistent with `*_test.go` convention; spec's tree omits it but acceptance criterion 7 requires tests.)
- Go 1.21+, cobra only — Tasks 1, 4. ✓
- All 7 acceptance criteria exercised in Task 5. ✓

**Placeholder scan:** The only intentional placeholder is `main.go` in Task 1 (`"fractals: not yet wired"`), explicitly replaced in Task 4. No other placeholders, TODOs, or stub returns remain.

**Type consistency:**
- `sierpinski.Generate(size, depth int, char rune) ([]string, error)` — produced Task 2, consumed Task 4 (passes `int, int, rune`). ✓
- `mandelbrot.Generate(width, height, iterations int, gradient string) ([]string, error)` — produced Task 3, consumed Task 4 (passes `int, int, int, string`). ✓ CLI converts single `--char` rune to a 1-rune string before calling, matching the `gradient string` parameter. ✓
- `mandelbrot.DefaultGradient` (untyped string const) — produced Task 3, consumed Task 4. ✓
- `singleRune(string) (rune, error)` defined once in `sierpinski.go`, reused by `mandelbrot.go` (same package `cli`) — DRY. ✓
- `NewRootCmd() *cobra.Command` / `Execute() error` — produced Task 4, consumed by `main.go` and tests. ✓

**Edge cases handled:** width/height/size == 1 (division-by-zero guarded in Mandelbrot via `width==1`/`height==1` branches); depth 0 (mask 0 → solid triangle); empty `--char` for mandelbrot means "use gradient" (intended), but for sierpinski `--char ""` yields a multi/zero-rune error via `singleRune`. ✓