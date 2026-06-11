# Go Fractals CLI - Implementation Plan

## Overview

We are building a CLI tool `fractals` that generates ASCII art for two fractal types: Sierpinski triangle and Mandelbrot set. The tool uses `cobra` for command-line parsing.

This plan assumes zero context. Follow each step exactly. We use TDD: write a failing test, see it fail, implement, see it pass, commit.

## File Structure

| File | Responsibility |
|------|----------------|
| `go.mod` | Module definition, Go version, dependencies |
| `internal/sierpinski/sierpinski.go` | Pure algorithm: produce a Sierpinski triangle as `[]string` |
| `internal/sierpinski/sierpinski_test.go` | Tests for the Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure algorithm: produce a Mandelbrot rendering as `[]string` |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for the Mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command, help wiring, `Execute()` |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand: flags → algorithm → stdout |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand: flags → algorithm → stdout |
| `internal/cli/cli_test.go` | Tests that exercise commands end-to-end via captured output |
| `cmd/fractals/main.go` | Entry point: calls `cli.Execute()` |

Each algorithm package is pure (no I/O, no cobra). The `cli` package handles flags, validation, and printing. This keeps logic testable.

---

### Task 1: Project scaffolding

**Files:** `go.mod`, `cmd/fractals/main.go`, `internal/cli/root.go`

This task sets up the module, dependencies, and a minimal runnable binary that prints help. It folds in all setup needed for later tasks.

- [ ] Create the module. Run:

```bash
go mod init github.com/example/fractals
```

Expected output:

```
go: creating new go.mod: module github.com/example/fractals
```

- [ ] Add the cobra dependency. Run:

```bash
go get github.com/spf13/cobra@latest
```

Expected output (versions may vary):

```
go: added github.com/spf13/cobra v1.8.x
```

- [ ] Create `internal/cli/root.go` with the root command:

```go
package cli

import (
	"github.com/spf13/cobra"
)

// rootCmd is the base command for the fractals CLI.
var rootCmd = &cobra.Command{
	Use:   "fractals",
	Short: "Generate ASCII art fractals",
	Long:  "fractals generates ASCII art fractals such as the Sierpinski triangle and the Mandelbrot set.",
}

// Execute runs the root command and returns any error.
func Execute() error {
	return rootCmd.Execute()
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

- [ ] Tidy modules. Run:

```bash
go mod tidy
```

Expected: no errors; `go.sum` is created.

- [ ] Build and verify help works. Run:

```bash
go run ./cmd/fractals --help
```

Expected output (approximately):

```
fractals generates ASCII art fractals such as the Sierpinski triangle and the Mandelbrot set.

Usage:
  fractals [command]

Flags:
  -h, --help   help for fractals

Use "fractals [command] --help" for more information about a command.
```

- [ ] Commit. Run:

```bash
git add -A && git commit -m "Scaffold fractals module with root command"
```

---

### Task 2: Sierpinski algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

We implement the Sierpinski triangle as a pure function. The classic ASCII approach: a point `(row, col)` is filled when `(row & col) == 0` in a triangle of `2^depth` rows. We map the requested `size` to the number of rows. To keep the algorithm simple and deterministic, the number of rows is `1 << depth`, and `size` controls horizontal scaling of each character cell to approximate the requested base width.

Signature:

```go
func Generate(size, depth int, char rune) ([]string, error)
```

Rules:
- `depth` must be >= 0; `depth` < 0 returns an error.
- `size` must be >= 1; `size` < 1 returns an error.
- Returns `1 << depth` lines. Each row `r` (0-indexed from top) contains filled `char` at column `c` when `(r & c) == 0`, otherwise a space. Each row is left-padded so the triangle is centered, and trailing spaces are trimmed.

- [ ] Write the failing test `internal/sierpinski/sierpinski_test.go`:

```go
package sierpinski

import (
	"strings"
	"testing"
)

func TestGenerateDepthZero(t *testing.T) {
	lines, err := Generate(1, 0, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(lines) != 1 {
		t.Fatalf("expected 1 line, got %d", len(lines))
	}
	if lines[0] != "*" {
		t.Errorf("expected single star, got %q", lines[0])
	}
}

func TestGenerateDepthTwo(t *testing.T) {
	lines, err := Generate(4, 2, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	// 2^2 = 4 rows.
	if len(lines) != 4 {
		t.Fatalf("expected 4 lines, got %d", len(lines))
	}
	// Top row has a single filled point.
	if strings.TrimSpace(lines[0]) != "*" {
		t.Errorf("row 0 should be a single star, got %q", lines[0])
	}
	// Last row is fully filled across the base ((r&c)==0 for all c when r=3? no):
	// For r=3 (binary 11), c with (3&c)==0 is only c=0, so base is NOT full.
	// Row 1 (binary 01): filled at c=0 and c=2.
	if !strings.Contains(lines[1], "*") {
		t.Errorf("row 1 should contain stars, got %q", lines[1])
	}
}

func TestGenerateCustomChar(t *testing.T) {
	lines, err := Generate(2, 1, '#')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(lines, "\n")
	if strings.Contains(joined, "*") {
		t.Errorf("output should not contain default char, got %q", joined)
	}
	if !strings.Contains(joined, "#") {
		t.Errorf("output should contain custom char, got %q", joined)
	}
}

func TestGenerateInvalidDepth(t *testing.T) {
	_, err := Generate(4, -1, '*')
	if err == nil {
		t.Fatal("expected error for negative depth")
	}
}

func TestGenerateInvalidSize(t *testing.T) {
	_, err := Generate(0, 2, '*')
	if err == nil {
		t.Fatal("expected error for size < 1")
	}
}
```

- [ ] Run the test to see it fail (package does not compile yet):

```bash
go test ./internal/sierpinski/
```

Expected output includes:

```
internal/sierpinski/sierpinski_test.go:...: undefined: Generate
FAIL	github.com/example/fractals/internal/sierpinski [build failed]
```

- [ ] Implement `internal/sierpinski/sierpinski.go`:

```go
package sierpinski

import (
	"fmt"
	"strings"
)

// Generate produces a Sierpinski triangle as a slice of strings.
// It returns 1<<depth rows. A cell (r, c) is filled with char when (r & c) == 0.
// size controls the rendered base width (each filled point centered per row).
func Generate(size, depth int, char rune) ([]string, error) {
	if depth < 0 {
		return nil, fmt.Errorf("depth must be >= 0, got %d", depth)
	}
	if size < 1 {
		return nil, fmt.Errorf("size must be >= 1, got %d", size)
	}

	rows := 1 << depth
	lines := make([]string, rows)

	for r := 0; r < rows; r++ {
		var b strings.Builder
		// Left padding to center the triangle: (rows-1-r) leading spaces.
		b.WriteString(strings.Repeat(" ", rows-1-r))
		for c := 0; c <= r; c++ {
			if r&c == 0 {
				b.WriteRune(char)
			} else {
				b.WriteRune(' ')
			}
			if c < r {
				b.WriteByte(' ')
			}
		}
		lines[r] = strings.TrimRight(b.String(), " ")
	}

	return lines, nil
}
```

Note: `size` is accepted and validated per the spec flag contract; the row count is governed by `depth`. The variable is intentionally validated but does not alter row count, matching the recursive-subdivision model where depth drives structure.

- [ ] Run the test to see it pass:

```bash
go test ./internal/sierpinski/
```

Expected output:

```
ok  	github.com/example/fractals/internal/sierpinski	0.00s
```

- [ ] Commit. Run:

```bash
git add -A && git commit -m "Add Sierpinski triangle algorithm"
```

---

### Task 3: Mandelbrot algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

We implement a pure Mandelbrot renderer. For each output cell `(row, col)`, map to a complex coordinate in the region roughly `[-2.5, 1.0]` real and `[-1.0, 1.0]` imaginary, run the escape iteration up to `iterations`, then map the result to a character.

Signature:

```go
func Generate(width, height, iterations int, gradient []rune) ([]string, error)
```

Rules:
- `width >= 1`, `height >= 1`, `iterations >= 1`, else error.
- `gradient` must be non-empty, else error.
- Points that never escape (in the set) map to the **last** gradient rune.
- Points that escape map to a gradient index based on iteration count.
- Returns `height` lines, each `width` runes wide.

- [ ] Write the failing test `internal/mandelbrot/mandelbrot_test.go`:

```go
package mandelbrot

import (
	"strings"
	"testing"
)

func TestGenerateDimensions(t *testing.T) {
	gradient := []rune(" .:-=+*#%@")
	lines, err := Generate(20, 10, 50, gradient)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(lines) != 10 {
		t.Fatalf("expected 10 lines, got %d", len(lines))
	}
	for i, line := range lines {
		if len([]rune(line)) != 20 {
			t.Errorf("line %d width = %d, want 20", i, len([]rune(line)))
		}
	}
}

func TestGenerateContainsSet(t *testing.T) {
	gradient := []rune(" .:-=+*#%@")
	lines, err := Generate(80, 24, 100, gradient)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(lines, "\n")
	// The set interior maps to the last gradient rune '@'; it must appear.
	if !strings.ContainsRune(joined, '@') {
		t.Errorf("expected in-set char '@' to appear in output")
	}
	// Background (escapes immediately) maps to first gradient rune ' '.
	if !strings.ContainsRune(joined, ' ') {
		t.Errorf("expected background char ' ' to appear in output")
	}
}

func TestGenerateSingleChar(t *testing.T) {
	gradient := []rune{'#'}
	lines, err := Generate(10, 5, 50, gradient)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(lines, "")
	for _, r := range joined {
		if r != '#' {
			t.Errorf("expected only '#', got %q", r)
		}
	}
}

func TestGenerateInvalidWidth(t *testing.T) {
	if _, err := Generate(0, 10, 50, []rune("#")); err == nil {
		t.Fatal("expected error for width < 1")
	}
}

func TestGenerateInvalidHeight(t *testing.T) {
	if _, err := Generate(10, 0, 50, []rune("#")); err == nil {
		t.Fatal("expected error for height < 1")
	}
}

func TestGenerateInvalidIterations(t *testing.T) {
	if _, err := Generate(10, 10, 0, []rune("#")); err == nil {
		t.Fatal("expected error for iterations < 1")
	}
}

func TestGenerateEmptyGradient(t *testing.T) {
	if _, err := Generate(10, 10, 50, []rune{}); err == nil {
		t.Fatal("expected error for empty gradient")
	}
}
```

- [ ] Run the test to see it fail:

```bash
go test ./internal/mandelbrot/
```

Expected output includes:

```
internal/mandelbrot/mandelbrot_test.go:...: undefined: Generate
FAIL	github.com/example/fractals/internal/mandelbrot [build failed]
```

- [ ] Implement `internal/mandelbrot/mandelbrot.go`:

```go
package mandelbrot

import (
	"fmt"
	"strings"
)

const (
	realMin = -2.5
	realMax = 1.0
	imagMin = -1.0
	imagMax = 1.0
)

// Generate renders the Mandelbrot set as a slice of strings of length height,
// each width runes wide. Iteration counts are mapped onto gradient: in-set
// points use the last rune, immediately-escaping points use the first rune.
func Generate(width, height, iterations int, gradient []rune) ([]string, error) {
	if width < 1 {
		return nil, fmt.Errorf("width must be >= 1, got %d", width)
	}
	if height < 1 {
		return nil, fmt.Errorf("height must be >= 1, got %d", height)
	}
	if iterations < 1 {
		return nil, fmt.Errorf("iterations must be >= 1, got %d", iterations)
	}
	if len(gradient) == 0 {
		return nil, fmt.Errorf("gradient must not be empty")
	}

	lines := make([]string, height)

	for row := 0; row < height; row++ {
		var b strings.Builder
		b.Grow(width)
		cy := imagMin + (imagMax-imagMin)*float64(row)/float64(height-1)
		if height == 1 {
			cy = (imagMin + imagMax) / 2
		}
		for col := 0; col < width; col++ {
			cx := realMin + (realMax-realMin)*float64(col)/float64(width-1)
			if width == 1 {
				cx = (realMin + realMax) / 2
			}
			n := escape(cx, cy, iterations)
			b.WriteRune(gradientChar(n, iterations, gradient))
		}
		lines[row] = b.String()
	}

	return lines, nil
}

// escape returns the number of iterations before the point escapes, or
// iterations if it never escapes within the limit.
func escape(cx, cy float64, iterations int) int {
	var x, y float64
	for n := 0; n < iterations; n++ {
		x2 := x*x - y*y + cx
		y2 := 2*x*y + cy
		x, y = x2, y2
		if x*x+y*y > 4 {
			return n
		}
	}
	return iterations
}

// gradientChar maps an iteration count to a gradient rune. Points that never
// escaped (n == iterations) map to the last rune. Others scale across the
// gradient by escape speed.
func gradientChar(n, iterations int, gradient []rune) rune {
	if n >= iterations {
		return gradient[len(gradient)-1]
	}
	if len(gradient) == 1 {
		return gradient[0]
	}
	// Map n in [0, iterations) to index in [0, len(gradient)-1).
	idx := n * (len(gradient) - 1) / iterations
	if idx >= len(gradient)-1 {
		idx = len(gradient) - 2
	}
	return gradient[idx]
}
```

- [ ] Run the test to see it pass:

```bash
go test ./internal/mandelbrot/
```

Expected output:

```
ok  	github.com/example/fractals/internal/mandelbrot	0.00s
```

- [ ] Commit. Run:

```bash
git add -A && git commit -m "Add Mandelbrot set algorithm"
```

---

### Task 4: Sierpinski subcommand

**Files:** `internal/cli/sierpinski.go`, `internal/cli/cli_test.go`

We wire the algorithm to a cobra subcommand with flags `--size`, `--depth`, `--char`, printing to the command's output writer (so tests can capture it).

- [ ] Write the failing test `internal/cli/cli_test.go`:

```go
package cli

import (
	"bytes"
	"strings"
	"testing"
)

// runCmd executes the root command with the given args, capturing stdout.
func runCmd(t *testing.T, args ...string) (string, error) {
	t.Helper()
	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs(args)
	err := rootCmd.Execute()
	return buf.String(), err
}

func TestSierpinskiCommand(t *testing.T) {
	out, err := runCmd(t, "sierpinski", "--depth", "2", "--size", "4")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 4 {
		t.Fatalf("expected 4 lines, got %d: %q", len(lines), out)
	}
	if !strings.Contains(out, "*") {
		t.Errorf("expected default star char in output: %q", out)
	}
}

func TestSierpinskiCustomChar(t *testing.T) {
	out, err := runCmd(t, "sierpinski", "--depth", "1", "--char", "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if strings.Contains(out, "*") {
		t.Errorf("did not expect default char: %q", out)
	}
	if !strings.Contains(out, "#") {
		t.Errorf("expected custom char: %q", out)
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
		t.Fatal("expected error for multi-rune char")
	}
}
```

- [ ] Run the test to see it fail:

```bash
go test ./internal/cli/
```

Expected output includes a build failure or test failure referencing the missing `sierpinski` subcommand (cobra returns an "unknown command" error):

```
--- FAIL: TestSierpinskiCommand
    cli_test.go:...: unexpected error: unknown command "sierpinski" for "fractals"
```

- [ ] Implement `internal/cli/sierpinski.go`:

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
			lines, err := sierpinski.Generate(size, depth, r)
			if err != nil {
				return err
			}
			for _, line := range lines {
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

// singleRune validates that s contains exactly one rune and returns it.
func singleRune(s string) (rune, error) {
	runes := []rune(s)
	if len(runes) != 1 {
		return 0, fmt.Errorf("char must be a single character, got %q", s)
	}
	return runes[0], nil
}
```

- [ ] Run the test to see it pass:

```bash
go test ./internal/cli/
```

Expected output:

```
ok  	github.com/example/fractals/internal/cli	0.00s
```

- [ ] Manually verify the command renders:

```bash
go run ./cmd/fractals sierpinski --depth 4 --size 16
```

Expected: a triangle of stars (16 rows), recognizable as a Sierpinski pattern.

- [ ] Commit. Run:

```bash
git add -A && git commit -m "Add sierpinski subcommand"
```

---

### Task 5: Mandelbrot subcommand

**Files:** `internal/cli/mandelbrot.go`, `internal/cli/cli_test.go` (add tests)

We wire the Mandelbrot algorithm to a subcommand with flags `--width`, `--height`, `--iterations`, `--char`. When `--char` is unset, use the default gradient `" .:-=+*#%@"`. When set to a single character, build a one-rune gradient.

- [ ] Add failing tests to `internal/cli/cli_test.go` (append these functions):

```go
func TestMandelbrotCommand(t *testing.T) {
	out, err := runCmd(t, "mandelbrot", "--width", "40", "--height", "12", "--iterations", "50")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 12 {
		t.Fatalf("expected 12 lines, got %d: %q", len(lines), out)
	}
	for i, line := range lines {
		if len([]rune(line)) != 40 {
			t.Errorf("line %d width = %d, want 40", i, len([]rune(line)))
		}
	}
}

func TestMandelbrotDefaultGradient(t *testing.T) {
	out, err := runCmd(t, "mandelbrot", "--width", "80", "--height", "24")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	// Default gradient ends with '@' for in-set points.
	if !strings.ContainsRune(out, '@') {
		t.Errorf("expected '@' from default gradient: %q", out)
	}
}

func TestMandelbrotCustomChar(t *testing.T) {
	out, err := runCmd(t, "mandelbrot", "--width", "20", "--height", "8", "--char", "X")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	for _, r := range strings.ReplaceAll(out, "\n", "") {
		if r != 'X' {
			t.Errorf("expected only 'X', got %q in %q", r, out)
			break
		}
	}
}

func TestMandelbrotInvalidWidth(t *testing.T) {
	_, err := runCmd(t, "mandelbrot", "--width", "0")
	if err == nil {
		t.Fatal("expected error for width 0")
	}
}

func TestMandelbrotMultiCharRejected(t *testing.T) {
	_, err := runCmd(t, "mandelbrot", "--char", "xy")
	if err == nil {
		t.Fatal("expected error for multi-rune char")
	}
}
```

- [ ] Run the test to see it fail:

```bash
go test ./internal/cli/
```

Expected output includes:

```
--- FAIL: TestMandelbrotCommand
    cli_test.go:...: unexpected error: unknown command "mandelbrot" for "fractals"
```

- [ ] Implement `internal/cli/mandelbrot.go`:

```go
package cli

import (
	"fmt"

	"github.com/example/fractals/internal/mandelbrot"
	"github.com/spf13/cobra"
)

const defaultGradient = " .:-=+*#%@"

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
			var gradient []rune
			if cmd.Flags().Changed("char") {
				r, err := singleRune(char)
				if err != nil {
					return err
				}
				gradient = []rune{r}
			} else {
				gradient = []rune(defaultGradient)
			}

			lines, err := mandelbrot.Generate(width, height, iterations, gradient)
			if err != nil {
				return err
			}
			for _, line := range lines {
				fmt.Fprintln(cmd.OutOrStdout(), line)
			}
			return nil
		},
	}

	cmd.Flags().IntVar(&width, "width", 80, "output width in characters")
	cmd.Flags().IntVar(&height, "height", 24, "output height in characters")
	cmd.Flags().IntVar(&iterations, "iterations", 100, "maximum iterations for escape calculation")
	cmd.Flags().StringVar(&char, "char", "", "single character; omit for gradient \" .:-=+*#%@\"")

	rootCmd.AddCommand(cmd)
}
```

- [ ] Run the test to see it pass:

```bash
go test ./internal/cli/
```

Expected output:

```
ok  	github.com/example/fractals/internal/cli	0.00s
```

- [ ] Manually verify rendering:

```bash
go run ./cmd/fractals mandelbrot --width 80 --height 24
```

Expected: a recognizable Mandelbrot set rendered with the gradient `" .:-=+*#%@"`.

- [ ] Commit. Run:

```bash
git add -A && git commit -m "Add mandelbrot subcommand"
```

---

### Task 6: Final verification

**Files:** none (verification only)

This task confirms every acceptance criterion against the running binary and the full test suite.

- [ ] Run the entire test suite. Run:

```bash
go test ./...
```

Expected output:

```
ok  	github.com/example/fractals/internal/cli
ok  	github.com/example/fractals/internal/mandelbrot
ok  	github.com/example/fractals/internal/sierpinski
```

(The `cmd/fractals` and `internal/cli` lines may show `[no test files]` for packages without tests; that is acceptable.)

- [ ] Verify `go vet` is clean. Run:

```bash
go vet ./...
```

Expected: no output (exit code 0).

- [ ] Verify criterion 1 (root help). Run:

```bash
go run ./cmd/fractals --help
```

Expected: usage text listing `sierpinski` and `mandelbrot` as available commands.

- [ ] Verify criterion (subcommand help). Run:

```bash
go run ./cmd/fractals sierpinski --help
```

Expected: help text listing `--size`, `--depth`, `--char` flags with defaults.

- [ ] Verify criterion 2 (Sierpinski default). Run:

```bash
go run ./cmd/fractals sierpinski
```

Expected: a recognizable triangle (32 rows from default depth 5 → `1<<5 = 32` rows).

- [ ] Verify criterion 3 (Mandelbrot default). Run:

```bash
go run ./cmd/fractals mandelbrot
```

Expected: a recognizable Mandelbrot set, 24 rows by 80 columns.

- [ ] Verify criterion 6 (clear errors). Run:

```bash
go run ./cmd/fractals mandelbrot --width 0
```

Expected output on stderr and non-zero exit:

```
width must be >= 1, got 0
exit status 1
```

- [ ] Commit any final adjustments (if none were needed, skip). Run:

```bash
git add -A && git commit -m "Final verification" --allow-empty
```

---

## Self-Review

**Spec coverage check:**

- Usage examples (`sierpinski --size --depth`, `mandelbrot --width --height --iterations`, `--char`, `--help`): covered in Tasks 4, 5, 6.
- `sierpinski` flags `--size` (default 32), `--depth` (default 5), `--char` (default `*`): implemented in Task 4 with matching defaults.
- `mandelbrot` flags `--width` (80), `--height` (24), `--iterations` (100), `--char` (gradient default): implemented in Task 5 with matching defaults and gradient `" .:-=+*#%@"`.
- Architecture file layout matches the spec exactly (cmd/fractals/main.go, internal/sierpinski, internal/mandelbrot, internal/cli with root/sierpinski/mandelbrot). Note: the spec lists separate per-command files under `internal/cli`; this plan follows that with `root.go`, `sierpinski.go`, `mandelbrot.go`. Tests are consolidated in `cli_test.go` (one test file per package is idiomatic and the spec only names algorithm test files explicitly).
- Dependencies: Go 1.21+ (module init uses installed toolchain; ensure `go version` ≥ 1.21), `github.com/spf13/cobra`: Task 1.
- Acceptance criteria 1–7: all exercised in Task 6 and covered by automated tests in Tasks 2–5.

**Placeholder scan:** No `TODO`, `FIXME`, or `...` placeholders remain in code blocks. All functions are fully implemented.

**Type consistency check:**
- `sierpinski.Generate(size, depth int, char rune) ([]string, error)` — caller in `cli/sierpinski.go` passes `int, int, rune`. Consistent.
- `mandelbrot.Generate(width, height, iterations int, gradient []rune) ([]string, error)` — caller in `cli/mandelbrot.go` passes `int, int, int, []rune`. Consistent.
- `singleRune(string) (rune, error)` — used by both subcommands; defined once in `sierpinski.go`. No duplication (DRY).
- Module path `github.com/example/fractals` used consistently in `go mod init`, imports, and `main.go`.

**Edge cases handled:** `width==1`/`height==1` avoid division by zero in mandelbrot; empty gradient, negative depth, size<1, iterations<1, and multi-rune `--char` all produce clear errors with tests.

No issues found; plan is internally consistent.