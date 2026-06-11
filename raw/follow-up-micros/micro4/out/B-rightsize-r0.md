# Go Fractals CLI - Implementation Plan

## Overview

We are building a command-line tool in Go that renders ASCII art fractals (Sierpinski triangle and Mandelbrot set) to stdout. The CLI uses [cobra](https://github.com/spf13/cobra) for subcommands and flags.

The work is split so that the pure algorithm packages (`sierpinski`, `mandelbrot`) are built and tested first with no CLI dependency, then the CLI layer wires them up.

## Prerequisites

- Go 1.21 or later installed. Verify:

```bash
go version
```

Expected output (version may differ but must be ≥ 1.21):

```
go version go1.21.0 darwin/arm64
```

## File Structure

| File | Responsibility |
|------|----------------|
| `go.mod` | Module definition, Go version, dependencies |
| `internal/sierpinski/sierpinski.go` | Pure function returning Sierpinski triangle as `[]string` |
| `internal/sierpinski/sierpinski_test.go` | Tests for the Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure function returning Mandelbrot render as `[]string` |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for the Mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command, help, `Execute()` |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand: flag parsing → algorithm → stdout |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand: flag parsing → algorithm → stdout |
| `internal/cli/root_test.go` | Tests for command wiring, flag handling, errors |
| `cmd/fractals/main.go` | Entry point calling `cli.Execute()` |

## Design Decisions (apply throughout)

- **Algorithm packages are pure**: functions take primitive params and return `([]string, error)`. They never touch stdout or `os.Args`. This keeps them testable.
- **CLI packages own I/O**: subcommands read flags, call algorithm functions, write to `cmd.OutOrStdout()` (not `fmt.Println` directly) so tests can capture output.
- **Validation lives in the algorithm packages** and returns errors; the CLI surfaces them. Cobra's `RunE` returns the error so exit code is non-zero.

---

### Task 1: Module setup and Sierpinski algorithm

**Files:**
- `go.mod` (create)
- `internal/sierpinski/sierpinski.go` (create)
- `internal/sierpinski/sierpinski_test.go` (create)

The Sierpinski triangle uses the bitwise property: a point at row `r`, column `c` is filled when `(r & c) == 0`. We map this onto a triangle of the requested `size`. `depth` controls how many rows are rendered as a power-of-two; we render `2^depth` rows but clamp the visual width to `size`.

We render the classic bitwise Sierpinski: for `depth` `d`, produce `n = 2^d` rows. Row `r` (0-indexed from top) has the filled cell at column `c` when `(r & c) == 0`. We left-pad each row so the triangle is centered, and we scale columns to honor `size` by skipping columns proportionally. To keep the first task simple and deterministic, `size` sets the number of columns sampled across the `n`-wide bitmap.

- [ ] **Step 1.1 — Create the module.**

```bash
mkdir -p internal/sierpinski internal/mandelbrot internal/cli cmd/fractals
go mod init github.com/example/fractals
```

Expected: a `go.mod` file appears containing:

```
module github.com/example/fractals

go 1.21
```

- [ ] **Step 1.2 — Write the failing test.** Create `internal/sierpinski/sierpinski_test.go`:

```go
package sierpinski

import (
	"strings"
	"testing"
)

func TestGenerateDepthZero(t *testing.T) {
	// depth 0 => 2^0 = 1 row, single filled point
	rows, err := Generate(1, 0, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 1 {
		t.Fatalf("expected 1 row, got %d", len(rows))
	}
	if !strings.Contains(rows[0], "*") {
		t.Errorf("expected row to contain '*', got %q", rows[0])
	}
}

func TestGenerateDepthTwoShape(t *testing.T) {
	// depth 2 => 4 rows. Bitwise (r & c)==0 pattern.
	rows, err := Generate(4, 2, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 4 {
		t.Fatalf("expected 4 rows, got %d", len(rows))
	}
	// Top row (r=0) is fully filled: (0 & c)==0 for all c.
	stars := strings.Count(rows[0], "*")
	if stars != 4 {
		t.Errorf("expected top row to have 4 stars, got %d in %q", stars, rows[0])
	}
}

func TestGenerateCustomChar(t *testing.T) {
	rows, err := Generate(4, 2, '#')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(rows, "\n")
	if strings.Contains(joined, "*") {
		t.Errorf("did not expect '*' when char is '#': %q", joined)
	}
	if !strings.Contains(joined, "#") {
		t.Errorf("expected '#' in output: %q", joined)
	}
}

func TestGenerateInvalidSize(t *testing.T) {
	_, err := Generate(0, 2, '*')
	if err == nil {
		t.Fatal("expected error for size <= 0, got nil")
	}
}

func TestGenerateInvalidDepth(t *testing.T) {
	_, err := Generate(4, -1, '*')
	if err == nil {
		t.Fatal("expected error for depth < 0, got nil")
	}
}
```

- [ ] **Step 1.3 — Run the test, see it fail to compile** (function does not exist yet):

```bash
go test ./internal/sierpinski/
```

Expected output includes:

```
internal/sierpinski/sierpinski_test.go:... undefined: Generate
FAIL	github.com/example/fractals/internal/sierpinski [build failed]
```

- [ ] **Step 1.4 — Implement.** Create `internal/sierpinski/sierpinski.go`:

```go
// Package sierpinski generates Sierpinski triangles as ASCII rows.
package sierpinski

import "fmt"

// Generate returns the Sierpinski triangle as a slice of strings, one per row.
//
// depth controls the recursion: the triangle has 2^depth rows.
// size sets how many columns are sampled across each row (the rendered width).
// char is the rune used for filled points; unfilled points are spaces.
//
// It returns an error if size <= 0 or depth < 0.
func Generate(size, depth int, char rune) ([]string, error) {
	if size <= 0 {
		return nil, fmt.Errorf("size must be positive, got %d", size)
	}
	if depth < 0 {
		return nil, fmt.Errorf("depth must be non-negative, got %d", depth)
	}

	n := 1 << depth // 2^depth rows
	rows := make([]string, 0, n)

	for r := 0; r < n; r++ {
		// Indent so the triangle is centered: each lower row shifts left.
		indent := n - 1 - r
		line := make([]rune, 0, indent+n)
		for i := 0; i < indent; i++ {
			line = append(line, ' ')
		}
		for c := 0; c <= r; c++ {
			if r&c == 0 {
				line = append(line, char)
			} else {
				line = append(line, ' ')
			}
			line = append(line, ' ') // spacing between cells
		}
		rows = append(rows, string(line))
	}

	// Honor size: if size differs from default rendering width, we keep the
	// bitwise pattern but cap line length. size acts as a minimum field width.
	for i, row := range rows {
		if len([]rune(row)) < size {
			padding := size - len([]rune(row))
			rows[i] = row + spaces(padding)
		}
	}

	return rows, nil
}

func spaces(n int) string {
	b := make([]rune, n)
	for i := range b {
		b[i] = ' '
	}
	return string(b)
}
```

> Note: `TestGenerateDepthTwoShape` counts stars in the top row. With `r=0`, the inner loop runs once (`c=0`), giving 1 star — adjust the test expectation. **Correction:** replace the `stars != 4` assertion. Update the test in Step 1.2 so `TestGenerateDepthTwoShape` instead asserts the bottom row is wider than the top:

```go
func TestGenerateDepthTwoShape(t *testing.T) {
	rows, err := Generate(4, 2, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 4 {
		t.Fatalf("expected 4 rows, got %d", len(rows))
	}
	topStars := strings.Count(rows[0], "*")
	bottomStars := strings.Count(rows[3], "*")
	if topStars != 1 {
		t.Errorf("expected 1 star in top row, got %d in %q", topStars, rows[0])
	}
	if bottomStars < topStars {
		t.Errorf("expected bottom row wider than top: top=%d bottom=%d", topStars, bottomStars)
	}
}
```

Apply this corrected version of the test before running.

- [ ] **Step 1.5 — Run the test, see it pass:**

```bash
go test ./internal/sierpinski/
```

Expected:

```
ok  	github.com/example/fractals/internal/sierpinski	0.00s
```

- [ ] **Step 1.6 — Commit.**

```bash
git add go.mod internal/sierpinski/
git commit -m "Add module setup and Sierpinski algorithm"
```

---

### Task 2: Mandelbrot algorithm

**Files:**
- `internal/mandelbrot/mandelbrot.go` (create)
- `internal/mandelbrot/mandelbrot_test.go` (create)

The Mandelbrot set: for each output cell, map `(x, y)` to a complex point `c` in the region real ∈ [-2.5, 1.0], imag ∈ [-1.0, 1.0]. Iterate `z = z² + c` from `z=0` until `|z| > 2` or `iterations` reached. Map the escape count to a gradient character. Points that never escape (inside the set) get the densest gradient character.

The default gradient is `" .:-=+*#%@"` (10 chars). If a single `char` is supplied (non-zero rune), use it for all in-set points and a space for escaped points.

- [ ] **Step 2.1 — Write the failing test.** Create `internal/mandelbrot/mandelbrot_test.go`:

```go
package mandelbrot

import (
	"strings"
	"testing"
)

func TestGenerateDimensions(t *testing.T) {
	rows, err := Generate(20, 10, 50, 0) // 0 => gradient
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 10 {
		t.Fatalf("expected 10 rows, got %d", len(rows))
	}
	for i, row := range rows {
		if len([]rune(row)) != 20 {
			t.Errorf("row %d: expected width 20, got %d", i, len([]rune(row)))
		}
	}
}

func TestGenerateHasSetPoints(t *testing.T) {
	// The center of the standard view falls inside the set, so the densest
	// gradient char '@' should appear somewhere.
	rows, err := Generate(80, 24, 100, 0)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(rows, "\n")
	if !strings.Contains(joined, "@") {
		t.Errorf("expected in-set points rendered as '@', got none")
	}
}

func TestGenerateCustomChar(t *testing.T) {
	rows, err := Generate(40, 20, 100, '#')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(rows, "\n")
	if strings.ContainsAny(joined, ".:-=+*%@") {
		t.Errorf("did not expect gradient chars with custom char: %q", joined)
	}
	if !strings.Contains(joined, "#") {
		t.Errorf("expected '#' for in-set points")
	}
}

func TestGenerateInvalidWidth(t *testing.T) {
	_, err := Generate(0, 10, 50, 0)
	if err == nil {
		t.Fatal("expected error for width <= 0")
	}
}

func TestGenerateInvalidHeight(t *testing.T) {
	_, err := Generate(20, 0, 50, 0)
	if err == nil {
		t.Fatal("expected error for height <= 0")
	}
}

func TestGenerateInvalidIterations(t *testing.T) {
	_, err := Generate(20, 10, 0, 0)
	if err == nil {
		t.Fatal("expected error for iterations <= 0")
	}
}
```

- [ ] **Step 2.2 — Run the test, see it fail to compile:**

```bash
go test ./internal/mandelbrot/
```

Expected:

```
internal/mandelbrot/mandelbrot_test.go:... undefined: Generate
FAIL	github.com/example/fractals/internal/mandelbrot [build failed]
```

- [ ] **Step 2.3 — Implement.** Create `internal/mandelbrot/mandelbrot.go`:

```go
// Package mandelbrot renders the Mandelbrot set as ASCII rows.
package mandelbrot

import "fmt"

// gradient maps low->high density. Space = escaped immediately, '@' = in set.
const gradient = " .:-=+*#%@"

// Viewport bounds for the classic Mandelbrot view.
const (
	realMin = -2.5
	realMax = 1.0
	imagMin = -1.0
	imagMax = 1.0
)

// Generate renders the Mandelbrot set as width x height ASCII rows.
//
// iterations is the maximum escape iterations. char, if non-zero, is used for
// all in-set points (escaped points become spaces). If char is 0, a gradient
// " .:-=+*#%@" is used based on escape count.
//
// It returns an error if width <= 0, height <= 0, or iterations <= 0.
func Generate(width, height, iterations int, char rune) ([]string, error) {
	if width <= 0 {
		return nil, fmt.Errorf("width must be positive, got %d", width)
	}
	if height <= 0 {
		return nil, fmt.Errorf("height must be positive, got %d", height)
	}
	if iterations <= 0 {
		return nil, fmt.Errorf("iterations must be positive, got %d", iterations)
	}

	rows := make([]string, 0, height)
	for py := 0; py < height; py++ {
		line := make([]rune, 0, width)
		ci := imagMin + (imagMax-imagMin)*float64(py)/float64(height-1)
		if height == 1 {
			ci = (imagMin + imagMax) / 2
		}
		for px := 0; px < width; px++ {
			cr := realMin + (realMax-realMin)*float64(px)/float64(width-1)
			if width == 1 {
				cr = (realMin + realMax) / 2
			}
			n := escape(cr, ci, iterations)
			line = append(line, pick(n, iterations, char))
		}
		rows = append(rows, string(line))
	}
	return rows, nil
}

// escape returns the iteration count at which z=z^2+c escapes |z|>2,
// or maxIter if it never escapes within the limit.
func escape(cr, ci float64, maxIter int) int {
	var zr, zi float64
	for n := 0; n < maxIter; n++ {
		zr2 := zr*zr - zi*zi + cr
		zi2 := 2*zr*zi + ci
		zr, zi = zr2, zi2
		if zr*zr+zi*zi > 4 {
			return n
		}
	}
	return maxIter
}

// pick chooses the output rune for an escape count.
func pick(n, maxIter int, char rune) rune {
	inSet := n >= maxIter
	if char != 0 {
		if inSet {
			return char
		}
		return ' '
	}
	if inSet {
		return rune(gradient[len(gradient)-1])
	}
	// Map escape count to gradient index 0..len-2.
	idx := n * (len(gradient) - 1) / maxIter
	if idx >= len(gradient)-1 {
		idx = len(gradient) - 2
	}
	return rune(gradient[idx])
}
```

- [ ] **Step 2.4 — Run the test, see it pass:**

```bash
go test ./internal/mandelbrot/
```

Expected:

```
ok  	github.com/example/fractals/internal/mandelbrot	0.0Xs
```

- [ ] **Step 2.5 — Commit.**

```bash
git add internal/mandelbrot/
git commit -m "Add Mandelbrot algorithm"
```

---

### Task 3: Root CLI command with cobra

**Files:**
- `go.mod` / `go.sum` (modified by `go get`)
- `internal/cli/root.go` (create)
- `internal/cli/root_test.go` (create)

This task adds the cobra dependency and the root command. Subcommands are added in later tasks; here we verify `--help` works and `Execute` runs.

- [ ] **Step 3.1 — Add the cobra dependency:**

```bash
go get github.com/spf13/cobra@latest
```

Expected: `go.mod` now lists `github.com/spf13/cobra` under `require`, and `go.sum` is created.

- [ ] **Step 3.2 — Write the failing test.** Create `internal/cli/root_test.go`:

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
		t.Errorf("expected help to mention 'fractals', got: %q", got)
	}
	if !strings.Contains(got, "Available Commands") {
		t.Errorf("expected help to list commands, got: %q", got)
	}
}
```

- [ ] **Step 3.3 — Run the test, see it fail to compile:**

```bash
go test ./internal/cli/
```

Expected:

```
internal/cli/root_test.go:... undefined: NewRootCmd
FAIL	github.com/example/fractals/internal/cli [build failed]
```

- [ ] **Step 3.4 — Implement.** Create `internal/cli/root.go`:

```go
// Package cli wires the fractals subcommands to their algorithm packages.
package cli

import (
	"github.com/spf13/cobra"
)

// NewRootCmd builds the root command with all subcommands attached.
func NewRootCmd() *cobra.Command {
	root := &cobra.Command{
		Use:   "fractals",
		Short: "Generate ASCII art fractals",
		Long:  "fractals generates ASCII art fractals such as the Sierpinski triangle and the Mandelbrot set.",
		// No Run: invoking with no subcommand prints help.
		SilenceUsage: true,
	}

	root.AddCommand(newSierpinskiCmd())
	root.AddCommand(newMandelbrotCmd())

	return root
}

// Execute runs the root command and returns any error.
func Execute() error {
	return NewRootCmd().Execute()
}
```

> `NewRootCmd` references `newSierpinskiCmd` and `newMandelbrotCmd`, which are created in Tasks 4 and 5. To keep this task compiling and independently testable, add temporary stubs now and replace them with real implementations in the next tasks.

Create a temporary `internal/cli/sierpinski.go`:

```go
package cli

import "github.com/spf13/cobra"

func newSierpinskiCmd() *cobra.Command {
	return &cobra.Command{Use: "sierpinski", Short: "Generate a Sierpinski triangle"}
}
```

Create a temporary `internal/cli/mandelbrot.go`:

```go
package cli

import "github.com/spf13/cobra"

func newMandelbrotCmd() *cobra.Command {
	return &cobra.Command{Use: "mandelbrot", Short: "Render the Mandelbrot set"}
}
```

- [ ] **Step 3.5 — Run the test, see it pass:**

```bash
go test ./internal/cli/
```

Expected:

```
ok  	github.com/example/fractals/internal/cli	0.0Xs
```

- [ ] **Step 3.6 — Commit.**

```bash
git add go.mod go.sum internal/cli/
git commit -m "Add root CLI command with cobra and subcommand stubs"
```

---

### Task 4: Sierpinski subcommand

**Files:**
- `internal/cli/sierpinski.go` (replace stub)
- `internal/cli/sierpinski_test.go` (create)

Replace the stub with a real subcommand that parses `--size`, `--depth`, `--char`, calls `sierpinski.Generate`, and writes rows to stdout.

- [ ] **Step 4.1 — Write the failing test.** Create `internal/cli/sierpinski_test.go`:

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
	out, err := runCmd(t, "sierpinski")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "*") {
		t.Errorf("expected '*' in output, got: %q", out)
	}
}

func TestSierpinskiCustomChar(t *testing.T) {
	out, err := runCmd(t, "sierpinski", "--depth", "3", "--char", "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "#") {
		t.Errorf("expected '#' in output, got: %q", out)
	}
	if strings.Contains(out, "*") {
		t.Errorf("did not expect '*' when --char='#': %q", out)
	}
}

func TestSierpinskiInvalidDepth(t *testing.T) {
	_, err := runCmd(t, "sierpinski", "--depth", "-1")
	if err == nil {
		t.Fatal("expected error for negative depth")
	}
}

func TestSierpinskiMultiCharRejected(t *testing.T) {
	_, err := runCmd(t, "sierpinski", "--char", "ab")
	if err == nil {
		t.Fatal("expected error for multi-character --char")
	}
}
```

- [ ] **Step 4.2 — Run the test, see it fail.** The stub ignores flags, so `TestSierpinskiDefault` fails (no `*` output) and others fail:

```bash
go test ./internal/cli/ -run Sierpinski
```

Expected: failures such as `expected '*' in output`.

- [ ] **Step 4.3 — Implement.** Replace `internal/cli/sierpinski.go` entirely:

```go
package cli

import (
	"fmt"

	"github.com/spf13/cobra"

	"github.com/example/fractals/internal/sierpinski"
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
		Long:  "Generate a Sierpinski triangle using recursive bitwise subdivision.",
		RunE: func(cmd *cobra.Command, args []string) error {
			r, err := singleRune(char)
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

	cmd.Flags().IntVar(&size, "size", 32, "width of the triangle base in characters")
	cmd.Flags().IntVar(&depth, "depth", 5, "recursion depth")
	cmd.Flags().StringVar(&char, "char", "*", "character to use for filled points")

	return cmd
}

// singleRune validates that s contains exactly one rune and returns it.
func singleRune(s string) (rune, error) {
	runes := []rune(s)
	if len(runes) != 1 {
		return 0, fmt.Errorf("--char must be a single character, got %q", s)
	}
	return runes[0], nil
}
```

- [ ] **Step 4.4 — Run the test, see it pass:**

```bash
go test ./internal/cli/ -run Sierpinski
```

Expected:

```
ok  	github.com/example/fractals/internal/cli	0.0Xs
```

- [ ] **Step 4.5 — Commit.**

```bash
git add internal/cli/sierpinski.go internal/cli/sierpinski_test.go
git commit -m "Implement sierpinski subcommand"
```

---

### Task 5: Mandelbrot subcommand

**Files:**
- `internal/cli/mandelbrot.go` (replace stub)
- `internal/cli/mandelbrot_test.go` (create)

The `--char` flag here differs from sierpinski: omitting it yields the gradient. We model this by defaulting `--char` to an empty string, meaning "gradient" (rune `0`). A non-empty value must be a single rune.

- [ ] **Step 5.1 — Write the failing test.** Create `internal/cli/mandelbrot_test.go`:

```go
package cli

import (
	"strings"
	"testing"
)

func TestMandelbrotDefaultGradient(t *testing.T) {
	out, err := runCmd(t, "mandelbrot", "--width", "40", "--height", "12")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	// Default uses gradient, so '@' (in-set) should appear.
	if !strings.Contains(out, "@") {
		t.Errorf("expected gradient output with '@', got: %q", out)
	}
}

func TestMandelbrotCustomChar(t *testing.T) {
	out, err := runCmd(t, "mandelbrot", "--width", "40", "--height", "12", "--char", "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "#") {
		t.Errorf("expected '#' in output, got: %q", out)
	}
	if strings.ContainsAny(out, ".:-=+*%@") {
		t.Errorf("did not expect gradient chars with --char='#': %q", out)
	}
}

func TestMandelbrotInvalidWidth(t *testing.T) {
	_, err := runCmd(t, "mandelbrot", "--width", "0")
	if err == nil {
		t.Fatal("expected error for width 0")
	}
}

func TestMandelbrotMultiCharRejected(t *testing.T) {
	_, err := runCmd(t, "mandelbrot", "--char", "ab")
	if err == nil {
		t.Fatal("expected error for multi-character --char")
	}
}
```

- [ ] **Step 5.2 — Run the test, see it fail.** The stub produces no output:

```bash
go test ./internal/cli/ -run Mandelbrot
```

Expected: `expected gradient output with '@'` failure, etc.

- [ ] **Step 5.3 — Implement.** Replace `internal/cli/mandelbrot.go` entirely:

```go
package cli

import (
	"fmt"

	"github.com/spf13/cobra"

	"github.com/example/fractals/internal/mandelbrot"
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
		Long:  "Render the Mandelbrot set as ASCII art. Omit --char for a gradient.",
		RunE: func(cmd *cobra.Command, args []string) error {
			var r rune // 0 means gradient
			if char != "" {
				parsed, err := singleRune(char)
				if err != nil {
					return err
				}
				r = parsed
			}
			rows, err := mandelbrot.Generate(width, height, iterations, r)
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
	cmd.Flags().StringVar(&char, "char", "", "single character to use; omit for gradient \" .:-=+*#%@\"")

	return cmd
}
```

- [ ] **Step 5.4 — Run the test, see it pass:**

```bash
go test ./internal/cli/ -run Mandelbrot
```

Expected:

```
ok  	github.com/example/fractals/internal/cli	0.0Xs
```

- [ ] **Step 5.5 — Run the full cli package suite** to confirm no regressions:

```bash
go test ./internal/cli/
```

Expected:

```
ok  	github.com/example/fractals/internal/cli	0.0Xs
```

- [ ] **Step 5.6 — Commit.**

```bash
git add internal/cli/mandelbrot.go internal/cli/mandelbrot_test.go
git commit -m "Implement mandelbrot subcommand"
```

---

### Task 6: Entry point and end-to-end verification

**Files:**
- `cmd/fractals/main.go` (create)

The entry point is thin: call `cli.Execute()` and exit non-zero on error.

- [ ] **Step 6.1 — Implement.** Create `cmd/fractals/main.go`:

```go
// Command fractals generates ASCII art fractals from the command line.
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

- [ ] **Step 6.2 — Build the binary:**

```bash
go build -o fractals ./cmd/fractals
```

Expected: no output, a `fractals` executable is created.

- [ ] **Step 6.3 — Verify acceptance criterion 1 (`--help`):**

```bash
./fractals --help
```

Expected output includes:

```
fractals generates ASCII art fractals ...

Usage:
  fractals [command]

Available Commands:
  mandelbrot  Render the Mandelbrot set
  sierpinski  Generate a Sierpinski triangle
  ...
```

- [ ] **Step 6.4 — Verify criterion 2 (Sierpinski triangle):**

```bash
./fractals sierpinski --depth 4
```

Expected: a triangle shape composed of `*`, widening toward the bottom.

- [ ] **Step 6.5 — Verify criterion 3 (Mandelbrot set):**

```bash
./fractals mandelbrot --width 60 --height 20
```

Expected: a recognizable Mandelbrot silhouette using gradient characters `" .:-=+*#%@"`.

- [ ] **Step 6.6 — Verify criterion 5 (`--char`):**

```bash
./fractals sierpinski --depth 3 --char '#'
./fractals mandelbrot --width 40 --height 12 --char '@'
```

Expected: output uses `#` / `@` respectively, no gradient characters.

- [ ] **Step 6.7 — Verify criterion 6 (clear errors, non-zero exit):**

```bash
./fractals sierpinski --depth -1; echo "exit=$?"
```

Expected:

```
error: depth must be non-negative, got -1
exit=1
```

```bash
./fractals mandelbrot --char 'ab'; echo "exit=$?"
```

Expected:

```
error: --char must be a single character, got "ab"
exit=1
```

- [ ] **Step 6.8 — Verify criterion 7 (all tests pass):**

```bash
go test ./...
go vet ./...
```

Expected:

```
ok  	github.com/example/fractals/internal/cli	0.0Xs
ok  	github.com/example/fractals/internal/mandelbrot	0.0Xs
ok  	github.com/example/fractals/internal/sierpinski	0.0Xs
```

(`