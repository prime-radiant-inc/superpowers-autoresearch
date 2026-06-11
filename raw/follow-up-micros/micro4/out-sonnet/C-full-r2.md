# Go Fractals CLI — Implementation Plan

## Global Constraints

- Go 1.21+
- `github.com/spf13/cobra` for CLI (no other third-party dependencies)
- Binary name: `fractals`
- Default Sierpinski char: `*`
- Default Mandelbrot gradient: `" .:-=+*#%@"` (10 chars, space through @)
- Sierpinski defaults: `--size 32`, `--depth 5`
- Mandelbrot defaults: `--width 80`, `--height 24`, `--iterations 100`
- Package layout exactly as specified: `cmd/fractals/main.go`, `internal/sierpinski/`, `internal/mandelbrot/`, `internal/cli/`

---

## File Structure

| File | Responsibility |
|---|---|
| `cmd/fractals/main.go` | Entry point; calls `cli.Execute()` |
| `internal/cli/root.go` | Root cobra command, `Execute()` function |
| `internal/cli/sierpinski.go` | Sierpinski subcommand; parses flags, calls algorithm, prints |
| `internal/cli/mandelbrot.go` | Mandelbrot subcommand; parses flags, calls algorithm, prints |
| `internal/sierpinski/sierpinski.go` | Pure algorithm: `Generate(size, depth int, ch rune) []string` |
| `internal/sierpinski/sierpinski_test.go` | Unit tests for the algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure algorithm: `Generate(width, height, iterations int, ch rune) []string` |
| `internal/mandelbrot/mandelbrot_test.go` | Unit tests for the algorithm |
| `go.mod` / `go.sum` | Module definition |

---

## Task 1: Module Scaffold and Cobra Dependency

**Interfaces:**
- Produces: `go.mod` declaring module `github.com/user/fractals`, Go 1.21, cobra dependency; `go.sum`; compilable `cmd/fractals/main.go` that exits 0

**Files:**
- `go.mod`
- `go.sum`
- `cmd/fractals/main.go`
- `internal/cli/root.go`

---

- [ ] **Create the module and install cobra**

  ```bash
  mkdir -p fractals && cd fractals
  go mod init github.com/user/fractals
  go get github.com/spf13/cobra@latest
  ```

  Expected: `go.mod` contains `require github.com/spf13/cobra v1.x.x`; `go.sum` populated.

- [ ] **Write `internal/cli/root.go`**

  ```go
  // internal/cli/root.go
  package cli

  import (
      "github.com/spf13/cobra"
  )

  var rootCmd = &cobra.Command{
      Use:   "fractals",
      Short: "Generate ASCII art fractals",
      Long:  "A command-line tool that generates ASCII art fractals (Sierpinski triangle, Mandelbrot set).",
  }

  // Execute runs the root command.
  func Execute() error {
      return rootCmd.Execute()
  }
  ```

- [ ] **Write `cmd/fractals/main.go`**

  ```go
  // cmd/fractals/main.go
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

- [ ] **Verify it compiles and `--help` works**

  ```bash
  go build ./cmd/fractals/
  ./fractals --help
  ```

  Expected output contains:
  ```
  A command-line tool that generates ASCII art fractals
  ```

- [ ] **Commit**

  ```bash
  git init
  git add .
  git commit -m "task 1: module scaffold, cobra root command"
  ```

---

## Task 2: Sierpinski Algorithm

**Interfaces:**
- Consumes: nothing
- Produces:
  ```go
  // package sierpinski
  func Generate(size, depth int, ch rune) ([]string, error)
  ```
  Returns `(nil, error)` when `size < 1`, `depth < 0`, or `ch == 0`.
  Returns a `[]string` of length `size`, each string exactly `size` bytes wide (spaces + `ch`), representing the triangle.

**Files:**
- `internal/sierpinski/sierpinski.go`
- `internal/sierpinski/sierpinski_test.go`

---

- [ ] **Write the failing tests first — `internal/sierpinski/sierpinski_test.go`**

  ```go
  // internal/sierpinski/sierpinski_test.go
  package sierpinski_test

  import (
      "strings"
      "testing"

      "github.com/user/fractals/internal/sierpinski"
  )

  func TestGenerate_InvalidInputs(t *testing.T) {
      cases := []struct {
          name       string
          size, depth int
          ch         rune
      }{
          {"zero size", 0, 3, '*'},
          {"negative size", -1, 3, '*'},
          {"negative depth", 4, -1, '*'},
          {"zero char", 4, 3, 0},
      }
      for _, tc := range cases {
          t.Run(tc.name, func(t *testing.T) {
              _, err := sierpinski.Generate(tc.size, tc.depth, tc.ch)
              if err == nil {
                  t.Errorf("expected error for size=%d depth=%d ch=%d", tc.size, tc.depth, tc.ch)
              }
          })
      }
  }

  func TestGenerate_RowCount(t *testing.T) {
      rows, err := sierpinski.Generate(8, 3, '*')
      if err != nil {
          t.Fatalf("unexpected error: %v", err)
      }
      if len(rows) != 8 {
          t.Errorf("expected 8 rows, got %d", len(rows))
      }
  }

  func TestGenerate_RowWidth(t *testing.T) {
      size := 16
      rows, err := sierpinski.Generate(size, 4, '*')
      if err != nil {
          t.Fatalf("unexpected error: %v", err)
      }
      for i, row := range rows {
          if len(row) != size {
              t.Errorf("row %d: expected width %d, got %d", i, size, len(row))
          }
      }
  }

  func TestGenerate_TopRowHasChar(t *testing.T) {
      rows, err := sierpinski.Generate(4, 2, '#')
      if err != nil {
          t.Fatalf("unexpected error: %v", err)
      }
      // The apex of the triangle must contain the fill character
      combined := strings.Join(rows, "\n")
      if !strings.ContainsRune(combined, '#') {
          t.Error("output contains no fill character")
      }
  }

  func TestGenerate_DepthZeroIsSolidTriangle(t *testing.T) {
      // depth=0 means no subdivision: every point in the lower-left triangle is filled
      rows, err := sierpinski.Generate(4, 0, '*')
      if err != nil {
          t.Fatalf("unexpected error: %v", err)
      }
      // Bottom row should be entirely fill characters
      bottom := rows[len(rows)-1]
      for i, c := range bottom {
          if c != '*' {
              t.Errorf("bottom row pos %d expected '*', got %q", i, c)
          }
      }
  }

  func TestGenerate_Size1(t *testing.T) {
      rows, err := sierpinski.Generate(1, 5, '*')
      if err != nil {
          t.Fatalf("unexpected error: %v", err)
      }
      if len(rows) != 1 || rows[0] != "*" {
          t.Errorf("size=1 expected [\"*\"], got %v", rows)
      }
  }
  ```

- [ ] **Run tests — confirm they fail (package doesn't exist yet)**

  ```bash
  go test ./internal/sierpinski/
  ```

  Expected: compilation error — `cannot find package`.

- [ ] **Implement `internal/sierpinski/sierpinski.go`**

  ```go
  // internal/sierpinski/sierpinski.go
  package sierpinski

  import (
      "errors"
      "strings"
  )

  // Generate returns a []string of length size, each exactly size bytes wide,
  // representing a Sierpinski triangle drawn with ch.
  // depth controls recursion; depth=0 gives a solid triangle.
  func Generate(size, depth int, ch rune) ([]string, error) {
      if size < 1 {
          return nil, errors.New("sierpinski: size must be >= 1")
      }
      if depth < 0 {
          return nil, errors.New("sierpinski: depth must be >= 0")
      }
      if ch == 0 {
          return nil, errors.New("sierpinski: ch must not be zero")
      }

      // Build a size×size grid, row-major, initialized to spaces.
      grid := make([][]rune, size)
      for i := range grid {
          grid[i] = []rune(strings.Repeat(" ", size))
      }

      fill(grid, 0, 0, size, depth, ch)

      rows := make([]string, size)
      for i, row := range grid {
          rows[i] = string(row)
      }
      return rows, nil
  }

  // fill draws a Sierpinski triangle of the given size into grid,
  // with its top-left corner at (col, row).
  // The triangle occupies rows [row, row+size) and is left-aligned.
  func fill(grid [][]rune, col, row, size, depth int, ch rune) {
      if size <= 0 {
          return
      }
      if size == 1 {
          setCell(grid, col, row, ch)
          return
      }
      if depth == 0 {
          // Solid filled triangle (lower-left half)
          for r := 0; r < size; r++ {
              for c := 0; c <= r; c++ {
                  setCell(grid, col+c, row+r, ch)
              }
          }
          return
      }

      half := size / 2
      // Top sub-triangle
      fill(grid, col, row, half, depth-1, ch)
      // Bottom-left sub-triangle
      fill(grid, col, row+half, half, depth-1, ch)
      // Bottom-right sub-triangle
      fill(grid, col+half, row+half, half, depth-1, ch)
  }

  func setCell(grid [][]rune, col, row int, ch rune) {
      if row >= 0 && row < len(grid) && col >= 0 && col < len(grid[row]) {
          grid[row][col] = ch
      }
  }
  ```

- [ ] **Run tests — all pass**

  ```bash
  go test ./internal/sierpinski/ -v
  ```

  Expected:
  ```
  --- PASS: TestGenerate_InvalidInputs/zero_size
  --- PASS: TestGenerate_InvalidInputs/negative_size
  --- PASS: TestGenerate_InvalidInputs/negative_depth
  --- PASS: TestGenerate_InvalidInputs/zero_char
  --- PASS: TestGenerate_RowCount
  --- PASS: TestGenerate_RowWidth
  --- PASS: TestGenerate_TopRowHasChar
  --- PASS: TestGenerate_DepthZeroIsSolidTriangle
  --- PASS: TestGenerate_Size1
  PASS
  ```

- [ ] **Commit**

  ```bash
  git add internal/sierpinski/
  git commit -m "task 2: Sierpinski algorithm with tests"
  ```

---

## Task 3: Mandelbrot Algorithm

**Interfaces:**
- Consumes: nothing
- Produces:
  ```go
  // package mandelbrot
  func Generate(width, height, iterations int, ch rune) ([]string, error)
  ```
  - `ch == 0` → use gradient `" .:-=+*#%@"` (10 chars)
  - `ch != 0` → use that single character for all non-escaped points; escaped points are `' '`
  - Returns `(nil, error)` when `width < 1`, `height < 1`, or `iterations < 1`
  - Returns `[]string` of length `height`, each string exactly `width` bytes wide

**Files:**
- `internal/mandelbrot/mandelbrot.go`
- `internal/mandelbrot/mandelbrot_test.go`

---

- [ ] **Write the failing tests — `internal/mandelbrot/mandelbrot_test.go`**

  ```go
  // internal/mandelbrot/mandelbrot_test.go
  package mandelbrot_test

  import (
      "strings"
      "testing"

      "github.com/user/fractals/internal/mandelbrot"
  )

  func TestGenerate_InvalidInputs(t *testing.T) {
      cases := []struct {
          name                   string
          width, height, iters   int
          ch                     rune
      }{
          {"zero width", 0, 10, 50, 0},
          {"negative width", -1, 10, 50, 0},
          {"zero height", 10, 0, 50, 0},
          {"negative height", 10, -1, 50, 0},
          {"zero iterations", 10, 10, 0, 0},
          {"negative iterations", 10, 10, -1, 0},
      }
      for _, tc := range cases {
          t.Run(tc.name, func(t *testing.T) {
              _, err := mandelbrot.Generate(tc.width, tc.height, tc.iters, tc.ch)
              if err == nil {
                  t.Errorf("expected error for width=%d height=%d iters=%d", tc.width, tc.height, tc.iters)
              }
          })
      }
  }

  func TestGenerate_Dimensions(t *testing.T) {
      rows, err := mandelbrot.Generate(40, 12, 50, 0)
      if err != nil {
          t.Fatalf("unexpected error: %v", err)
      }
      if len(rows) != 12 {
          t.Errorf("expected 12 rows, got %d", len(rows))
      }
      for i, row := range rows {
          if len(row) != 40 {
              t.Errorf("row %d: expected width 40, got %d", i, len(row))
          }
      }
  }

  func TestGenerate_GradientContainsNonSpace(t *testing.T) {
      // With gradient mode the Mandelbrot interior should produce non-space chars
      rows, err := mandelbrot.Generate(40, 12, 50, 0)
      if err != nil {
          t.Fatalf("unexpected error: %v", err)
      }
      combined := strings.Join(rows, "")
      if combined == strings.Repeat(" ", 40*12) {
          t.Error("gradient output is all spaces — Mandelbrot not rendering")
      }
  }

  func TestGenerate_CustomChar(t *testing.T) {
      rows, err := mandelbrot.Generate(40, 12, 50, '#')
      if err != nil {
          t.Fatalf("unexpected error: %v", err)
      }
      combined := strings.Join(rows, "")
      if !strings.ContainsRune(combined, '#') {
          t.Error("custom char '#' not found in output")
      }
      // No gradient chars other than '#' and ' ' should appear
      for _, c := range combined {
          if c != '#' && c != ' ' {
              t.Errorf("unexpected char %q in custom-char mode", c)
          }
      }
  }

  func TestGenerate_Size1x1(t *testing.T) {
      rows, err := mandelbrot.Generate(1, 1, 10, 0)
      if err != nil {
          t.Fatalf("unexpected error: %v", err)
      }
      if len(rows) != 1 || len(rows[0]) != 1 {
          t.Errorf("expected 1×1 grid, got %v", rows)
      }
  }
  ```

- [ ] **Run tests — confirm they fail**

  ```bash
  go test ./internal/mandelbrot/
  ```

  Expected: compilation error — package not found.

- [ ] **Implement `internal/mandelbrot/mandelbrot.go`**

  ```go
  // internal/mandelbrot/mandelbrot.go
  package mandelbrot

  import (
      "errors"
      "math/cmplx"
      "strings"
  )

  const gradient = " .:-=+*#%@"

  // Generate renders the Mandelbrot set into a []string of length height,
  // each string exactly width bytes wide.
  // ch==0 selects the default gradient; any other rune is used for set members
  // (non-members are rendered as space).
  func Generate(width, height, iterations int, ch rune) ([]string, error) {
      if width < 1 {
          return nil, errors.New("mandelbrot: width must be >= 1")
      }
      if height < 1 {
          return nil, errors.New("mandelbrot: height must be >= 1")
      }
      if iterations < 1 {
          return nil, errors.New("mandelbrot: iterations must be >= 1")
      }

      // Viewport: real [-2.5, 1.0], imag [-1.2, 1.2]
      const (
          rMin = -2.5
          rMax = 1.0
          iMin = -1.2
          iMax = 1.2
      )

      rows := make([]string, height)
      glyphs := []rune(gradient)
      useGradient := ch == 0

      for row := 0; row < height; row++ {
          var sb strings.Builder
          sb.Grow(width)
          im := iMax - (iMax-iMin)*float64(row)/float64(height)
          for col := 0; col < width; col++ {
              re := rMin + (rMax-rMin)*float64(col)/float64(width)
              c := complex(re, im)
              escaped, iter := escape(c, iterations)
              var out rune
              if useGradient {
                  if escaped {
                      idx := iter * (len(glyphs) - 1) / iterations
                      out = glyphs[idx]
                  } else {
                      out = glyphs[len(glyphs)-1]
                  }
              } else {
                  if escaped {
                      out = ' '
                  } else {
                      out = ch
                  }
              }
              sb.WriteRune(out)
          }
          rows[row] = sb.String()
      }
      return rows, nil
  }

  // escape returns whether c escaped within maxIter iterations and the
  // iteration count at escape (0 if it did not escape).
  func escape(c complex128, maxIter int) (bool, int) {
      z := complex128(0)
      for i := 0; i < maxIter; i++ {
          z = z*z + c
          if cmplx.Abs(z) > 2.0 {
              return true, i
          }
      }
      return false, 0
  }
  ```

- [ ] **Run tests — all pass**

  ```bash
  go test ./internal/mandelbrot/ -v
  ```

  Expected:
  ```
  --- PASS: TestGenerate_InvalidInputs/zero_width
  --- PASS: TestGenerate_InvalidInputs/negative_width
  --- PASS: TestGenerate_InvalidInputs/zero_height
  --- PASS: TestGenerate_InvalidInputs/negative_height
  --- PASS: TestGenerate_InvalidInputs/zero_iterations
  --- PASS: TestGenerate_InvalidInputs/negative_iterations
  --- PASS: TestGenerate_Dimensions
  --- PASS: TestGenerate_GradientContainsNonSpace
  --- PASS: TestGenerate_CustomChar
  --- PASS: TestGenerate_Size1x1
  PASS
  ```

- [ ] **Commit**

  ```bash
  git add internal/mandelbrot/
  git commit -m "task 3: Mandelbrot algorithm with tests"
  ```

---

## Task 4: Sierpinski CLI Subcommand

**Interfaces:**
- Consumes:
  ```go
  sierpinski.Generate(size, depth int, ch rune) ([]string, error)
  ```
- Produces: `sierpinski` cobra subcommand registered on `rootCmd`; `internal/cli/sierpinski.go`

**Files:**
- `internal/cli/sierpinski.go`
- `internal/cli/root.go` (add `init()` registration)

---

- [ ] **Write `internal/cli/sierpinski.go`**

  ```go
  // internal/cli/sierpinski.go
  package cli

  import (
      "fmt"
      "os"

      "github.com/spf13/cobra"
      "github.com/user/fractals/internal/sierpinski"
  )

  var sierpinskiCmd = &cobra.Command{
      Use:   "sierpinski",
      Short: "Generate a Sierpinski triangle",
      Long:  "Generates a Sierpinski triangle using recursive subdivision.",
      RunE:  runSierpinski,
  }

  var (
      sSize  int
      sDepth int
      sChar  string
  )

  func init() {
      sierpinskiCmd.Flags().IntVar(&sSize, "size", 32, "Width of the triangle base in characters")
      sierpinskiCmd.Flags().IntVar(&sDepth, "depth", 5, "Recursion depth")
      sierpinskiCmd.Flags().StringVar(&sChar, "char", "*", "Character to use for filled points")
      rootCmd.AddCommand(sierpinskiCmd)
  }

  func runSierpinski(cmd *cobra.Command, args []string) error {
      ch, err := parseSingleChar(sChar, "char")
      if err != nil {
          return err
      }
      rows, err := sierpinski.Generate(sSize, sDepth, ch)
      if err != nil {
          return err
      }
      for _, row := range rows {
          fmt.Fprintln(os.Stdout, row)
      }
      return nil
  }
  ```

- [ ] **Add `parseSingleChar` helper to `internal/cli/root.go`**

  ```go
  // internal/cli/root.go
  package cli

  import (
      "fmt"

      "github.com/spf13/cobra"
  )

  var rootCmd = &cobra.Command{
      Use:   "fractals",
      Short: "Generate ASCII art fractals",
      Long:  "A command-line tool that generates ASCII art fractals (Sierpinski triangle, Mandelbrot set).",
  }

  // Execute runs the root command.
  func Execute() error {
      return rootCmd.Execute()
  }

  // parseSingleChar validates that s is exactly one Unicode character.
  func parseSingleChar(s, flagName string) (rune, error) {
      runes := []rune(s)
      if len(runes) != 1 {
          return 0, fmt.Errorf("flag --%s must be exactly one character, got %q", flagName, s)
      }
      return runes[0], nil
  }
  ```

- [ ] **Build and smoke-test the subcommand**

  ```bash
  go build ./cmd/fractals/
  ./fractals sierpinski --help
  ```

  Expected output contains:
  ```
  --size int    Width of the triangle base in characters (default 32)
  --depth int   Recursion depth (default 5)
  --char string Character to use for filled points (default "*")
  ```

- [ ] **Run a quick visual check**

  ```bash
  ./fractals sierpinski --size 8 --depth 3
  ```

  Expected: 8-line ASCII triangle printed to stdout (non-empty, contains `*`).

- [ ] **Test invalid `--char`**

  ```bash
  ./fractals sierpinski --char "ab"
  echo "exit: $?"
  ```

  Expected: error message containing `must be exactly one character`; exit code `1`.

- [ ] **Test invalid `--size`**

  ```bash
  ./fractals sierpinski --size 0
  echo "exit: $?"
  ```

  Expected: error message containing `size must be >= 1`; exit code `1`.

- [ ] **Commit**

  ```bash
  git add internal/cli/
  git commit -m "task 4: sierpinski CLI subcommand"
  ```

---

## Task 5: Mandelbrot CLI Subcommand

**Interfaces:**
- Consumes:
  ```go
  mandelbrot.Generate(width, height, iterations int, ch rune) ([]string, error)
  ```
- Produces: `mandelbrot` cobra subcommand registered on `rootCmd`; `internal/cli/mandelbrot.go`

**Files:**
- `internal/cli/mandelbrot.go`

---

- [ ] **Write `internal/cli/mandelbrot.go`**

  ```go
  // internal/cli/mandelbrot.go
  package cli

  import (
      "fmt"
      "os"

      "github.com/spf13/cobra"
      "github.com/user/fractals/internal/mandelbrot"
  )

  var mandelbrotCmd = &cobra.Command{
      Use:   "mandelbrot",
      Short: "Render the Mandelbrot set as ASCII art",
      Long:  "Renders the Mandelbrot set as ASCII art, mapping iteration count to characters.",
      RunE:  runMandelbrot,
  }

  var (
      mWidth      int
      mHeight     int
      mIterations int
      mChar       string
  )

  func init() {
      mandelbrotCmd.Flags().IntVar(&mWidth, "width", 80, "Output width in characters")
      mandelbrotCmd.Flags().IntVar(&mHeight, "height", 24, "Output height in characters")
      mandelbrotCmd.Flags().IntVar(&mIterations, "iterations", 100, "Maximum iterations for escape calculation")
      mandelbrotCmd.Flags().StringVar(&mChar, "char", "", "Single character override (omit for gradient)")
      rootCmd.AddCommand(mandelbrotCmd)
  }

  func runMandelbrot(cmd *cobra.Command, args []string) error {
      var ch rune
      if mChar != "" {
          var err error
          ch, err = parseSingleChar(mChar, "char")
          if err != nil {
              return err
          }
      }
      // ch==0 signals gradient mode to Generate
      rows, err := mandelbrot.Generate(mWidth, mHeight, mIterations, ch)
      if err != nil {
          return err
      }
      for _, row := range rows {
          fmt.Fprintln(os.Stdout, row)
      }
      return nil
  }
  ```

- [ ] **Build and smoke-test**

  ```bash
  go build ./cmd/fractals/
  ./fractals mandelbrot --help
  ```

  Expected output contains:
  ```
  --width int       Output width in characters (default 80)
  --height int      Output height in characters (default 24)
  --iterations int  Maximum iterations for escape calculation (default 100)
  --char string     Single character override (omit for gradient)
  ```

- [ ] **Run a quick visual check**

  ```bash
  ./fractals mandelbrot --width 40 --height 12
  ```

  Expected: 12 lines of 40 characters each, containing recognizable Mandelbrot shape.

- [ ] **Test custom char**

  ```bash
  ./fractals mandelbrot --width 20 --height 6 --char '#'
  ```

  Expected: output contains `#` and only `#` and space.

- [ ] **Test invalid `--iterations`**

  ```bash
  ./fractals mandelbrot --iterations 0
  echo "exit: $?"
  ```

  Expected: error message containing `iterations must be >= 1`; exit code `1`.

- [ ] **Test invalid `--char`**

  ```bash
  ./fractals mandelbrot --char "xy"
  echo "exit: $?"
  ```

  Expected: error message containing `must be exactly one character`; exit code `1`.

- [ ] **Commit**

  ```bash
  git add internal/cli/mandelbrot.go
  git commit -m "task 5: mandelbrot CLI subcommand"
  ```

---

## Task 6: Full Test Suite and Final Acceptance Verification

**Interfaces:**
- Consumes: all packages from tasks 1–5
- Produces: all tests green; binary satisfies every acceptance criterion

**Files:**
- No new source files; runs existing tests and the built binary

---

- [ ] **Run the complete test suite**

  ```bash
  go test ./... -v
  ```

  Expected: every `--- PASS` line, final `ok` for both internal packages, no failures.

- [ ] **Acceptance criterion 1 — `fractals --help`**

  ```bash
  ./fractals --help
  ```

  Expected output contains `sierpinski` and `mandelbrot` in the list of available commands.

- [ ] **Acceptance criterion 2 — Sierpinski default output**

  ```bash
  ./fractals sierpinski | wc -l
  ```

  Expected: `32`

- [ ] **Acceptance criterion 3 — Mandelbrot default output**

  ```bash
  ./fractals mandelbrot | wc -l
  ```

  Expected: `24`

- [ ] **Acceptance criterion 4 — flags work**

  ```bash
  ./fractals sierpinski --size 16 --depth 4 | wc -l
  ```
  Expected: `16`

  ```bash
  ./fractals mandelbrot --width 40 --height 10 --iterations 50 | wc -l
  ```
  Expected: `10`

- [ ] **Acceptance criterion 5 — `--char` customises output**

  ```bash
  ./fractals sierpinski --size 8 --char '@' | grep -c '@'
  ```
  Expected: number > 0 (lines containing `@`).

  ```bash
  ./fractals mandelbrot --width 20 --height 6 --char '+'
  ```
  Expected: output contains `+`.

- [ ] **Acceptance criterion 6 — invalid inputs produce clear errors**

  ```bash
  ./fractals sierpinski --size -1 2>&1
  ```
  Expected: stderr contains `size must be >= 1`.

  ```bash
  ./fractals mandelbrot --width 0 2>&1
  ```
  Expected: stderr contains `width must be >= 1`.

  ```bash
  ./fractals sierpinski --char "!!" 2>&1
  ```
  Expected: stderr contains `must be exactly one character`.

- [ ] **Vet and check for issues**

  ```bash
  go vet ./...
  ```

  Expected: no output (no issues).

- [ ] **Final commit**

  ```bash
  git add .
  git commit -m "task 6: all tests pass, acceptance criteria verified"
  ```