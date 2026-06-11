# Go Fractals CLI - Implementation Plan

## Global Constraints

- Go 1.21+ (set `go 1.21` in `go.mod`)
- CLI framework: `github.com/spf13/cobra`
- Binary name: `fractals`
- Module path: `github.com/example/fractals`
- Sierpinski defaults: `--size 32`, `--depth 5`, `--char '*'`
- Mandelbrot defaults: `--width 80`, `--height 24`, `--iterations 100`, `--char` gradient `" .:-=+*#%@"`
- Invalid inputs must produce clear error messages (non-zero exit, message to stderr)

## File Structure

| File | Responsibility |
|------|----------------|
| `go.mod` | Module definition, Go version, cobra dependency |
| `internal/sierpinski/sierpinski.go` | Sierpinski triangle generation algorithm |
| `internal/sierpinski/sierpinski_test.go` | Tests for sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Mandelbrot set rendering algorithm |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command + help |
| `internal/cli/sierpinski.go` | Sierpinski subcommand wiring |
| `internal/cli/mandelbrot.go` | Mandelbrot subcommand wiring |
| `internal/cli/cli_test.go` | Integration tests executing commands |
| `cmd/fractals/main.go` | Entry point calling cli.Execute |

---

### Task 1: Project scaffolding and module setup

**Files:** `go.mod`, `cmd/fractals/main.go`

**Interfaces:**
- Consumes: nothing
- Produces: `package main` in `cmd/fractals/main.go` calling `cli.Execute() error`; module `github.com/example/fractals` with Go 1.21 and cobra dependency

Steps:

- [ ] Initialize the module:
  ```bash
  go mod init github.com/example/fractals
  ```
  Expected: creates `go.mod` containing `module github.com/example/fractals` and `go 1.21` (or higher).

- [ ] Verify Go version line. Open `go.mod`; if it shows a version below `1.21`, edit it to read:
  ```
  go 1.21
  ```

- [ ] Add cobra dependency:
  ```bash
  go get github.com/spf13/cobra@latest
  ```
  Expected: `go.mod` now lists `github.com/spf13/cobra` under `require`.

- [ ] Create the entry point `cmd/fractals/main.go`:
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

- [ ] This will not yet build because `internal/cli` does not exist. Confirm the file is syntactically valid by formatting:
  ```bash
  gofmt -l cmd/fractals/main.go
  ```
  Expected: no output (file already formatted).

- [ ] Commit:
  ```bash
  git add go.mod go.sum cmd/fractals/main.go
  git commit -m "Scaffold module and entry point"
  ```

---

### Task 2: Sierpinski algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

**Interfaces:**
- Consumes: nothing
- Produces:
  ```go
  // Generate returns the rows of a Sierpinski triangle.
  // size is the triangle base width (number of rows = size).
  // depth controls recursion depth used to decide filled cells.
  // char is the fill character; empty cells are spaces.
  // Returns an error if size < 1 or depth < 0.
  func Generate(size, depth int, char rune) ([]string, error)
  ```

The fill rule uses the classic bitwise property: cell `(row, col)` is filled when `(row & col) == col`, masked by depth so only the first `2^depth` rows form the pattern within `size` rows.

Steps:

- [ ] Write the failing test `internal/sierpinski/sierpinski_test.go`:
  ```go
  package sierpinski

  import (
  	"strings"
  	"testing"
  )

  func TestGenerateRowCount(t *testing.T) {
  	rows, err := Generate(8, 3, '*')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 8 {
  		t.Fatalf("expected 8 rows, got %d", len(rows))
  	}
  }

  func TestGenerateTopRowSingleChar(t *testing.T) {
  	rows, err := Generate(8, 3, '*')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	// Top row has exactly one filled cell.
  	if got := strings.Count(rows[0], "*"); got != 1 {
  		t.Fatalf("expected 1 star in top row, got %d in %q", got, rows[0])
  	}
  }

  func TestGenerateBottomRowFull(t *testing.T) {
  	rows, err := Generate(8, 3, '*')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	// Bottom row (index size-1, all bits) is fully filled.
  	if got := strings.Count(rows[7], "*"); got != 8 {
  		t.Fatalf("expected 8 stars in bottom row, got %d in %q", got, rows[7])
  	}
  }

  func TestGenerateCustomChar(t *testing.T) {
  	rows, err := Generate(4, 2, '#')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(rows[0], "#") {
  		t.Fatalf("expected '#' in output, got %q", rows[0])
  	}
  }

  func TestGenerateInvalidSize(t *testing.T) {
  	if _, err := Generate(0, 3, '*'); err == nil {
  		t.Fatal("expected error for size 0")
  	}
  }

  func TestGenerateInvalidDepth(t *testing.T) {
  	if _, err := Generate(8, -1, '*'); err == nil {
  		t.Fatal("expected error for negative depth")
  	}
  }
  ```

- [ ] Run the test to see it fail (no implementation):
  ```bash
  go test ./internal/sierpinski/
  ```
  Expected: build/compile failure — `undefined: Generate`.

- [ ] Implement `internal/sierpinski/sierpinski.go`:
  ```go
  // Package sierpinski generates Sierpinski triangle ASCII art.
  package sierpinski

  import (
  	"fmt"
  	"strings"
  )

  // Generate returns the rows of a Sierpinski triangle.
  // The triangle has `size` rows; each cell (row, col) is filled when
  // (row & col) == col. depth limits how many leading rows participate
  // in the fractal pattern (first 2^depth rows).
  func Generate(size, depth int, char rune) ([]string, error) {
  	if size < 1 {
  		return nil, fmt.Errorf("size must be >= 1, got %d", size)
  	}
  	if depth < 0 {
  		return nil, fmt.Errorf("depth must be >= 0, got %d", depth)
  	}

  	limit := 1 << depth // number of rows the fractal pattern spans
  	rows := make([]string, size)
  	for row := 0; row < size; row++ {
  		var b strings.Builder
  		// Leading spaces to center the triangle.
  		for s := 0; s < size-row-1; s++ {
  			b.WriteRune(' ')
  		}
  		for col := 0; col <= row; col++ {
  			if row < limit && (row&col) == col {
  				b.WriteRune(char)
  			} else {
  				b.WriteRune(' ')
  			}
  			if col != row {
  				b.WriteRune(' ')
  			}
  		}
  		rows[row] = b.String()
  	}
  	return rows, nil
  }
  ```

- [ ] Run the tests:
  ```bash
  go test ./internal/sierpinski/
  ```
  Expected: `ok  github.com/example/fractals/internal/sierpinski`.

  Note: the bottom-row test asserts 8 stars in row index 7 with depth 3 (`limit = 8`, so row 7 < 8 participates and all bits of col are subsets of 7 → fully filled). Confirm it passes.

- [ ] Commit:
  ```bash
  git add internal/sierpinski/
  git commit -m "Add sierpinski triangle generator"
  ```

---

### Task 3: Mandelbrot algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

**Interfaces:**
- Consumes: nothing
- Produces:
  ```go
  // DefaultGradient is the gradient used when no single char is supplied.
  const DefaultGradient = " .:-=+*#%@"

  // Render returns the rows of an ASCII Mandelbrot set.
  // width/height are output dimensions; iterations is the escape cap.
  // If singleChar is 0, the DefaultGradient maps iteration counts to chars.
  // Otherwise, in-set points use singleChar and escaped points use space.
  // Returns an error if width < 1, height < 1, or iterations < 1.
  func Render(width, height, iterations int, singleChar rune) ([]string, error)
  ```

Steps:

- [ ] Write the failing test `internal/mandelbrot/mandelbrot_test.go`:
  ```go
  package mandelbrot

  import (
  	"strings"
  	"testing"
  	"unicode/utf8"
  )

  func TestRenderDimensions(t *testing.T) {
  	rows, err := Render(40, 12, 50, 0)
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 12 {
  		t.Fatalf("expected 12 rows, got %d", len(rows))
  	}
  	for i, r := range rows {
  		if utf8.RuneCountInString(r) != 40 {
  			t.Fatalf("row %d: expected width 40, got %d", i, utf8.RuneCountInString(r))
  		}
  	}
  }

  func TestRenderHasSetPoints(t *testing.T) {
  	// With the default gradient, the dense interior should produce the
  	// last gradient character somewhere.
  	rows, err := Render(80, 24, 100, 0)
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	joined := strings.Join(rows, "\n")
  	last := string(DefaultGradient[len(DefaultGradient)-1])
  	if !strings.Contains(joined, last) {
  		t.Fatalf("expected interior char %q in output", last)
  	}
  }

  func TestRenderSingleChar(t *testing.T) {
  	rows, err := Render(80, 24, 100, '#')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	joined := strings.Join(rows, "\n")
  	if !strings.Contains(joined, "#") {
  		t.Fatalf("expected '#' in output")
  	}
  	// Single-char mode must not contain gradient interior chars.
  	if strings.Contains(joined, "@") {
  		t.Fatalf("single-char mode should not contain gradient chars")
  	}
  }

  func TestRenderInvalidWidth(t *testing.T) {
  	if _, err := Render(0, 24, 100, 0); err == nil {
  		t.Fatal("expected error for width 0")
  	}
  }

  func TestRenderInvalidHeight(t *testing.T) {
  	if _, err := Render(80, 0, 100, 0); err == nil {
  		t.Fatal("expected error for height 0")
  	}
  }

  func TestRenderInvalidIterations(t *testing.T) {
  	if _, err := Render(80, 24, 0, 0); err == nil {
  		t.Fatal("expected error for iterations 0")
  	}
  }
  ```

- [ ] Run the test to see it fail:
  ```bash
  go test ./internal/mandelbrot/
  ```
  Expected: compile failure — `undefined: Render` and `undefined: DefaultGradient`.

- [ ] Implement `internal/mandelbrot/mandelbrot.go`:
  ```go
  // Package mandelbrot renders the Mandelbrot set as ASCII art.
  package mandelbrot

  import (
  	"fmt"
  	"strings"
  )

  // DefaultGradient maps low->high iteration counts to characters.
  const DefaultGradient = " .:-=+*#%@"

  // Complex plane viewport.
  const (
  	minRe = -2.5
  	maxRe = 1.0
  	minIm = -1.25
  	maxIm = 1.25
  )

  // Render returns the rows of an ASCII Mandelbrot set.
  func Render(width, height, iterations int, singleChar rune) ([]string, error) {
  	if width < 1 {
  		return nil, fmt.Errorf("width must be >= 1, got %d", width)
  	}
  	if height < 1 {
  		return nil, fmt.Errorf("height must be >= 1, got %d", height)
  	}
  	if iterations < 1 {
  		return nil, fmt.Errorf("iterations must be >= 1, got %d", iterations)
  	}

  	gradient := []rune(DefaultGradient)
  	rows := make([]string, height)
  	for py := 0; py < height; py++ {
  		var b strings.Builder
  		im := minIm + (maxIm-minIm)*float64(py)/float64(height-1)
  		if height == 1 {
  			im = minIm
  		}
  		for px := 0; px < width; px++ {
  			re := minRe + (maxRe-minRe)*float64(px)/float64(width-1)
  			if width == 1 {
  				re = minRe
  			}
  			n := escape(re, im, iterations)
  			b.WriteRune(cellChar(n, iterations, singleChar, gradient))
  		}
  		rows[py] = b.String()
  	}
  	return rows, nil
  }

  // escape returns the iteration count before |z| exceeds 2, capped at max.
  func escape(cre, cim float64, max int) int {
  	var zr, zi float64
  	for n := 0; n < max; n++ {
  		zr2, zi2 := zr*zr, zi*zi
  		if zr2+zi2 > 4.0 {
  			return n
  		}
  		zi = 2*zr*zi + cim
  		zr = zr2 - zi2 + cre
  	}
  	return max
  }

  // cellChar picks the output rune for an escape count.
  func cellChar(n, max int, singleChar rune, gradient []rune) rune {
  	inSet := n >= max
  	if singleChar != 0 {
  		if inSet {
  			return singleChar
  		}
  		return ' '
  	}
  	if inSet {
  		return gradient[len(gradient)-1]
  	}
  	idx := n * (len(gradient) - 1) / max
  	if idx >= len(gradient) {
  		idx = len(gradient) - 1
  	}
  	return gradient[idx]
  }
  ```

- [ ] Run the tests:
  ```bash
  go test ./internal/mandelbrot/
  ```
  Expected: `ok  github.com/example/fractals/internal/mandelbrot`.

- [ ] Commit:
  ```bash
  git add internal/mandelbrot/
  git commit -m "Add mandelbrot renderer"
  ```

---

### Task 4: Root CLI command

**Files:** `internal/cli/root.go`

**Interfaces:**
- Consumes: nothing yet (subcommands attached in later tasks via `rootCmd`)
- Produces:
  ```go
  // Execute runs the root command. Returns any command error.
  func Execute() error

  // rootCmd is the package-level root command other files add subcommands to.
  var rootCmd *cobra.Command
  ```

Steps:

- [ ] Create `internal/cli/root.go`:
  ```go
  // Package cli wires the fractals command-line interface.
  package cli

  import (
  	"github.com/spf13/cobra"
  )

  var rootCmd = &cobra.Command{
  	Use:   "fractals",
  	Short: "Generate ASCII art fractals",
  	Long:  "fractals generates ASCII art fractals (Sierpinski triangle, Mandelbrot set).",
  }

  // Execute runs the root command.
  func Execute() error {
  	return rootCmd.Execute()
  }
  ```

- [ ] Build the whole module to confirm wiring through `main.go`:
  ```bash
  go build ./...
  ```
  Expected: no output (success).

- [ ] Run the binary's help to confirm the root command works:
  ```bash
  go run ./cmd/fractals --help
  ```
  Expected: usage text containing `fractals generates ASCII art fractals` and an `Available Commands` / `Flags` section (no subcommands yet).

- [ ] Commit:
  ```bash
  git add internal/cli/root.go
  git commit -m "Add root CLI command"
  ```

---

### Task 5: Sierpinski subcommand

**Files:** `internal/cli/sierpinski.go`

**Interfaces:**
- Consumes: `rootCmd` from `internal/cli/root.go`; `sierpinski.Generate(size, depth int, char rune) ([]string, error)`
- Produces: `sierpinski` subcommand registered on `rootCmd` with flags `--size int`, `--depth int`, `--char string`

Steps:

- [ ] Create `internal/cli/sierpinski.go`:
  ```go
  package cli

  import (
  	"fmt"

  	"github.com/example/fractals/internal/sierpinski"
  	"github.com/spf13/cobra"
  )

  func init() {
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

  	cmd.Flags().IntVar(&size, "size", 32, "width of the triangle base in characters")
  	cmd.Flags().IntVar(&depth, "depth", 5, "recursion depth")
  	cmd.Flags().StringVar(&char, "char", "*", "character to use for filled points")

  	rootCmd.AddCommand(cmd)
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

- [ ] Build:
  ```bash
  go build ./...
  ```
  Expected: no output.

- [ ] Run the subcommand manually:
  ```bash
  go run ./cmd/fractals sierpinski --size 8 --depth 3
  ```
  Expected: a centered triangle of `*` characters, 8 lines tall, widest at the bottom.

- [ ] Verify custom char and invalid char:
  ```bash
  go run ./cmd/fractals sierpinski --size 8 --depth 3 --char '#'
  go run ./cmd/fractals sierpinski --char 'ab'; echo "exit=$?"
  ```
  Expected: first prints triangle with `#`; second prints `char must be a single character, got "ab"` to stderr and `exit=1`.

- [ ] Commit:
  ```bash
  git add internal/cli/sierpinski.go
  git commit -m "Add sierpinski subcommand"
  ```

---

### Task 6: Mandelbrot subcommand

**Files:** `internal/cli/mandelbrot.go`

**Interfaces:**
- Consumes: `rootCmd` from `root.go`; `singleRune(string) (rune, error)` from `sierpinski.go`; `mandelbrot.Render(width, height, iterations int, singleChar rune) ([]string, error)`
- Produces: `mandelbrot` subcommand registered on `rootCmd` with flags `--width int`, `--height int`, `--iterations int`, `--char string`. When `--char` is unset/empty, gradient mode is used (passes rune `0` to `Render`).

Steps:

- [ ] Create `internal/cli/mandelbrot.go`:
  ```go
  package cli

  import (
  	"fmt"

  	"github.com/example/fractals/internal/mandelbrot"
  	"github.com/spf13/cobra"
  )

  func init() {
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
  			var r rune // 0 means gradient mode
  			if char != "" {
  				validated, err := singleRune(char)
  				if err != nil {
  					return err
  				}
  				r = validated
  			}
  			rows, err := mandelbrot.Render(width, height, iterations, r)
  			if err != nil {
  				return err
  			}
  			for _, line := range rows {
  				fmt.Fprintln(cmd.OutOrStdout(), line)
  			}
  			return nil
  		},
  	}

  	cmd.Flags().IntVar(&width, "width", 80, "output width in characters")
  	cmd.Flags().IntVar(&height, "height", 24, "output height in characters")
  	cmd.Flags().IntVar(&iterations, "iterations", 100, "maximum iterations for escape calculation")
  	cmd.Flags().StringVar(&char, "char", "", "single character, or omit for gradient \" .:-=+*#%@\"")

  	rootCmd.AddCommand(cmd)
  }
  ```

- [ ] Build:
  ```bash
  go build ./...
  ```
  Expected: no output.

- [ ] Run with default gradient:
  ```bash
  go run ./cmd/fractals mandelbrot --width 80 --height 24 --iterations 100
  ```
  Expected: an 80×24 ASCII Mandelbrot set, dense `@` interior bulging to the left, gradient fringe.

- [ ] Run with single char and invalid input:
  ```bash
  go run ./cmd/fractals mandelbrot --width 40 --height 12 --char '#'
  go run ./cmd/fractals mandelbrot --width 0; echo "exit=$?"
  ```
  Expected: first renders with `#` interior and spaces elsewhere; second prints `width must be >= 1, got 0` to stderr and `exit=1`.

- [ ] Commit:
  ```bash
  git add internal/cli/mandelbrot.go
  git commit -m "Add mandelbrot subcommand"
  ```

---

### Task 7: CLI integration tests

**Files:** `internal/cli/cli_test.go`

**Interfaces:**
- Consumes: `rootCmd` from `root.go`
- Produces: integration tests that drive `rootCmd` with `SetArgs`/`SetOut`/`SetErr` and assert output

Steps:

- [ ] Create `internal/cli/cli_test.go`:
  ```go
  package cli

  import (
  	"bytes"
  	"strings"
  	"testing"
  )

  // run executes rootCmd with args, capturing stdout and the returned error.
  func run(t *testing.T, args ...string) (string, error) {
  	t.Helper()
  	var out bytes.Buffer
  	rootCmd.SetOut(&out)
  	rootCmd.SetErr(&out)
  	rootCmd.SetArgs(args)
  	err := rootCmd.Execute()
  	return out.String(), err
  }

  func TestRootHelp(t *testing.T) {
  	out, err := run(t, "--help")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(out, "Generate ASCII art fractals") {
  		t.Fatalf("help missing description, got:\n%s", out)
  	}
  	if !strings.Contains(out, "sierpinski") || !strings.Contains(out, "mandelbrot") {
  		t.Fatalf("help missing subcommands, got:\n%s", out)
  	}
  }

  func TestSierpinskiCommand(t *testing.T) {
  	out, err := run(t, "sierpinski", "--size", "8", "--depth", "3")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 8 {
  		t.Fatalf("expected 8 lines, got %d:\n%s", len(lines), out)
  	}
  	if !strings.Contains(out, "*") {
  		t.Fatalf("expected '*' in output:\n%s", out)
  	}
  }

  func TestSierpinskiInvalidChar(t *testing.T) {
  	_, err := run(t, "sierpinski", "--char", "ab")
  	if err == nil {
  		t.Fatal("expected error for multi-char --char")
  	}
  }

  func TestSierpinskiInvalidSize(t *testing.T) {
  	_, err := run(t, "sierpinski", "--size", "0")
  	if err == nil {
  		t.Fatal("expected error for size 0")
  	}
  }

  func TestMandelbrotCommand(t *testing.T) {
  	out, err := run(t, "mandelbrot", "--width", "40", "--height", "12", "--iterations", "50")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 12 {
  		t.Fatalf("expected 12 lines, got %d:\n%s", len(lines), out)
  	}
  }

  func TestMandelbrotSingleChar(t *testing.T) {
  	out, err := run(t, "mandelbrot", "--width", "40", "--height", "12", "--char", "#")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(out, "#") {
  		t.Fatalf("expected '#' in output:\n%s", out)
  	}
  }

  func TestMandelbrotInvalidIterations(t *testing.T) {
  	_, err := run(t, "mandelbrot", "--iterations", "0")
  	if err == nil {
  		t.Fatal("expected error for iterations 0")
  	}
  }
  ```

  Note: tests reset `rootCmd` flag state implicitly because flag variables are bound once in `init`; each `run` call sets fresh args, and cobra parses defaults for unset flags. Run tests sequentially (default) so shared `rootCmd` output buffers do not collide.

- [ ] Run the CLI tests:
  ```bash
  go test ./internal/cli/
  ```
  Expected: `ok  github.com/example/fractals/internal/cli`.

- [ ] Run the full suite and build:
  ```bash
  go test ./...
  go build ./...
  ```
  Expected: all packages `ok`; build produces no output.

- [ ] Commit:
  ```bash
  git add internal/cli/cli_test.go
  git commit -m "Add CLI integration tests"
  ```

---

### Task 8: Final verification

**Files:** none (verification only)

**Interfaces:**
- Consumes: full built binary
- Produces: confirmed acceptance criteria

Steps:

- [ ] Format and vet the whole module:
  ```bash
  gofmt -l .
  go vet ./...
  ```
  Expected: `gofmt -l .` prints nothing; `go vet` prints nothing.

- [ ] Build the named binary:
  ```bash
  go build -o fractals ./cmd/fractals
  ```
  Expected: produces `./fractals`.

- [ ] Verify acceptance criteria 1–6 manually:
  ```bash
  ./fractals --help
  ./fractals sierpinski
  ./fractals mandelbrot
  ./fractals sierpinski --size 16 --depth 4 --char '#'
  ./fractals mandelbrot --width 60 --height 20 --iterations 80
  ./fractals sierpinski --size -1; echo "exit=$?"
  ```
  Expected: help text; a recognizable triangle; a recognizable Mandelbrot set; custom-char triangle; sized Mandelbrot; final command prints `size must be >= 1, got -1` to stderr with `exit=1`.

- [ ] Confirm all tests pass (criterion 7):
  ```bash
  go test ./...
  ```
  Expected: every package reports `ok`.

- [ ] Commit any formatting fixes if `gofmt`/`vet` required changes (otherwise skip):
  ```bash
  git add -A
  git commit -m "Final formatting and verification"
  ```

---

## Self-Review

- **Spec coverage:**
  - `sierpinski` with `--size/--depth/--char` → Tasks 2, 5. ✓
  - `mandelbrot` with `--width/--height/--iterations/--char` → Tasks 3, 6. ✓
  - Gradient default `" .:-=+*#%@"` → defined verbatim as `DefaultGradient` (Task 3) and referenced in flag help (Task 6). ✓
  - `--help` for root → Task 4/7. Subcommand help is provided automatically by cobra (each subcommand has `Use`/`Short`). ✓
  - Architecture file layout matches spec exactly (cmd/fractals, internal/sierpinski, internal/mandelbrot, internal/cli with root/sierpinski/mandelbrot files). ✓
  - Dependencies Go 1.21+ and cobra → Task 1 + Global Constraints. ✓
  - Acceptance criteria 1–7 → Task 8 explicit checks. ✓

- **Placeholder scan:** No `TODO`, `FIXME`, or stub-only code blocks; every function body is complete.

- **Type consistency:** `Generate(size, depth int, char rune) ([]string, error)` and `Render(width, height, iterations int, singleChar rune) ([]string, error)` signatures are identical across their producing tasks (2, 3) and consuming tasks (5, 6). `singleRune(string) (rune, error)` is defined once in `sierpinski.go` (Task 5) and consumed in `mandelbrot.go` (Task 6) — Interfaces block in Task 6 names this dependency. `rootCmd` is a package-level `*cobra.Command` produced in Task 4 and consumed via `init()` in Tasks 5–7.

- **Fix applied during review:** Module path `github.com/example/fractals` standardized across `main.go`, internal imports, and all Interfaces blocks. Gradient-mode sentinel (`rune(0)`) is documented in both `Render`'s contract (Task 3) and the mandelbrot subcommand Interfaces (Task 6) to prevent ambiguity.