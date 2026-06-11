# Go Fractals CLI — Implementation Plan

## Global Constraints

- Go 1.21+
- Dependency: `github.com/spf13/cobra` (CLI framework)
- Binary name: `fractals`
- Default sierpinski char: `*`
- Default mandelbrot gradient: `" .:-=+*#%@"` (10 chars, space through @)
- Sierpinski default size: 32, default depth: 5
- Mandelbrot default width: 80, default height: 24, default iterations: 100
- All output to stdout; errors to stderr via cobra

---

## File Structure

| File | Responsibility |
|---|---|
| `go.mod` / `go.sum` | Module declaration, dependency lock |
| `cmd/fractals/main.go` | Binary entry point — calls `cli.Execute()` |
| `internal/sierpinski/sierpinski.go` | Pure algorithm: produces `[]string` grid |
| `internal/sierpinski/sierpinski_test.go` | Unit tests for Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure algorithm: produces `[]string` grid |
| `internal/mandelbrot/mandelbrot_test.go` | Unit tests for Mandelbrot algorithm |
| `internal/cli/root.go` | Root cobra command, `Execute()` |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand, flag wiring |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand, flag wiring |

---

## Task 1: Module Scaffold & Sierpinski Algorithm

**Interfaces:**
- Produces: `sierpinski.Generate(size int, depth int, ch rune) []string`
  - `size`: base width (must be power of 2, ≥ 1)
  - `depth`: recursion depth (≥ 0)
  - `ch`: fill character
  - Returns slice of strings, one per row, each exactly `size` chars wide

### Files
- `go.mod`
- `go.sum` (generated)
- `internal/sierpinski/sierpinski.go`
- `internal/sierpinski/sierpinski_test.go`

---

- [ ] **Init module**

  ```bash
  mkdir -p fractals
  cd fractals
  go mod init github.com/user/fractals
  ```

  Expected: `go.mod` created with `module github.com/user/fractals` and `go 1.21`.

---

- [ ] **Write failing tests** — `internal/sierpinski/sierpinski_test.go`

  ```go
  package sierpinski_test

  import (
  	"strings"
  	"testing"

  	"github.com/user/fractals/internal/sierpinski"
  )

  func TestGenerate_Size1_Depth0(t *testing.T) {
  	lines := sierpinski.Generate(1, 0, '*')
  	if len(lines) != 1 {
  		t.Fatalf("expected 1 row, got %d", len(lines))
  	}
  	if lines[0] != "*" {
  		t.Fatalf("expected \"*\", got %q", lines[0])
  	}
  }

  func TestGenerate_RowCount(t *testing.T) {
  	for _, size := range []int{1, 2, 4, 8, 16, 32} {
  		lines := sierpinski.Generate(size, 5, '*')
  		if len(lines) != size {
  			t.Errorf("size=%d: expected %d rows, got %d", size, size, len(lines))
  		}
  	}
  }

  func TestGenerate_RowWidth(t *testing.T) {
  	size := 8
  	lines := sierpinski.Generate(size, 3, '*')
  	for i, line := range lines {
  		if len(line) != size {
  			t.Errorf("row %d: expected width %d, got %d (%q)", i, size, len(line), line)
  		}
  	}
  }

  func TestGenerate_TopRowIsFilled(t *testing.T) {
  	// Row 0 is always the apex: a single char at the center of the base row
  	// For a triangle rendered top-to-bottom, row 0 (top) has the tip.
  	lines := sierpinski.Generate(8, 3, '*')
  	filled := strings.TrimSpace(lines[0])
  	if len(filled) == 0 {
  		t.Error("first row should contain at least one fill character")
  	}
  }

  func TestGenerate_CustomChar(t *testing.T) {
  	lines := sierpinski.Generate(4, 2, '#')
  	for _, line := range lines {
  		if strings.ContainsRune(line, '*') {
  			t.Error("should not contain default char '*' when custom char '#' specified")
  		}
  	}
  }

  func TestGenerate_Depth0_FullTriangle(t *testing.T) {
  	// depth=0 means no subdivision — entire triangle is filled
  	lines := sierpinski.Generate(4, 0, '*')
  	// Bottom row must be all fill chars
  	bottom := lines[len(lines)-1]
  	if strings.TrimLeft(bottom, "*") != "" {
  		t.Errorf("depth=0 bottom row should be all '*', got %q", bottom)
  	}
  }

  func TestGenerate_Size2_Depth1(t *testing.T) {
  	//  *
  	// **
  	lines := sierpinski.Generate(2, 1, '*')
  	if len(lines) != 2 {
  		t.Fatalf("expected 2 rows, got %d", len(lines))
  	}
  	// top row: one star somewhere
  	if strings.Count(lines[0], "*") != 1 {
  		t.Errorf("row 0 should have 1 star, got %q", lines[0])
  	}
  	// bottom row: two stars
  	if strings.Count(lines[1], "*") != 2 {
  		t.Errorf("row 1 should have 2 stars, got %q", lines[1])
  	}
  }
  ```

- [ ] **Run tests — expect compilation failure**

  ```bash
  go test ./internal/sierpinski/...
  ```

  Expected: `cannot find package` or `undefined: sierpinski.Generate`

---

- [ ] **Implement** — `internal/sierpinski/sierpinski.go`

  ```go
  // Package sierpinski generates Sierpinski triangle ASCII art.
  package sierpinski

  import "strings"

  // Generate returns a slice of strings representing a Sierpinski triangle.
  // size is the base width (should be a power of 2).
  // depth controls recursion (0 = solid triangle, higher = more holes).
  // ch is the character used for filled cells.
  // Each returned string is exactly size runes wide (padded with spaces).
  func Generate(size, depth int, ch rune) []string {
  	if size <= 0 {
  		return nil
  	}
  	// Build a 2D grid: grid[row][col] = true means filled
  	grid := make([][]bool, size)
  	for i := range grid {
  		grid[i] = make([]bool, size)
  	}
  	fill(grid, 0, 0, size, depth)

  	lines := make([]string, size)
  	for r := 0; r < size; r++ {
  		var sb strings.Builder
  		for c := 0; c < size; c++ {
  			if grid[r][c] {
  				sb.WriteRune(ch)
  			} else {
  				sb.WriteRune(' ')
  			}
  		}
  		lines[r] = sb.String()
  	}
  	return lines
  }

  // fill marks cells in the triangular region starting at (topRow, leftCol)
  // with the given size. depth controls subdivision.
  // The triangle is right-aligned within its size×size bounding box,
  // growing wider toward the bottom (standard Sierpinski orientation).
  func fill(grid [][]bool, topRow, leftCol, size, depth int) {
  	if size == 0 {
  		return
  	}
  	if size == 1 {
  		grid[topRow][leftCol] = true
  		return
  	}
  	if depth == 0 {
  		// Fill the entire triangular region
  		fillSolid(grid, topRow, leftCol, size)
  		return
  	}
  	half := size / 2
  	// Top sub-triangle
  	fill(grid, topRow, leftCol+half, half, depth-1)
  	// Bottom-left sub-triangle
  	fill(grid, topRow+half, leftCol, half, depth-1)
  	// Bottom-right sub-triangle
  	fill(grid, topRow+half, leftCol+half, half, depth-1)
  	// Middle is left empty (the hole)
  }

  // fillSolid fills the triangular region (no holes) within the bounding box.
  // Row r (0-indexed within the triangle) has (r+1) cells, right-aligned
  // in the bottom-left corner of the size×size box.
  func fillSolid(grid [][]bool, topRow, leftCol, size int) {
  	for r := 0; r < size; r++ {
  		rowStart := size - 1 - r // offset from leftCol for the leftmost cell in this row
  		for c := rowStart; c < size; c++ {
  			grid[topRow+r][leftCol+c] = true
  		}
  	}
  }
  ```

- [ ] **Run tests — expect pass**

  ```bash
  go test ./internal/sierpinski/... -v
  ```

  Expected:
  ```
  --- PASS: TestGenerate_Size1_Depth0
  --- PASS: TestGenerate_RowCount
  --- PASS: TestGenerate_RowWidth
  --- PASS: TestGenerate_TopRowIsFilled
  --- PASS: TestGenerate_CustomChar
  --- PASS: TestGenerate_Depth0_FullTriangle
  --- PASS: TestGenerate_Size2_Depth1
  PASS
  ok  	github.com/user/fractals/internal/sierpinski
  ```

- [ ] **Commit**

  ```bash
  git init
  git add .
  git commit -m "task 1: sierpinski algorithm with tests"
  ```

---

## Task 2: Mandelbrot Algorithm

**Interfaces:**
- Consumes: nothing from earlier tasks
- Produces: `mandelbrot.Generate(width, height, maxIter int, ch string) []string`
  - `width`: output columns
  - `height`: output rows
  - `maxIter`: escape iteration ceiling (≥ 1)
  - `ch`: if `""` use gradient `" .:-=+*#%@"`; if single-char string, use that char for all non-background pixels
  - Returns `[]string`, `len == height`, each string exactly `width` runes wide

### Files
- `internal/mandelbrot/mandelbrot.go`
- `internal/mandelbrot/mandelbrot_test.go`

---

- [ ] **Write failing tests** — `internal/mandelbrot/mandelbrot_test.go`

  ```go
  package mandelbrot_test

  import (
  	"strings"
  	"testing"

  	"github.com/user/fractals/internal/mandelbrot"
  )

  func TestGenerate_Dimensions(t *testing.T) {
  	lines := mandelbrot.Generate(40, 12, 50, "")
  	if len(lines) != 12 {
  		t.Fatalf("expected 12 rows, got %d", len(lines))
  	}
  	for i, line := range lines {
  		if len(line) != 40 {
  			t.Errorf("row %d: expected width 40, got %d", i, len(line))
  		}
  	}
  }

  func TestGenerate_ContainsNonSpace(t *testing.T) {
  	lines := mandelbrot.Generate(80, 24, 100, "")
  	hasNonSpace := false
  	for _, line := range lines {
  		if strings.TrimSpace(line) != "" {
  			hasNonSpace = true
  			break
  		}
  	}
  	if !hasNonSpace {
  		t.Error("output should contain non-space characters (the Mandelbrot set)")
  	}
  }

  func TestGenerate_ContainsSpaces(t *testing.T) {
  	// The interior of the set (spaces in gradient mode) should be present
  	lines := mandelbrot.Generate(80, 24, 100, "")
  	hasSpace := false
  	for _, line := range lines {
  		if strings.Contains(line, " ") {
  			hasSpace = true
  			break
  		}
  	}
  	if !hasSpace {
  		t.Error("output should contain spaces (interior/exterior of set)")
  	}
  }

  func TestGenerate_CustomChar(t *testing.T) {
  	lines := mandelbrot.Generate(40, 12, 50, "#")
  	for _, line := range lines {
  		for _, ch := range line {
  			if ch != '#' && ch != ' ' {
  				t.Errorf("custom char mode: unexpected char %q", ch)
  			}
  		}
  	}
  }

  func TestGenerate_GradientCharsOnly(t *testing.T) {
  	gradient := " .:-=+*#%@"
  	lines := mandelbrot.Generate(40, 12, 50, "")
  	allowed := make(map[rune]bool)
  	for _, ch := range gradient {
  		allowed[ch] = true
  	}
  	for r, line := range lines {
  		for c, ch := range line {
  			if !allowed[ch] {
  				t.Errorf("row %d col %d: unexpected char %q not in gradient", r, c, ch)
  			}
  		}
  	}
  }

  func TestGenerate_Symmetry(t *testing.T) {
  	// Mandelbrot set is symmetric about the real axis (horizontal center)
  	width, height := 80, 25 // odd height so there is a true midpoint row
  	lines := mandelbrot.Generate(width, height, 100, "")
  	for r := 0; r < height/2; r++ {
  		mirror := height - 1 - r
  		if lines[r] != lines[mirror] {
  			t.Errorf("symmetry broken: row %d != row %d", r, mirror)
  			break
  		}
  	}
  }

  func TestGenerate_SmallDimensions(t *testing.T) {
  	lines := mandelbrot.Generate(1, 1, 10, "")
  	if len(lines) != 1 || len(lines[0]) != 1 {
  		t.Errorf("1×1 grid failed: got %v", lines)
  	}
  }
  ```

- [ ] **Run tests — expect compilation failure**

  ```bash
  go test ./internal/mandelbrot/...
  ```

  Expected: `undefined: mandelbrot.Generate`

---

- [ ] **Implement** — `internal/mandelbrot/mandelbrot.go`

  ```go
  // Package mandelbrot generates Mandelbrot set ASCII art.
  package mandelbrot

  import "strings"

  const gradient = " .:-=+*#%@"

  // Generate returns a slice of strings representing the Mandelbrot set.
  // width and height define output dimensions.
  // maxIter is the maximum escape iteration count.
  // ch: if empty string, use gradient mapping; if single char, use it for
  // non-background (escaped) pixels with space for the set interior.
  // Each returned string is exactly width runes wide.
  func Generate(width, height, maxIter int, ch string) []string {
  	// Viewport: real in [-2.5, 1.0], imag in [-1.2, 1.2]
  	const (
  		realMin = -2.5
  		realMax = 1.0
  		imagMin = -1.2
  		imagMax = 1.2
  	)

  	lines := make([]string, height)
  	gradRunes := []rune(gradient)
  	gradLen := len(gradRunes)

  	useGradient := ch == ""
  	var fillRune rune
  	if !useGradient && len([]rune(ch)) > 0 {
  		fillRune = []rune(ch)[0]
  	}

  	for row := 0; row < height; row++ {
  		var sb strings.Builder
  		// Map row to imaginary axis (top = imagMax, bottom = imagMin)
  		var imag0 float64
  		if height == 1 {
  			imag0 = 0
  		} else {
  			imag0 = imagMax - float64(row)*(imagMax-imagMin)/float64(height-1)
  		}

  		for col := 0; col < width; col++ {
  			var real0 float64
  			if width == 1 {
  				real0 = (realMin + realMax) / 2
  			} else {
  				real0 = realMin + float64(col)*(realMax-realMin)/float64(width-1)
  			}

  			iter := escape(real0, imag0, maxIter)

  			var out rune
  			if useGradient {
  				// iter == maxIter → inside set → index 0 (' ')
  				// iter == 0 → barely escaped → index 1
  				if iter == maxIter {
  					out = gradRunes[0]
  				} else {
  					idx := 1 + (iter*(gradLen-1))/maxIter
  					if idx >= gradLen {
  						idx = gradLen - 1
  					}
  					out = gradRunes[idx]
  				}
  			} else {
  				if iter == maxIter {
  					out = ' '
  				} else {
  					out = fillRune
  				}
  			}
  			sb.WriteRune(out)
  		}
  		lines[row] = sb.String()
  	}
  	return lines
  }

  // escape returns the number of iterations before |z| > 2, capped at maxIter.
  // Returns maxIter if the point does not escape (inside the set).
  func escape(c0real, c0imag float64, maxIter int) int {
  	zr, zi := 0.0, 0.0
  	for i := 0; i < maxIter; i++ {
  		zr2 := zr*zr - zi*zi + c0real
  		zi2 := 2*zr*zi + c0imag
  		zr, zi = zr2, zi2
  		if zr*zr+zi*zi > 4 {
  			return i
  		}
  	}
  	return maxIter
  }
  ```

- [ ] **Run tests — expect pass**

  ```bash
  go test ./internal/mandelbrot/... -v
  ```

  Expected:
  ```
  --- PASS: TestGenerate_Dimensions
  --- PASS: TestGenerate_ContainsNonSpace
  --- PASS: TestGenerate_ContainsSpaces
  --- PASS: TestGenerate_CustomChar
  --- PASS: TestGenerate_GradientCharsOnly
  --- PASS: TestGenerate_Symmetry
  --- PASS: TestGenerate_SmallDimensions
  PASS
  ok  	github.com/user/fractals/internal/mandelbrot
  ```

- [ ] **Commit**

  ```bash
  git add .
  git commit -m "task 2: mandelbrot algorithm with tests"
  ```

---

## Task 3: CLI Wiring & Binary

**Interfaces:**
- Consumes:
  - `sierpinski.Generate(size int, depth int, ch rune) []string`
  - `mandelbrot.Generate(width, height, maxIter int, ch string) []string`
- Produces:
  - `cli.Execute() error` (called by `main.go`)
  - Binary `fractals` at `cmd/fractals/main.go`

### Files
- `internal/cli/root.go`
- `internal/cli/sierpinski.go`
- `internal/cli/mandelbrot.go`
- `cmd/fractals/main.go`

---

- [ ] **Add cobra dependency**

  ```bash
  go get github.com/spf13/cobra@latest
  go mod tidy
  ```

  Expected: `go.mod` now lists `github.com/spf13/cobra`, `go.sum` updated.

---

- [ ] **Write CLI integration tests** — `internal/cli/cli_test.go`

  ```go
  package cli_test

  import (
  	"bytes"
  	"strings"
  	"testing"

  	"github.com/user/fractals/internal/cli"
  )

  func runCLI(args ...string) (string, error) {
  	buf := new(bytes.Buffer)
  	err := cli.ExecuteWithWriter(buf, args...)
  	return buf.String(), err
  }

  func TestHelp(t *testing.T) {
  	out, err := runCLI("--help")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if !strings.Contains(out, "sierpinski") || !strings.Contains(out, "mandelbrot") {
  		t.Errorf("help should mention both subcommands, got:\n%s", out)
  	}
  }

  func TestSierpinskiDefault(t *testing.T) {
  	out, err := runCLI("sierpinski")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 32 {
  		t.Errorf("default sierpinski: expected 32 rows, got %d", len(lines))
  	}
  }

  func TestSierpinskiSize(t *testing.T) {
  	out, err := runCLI("sierpinski", "--size", "8")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 8 {
  		t.Errorf("sierpinski --size 8: expected 8 rows, got %d", len(lines))
  	}
  }

  func TestSierpinskiCustomChar(t *testing.T) {
  	out, err := runCLI("sierpinski", "--size", "4", "--char", "#")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if strings.ContainsRune(out, '*') {
  		t.Error("should not contain default '*' when --char '#' specified")
  	}
  	if !strings.ContainsRune(out, '#') {
  		t.Error("output should contain '#'")
  	}
  }

  func TestMandelbrotDefault(t *testing.T) {
  	out, err := runCLI("mandelbrot")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 24 {
  		t.Errorf("default mandelbrot: expected 24 rows, got %d", len(lines))
  	}
  	if len(lines[0]) != 80 {
  		t.Errorf("default mandelbrot: expected width 80, got %d", len(lines[0]))
  	}
  }

  func TestMandelbrotDimensions(t *testing.T) {
  	out, err := runCLI("mandelbrot", "--width", "40", "--height", "12")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
  	if len(lines) != 12 {
  		t.Errorf("expected 12 rows, got %d", len(lines))
  	}
  	if len(lines[0]) != 40 {
  		t.Errorf("expected width 40, got %d", len(lines[0]))
  	}
  }

  func TestMandelbrotCustomChar(t *testing.T) {
  	out, err := runCLI("mandelbrot", "--width", "20", "--height", "6", "--char", "@")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	for _, ch := range out {
  		if ch != '@' && ch != ' ' && ch != '\n' {
  			t.Errorf("unexpected char %q in custom-char mandelbrot", ch)
  		}
  	}
  }

  func TestSierpinskiInvalidSize(t *testing.T) {
  	_, err := runCLI("sierpinski", "--size", "-1")
  	if err == nil {
  		t.Error("expected error for negative size")
  	}
  }

  func TestMandelbrotInvalidWidth(t *testing.T) {
  	_, err := runCLI("mandelbrot", "--width", "0")
  	if err == nil {
  		t.Error("expected error for zero width")
  	}
  }

  func TestMandelbrotInvalidIterations(t *testing.T) {
  	_, err := runCLI("mandelbrot", "--iterations", "0")
  	if err == nil {
  		t.Error("expected error for zero iterations")
  	}
  }
  ```

- [ ] **Run tests — expect compilation failure**

  ```bash
  go test ./internal/cli/...
  ```

  Expected: `undefined: cli.ExecuteWithWriter`

---

- [ ] **Implement root command** — `internal/cli/root.go`

  ```go
  // Package cli wires cobra commands for the fractals tool.
  package cli

  import (
  	"io"
  	"os"

  	"github.com/spf13/cobra"
  )

  // newRootCmd builds the root cobra command with w as the output writer.
  func newRootCmd(w io.Writer) *cobra.Command {
  	cmd := &cobra.Command{
  		Use:   "fractals",
  		Short: "Generate ASCII art fractals",
  		Long:  "A CLI tool that generates ASCII art fractals.\n\nAvailable fractals: sierpinski, mandelbrot",
  	}
  	cmd.SetOut(w)
  	cmd.SetErr(w)
  	return cmd
  }

  // ExecuteWithWriter runs the CLI with the given output writer and arguments.
  // Returns an error if the command fails.
  func ExecuteWithWriter(w io.Writer, args ...string) error {
  	root := newRootCmd(w)
  	root.AddCommand(newSierpinskiCmd(w))
  	root.AddCommand(newMandelbrotCmd(w))
  	root.SetArgs(args)
  	return root.Execute()
  }

  // Execute runs the CLI writing to stdout, reading args from os.Args.
  func Execute() error {
  	root := newRootCmd(os.Stdout)
  	root.AddCommand(newSierpinskiCmd(os.Stdout))
  	root.AddCommand(newMandelbrotCmd(os.Stdout))
  	return root.Execute()
  }
  ```

- [ ] **Implement sierpinski subcommand** — `internal/cli/sierpinski.go`

  ```go
  package cli

  import (
  	"fmt"
  	"io"

  	"github.com/spf13/cobra"
  	"github.com/user/fractals/internal/sierpinski"
  )

  func newSierpinskiCmd(w io.Writer) *cobra.Command {
  	var size, depth int
  	var char string

  	cmd := &cobra.Command{
  		Use:   "sierpinski",
  		Short: "Generate a Sierpinski triangle",
  		Long:  "Generates a Sierpinski triangle using recursive subdivision.",
  		RunE: func(cmd *cobra.Command, args []string) error {
  			if size < 1 {
  				return fmt.Errorf("--size must be >= 1, got %d", size)
  			}
  			if depth < 0 {
  				return fmt.Errorf("--depth must be >= 0, got %d", depth)
  			}
  			ch := '*'
  			if char != "" {
  				runes := []rune(char)
  				if len(runes) != 1 {
  					return fmt.Errorf("--char must be a single character, got %q", char)
  				}
  				ch = runes[0]
  			}
  			lines := sierpinski.Generate(size, depth, ch)
  			for _, line := range lines {
  				fmt.Fprintln(w, line)
  			}
  			return nil
  		},
  	}
  	cmd.SetOut(w)
  	cmd.Flags().IntVar(&size, "size", 32, "Width of the triangle base in characters")
  	cmd.Flags().IntVar(&depth, "depth", 5, "Recursion depth")
  	cmd.Flags().StringVar(&char, "char", "*", "Character to use for filled points")
  	return cmd
  }
  ```

- [ ] **Implement mandelbrot subcommand** — `internal/cli/mandelbrot.go`

  ```go
  package cli

  import (
  	"fmt"
  	"io"

  	"github.com/spf13/cobra"
  	"github.com/user/fractals/internal/mandelbrot"
  )

  func newMandelbrotCmd(w io.Writer) *cobra.Command {
  	var width, height, iterations int
  	var char string

  	cmd := &cobra.Command{
  		Use:   "mandelbrot",
  		Short: "Render the Mandelbrot set as ASCII art",
  		Long:  "Renders the Mandelbrot set as ASCII art, mapping iteration count to characters.",
  		RunE: func(cmd *cobra.Command, args []string) error {
  			if width < 1 {
  				return fmt.Errorf("--width must be >= 1, got %d", width)
  			}
  			if height < 1 {
  				return fmt.Errorf("--height must be >= 1, got %d", height)
  			}
  			if iterations < 1 {
  				return fmt.Errorf("--iterations must be >= 1, got %d", iterations)
  			}
  			ch := ""
  			if char != "" {
  				runes := []rune(char)
  				if len(runes) != 1 {
  					return fmt.Errorf("--char must be a single character, got %q", char)
  				}
  				ch = char
  			}
  			lines := mandelbrot.Generate(width, height, iterations, ch)
  			for _, line := range lines {
  				fmt.Fprintln(w, line)
  			}
  			return nil
  		},
  	}
  	cmd.SetOut(w)
  	cmd.Flags().IntVar(&width, "width", 80, "Output width in characters")
  	cmd.Flags().IntVar(&height, "height", 24, "Output height in characters")
  	cmd.Flags().IntVar(&iterations, "iterations", 100, "Maximum iterations for escape calculation")
  	cmd.Flags().StringVar(&char, "char", "", "Single character override (omit for gradient)")
  	return cmd
  }
  ```

- [ ] **Implement entry point** — `cmd/fractals/main.go`

  ```go
  package main

  import (
  	"fmt"
  	"os"

  	"github.com/user/fractals/internal/cli"
  )

  func main() {
  	if err := cli.Execute(); err != nil {
  		fmt.Fprintln(os.Stderr, err)
  		os.Exit(1)
  	}
  }
  ```

- [ ] **Run CLI tests — expect pass**

  ```bash
  go test ./internal/cli/... -v
  ```

  Expected:
  ```
  --- PASS: TestHelp
  --- PASS: TestSierpinskiDefault
  --- PASS: TestSierpinskiSize
  --- PASS: TestSierpinskiCustomChar
  --- PASS: TestMandelbrotDefault
  --- PASS: TestMandelbrotDimensions
  --- PASS: TestMandelbrotCustomChar
  --- PASS: TestSierpinskiInvalidSize
  --- PASS: TestMandelbrotInvalidWidth
  --- PASS: TestMandelbrotInvalidIterations
  PASS
  ok  	github.com/user/fractals/internal/cli
  ```

- [ ] **Run full test suite**

  ```bash
  go test ./...
  ```

  Expected:
  ```
  ok  	github.com/user/fractals/internal/sierpinski
  ok  	github.com/user/fractals/internal/mandelbrot
  ok  	github.com/user/fractals/internal/cli
  ```

- [ ] **Build and smoke-test binary**

  ```bash
  go build -o fractals ./cmd/fractals

  ./fractals --help
  ```

  Expected output contains:
  ```
  sierpinski
  mandelbrot
  ```

  ```bash
  ./fractals sierpinski --size 8 --depth 3
  ```

  Expected: 8 lines of triangle art printed to stdout.

  ```bash
  ./fractals mandelbrot --width 40 --height 12
  ```

  Expected: 12 lines of Mandelbrot art, each 40 chars wide.

  ```bash
  ./fractals sierpinski --size -1
  ```

  Expected: non-zero exit code, error message on stderr mentioning `--size`.

  ```bash
  ./fractals mandelbrot --iterations 0
  ```

  Expected: non-zero exit code, error message on stderr mentioning `--iterations`.

- [ ] **Commit**

  ```bash
  git add .
  git commit -m "task 3: cobra CLI wiring, subcommands, entry point, integration tests"
  ```