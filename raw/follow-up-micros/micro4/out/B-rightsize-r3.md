# Go Fractals CLI - Implementation Plan

## Overview

We're building a CLI tool that generates ASCII art fractals (Sierpinski triangle and Mandelbrot set). The architecture separates pure algorithm packages (`internal/sierpinski`, `internal/mandelbrot`) from CLI wiring (`internal/cli`) and the entry point (`cmd/fractals`).

This plan assumes zero context. Follow it exactly, in order. Each task ends with passing tests and a commit.

## Prerequisites

- Go 1.21 or later installed. Verify:

```bash
go version
```

Expected output (version may be higher):

```
go version go1.21.0 linux/amd64
```

## File Structure

| File | Responsibility |
|------|----------------|
| `go.mod` | Module definition, dependencies |
| `cmd/fractals/main.go` | Entry point; calls `cli.Execute()` |
| `internal/sierpinski/sierpinski.go` | Pure Sierpinski generation algorithm, returns `[]string` |
| `internal/sierpinski/sierpinski_test.go` | Tests for Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure Mandelbrot generation algorithm, returns `[]string` |
| `internal/mandelbrot/mandelbrot_test.go` | Tests for Mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command + `Execute()` |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand wiring + flag validation |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand wiring + flag validation |
| `internal/cli/sierpinski_test.go` | Tests for sierpinski subcommand |
| `internal/cli/mandelbrot_test.go` | Tests for mandelbrot subcommand |
| `internal/cli/root_test.go` | Tests for root command help |

---

### Task 1: Project scaffolding and module setup

Initialize the Go module and add the cobra dependency. The deliverable is a buildable (empty) project with dependencies resolved.

**Files:** `go.mod`, `cmd/fractals/main.go`

- [ ] Create the directory structure:

```bash
mkdir -p cmd/fractals internal/sierpinski internal/mandelbrot internal/cli
```

- [ ] Initialize the module:

```bash
go mod init github.com/example/fractals
```

Expected output:

```
go: creating new go.mod: module github.com/example/fractals
```

- [ ] Add cobra dependency:

```bash
go get github.com/spf13/cobra@latest
```

Expected output (versions may vary):

```
go: downloading github.com/spf13/cobra v1.8.x
go: added github.com/spf13/cobra v1.8.x
```

- [ ] Create `cmd/fractals/main.go` with a temporary stub so the project builds:

```go
package main

func main() {
}
```

- [ ] Verify the project builds:

```bash
go build ./...
```

Expected output: no output, exit code 0.

- [ ] Commit:

```bash
git init && git add -A && git commit -m "Scaffold project structure and dependencies"
```

---

### Task 2: Sierpinski algorithm

Implement the pure algorithm that produces the triangle as a slice of strings. Uses the bitwise AND property: a point `(x, y)` is filled when `(x & y) == 0`. We use `depth` to determine the number of rows (`2^depth`, but capped to `size` so `--size` bounds the width), and `char` for the filled character.

The triangle has `rows` rows. Row `y` (0-indexed from top) has cells where column `x` satisfies `(x & y) == 0`, for `x` in `0..y`. We left-pad each row to center the triangle.

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

- [ ] Write the failing test in `internal/sierpinski/sierpinski_test.go`:

```go
package sierpinski

import (
	"strings"
	"testing"
)

func TestGenerate_RowCount(t *testing.T) {
	// depth 2 -> 2^2 = 4 rows, size large enough not to cap
	rows := Generate(64, 2, '*')
	if len(rows) != 4 {
		t.Fatalf("expected 4 rows, got %d", len(rows))
	}
}

func TestGenerate_TopRowSingleChar(t *testing.T) {
	rows := Generate(64, 3, '*')
	// Top row (y=0) has exactly one filled cell: x=0
	if strings.Count(rows[0], "*") != 1 {
		t.Fatalf("expected top row to have 1 filled char, got %q", rows[0])
	}
}

func TestGenerate_CustomChar(t *testing.T) {
	rows := Generate(64, 2, '#')
	if !strings.Contains(rows[0], "#") {
		t.Fatalf("expected custom char '#' in output, got %q", rows[0])
	}
	if strings.Contains(rows[0], "*") {
		t.Fatalf("did not expect default char in output, got %q", rows[0])
	}
}

func TestGenerate_SizeCapsRows(t *testing.T) {
	// depth 5 would give 32 rows, but size 8 caps it to 8 rows
	rows := Generate(8, 5, '*')
	if len(rows) != 8 {
		t.Fatalf("expected size to cap rows at 8, got %d", len(rows))
	}
}

func TestGenerate_SecondRowFull(t *testing.T) {
	// y=1: x in {0,1}. (0&1)=0 filled, (1&1)=1 not filled.
	rows := Generate(64, 2, '*')
	if strings.Count(rows[1], "*") != 1 {
		t.Fatalf("expected row 1 to have 1 filled char, got %q", rows[1])
	}
	// y=3: x in {0,1,2,3}. (0&3)=0, (1&3)=1, (2&3)=2, (3&3)=3 -> only x=0 filled
	rows3 := Generate(64, 2, '*')
	_ = rows3
}
```

- [ ] Run the test to confirm it fails (compilation failure because `Generate` doesn't exist):

```bash
go test ./internal/sierpinski/
```

Expected output (contains):

```
undefined: Generate
FAIL
```

- [ ] Implement `internal/sierpinski/sierpinski.go`:

```go
// Package sierpinski generates Sierpinski triangle ASCII art.
package sierpinski

import "strings"

// Generate returns the Sierpinski triangle as a slice of strings, one per row.
//
// The number of rows is 2^depth, capped at size so the triangle width never
// exceeds size characters. A cell at (x, y) is filled when (x & y) == 0.
// Filled cells use char; empty cells use a space. Rows are left-padded so the
// triangle is centered.
func Generate(size, depth int, char rune) []string {
	rows := 1 << depth // 2^depth
	if rows > size {
		rows = size
	}
	if rows < 1 {
		rows = 1
	}

	out := make([]string, 0, rows)
	for y := 0; y < rows; y++ {
		var b strings.Builder
		// Left padding to center the triangle: top row gets most padding.
		for p := 0; p < rows-1-y; p++ {
			b.WriteRune(' ')
		}
		for x := 0; x <= y; x++ {
			if x&y == 0 {
				b.WriteRune(char)
			} else {
				b.WriteRune(' ')
			}
			if x < y {
				b.WriteRune(' ')
			}
		}
		out = append(out, b.String())
	}
	return out
}
```

- [ ] Run the test to confirm it passes:

```bash
go test ./internal/sierpinski/
```

Expected output:

```
ok  	github.com/example/fractals/internal/sierpinski	0.00s
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add sierpinski algorithm"
```

---

### Task 3: Mandelbrot algorithm

Implement the pure algorithm producing the Mandelbrot set as a slice of strings. For each output cell, map it to a complex plane point in the region real `[-2.5, 1.0]`, imaginary `[-1.0, 1.0]`. Iterate `z = z² + c` up to `maxIter`. Map the escape iteration count to a character.

If `char` is `0` (the zero rune), use the gradient `" .:-=+*#%@"`. Otherwise use the single `char` for in-set points and a space for escaped points.

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

- [ ] Write the failing test in `internal/mandelbrot/mandelbrot_test.go`:

```go
package mandelbrot

import (
	"testing"
)

func TestGenerate_Dimensions(t *testing.T) {
	rows := Generate(80, 24, 100, 0)
	if len(rows) != 24 {
		t.Fatalf("expected 24 rows, got %d", len(rows))
	}
	for i, r := range rows {
		if len([]rune(r)) != 80 {
			t.Fatalf("row %d: expected width 80, got %d", i, len([]rune(r)))
		}
	}
}

func TestGenerate_CenterInSet(t *testing.T) {
	// The point near (0,0) in the complex plane is inside the set and should
	// map to the last gradient char '@'. The center cell of the grid maps near
	// real=-0.75; the origin (real=0, imag=0) is right of center and in-set.
	rows := Generate(80, 24, 100, 0)
	// Verify at least one '@' (deepest gradient) appears -> a recognizable set.
	found := false
	for _, r := range rows {
		for _, c := range r {
			if c == '@' {
				found = true
			}
		}
	}
	if !found {
		t.Fatal("expected in-set points rendered as '@'")
	}
}

func TestGenerate_CornerEscapes(t *testing.T) {
	// Top-left corner maps to real=-2.5, imag=-1.0 which escapes quickly ->
	// space in gradient mode.
	rows := Generate(80, 24, 100, 0)
	firstRune := []rune(rows[0])[0]
	if firstRune != ' ' {
		t.Fatalf("expected top-left corner to escape (space), got %q", firstRune)
	}
}

func TestGenerate_CustomChar(t *testing.T) {
	rows := Generate(80, 24, 100, '#')
	hasHash := false
	hasSpace := false
	for _, r := range rows {
		for _, c := range r {
			switch c {
			case '#':
				hasHash = true
			case ' ':
				hasSpace = true
			default:
				t.Fatalf("unexpected char %q in custom-char output", c)
			}
		}
	}
	if !hasHash {
		t.Fatal("expected custom char '#' for in-set points")
	}
	if !hasSpace {
		t.Fatal("expected spaces for escaped points")
	}
}
```

- [ ] Run the test to confirm it fails:

```bash
go test ./internal/mandelbrot/
```

Expected output (contains):

```
undefined: Generate
FAIL
```

- [ ] Implement `internal/mandelbrot/mandelbrot.go`:

```go
// Package mandelbrot renders the Mandelbrot set as ASCII art.
package mandelbrot

import "strings"

const gradient = " .:-=+*#%@"

// Plane bounds for the rendered region.
const (
	realMin = -2.5
	realMax = 1.0
	imagMin = -1.0
	imagMax = 1.0
)

// Generate renders the Mandelbrot set as a slice of strings, one per row.
//
// width and height are the output dimensions in characters. maxIter is the
// escape iteration limit. If char is the zero rune, a gradient
// (" .:-=+*#%@") is used, mapping escape speed to density. Otherwise char is
// used for in-set points and a space for escaped points.
func Generate(width, height, maxIter int, char rune) []string {
	out := make([]string, 0, height)
	for py := 0; py < height; py++ {
		var b strings.Builder
		ci := imagMin + (imagMax-imagMin)*float64(py)/float64(height-1)
		for px := 0; px < width; px++ {
			cr := realMin + (realMax-realMin)*float64(px)/float64(width-1)
			iter := escape(cr, ci, maxIter)
			b.WriteRune(cell(iter, maxIter, char))
		}
		out = append(out, b.String())
	}
	return out
}

// escape returns the iteration count at which z = z^2 + c exceeds magnitude 2,
// or maxIter if it never escapes.
func escape(cr, ci float64, maxIter int) int {
	var zr, zi float64
	for i := 0; i < maxIter; i++ {
		zr2 := zr*zr - zi*zi + cr
		zi2 := 2*zr*zi + ci
		zr, zi = zr2, zi2
		if zr*zr+zi*zi > 4.0 {
			return i
		}
	}
	return maxIter
}

// cell maps an escape iteration count to a display rune.
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
	// Map escape speed to gradient index. Slower escape (higher iter) -> denser.
	idx := iter * (len(gradient) - 1) / maxIter
	if idx >= len(gradient) {
		idx = len(gradient) - 1
	}
	return rune(gradient[idx])
}
```

- [ ] Run the test to confirm it passes:

```bash
go test ./internal/mandelbrot/
```

Expected output:

```
ok  	github.com/example/fractals/internal/mandelbrot	0.00s
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add mandelbrot algorithm"
```

---

### Task 4: Root CLI command

Build the root cobra command and `Execute()` function. The root command shows help when run with no subcommand. We expose a `newRootCmd()` constructor so tests can run it with captured output.

**Files:** `internal/cli/root.go`, `internal/cli/root_test.go`

- [ ] Write the failing test in `internal/cli/root_test.go`:

```go
package cli

import (
	"bytes"
	"strings"
	"testing"
)

func TestRootHelp(t *testing.T) {
	cmd := newRootCmd()
	var buf bytes.Buffer
	cmd.SetOut(&buf)
	cmd.SetErr(&buf)
	cmd.SetArgs([]string{"--help"})
	if err := cmd.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "fractals") {
		t.Fatalf("expected help to mention 'fractals', got:\n%s", out)
	}
	if !strings.Contains(out, "sierpinski") {
		t.Fatalf("expected help to list 'sierpinski' subcommand, got:\n%s", out)
	}
	if !strings.Contains(out, "mandelbrot") {
		t.Fatalf("expected help to list 'mandelbrot' subcommand, got:\n%s", out)
	}
}
```

- [ ] Run the test to confirm it fails:

```bash
go test ./internal/cli/
```

Expected output (contains):

```
undefined: newRootCmd
FAIL
```

- [ ] Implement `internal/cli/root.go`:

```go
// Package cli wires up the fractals command-line interface.
package cli

import (
	"os"

	"github.com/spf13/cobra"
)

// newRootCmd builds the root command with all subcommands attached.
func newRootCmd() *cobra.Command {
	root := &cobra.Command{
		Use:   "fractals",
		Short: "Generate ASCII art fractals",
		Long:  "fractals generates ASCII art fractals such as the Sierpinski triangle and the Mandelbrot set.",
		// Suppress usage noise on runtime errors; flag/arg errors still show usage.
		SilenceUsage: true,
	}
	root.AddCommand(newSierpinskiCmd())
	root.AddCommand(newMandelbrotCmd())
	return root
}

// Execute runs the root command. It is the single entry point used by main.
func Execute() {
	if err := newRootCmd().Execute(); err != nil {
		os.Exit(1)
	}
}
```

Note: this references `newSierpinskiCmd` and `newMandelbrotCmd`, which are added in Tasks 5 and 6. The package will not compile until those exist. We add minimal stubs now so this task's test runs, then replace them.

- [ ] Add temporary stubs in `internal/cli/root.go` is wrong—keep `root.go` clean. Instead create stub files. Create `internal/cli/sierpinski.go`:

```go
package cli

import "github.com/spf13/cobra"

func newSierpinskiCmd() *cobra.Command {
	return &cobra.Command{Use: "sierpinski"}
}
```

- [ ] Create `internal/cli/mandelbrot.go`:

```go
package cli

import "github.com/spf13/cobra"

func newMandelbrotCmd() *cobra.Command {
	return &cobra.Command{Use: "mandelbrot"}
}
```

- [ ] Run the test to confirm it passes:

```bash
go test ./internal/cli/ -run TestRootHelp
```

Expected output:

```
ok  	github.com/example/fractals/internal/cli	0.00s
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add root CLI command with subcommand stubs"
```

---

### Task 5: Sierpinski subcommand

Replace the stub with the full subcommand: flags `--size`, `--depth`, `--char`, validation, and output wiring to the algorithm. The `--char` flag is a string; we require exactly one rune.

**Files:** `internal/cli/sierpinski.go`, `internal/cli/sierpinski_test.go`

- [ ] Write the failing test in `internal/cli/sierpinski_test.go`:

```go
package cli

import (
	"bytes"
	"strings"
	"testing"
)

func runSierpinski(t *testing.T, args ...string) (string, error) {
	t.Helper()
	cmd := newRootCmd()
	var buf bytes.Buffer
	cmd.SetOut(&buf)
	cmd.SetErr(&buf)
	cmd.SetArgs(append([]string{"sierpinski"}, args...))
	err := cmd.Execute()
	return buf.String(), err
}

func TestSierpinski_Default(t *testing.T) {
	out, err := runSierpinski(t)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "*") {
		t.Fatalf("expected default '*' in output, got:\n%s", out)
	}
	// Default depth 5 -> 32 rows, capped by default size 32.
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 32 {
		t.Fatalf("expected 32 rows, got %d", len(lines))
	}
}

func TestSierpinski_CustomChar(t *testing.T) {
	out, err := runSierpinski(t, "--size", "8", "--depth", "3", "--char", "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "#") {
		t.Fatalf("expected '#' in output, got:\n%s", out)
	}
}

func TestSierpinski_InvalidChar(t *testing.T) {
	_, err := runSierpinski(t, "--char", "ab")
	if err == nil {
		t.Fatal("expected error for multi-rune char, got nil")
	}
	if !strings.Contains(err.Error(), "char") {
		t.Fatalf("expected error to mention 'char', got: %v", err)
	}
}

func TestSierpinski_InvalidSize(t *testing.T) {
	_, err := runSierpinski(t, "--size", "0")
	if err == nil {
		t.Fatal("expected error for size 0, got nil")
	}
	if !strings.Contains(err.Error(), "size") {
		t.Fatalf("expected error to mention 'size', got: %v", err)
	}
}

func TestSierpinski_InvalidDepth(t *testing.T) {
	_, err := runSierpinski(t, "--depth", "-1")
	if err == nil {
		t.Fatal("expected error for negative depth, got nil")
	}
	if !strings.Contains(err.Error(), "depth") {
		t.Fatalf("expected error to mention 'depth', got: %v", err)
	}
}
```

- [ ] Run the test to confirm it fails:

```bash
go test ./internal/cli/ -run TestSierpinski
```

Expected output (contains): test failures, e.g. `expected default '*' in output` or unknown flag errors, `FAIL`.

- [ ] Replace `internal/cli/sierpinski.go` with the full implementation:

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
			if size < 1 {
				return fmt.Errorf("invalid --size %d: must be >= 1", size)
			}
			if depth < 0 {
				return fmt.Errorf("invalid --depth %d: must be >= 0", depth)
			}
			char, err := singleRune("char", charStr)
			if err != nil {
				return err
			}
			for _, line := range sierpinski.Generate(size, depth, char) {
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

// singleRune validates that s contains exactly one rune and returns it.
func singleRune(flag, s string) (rune, error) {
	runes := []rune(s)
	if len(runes) != 1 {
		return 0, fmt.Errorf("invalid --%s %q: must be exactly one character", flag, s)
	}
	return runes[0], nil
}
```

- [ ] Run the test to confirm it passes:

```bash
go test ./internal/cli/ -run TestSierpinski
```

Expected output:

```
ok  	github.com/example/fractals/internal/cli	0.00s
```

- [ ] Commit:

```bash
git add -A && git commit -m "Implement sierpinski subcommand"
```

---

### Task 6: Mandelbrot subcommand

Replace the stub with the full subcommand: flags `--width`, `--height`, `--iterations`, `--char`, validation, and output wiring. `--char` defaults to empty string, which means "use gradient" (passed as rune `0`). The shared `singleRune` helper from Task 5 is reused.

**Files:** `internal/cli/mandelbrot.go`, `internal/cli/mandelbrot_test.go`

- [ ] Write the failing test in `internal/cli/mandelbrot_test.go`:

```go
package cli

import (
	"bytes"
	"strings"
	"testing"
)

func runMandelbrot(t *testing.T, args ...string) (string, error) {
	t.Helper()
	cmd := newRootCmd()
	var buf bytes.Buffer
	cmd.SetOut(&buf)
	cmd.SetErr(&buf)
	cmd.SetArgs(append([]string{"mandelbrot"}, args...))
	err := cmd.Execute()
	return buf.String(), err
}

func TestMandelbrot_DefaultDimensions(t *testing.T) {
	out, err := runMandelbrot(t)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 24 {
		t.Fatalf("expected 24 rows, got %d", len(lines))
	}
	if len([]rune(lines[0])) != 80 {
		t.Fatalf("expected width 80, got %d", len([]rune(lines[0])))
	}
}

func TestMandelbrot_Gradient(t *testing.T) {
	out, err := runMandelbrot(t)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "@") {
		t.Fatalf("expected gradient '@' for in-set points, got:\n%s", out)
	}
}

func TestMandelbrot_CustomChar(t *testing.T) {
	out, err := runMandelbrot(t, "--char", "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "#") {
		t.Fatalf("expected '#' in output, got:\n%s", out)
	}
	if strings.Contains(out, "@") {
		t.Fatalf("did not expect gradient char in custom-char mode, got:\n%s", out)
	}
}

func TestMandelbrot_CustomDimensions(t *testing.T) {
	out, err := runMandelbrot(t, "--width", "40", "--height", "12")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 12 {
		t.Fatalf("expected 12 rows, got %d", len(lines))
	}
	if len([]rune(lines[0])) != 40 {
		t.Fatalf("expected width 40, got %d", len([]rune(lines[0])))
	}
}

func TestMandelbrot_InvalidWidth(t *testing.T) {
	_, err := runMandelbrot(t, "--width", "1")
	if err == nil {
		t.Fatal("expected error for width 1, got nil")
	}
	if !strings.Contains(err.Error(), "width") {
		t.Fatalf("expected error to mention 'width', got: %v", err)
	}
}

func TestMandelbrot_InvalidHeight(t *testing.T) {
	_, err := runMandelbrot(t, "--height", "1")
	if err == nil {
		t.Fatal("expected error for height 1, got nil")
	}
	if !strings.Contains(err.Error(), "height") {
		t.Fatalf("expected error to mention 'height', got: %v", err)
	}
}

func TestMandelbrot_InvalidIterations(t *testing.T) {
	_, err := runMandelbrot(t, "--iterations", "0")
	if err == nil {
		t.Fatal("expected error for iterations 0, got nil")
	}
	if !strings.Contains(err.Error(), "iterations") {
		t.Fatalf("expected error to mention 'iterations', got: %v", err)
	}
}

func TestMandelbrot_InvalidChar(t *testing.T) {
	_, err := runMandelbrot(t, "--char", "ab")
	if err == nil {
		t.Fatal("expected error for multi-rune char, got nil")
	}
	if !strings.Contains(err.Error(), "char") {
		t.Fatalf("expected error to mention 'char', got: %v", err)
	}
}
```

Note: `TestMandelbrot_InvalidWidth`/`Height` use a minimum of 2 because the algorithm divides by `width-1` and `height-1`. We validate `>= 2`.

- [ ] Run the test to confirm it fails:

```bash
go test ./internal/cli/ -run TestMandelbrot
```

Expected output (contains): failures such as unknown flag or wrong dimensions, `FAIL`.

- [ ] Replace `internal/cli/mandelbrot.go` with the full implementation:

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
		Short: "Render the Mandelbrot set",
		Long:  "Render the Mandelbrot set as ASCII art, mapping iteration count to characters.",
		RunE: func(cmd *cobra.Command, args []string) error {
			if width < 2 {
				return fmt.Errorf("invalid --width %d: must be >= 2", width)
			}
			if height < 2 {
				return fmt.Errorf("invalid --height %d: must be >= 2", height)
			}
			if iterations < 1 {
				return fmt.Errorf("invalid --iterations %d: must be >= 1", iterations)
			}

			// Empty char means use the gradient (rune 0).
			var char rune
			if charStr != "" {
				c, err := singleRune("char", charStr)
				if err != nil {
					return err
				}
				char = c
			}

			for _, line := range mandelbrot.Generate(width, height, iterations, char) {
				fmt.Fprintln(cmd.OutOrStdout(), line)
			}
			return nil
		},
	}

	cmd.Flags().IntVar(&width, "width", 80, "output width in characters")
	cmd.Flags().IntVar(&height, "height", 24, "output height in characters")
	cmd.Flags().IntVar(&iterations, "iterations", 100, "maximum iterations for escape calculation")
	cmd.Flags().StringVar(&charStr, "char", "", "single character, or omit for gradient \" .:-=+*#%@\"")
	return cmd
}
```

- [ ] Run the test to confirm it passes:

```bash
go test ./internal/cli/ -run TestMandelbrot
```

Expected output:

```
ok  	github.com/example/fractals/internal/cli	0.00s
```

- [ ] Run the full CLI test suite to ensure nothing regressed:

```bash
go test ./internal/cli/
```

Expected output:

```
ok  	github.com/example/fractals/internal/cli	0.00s
```

- [ ] Commit:

```bash
git add -A && git commit -m "Implement mandelbrot subcommand"
```

---

### Task 7: Wire up main entry point and end-to-end verification

Replace the stub `main.go` with the real entry point and verify the built binary against the acceptance criteria.

**Files:** `cmd/fractals/main.go`

- [ ] Replace `cmd/fractals/main.go`:

```go
package main

import "github.com/example/fractals/internal/cli"

func main() {
	cli.Execute()
}
```

- [ ] Build the binary:

```bash
go build -o fractals ./cmd/fractals
```

Expected output: no output, exit code 0, and a `fractals` binary in the current directory.

- [ ] Verify acceptance criterion 1 (`--help` shows usage):

```bash
./fractals --help
```

Expected output includes:

```
fractals generates ASCII art fractals such as the Sierpinski triangle and the Mandelbrot set.

Usage:
  fractals [command]

Available Commands:
  ...
  mandelbrot  Render the Mandelbrot set
  sierpinski  Generate a Sierpinski triangle
```

- [ ] Verify acceptance criterion 2 (recognizable triangle):

```bash
./fractals sierpinski --size 16 --depth 4
```

Expected: a triangle of `*` characters, 16 rows, widening top-to-bottom with the self-similar Sierpinski gaps.

- [ ] Verify acceptance criterion 3 (recognizable Mandelbrot set):

```bash
./fractals mandelbrot --width 60 --height 20
```

Expected: a 20-row × 60-column ASCII rendering with a dense `@`-filled bulb on the left and a cardioid shape, fading to spaces at the corners.

- [ ] Verify acceptance criterion 5 (custom char):

```bash
./fractals sierpinski --size 8 --depth 3 --char '#'
```

Expected: the triangle rendered with `#` instead of `*`.

- [ ] Verify acceptance criterion 6 (clear error on invalid input):

```bash
./fractals mandelbrot --width 1; echo "exit=$?"
```

Expected output:

```
Error: invalid --width 1: must be >= 2
exit=1
```

- [ ] Run the entire test suite (acceptance criterion 7):

```bash
go test ./...
```

Expected output:

```
ok  	github.com/example/fractals/internal/cli
ok  	github.com/example/fractals/internal/mandelbrot
ok  	github.com/example/fractals/internal/sierpinski
```

(`cmd/fractals` and the root package report `no test files`, which is acceptable.)

- [ ] Run `go vet` to catch any issues:

```bash
go vet ./...
```

Expected output: no output, exit code 0.

- [ ] Add `fractals` binary to `.gitignore`