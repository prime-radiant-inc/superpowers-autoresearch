# Go Fractals CLI - Implementation Plan

## Overview

We are building a command-line tool that renders ASCII art fractals (Sierpinski triangle and Mandelbrot set). The work proceeds bottom-up: pure algorithm packages first (fully unit-tested), then the Cobra CLI layer wired on top, then the entry point.

This plan assumes **zero context**. Follow every step literally. Each task ends with a green test run and a commit.

## Prerequisites

- Go 1.21 or later installed. Verify:

```bash
go version
```

Expected output (version may be higher):

```
go version go1.21.0 darwin/arm64
```

## File Structure

| File | Responsibility |
|------|----------------|
| `go.mod` | Module definition, Go version, dependency on cobra |
| `internal/sierpinski/sierpinski.go` | Pure function: produce Sierpinski triangle as `[]string` |
| `internal/sierpinski/sierpinski_test.go` | Unit tests for the Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure function: produce Mandelbrot render as `[]string` |
| `internal/mandelbrot/mandelbrot_test.go` | Unit tests for the Mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command, help wiring, `Execute()` |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand: flag parsing, validation, output |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand: flag parsing, validation, output |
| `internal/cli/cli_test.go` | Integration tests that run commands and assert on output |
| `cmd/fractals/main.go` | Entry point: calls `cli.Execute()` |

Design conventions used throughout:

- Algorithm packages are **pure**: they take parameters, return `([]string, error)`, and never touch stdout. This makes them trivially testable.
- The CLI layer handles flags, validation, and printing.
- Errors for invalid input are returned, not panicked.

---

### Task 1: Module setup and dependency

**Files:** `go.mod`

- [ ] Create the module. Run from the repository root:

```bash
go mod init github.com/example/fractals
```

Expected output:

```
go: creating new go.mod: module github.com/example/fractals
```

- [ ] Add the cobra dependency:

```bash
go get github.com/spf13/cobra@latest
```

Expected output (versions may differ):

```
go: added github.com/spf13/cobra v1.8.0
```

- [ ] Confirm `go.mod` now lists Go version and cobra. Run:

```bash
cat go.mod
```

Expected output contains (exact patch versions may differ):

```
module github.com/example/fractals

go 1.21

require github.com/spf13/cobra v1.8.0

require (
	github.com/inconshreveable/mousetrap v1.1.0 // indirect
	github.com/spf13/pflag v1.0.5 // indirect
)
```

If the `go 1.21` line shows a higher version (e.g. `go 1.22`), that is fine.

- [ ] Commit:

```bash
git add go.mod go.sum
git commit -m "Initialize module and add cobra dependency"
```

---

### Task 2: Sierpinski algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

The algorithm uses the classic bitwise property: cell `(row, col)` is filled if `(row & col) == 0` is **not** the rule we want — the standard ASCII Sierpinski uses: a point is filled when `(x & y) == 0`. We render `size` rows. For row `y` (0-indexed from the top, where the apex is at top), we indent and place a character at column `x` when `x AND (size-1-y) ... ` — to keep it simple and well-defined we use the established Pascal-triangle-mod-2 form below.

We define the output as `size` rows. Row `r` (0 = top apex) contains characters for `r+1` triangle positions, where position `c` (0..r) is filled when `(c & (r - c)) == 0`. Each row is left-padded with `size - 1 - r` spaces so the triangle is centered. Filled positions use `char`; unfilled use a space. Positions are separated by a single space for visual clarity.

`depth` controls how many recursive subdivisions are *masked*: we only render rows `r` where `r < size`, and a row is included fully; `depth` limits the effective resolution by rendering only the top `min(size, 2^depth)` rows. This keeps both flags meaningful.

- [ ] Create the test file with a failing test. Create `internal/sierpinski/sierpinski_test.go`:

```go
package sierpinski

import (
	"strings"
	"testing"
)

func TestGenerateReturnsRequestedRows(t *testing.T) {
	rows, err := Generate(4, 5, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 4 {
		t.Fatalf("expected 4 rows, got %d", len(rows))
	}
}

func TestGenerateApexIsSingleChar(t *testing.T) {
	rows, err := Generate(4, 5, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if strings.Count(rows[0], "*") != 1 {
		t.Fatalf("expected apex row to contain exactly one '*', got %q", rows[0])
	}
}

func TestGenerateUsesCustomChar(t *testing.T) {
	rows, err := Generate(4, 5, '#')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(rows, "\n")
	if strings.Contains(joined, "*") {
		t.Fatalf("output should not contain default '*' when custom char used: %q", joined)
	}
	if !strings.Contains(joined, "#") {
		t.Fatalf("output should contain custom '#': %q", joined)
	}
}

func TestGenerateRejectsNonPositiveSize(t *testing.T) {
	if _, err := Generate(0, 5, '*'); err == nil {
		t.Fatal("expected error for size 0")
	}
	if _, err := Generate(-3, 5, '*'); err == nil {
		t.Fatal("expected error for negative size")
	}
}

func TestGenerateRejectsNegativeDepth(t *testing.T) {
	if _, err := Generate(8, -1, '*'); err == nil {
		t.Fatal("expected error for negative depth")
	}
}

func TestGenerateDepthLimitsRows(t *testing.T) {
	// depth 1 => 2^1 = 2 effective rows even though size is 8
	rows, err := Generate(8, 1, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 2 {
		t.Fatalf("expected 2 rows for depth 1, got %d", len(rows))
	}
}
```

- [ ] Run the test to see it fail (package does not compile yet):

```bash
go test ./internal/sierpinski/
```

Expected output (the key signal is failure):

```
internal/sierpinski/sierpinski_test.go:9:14: undefined: Generate
FAIL	github.com/example/fractals/internal/sierpinski [build failed]
```

- [ ] Implement the algorithm. Create `internal/sierpinski/sierpinski.go`:

```go
// Package sierpinski generates Sierpinski triangle ASCII art.
package sierpinski

import "fmt"

// Generate returns the Sierpinski triangle as a slice of strings, one per row.
//
// size is the number of rows in the full triangle. depth limits the effective
// resolution to the top 2^depth rows (capped at size). char is the rune used
// for filled cells.
func Generate(size, depth int, char rune) ([]string, error) {
	if size <= 0 {
		return nil, fmt.Errorf("size must be positive, got %d", size)
	}
	if depth < 0 {
		return nil, fmt.Errorf("depth must be non-negative, got %d", depth)
	}

	effectiveRows := size
	if limit := 1 << depth; limit < effectiveRows {
		effectiveRows = limit
	}

	rows := make([]string, 0, effectiveRows)
	for r := 0; r < effectiveRows; r++ {
		line := make([]rune, 0, effectiveRows*2)
		// Left padding so the triangle is centered under its base.
		for p := 0; p < effectiveRows-1-r; p++ {
			line = append(line, ' ')
		}
		for c := 0; c <= r; c++ {
			if c&(r-c) == 0 {
				line = append(line, char)
			} else {
				line = append(line, ' ')
			}
			if c < r {
				line = append(line, ' ')
			}
		}
		rows = append(rows, string(line))
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
ok  	github.com/example/fractals/internal/sierpinski	0.XXXs
```

- [ ] Commit:

```bash
git add internal/sierpinski/
git commit -m "Add Sierpinski triangle algorithm with tests"
```

---

### Task 3: Mandelbrot algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

The Mandelbrot function maps a `width x height` grid onto the complex plane region real ∈ [-2.5, 1.0], imaginary ∈ [-1.25, 1.25]. For each cell it iterates `z = z² + c` up to `iterations` times, counting how many steps before |z| > 2. The escape count is mapped to a character.

The gradient string is `" .:-=+*#%@"` (10 chars). When a custom single char is supplied (`char != 0`), points *inside* the set (never escaped) render as that char and points outside render as a space. When `char == 0`, the gradient is used: escape count scaled into the gradient index, with non-escaping (in-set) points using the last gradient character `'@'`.

- [ ] Create the test file. Create `internal/mandelbrot/mandelbrot_test.go`:

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
			t.Fatalf("row %d: expected width 20, got %d (%q)", i, len([]rune(row)), row)
		}
	}
}

func TestGenerateGradientContainsInSetChar(t *testing.T) {
	// The center region of the plane is inside the set and should render '@'.
	rows, err := Generate(80, 24, 100, 0)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(rows, "\n")
	if !strings.Contains(joined, "@") {
		t.Fatalf("expected gradient output to contain in-set char '@'")
	}
	if !strings.Contains(joined, " ") {
		t.Fatalf("expected gradient output to contain background spaces")
	}
}

func TestGenerateCustomChar(t *testing.T) {
	rows, err := Generate(80, 24, 100, '#')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	joined := strings.Join(rows, "\n")
	if !strings.Contains(joined, "#") {
		t.Fatalf("expected custom char '#' for in-set points")
	}
	// Gradient chars should not appear when a custom char is used.
	if strings.ContainsAny(joined, ".:-=+*%@") {
		t.Fatalf("custom char output leaked gradient chars: %q", joined)
	}
}

func TestGenerateRejectsBadDimensions(t *testing.T) {
	if _, err := Generate(0, 10, 50, 0); err == nil {
		t.Fatal("expected error for width 0")
	}
	if _, err := Generate(10, 0, 50, 0); err == nil {
		t.Fatal("expected error for height 0")
	}
	if _, err := Generate(-1, 10, 50, 0); err == nil {
		t.Fatal("expected error for negative width")
	}
}

func TestGenerateRejectsBadIterations(t *testing.T) {
	if _, err := Generate(10, 10, 0, 0); err == nil {
		t.Fatal("expected error for iterations 0")
	}
	if _, err := Generate(10, 10, -5, 0); err == nil {
		t.Fatal("expected error for negative iterations")
	}
}
```

- [ ] Run the test to see it fail:

```bash
go test ./internal/mandelbrot/
```

Expected output:

```
internal/mandelbrot/mandelbrot_test.go:9:14: undefined: Generate
FAIL	github.com/example/fractals/internal/mandelbrot [build failed]
```

- [ ] Implement the algorithm. Create `internal/mandelbrot/mandelbrot.go`:

```go
// Package mandelbrot renders the Mandelbrot set as ASCII art.
package mandelbrot

import "fmt"

// gradient maps low->high "intensity" of escape iterations to characters.
// The last character is used for points that never escape (inside the set).
const gradient = " .:-=+*#%@"

// Plane bounds for the rendered region.
const (
	realMin = -2.5
	realMax = 1.0
	imagMin = -1.25
	imagMax = 1.25
)

// Generate renders the Mandelbrot set as a slice of strings of length width,
// with height rows. iterations is the escape-test cap.
//
// If char is 0, a gradient is used. Otherwise in-set points use char and
// escaping points use a space.
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

	gradRunes := []rune(gradient)
	rows := make([]string, 0, height)

	for py := 0; py < height; py++ {
		ci := imagMin + (imagMax-imagMin)*float64(py)/float64(height-1)
		if height == 1 {
			ci = (imagMin + imagMax) / 2
		}
		line := make([]rune, 0, width)
		for px := 0; px < width; px++ {
			cr := realMin + (realMax-realMin)*float64(px)/float64(width-1)
			if width == 1 {
				cr = (realMin + realMax) / 2
			}
			n := escapeCount(cr, ci, iterations)
			line = append(line, cellRune(n, iterations, char, gradRunes))
		}
		rows = append(rows, string(line))
	}
	return rows, nil
}

// escapeCount returns the number of iterations before z escapes |z|>2,
// or iterations if it never escapes.
func escapeCount(cr, ci float64, iterations int) int {
	var zr, zi float64
	for n := 0; n < iterations; n++ {
		zr2 := zr*zr - zi*zi + cr
		zi2 := 2*zr*zi + ci
		zr, zi = zr2, zi2
		if zr*zr+zi*zi > 4 {
			return n
		}
	}
	return iterations
}

// cellRune maps an escape count to an output rune.
func cellRune(n, iterations int, char rune, gradRunes []rune) rune {
	inSet := n >= iterations
	if char != 0 {
		if inSet {
			return char
		}
		return ' '
	}
	if inSet {
		return gradRunes[len(gradRunes)-1]
	}
	idx := n * (len(gradRunes) - 1) / iterations
	if idx >= len(gradRunes) {
		idx = len(gradRunes) - 1
	}
	return gradRunes[idx]
}
```

- [ ] Run the tests to see them pass:

```bash
go test ./internal/mandelbrot/
```

Expected output:

```
ok  	github.com/example/fractals/internal/mandelbrot	0.XXXs
```

- [ ] Commit:

```bash
git add internal/mandelbrot/
git commit -m "Add Mandelbrot algorithm with tests"
```

---

### Task 4: CLI root command

**Files:** `internal/cli/root.go`

This task wires the root cobra command and an `Execute` entry point. Subcommands are added in later tasks. We test the root via the integration test file added in Task 6, so for now this task delivers a compiling root command and a help string.

- [ ] Create `internal/cli/root.go`:

```go
// Package cli wires the fractals command-line interface.
package cli

import (
	"github.com/spf13/cobra"
)

// newRootCmd builds the root command with all subcommands attached.
func newRootCmd() *cobra.Command {
	root := &cobra.Command{
		Use:   "fractals",
		Short: "Generate ASCII art fractals",
		Long:  "fractals generates ASCII art fractals (Sierpinski triangle and Mandelbrot set).",
		// Don't show usage on runtime errors from subcommands; only on usage errors.
		SilenceUsage: true,
	}
	root.AddCommand(newSierpinskiCmd())
	root.AddCommand(newMandelbrotCmd())
	return root
}

// Execute runs the root command. Called by main.
func Execute() error {
	return newRootCmd().Execute()
}
```

- [ ] This file references `newSierpinskiCmd` and `newMandelbrotCmd`, which do not exist yet, so it will not compile alone. Confirm the expected failure:

```bash
go build ./internal/cli/
```

Expected output:

```
internal/cli/root.go:18:21: undefined: newSierpinskiCmd
internal/cli/root.go:19:21: undefined: newMandelbrotCmd
```

This is expected; the next two tasks supply those functions. Do **not** commit yet — commit at the end of Task 5 once the package compiles.

---

### Task 5: Sierpinski and Mandelbrot subcommands

**Files:** `internal/cli/sierpinski.go`, `internal/cli/mandelbrot.go`

These two subcommands complete the `cli` package so it compiles. They are folded into one task because the root command from Task 4 cannot build until both exist.

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
		return 0, fmt.Errorf("--char must be a single character, got %q", s)
	}
	return runes[0], nil
}
```

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
		char       string
	)

	cmd := &cobra.Command{
		Use:   "mandelbrot",
		Short: "Render the Mandelbrot set",
		RunE: func(cmd *cobra.Command, args []string) error {
			var r rune // 0 means "use gradient"
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
			for _, line := range rows {
				fmt.Fprintln(cmd.OutOrStdout(), line)
			}
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

- [ ] Confirm the package now compiles:

```bash
go build ./internal/cli/
```

Expected output: no output (success).

- [ ] Commit Tasks 4 and 5 together (the package is now coherent):

```bash
git add internal/cli/root.go internal/cli/sierpinski.go internal/cli/mandelbrot.go
git commit -m "Add CLI root and sierpinski/mandelbrot subcommands"
```

---

### Task 6: CLI integration tests

**Files:** `internal/cli/cli_test.go`

These tests drive the cobra commands directly, capture stdout, and assert on behavior and error handling. They cover acceptance criteria 1–6.

- [ ] Create `internal/cli/cli_test.go`:

```go
package cli

import (
	"bytes"
	"strings"
	"testing"
)

// run executes the root command with args and returns combined output and error.
func run(args ...string) (string, error) {
	root := newRootCmd()
	var buf bytes.Buffer
	root.SetOut(&buf)
	root.SetErr(&buf)
	root.SetArgs(args)
	err := root.Execute()
	return buf.String(), err
}

func TestRootHelp(t *testing.T) {
	out, err := run("--help")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "fractals") {
		t.Fatalf("help output missing program name: %q", out)
	}
	if !strings.Contains(out, "sierpinski") || !strings.Contains(out, "mandelbrot") {
		t.Fatalf("help output missing subcommands: %q", out)
	}
}

func TestSierpinskiOutputsTriangle(t *testing.T) {
	out, err := run("sierpinski", "--size", "4", "--depth", "5")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 4 {
		t.Fatalf("expected 4 lines, got %d: %q", len(lines), out)
	}
	if strings.Count(out, "*") < 1 {
		t.Fatalf("expected triangle to contain '*': %q", out)
	}
}

func TestSierpinskiCustomChar(t *testing.T) {
	out, err := run("sierpinski", "--size", "4", "--char", "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "#") {
		t.Fatalf("expected custom char '#': %q", out)
	}
	if strings.Contains(out, "*") {
		t.Fatalf("unexpected default char in output: %q", out)
	}
}

func TestSierpinskiInvalidSize(t *testing.T) {
	_, err := run("sierpinski", "--size", "0")
	if err == nil {
		t.Fatal("expected error for size 0")
	}
}

func TestSierpinskiInvalidChar(t *testing.T) {
	_, err := run("sierpinski", "--char", "ab")
	if err == nil {
		t.Fatal("expected error for multi-character --char")
	}
}

func TestMandelbrotOutputsRectangle(t *testing.T) {
	out, err := run("mandelbrot", "--width", "20", "--height", "10")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 10 {
		t.Fatalf("expected 10 lines, got %d: %q", len(lines), out)
	}
	for i, line := range lines {
		if len([]rune(line)) != 20 {
			t.Fatalf("line %d width: expected 20, got %d (%q)", i, len([]rune(line)), line)
		}
	}
}

func TestMandelbrotGradientByDefault(t *testing.T) {
	out, err := run("mandelbrot", "--width", "80", "--height", "24")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "@") {
		t.Fatalf("expected gradient in-set char '@': %q", out)
	}
}

func TestMandelbrotCustomChar(t *testing.T) {
	out, err := run("mandelbrot", "--width", "80", "--height", "24", "--char", "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "#") {
		t.Fatalf("expected custom char '#': %q", out)
	}
}

func TestMandelbrotInvalidIterations(t *testing.T) {
	_, err := run("mandelbrot", "--iterations", "0")
	if err == nil {
		t.Fatal("expected error for iterations 0")
	}
}
```

- [ ] Run the CLI tests to see them pass:

```bash
go test ./internal/cli/
```

Expected output:

```
ok  	github.com/example/fractals/internal/cli	0.XXXs
```

- [ ] Commit:

```bash
git add internal/cli/cli_test.go
git commit -m "Add CLI integration tests"
```

---

### Task 7: Entry point

**Files:** `cmd/fractals/main.go`

- [ ] Create `cmd/fractals/main.go`:

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

- [ ] Build the binary:

```bash
go build -o fractals ./cmd/fractals/
```

Expected output: no output (success), and a `fractals` binary exists. Verify:

```bash
ls fractals
```

Expected output:

```
fractals
```

- [ ] Manually verify acceptance criteria. Run help:

```bash
./fractals --help
```

Expected output includes the program description, an `Available Commands` section listing `mandelbrot` and `sierpinski`, and a `Flags` section with `-h, --help`.

- [ ] Run a small Sierpinski triangle:

```bash
./fractals sierpinski --size 8 --depth 5
```

Expected output is a centered triangle of `*` characters, 8 lines tall, apex at top, e.g.:

```
       *
      * *
     *   *
    * * * *
   *       *
  * *     * *
 *   *   *   *
* * * * * * * *
```

- [ ] Run a small Mandelbrot render:

```bash
./fractals mandelbrot --width 40 --height 15
```

Expected output is a 15-line, 40-column block of gradient characters with a recognizable bulbous Mandelbrot shape (a dense `@`/`%`/`#` region on the left-center surrounded by lighter `.`/`:` characters and spaces).

- [ ] Verify an invalid input produces a clear error and non-zero exit:

```bash
./fractals sierpinski --size 0; echo "exit=$?"
```

Expected output:

```
error: size must be positive, got 0
exit=1
```

- [ ] Add the binary to gitignore so it is not committed. Create or append `.gitignore`:

```bash
echo "/fractals" >> .gitignore
```

- [ ] Commit:

```bash
git add cmd/fractals/main.go .gitignore
git commit -m "Add entry point and gitignore built binary"
```

---

### Task 8: Full verification

**Files:** none (verification only)

- [ ] Run the entire test suite:

```bash
go test ./...
```

Expected output:

```
ok  	github.com/example/fractals/internal/cli	0.XXXs
ok  	github.com/example/fractals/internal/mandelbrot	0.XXXs
ok  	github.com/example/fractals/internal/sierpinski	0.XXXs
```

(There is no `cmd/fractals` test file, so `go test` may print `?   github.com/example/fractals/cmd/fractals	[no test files]` — that is acceptable.)

- [ ] Run `go vet` to catch suspicious constructs:

```bash
go vet ./...
```

Expected output: no output (success).

- [ ] Confirm formatting is clean:

```bash
gofmt -l .
```

Expected output: no output (no files need formatting). If any file is listed, run `gofmt -w <file>`, re-run the tests, and commit the formatting fix.

- [ ] If `gofmt` produced changes, commit them:

```bash
git add -A
git commit -m "Apply gofmt"
```

If there were no changes, skip this commit.

---

## Self-Review

**Spec coverage check:**

1. `fractals --help` shows usage — covered by `TestRootHelp` (Task 6) and manual check (Task 7). ✓
2. `fractals sierpinski` outputs a recognizable triangle — `TestSierpinskiOutputsTriangle` + manual (Tasks 6, 7). ✓
3. `fractals mandelbrot` outputs a recognizable Mandelbrot set — `TestMandelbrotOutputsRectangle`, `TestMandelbrotGradientByDefault` + manual (Tasks 6, 7). ✓
4. `--size`, `--width`, `--height`, `--depth`, `--iterations` flags — all defined in Task 5; size/width/height/depth/iterations exercised in Tasks 2, 3, 6. ✓
5. `--char` customizes output — `TestSierpinskiCustomChar`, `TestMandelbrotCustomChar`; gradient default preserved via empty-string flag + rune 0 sentinel. ✓
6. Invalid inputs produce clear error messages — validation in algorithm packages returns descriptive errors; surfaced via `RunE` and main; tested by `TestSierpinskiInvalidSize`, `TestSierpinskiInvalidChar`, `TestMandelbrotInvalidIterations` and manual check. ✓
7. All tests pass — Task 8. ✓

**Type consistency check:** Both algorithm packages expose `Generate(...) ([]string, error)`. Sierpinski takes `(size, depth int, char rune)`; Mandelbrot takes `(width, height, iterations int, char rune)`. CLI passes `rune(0)` as the Mandelbrot gradient sentinel, matching the `char == 0` branch in `cellRune`. Sierpinski's CLI requires a single rune (default `*`). Consistent throughout.

**Placeholder scan:** No `TODO`, no stub functions, no `panic("not implemented")`. The module path `github.com/example/fractals` is used consistently in `go mod init`, all imports, and the entry point — if you publish under a different path, change it in Task 1 and update the two import lines in Task 5 and one in Task 7.

**Dependency check:** Only `github.com/spf13/cobra` is added, matching the spec. Go 1.21+ enforced by `go.mod` and the prerequisite check.

**Build-order note:** Task 4 intentionally does not compile in isolation (it references functions added in Task 5); the plan calls this out and defers the commit to the end of Task 5 so every commit after that point builds cleanly.