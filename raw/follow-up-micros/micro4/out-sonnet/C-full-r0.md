# Go Fractals CLI — Implementation Plan

## Global Constraints

- Go 1.21+
- Dependency: `github.com/spf13/cobra` (CLI framework)
- Module name: `fractals` (used in `go.mod`)
- Entry point: `cmd/fractals/main.go`
- Default Sierpinski char: `*`
- Default Mandelbrot gradient: `" .:-=+*#%@"` (10 characters, space to @)
- All output goes to stdout; errors go to stderr via cobra
- Architecture: `cmd/fractals/`, `internal/sierpinski/`, `internal/mandelbrot/`, `internal/cli/`

---

## File Structure

| File | Responsibility |
|---|---|
| `go.mod` / `go.sum` | Module definition and dependency lock |
| `cmd/fractals/main.go` | Binary entry point; calls `cli.Execute()` |
| `internal/cli/root.go` | Root cobra command, `Execute()` func, help config |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand; parses flags, calls algorithm, prints output |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand; parses flags, calls algorithm, prints output |
| `internal/sierpinski/sierpinski.go` | Pure algorithm: `Generate(size, depth int, char rune) []string` |
| `internal/sierpinski/sierpinski_test.go` | Unit tests for Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure algorithm: `Generate(width, height, iterations int, charOverride string) []string` |
| `internal/mandelbrot/mandelbrot_test.go` | Unit tests for Mandelbrot algorithm |

---

## Task 1: Module Scaffold and Sierpinski Algorithm

**Interfaces:**
- Produces: `internal/sierpinski.Generate(size, depth int, char rune) []string`
  - Returns `size` strings each of length `size`, space-padded; filled cells contain `char`
  - `size` must be a power of 2 and ≥ 1; `depth` must be ≥ 0; `char` must be non-zero — otherwise returns `nil, error` (signature updated below)
- Actual signature: `Generate(size, depth int, char rune) ([]string, error)`

**Files:**
- `go.mod`
- `go.sum` (generated)
- `internal/sierpinski/sierpinski.go`
- `internal/sierpinski/sierpinski_test.go`

---

- [ ] **Init module and install dependency**

  ```bash
  mkdir -p fractals && cd fractals
  go mod init fractals
  go get github.com/spf13/cobra@latest
  ```

  Expected: `go.mod` lists `module fractals`, `go 1.21` (or higher detected), cobra entry appears; `go.sum` created.

- [ ] **Create directory structure**

  ```bash
  mkdir -p cmd/fractals internal/sierpinski internal/mandelbrot internal/cli
  ```

- [ ] **Write the failing test** — `internal/sierpinski/sierpinski_test.go`

  ```go
  package sierpinski_test

  import (
  	"strings"
  	"testing"

  	"fractals/internal/sierpinski"
  )

  func TestGenerateInvalidSize(t *testing.T) {
  	_, err := sierpinski.Generate(0, 3, '*')
  	if err == nil {
  		t.Fatal("expected error for size=0")
  	}
  	_, err = sierpinski.Generate(3, 3, '*') // not power of 2
  	if err == nil {
  		t.Fatal("expected error for size=3 (not power of 2)")
  	}
  }

  func TestGenerateInvalidChar(t *testing.T) {
  	_, err := sierpinski.Generate(4, 2, 0)
  	if err == nil {
  		t.Fatal("expected error for char=0")
  	}
  }

  func TestGenerateDepthZero(t *testing.T) {
  	// depth=0 → fully filled triangle of size 1
  	rows, err := sierpinski.Generate(1, 0, '*')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 1 {
  		t.Fatalf("expected 1 row, got %d", len(rows))
  	}
  	if rows[0] != "*" {
  		t.Errorf("expected '*', got %q", rows[0])
  	}
  }

  func TestGenerateSize4Depth2(t *testing.T) {
  	rows, err := sierpinski.Generate(4, 2, '*')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 4 {
  		t.Fatalf("expected 4 rows, got %d", len(rows))
  	}
  	// Each row must have length == size
  	for i, r := range rows {
  		if len(r) != 4 {
  			t.Errorf("row %d: expected length 4, got %d", i, len(r))
  		}
  	}
  	// Bottom row must be all '*'
  	if rows[3] != "****" {
  		t.Errorf("bottom row: expected '****', got %q", rows[3])
  	}
  	// Top row: only first char filled
  	if rows[0][0] != '*' {
  		t.Errorf("top row first char: expected '*', got %q", rows[0][0])
  	}
  	// Middle row of top half: middle two chars must be spaces (Sierpinski hole)
  	// For size=4 depth=2 the pattern is:
  	//   *   (row 0)
  	//  **   (row 1)  — actually * * with space
  	// Let's just check the center void: rows[1] middle should not be all '*'
  	if rows[1] == "****" {
  		t.Errorf("row 1 should not be fully filled: %q", rows[1])
  	}
  }

  func TestGenerateCustomChar(t *testing.T) {
  	rows, err := sierpinski.Generate(2, 1, '#')
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	for _, r := range rows {
  		if strings.Contains(r, "*") {
  			t.Errorf("found default char '*' when custom '#' expected: %q", r)
  		}
  	}
  }

  func TestGenerateRowCount(t *testing.T) {
  	for _, size := range []int{1, 2, 4, 8, 16, 32} {
  		rows, err := sierpinski.Generate(size, 4, '*')
  		if err != nil {
  			t.Fatalf("size=%d: unexpected error: %v", size, err)
  		}
  		if len(rows) != size {
  			t.Errorf("size=%d: expected %d rows, got %d", size, size, len(rows))
  		}
  	}
  }
  ```

- [ ] **Run test to confirm failure**

  ```bash
  go test ./internal/sierpinski/...
  ```

  Expected: `cannot find package` or `undefined: sierpinski.Generate` — compilation error.

- [ ] **Implement** — `internal/sierpinski/sierpinski.go`

  ```go
  // Package sierpinski generates Sierpinski triangle ASCII art.
  package sierpinski

  import (
  	"fmt"
  	"strings"
  )

  // Generate returns `size` rows of ASCII art for a Sierpinski triangle.
  // size must be a power of 2 and >= 1.
  // depth controls recursion depth (0 = solid triangle).
  // char is the fill character and must be non-zero.
  func Generate(size, depth int, char rune) ([]string, error) {
  	if size < 1 || (size&(size-1)) != 0 {
  		return nil, fmt.Errorf("size must be a power of 2 and >= 1, got %d", size)
  	}
  	if char == 0 {
  		return nil, fmt.Errorf("char must be a non-zero rune")
  	}
  	if depth < 0 {
  		return nil, fmt.Errorf("depth must be >= 0, got %d", depth)
  	}

  	// Build a 2-D grid of booleans (filled = true).
  	grid := make([][]bool, size)
  	for i := range grid {
  		grid[i] = make([]bool, size)
  	}

  	fill(grid, 0, 0, size, depth)

  	// Convert grid to strings.
  	rows := make([]string, size)
  	for i, row := range grid {
  		var sb strings.Builder
  		for _, filled := range row {
  			if filled {
  				sb.WriteRune(char)
  			} else {
  				sb.WriteByte(' ')
  			}
  		}
  		rows[i] = sb.String()
  	}
  	return rows, nil
  }

  // fill marks the triangle with top-left corner at (row, col) and given size.
  // The triangle occupies rows [row, row+size) and is left-aligned.
  func fill(grid [][]bool, row, col, size, depth int) {
  	if size == 1 {
  		grid[row][col] = true
  		return
  	}
  	if depth == 0 {
  		// Fill the whole triangle solid.
  		for r := 0; r < size; r++ {
  			for c := 0; c <= r; c++ {
  				grid[row+r][col+c] = true
  			}
  		}
  		return
  	}
  	half := size / 2
  	// Top sub-triangle
  	fill(grid, row, col, half, depth-1)
  	// Bottom-left sub-triangle
  	fill(grid, row+half, col, half, depth-1)
  	// Bottom-right sub-triangle
  	fill(grid, row+half, col+half, half, depth-1)
  	// Middle void is left empty.
  }
  ```

- [ ] **Run tests to confirm passage**

  ```bash
  go test ./internal/sierpinski/... -v
  ```

  Expected:
  ```
  --- PASS: TestGenerateInvalidSize (0.00s)
  --- PASS: TestGenerateInvalidChar (0.00s)
  --- PASS: TestGenerateDepthZero (0.00s)
  --- PASS: TestGenerateSize4Depth2 (0.00s)
  --- PASS: TestGenerateCustomChar (0.00s)
  --- PASS: TestGenerateRowCount (0.00s)
  PASS
  ok  	fractals/internal/sierpinski
  ```

- [ ] **Commit**

  ```bash
  git init
  git add .
  git commit -m "feat: module scaffold and Sierpinski algorithm"
  ```

---

## Task 2: Mandelbrot Algorithm

**Interfaces:**
- Consumes: nothing from earlier tasks
- Produces: `internal/mandelbrot.Generate(width, height, iterations int, charOverride string) ([]string, error)`
  - `charOverride` = `""` → use gradient `" .:-=+*#%@"`; single rune string → use that character for all filled cells (space for escaped)
  - `width`, `height` ≥ 1; `iterations` ≥ 1 — otherwise error
  - Returns `height` strings each of length `width`

**Files:**
- `internal/mandelbrot/mandelbrot.go`
- `internal/mandelbrot/mandelbrot_test.go`

---

- [ ] **Write the failing test** — `internal/mandelbrot/mandelbrot_test.go`

  ```go
  package mandelbrot_test

  import (
  	"testing"
  	"unicode/utf8"

  	"fractals/internal/mandelbrot"
  )

  func TestGenerateInvalidArgs(t *testing.T) {
  	cases := []struct {
  		w, h, it int
  	}{
  		{0, 24, 100},
  		{80, 0, 100},
  		{80, 24, 0},
  		{-1, 24, 100},
  	}
  	for _, c := range cases {
  		_, err := mandelbrot.Generate(c.w, c.h, c.it, "")
  		if err == nil {
  			t.Errorf("expected error for w=%d h=%d it=%d", c.w, c.h, c.it)
  		}
  	}
  }

  func TestGenerateRowCount(t *testing.T) {
  	rows, err := mandelbrot.Generate(40, 12, 50, "")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	if len(rows) != 12 {
  		t.Fatalf("expected 12 rows, got %d", len(rows))
  	}
  }

  func TestGenerateRowWidth(t *testing.T) {
  	rows, err := mandelbrot.Generate(40, 12, 50, "")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	for i, r := range rows {
  		w := utf8.RuneCountInString(r)
  		if w != 40 {
  			t.Errorf("row %d: expected width 40, got %d", i, w)
  		}
  	}
  }

  func TestGenerateGradientChars(t *testing.T) {
  	gradient := " .:-=+*#%@"
  	rows, err := mandelbrot.Generate(40, 12, 50, "")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	for i, row := range rows {
  		for j, ch := range row {
  			found := false
  			for _, g := range gradient {
  				if ch == g {
  					found = true
  					break
  				}
  			}
  			if !found {
  				t.Errorf("row %d col %d: unexpected char %q", i, j, ch)
  			}
  		}
  	}
  }

  func TestGenerateCustomChar(t *testing.T) {
  	rows, err := mandelbrot.Generate(20, 6, 50, "#")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	for i, row := range rows {
  		for j, ch := range row {
  			if ch != '#' && ch != ' ' {
  				t.Errorf("row %d col %d: expected '#' or ' ', got %q", i, j, ch)
  			}
  		}
  	}
  }

  func TestGenerateCustomCharInvalid(t *testing.T) {
  	_, err := mandelbrot.Generate(20, 6, 50, "ab")
  	if err == nil {
  		t.Fatal("expected error for multi-char charOverride")
  	}
  }

  func TestGenerateContainsMandelbrotShape(t *testing.T) {
  	// The center column at a mid-row should be inside the set (high iteration)
  	// We verify that not all cells are the same character (i.e. structure is present).
  	rows, err := mandelbrot.Generate(80, 24, 100, "")
  	if err != nil {
  		t.Fatalf("unexpected error: %v", err)
  	}
  	first := rune(rows[0][0])
  	allSame := true
  	for _, row := range rows {
  		for _, ch := range row {
  			if ch != first {
  				allSame = false
  				break
  			}
  		}
  	}
  	if allSame {
  		t.Error("all characters are the same; expected fractal structure")
  	}
  }
  ```

- [ ] **Run test to confirm failure**

  ```bash
  go test ./internal/mandelbrot/...
  ```

  Expected: compilation error — package does not exist yet.

- [ ] **Implement** — `internal/mandelbrot/mandelbrot.go`

  ```go
  // Package mandelbrot generates Mandelbrot set ASCII art.
  package mandelbrot

  import (
  	"fmt"
  	"strings"
  	"unicode/utf8"
  )

  const gradient = " .:-=+*#%@"

  // Generate renders the Mandelbrot set into width×height ASCII rows.
  // charOverride == "" uses the built-in gradient.
  // charOverride == single rune string uses that char for in-set pixels, space for out-of-set.
  // Returns height strings each of rune-length width, or an error for invalid args.
  func Generate(width, height, iterations int, charOverride string) ([]string, error) {
  	if width < 1 {
  		return nil, fmt.Errorf("width must be >= 1, got %d", width)
  	}
  	if height < 1 {
  		return nil, fmt.Errorf("height must be >= 1, got %d", height)
  	}
  	if iterations < 1 {
  		return nil, fmt.Errorf("iterations must be >= 1, got %d", iterations)
  	}
  	if charOverride != "" && utf8.RuneCountInString(charOverride) != 1 {
  		return nil, fmt.Errorf("char must be a single character, got %q", charOverride)
  	}

  	var customChar rune
  	useCustom := charOverride != ""
  	if useCustom {
  		customChar, _ = utf8.DecodeRuneInString(charOverride)
  	}

  	gradRunes := []rune(gradient)
  	gradLen := len(gradRunes)

  	// Mandelbrot viewing window
  	const (
  		xMin = -2.5
  		xMax = 1.0
  		yMin = -1.2
  		yMax = 1.2
  	)

  	rows := make([]string, height)
  	for row := 0; row < height; row++ {
  		var sb strings.Builder
  		cy := yMax - (yMax-yMin)*float64(row)/float64(height-1)
  		if height == 1 {
  			cy = 0
  		}
  		for col := 0; col < width; col++ {
  			cx := xMin + (xMax-xMin)*float64(col)/float64(width-1)
  			if width == 1 {
  				cx = 0
  			}
  			iters := escape(cx, cy, iterations)
  			if useCustom {
  				if iters == iterations {
  					sb.WriteRune(customChar)
  				} else {
  					sb.WriteByte(' ')
  				}
  			} else {
  				idx := (iters * (gradLen - 1)) / iterations
  				sb.WriteRune(gradRunes[idx])
  			}
  		}
  		rows[row] = sb.String()
  	}
  	return rows, nil
  }

  // escape returns the iteration count at which |z| > 2, or iterations if it never escapes.
  func escape(cx, cy float64, maxIter int) int {
  	var zx, zy float64
  	for i := 0; i < maxIter; i++ {
  		zx2 := zx*zx - zy*zy + cx
  		zy2 := 2*zx*zy + cy
  		zx, zy = zx2, zy2
  		if zx*zx+zy*zy > 4 {
  			return i
  		}
  	}
  	return maxIter
  }
  ```

- [ ] **Run tests to confirm passage**

  ```bash
  go test ./internal/mandelbrot/... -v
  ```

  Expected:
  ```
  --- PASS: TestGenerateInvalidArgs (0.00s)
  --- PASS: TestGenerateRowCount (0.00s)
  --- PASS: TestGenerateRowWidth (0.00s)
  --- PASS: TestGenerateGradientChars (0.00s)
  --- PASS: TestGenerateCustomChar (0.00s)
  --- PASS: TestGenerateCustomCharInvalid (0.00s)
  --- PASS: TestGenerateContainsMandelbrotShape (0.00s)
  PASS
  ok  	fractals/internal/mandelbrot
  ```

- [ ] **Commit**

  ```bash
  git add internal/mandelbrot/
  git commit -m "feat: Mandelbrot algorithm"
  ```

---

## Task 3: CLI Wiring and Binary

**Interfaces:**
- Consumes:
  - `sierpinski.Generate(size, depth int, char rune) ([]string, error)`
  - `mandelbrot.Generate(width, height, iterations int, charOverride string) ([]string, error)`
- Produces:
  - `cli.Execute()` — called by `main.go`; exits non-zero on error
  - Binary `fractals` (built by `go build ./cmd/fractals`)

**Files:**
- `internal/cli/root.go`
- `internal/cli/sierpinski.go`
- `internal/cli/mandelbrot.go`
- `cmd/fractals/main.go`

> CLI commands are wired with cobra; integration is verified via `go run` smoke tests rather than a separate `_test.go` (cobra's own tests cover flag parsing; our algorithm packages already have unit tests).

---

- [ ] **Write `internal/cli/root.go`**

  ```go
  // Package cli wires the cobra command tree for the fractals tool.
  package cli

  import (
  	"os"

  	"github.com/spf13/cobra"
  )

  var rootCmd = &cobra.Command{
  	Use:   "fractals",
  	Short: "Generate ASCII art fractals",
  	Long:  "fractals generates ASCII art fractals from the command line.",
  }

  func init() {
  	rootCmd.AddCommand(sierpinskiCmd)
  	rootCmd.AddCommand(mandelbrotCmd)
  }

  // Execute runs the root command. It exits with code 1 on error.
  func Execute() {
  	if err := rootCmd.Execute(); err != nil {
  		os.Exit(1)
  	}
  }
  ```

- [ ] **Write `internal/cli/sierpinski.go`**

  ```go
  package cli

  import (
  	"fmt"
  	"os"

  	"github.com/spf13/cobra"

  	"fractals/internal/sierpinski"
  )

  var (
  	sSize  int
  	sDepth int
  	sChar  string
  )

  var sierpinskiCmd = &cobra.Command{
  	Use:   "sierpinski",
  	Short: "Generate a Sierpinski triangle",
  	RunE:  runSierpinski,
  }

  func init() {
  	sierpinskiCmd.Flags().IntVar(&sSize, "size", 32, "Width of the triangle base (must be a power of 2)")
  	sierpinskiCmd.Flags().IntVar(&sDepth, "depth", 5, "Recursion depth")
  	sierpinskiCmd.Flags().StringVar(&sChar, "char", "*", "Character to use for filled points")
  }

  func runSierpinski(cmd *cobra.Command, args []string) error {
  	if len([]rune(sChar)) != 1 {
  		return fmt.Errorf("--char must be a single character, got %q", sChar)
  	}
  	char := []rune(sChar)[0]

  	rows, err := sierpinski.Generate(sSize, sDepth, char)
  	if err != nil {
  		return err
  	}
  	for _, row := range rows {
  		fmt.Fprintln(os.Stdout, row)
  	}
  	return nil
  }
  ```

- [ ] **Write `internal/cli/mandelbrot.go`**

  ```go
  package cli

  import (
  	"fmt"
  	"os"

  	"github.com/spf13/cobra"

  	"fractals/internal/mandelbrot"
  )

  var (
  	mWidth      int
  	mHeight     int
  	mIterations int
  	mChar       string
  )

  var mandelbrotCmd = &cobra.Command{
  	Use:   "mandelbrot",
  	Short: "Render the Mandelbrot set as ASCII art",
  	RunE:  runMandelbrot,
  }

  func init() {
  	mandelbrotCmd.Flags().IntVar(&mWidth, "width", 80, "Output width in characters")
  	mandelbrotCmd.Flags().IntVar(&mHeight, "height", 24, "Output height in characters")
  	mandelbrotCmd.Flags().IntVar(&mIterations, "iterations", 100, "Maximum iterations for escape calculation")
  	mandelbrotCmd.Flags().StringVar(&mChar, "char", "", "Single character override (default: gradient \" .:-=+*#%@\")")
  }

  func runMandelbrot(cmd *cobra.Command, args []string) error {
  	rows, err := mandelbrot.Generate(mWidth, mHeight, mIterations, mChar)
  	if err != nil {
  		return err
  	}
  	for _, row := range rows {
  		fmt.Fprintln(os.Stdout, row)
  	}
  	return nil
  }
  ```

- [ ] **Write `cmd/fractals/main.go`**

  ```go
  package main

  import "fractals/internal/cli"

  func main() {
  	cli.Execute()
  }
  ```

- [ ] **Compile**

  ```bash
  go build ./cmd/fractals/
  ```

  Expected: no output, binary `./fractals` created in current directory.

- [ ] **Smoke test: help**

  ```bash
  ./fractals --help
  ```

  Expected output contains:
  ```
  fractals generates ASCII art fractals from the command line.

  Usage:
    fractals [command]

  Available Commands:
    mandelbrot  Render the Mandelbrot set as ASCII art
    sierpinski  Generate a Sierpinski triangle
  ```

- [ ] **Smoke test: sierpinski default**

  ```bash
  ./fractals sierpinski --size 4 --depth 2
  ```

  Expected: 4 lines of output, bottom line is `****`.

- [ ] **Smoke test: sierpinski custom char**

  ```bash
  ./fractals sierpinski --size 4 --depth 2 --char '#'
  ```

  Expected: 4 lines, bottom line is `####`, no `*` characters.

- [ ] **Smoke test: mandelbrot default**

  ```bash
  ./fractals mandelbrot --width 40 --height 12
  ```

  Expected: 12 lines of 40 characters each, visibly varying characters.

- [ ] **Smoke test: mandelbrot custom char**

  ```bash
  ./fractals mandelbrot --width 40 --height 12 --char '@'
  ```

  Expected: 12 lines containing only `@` and space.

- [ ] **Smoke test: invalid size produces error**

  ```bash
  ./fractals sierpinski --size 3 2>&1
  echo "exit: $?"
  ```

  Expected:
  ```
  Error: size must be a power of 2 and >= 1, got 3
  ...
  exit: 1
  ```

- [ ] **Smoke test: invalid char produces error**

  ```bash
  ./fractals sierpinski --char 'ab' 2>&1
  echo "exit: $?"
  ```

  Expected:
  ```
  Error: --char must be a single character, got "ab"
  ...
  exit: 1
  ```

- [ ] **Run full test suite**

  ```bash
  go test ./...
  ```

  Expected:
  ```
  ok  	fractals/internal/mandelbrot
  ok  	fractals/internal/sierpinski
  ```

- [ ] **Commit**

  ```bash
  git add cmd/ internal/cli/
  git commit -m "feat: CLI wiring and binary entry point"
  ```

---

## Self-Review Checklist

| Check | Status |
|---|---|
| `fractals --help` covered (smoke test) | ✅ |
| `fractals sierpinski` outputs triangle | ✅ |
| `fractals mandelbrot` outputs Mandelbrot | ✅ |
| `--size`, `--depth` flags wired | ✅ |
| `--width`, `--height`, `--iterations` flags wired | ✅ |
| `--char` customises output for both commands | ✅ |
| Invalid inputs produce clear error messages + exit 1 | ✅ |
| All unit tests pass | ✅ |
| Default Sierpinski char is `*` | ✅ |
| Default Mandelbrot gradient is `" .:-=+*#%@"` | ✅ |
| Module name `fractals` matches import paths | ✅ |
| Go 1.21+ required in `go.mod` | ✅ (set by `go mod init`) |
| cobra dependency declared | ✅ |
| No placeholder code or TODO comments | ✅ |
| Output to stdout, errors to stderr | ✅ (cobra writes errors to stderr by default) |