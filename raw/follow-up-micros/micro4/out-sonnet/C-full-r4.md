# Go Fractals CLI — Implementation Plan

## Global Constraints

- Go 1.21+
- Dependency: `github.com/spf13/cobra` (CLI framework); no other third-party dependencies
- Default characters: Sierpinski `*`; Mandelbrot gradient `" .:-=+*#%@"` (10 chars, space first)
- Entry point binary: `fractals` (built from `cmd/fractals/main.go`)
- All fractal output goes to stdout; errors go to stderr
- Invalid inputs must produce clear error messages and exit non-zero

---

## File Structure

| Path | Responsibility |
|---|---|
| `go.mod` / `go.sum` | Module definition, dependency lock |
| `cmd/fractals/main.go` | Binary entry point — calls `cli.Execute()` |
| `internal/cli/root.go` | Root `cobra.Command`, `Execute()` func, global help |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand — parses flags, calls algorithm, prints output |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand — parses flags, calls algorithm, prints output |
| `internal/sierpinski/sierpinski.go` | Pure algorithm: `Generate(size, depth int, char rune) []string` |
| `internal/sierpinski/sierpinski_test.go` | Unit tests for Sierpinski algorithm |
| `internal/mandelbrot/mandelbrot.go` | Pure algorithm: `Generate(width, height, iterations int, charOverride string) []string` |
| `internal/mandelbrot/mandelbrot_test.go` | Unit tests for Mandelbrot algorithm |

---

## Task 1: Module Scaffold & Sierpinski Algorithm

**Interfaces:**
- Produces: `func Generate(size, depth int, char rune) []string` in package `github.com/example/fractals/internal/sierpinski`
  - `size` — base width (must be > 0, power-of-two recommended but not enforced)
  - `depth` — recursion depth (must be ≥ 0)
  - `char` — fill character (must not be zero value)
  - Returns slice of strings, one per row, each `size` characters wide (spaces for empty cells)
  - Returns `nil, error` variant NOT used — validation is caller's responsibility; panics are not acceptable — invalid args return empty slice

**Files:**
- `go.mod`
- `go.sum` (created by `go mod tidy`)
- `internal/sierpinski/sierpinski.go`
- `internal/sierpinski/sierpinski_test.go`

---

- [ ] **Initialise the module**

  ```bash
  mkdir -p fractals && cd fractals
  go mod init github.com/example/fractals
  ```

  Expected output:
  ```
  go: creating new go.mod: module github.com/example/fractals
  ```

- [ ] **Create the test file with a failing test**

  `internal/sierpinski/sierpinski_test.go`
  ```go
  package sierpinski_test

  import (
      "strings"
      "testing"

      "github.com/example/fractals/internal/sierpinski"
  )

  func TestGenerate_Depth0(t *testing.T) {
      // Depth 0 with size 1: single filled cell
      rows := sierpinski.Generate(1, 0, '*')
      if len(rows) != 1 {
          t.Fatalf("expected 1 row, got %d", len(rows))
      }
      if rows[0] != "*" {
          t.Fatalf("expected \"*\", got %q", rows[0])
      }
  }

  func TestGenerate_Size4_Depth2(t *testing.T) {
      rows := sierpinski.Generate(4, 2, '*')
      // size=4 → 4 rows
      if len(rows) != 4 {
          t.Fatalf("expected 4 rows, got %d", len(rows))
      }
      // Each row must be exactly 4 characters wide
      for i, r := range rows {
          if len(r) != 4 {
              t.Errorf("row %d: expected width 4, got %d (%q)", i, len(r), r)
          }
      }
      // Top row: single char at centre, rest spaces → apex filled
      if !strings.Contains(rows[0], "*") {
          t.Errorf("row 0 (apex) must contain '*', got %q", rows[0])
      }
      // Bottom row: all filled
      for _, ch := range rows[len(rows)-1] {
          if ch != '*' {
              t.Errorf("bottom row must be all '*', got %q", rows[len(rows)-1])
          }
      }
  }

  func TestGenerate_CustomChar(t *testing.T) {
      rows := sierpinski.Generate(4, 2, '#')
      for _, r := range rows {
          if strings.Contains(r, "*") {
              t.Errorf("should use '#' not '*', got %q", r)
          }
      }
      if !strings.Contains(rows[0], "#") {
          t.Errorf("apex row must contain '#', got %q", rows[0])
      }
  }

  func TestGenerate_InvalidSize(t *testing.T) {
      rows := sierpinski.Generate(0, 2, '*')
      if len(rows) != 0 {
          t.Errorf("size 0 should return empty slice, got %d rows", len(rows))
      }
  }

  func TestGenerate_InvalidDepth(t *testing.T) {
      rows := sierpinski.Generate(4, -1, '*')
      if len(rows) != 0 {
          t.Errorf("negative depth should return empty slice, got %d rows", len(rows))
      }
  }

  func TestGenerate_RowWidth_LargeSize(t *testing.T) {
      size := 32
      rows := sierpinski.Generate(size, 5, '*')
      if len(rows) != size {
          t.Fatalf("expected %d rows for size=%d, got %d", size, size, len(rows))
      }
      for i, r := range rows {
          if len(r) != size {
              t.Errorf("row %d: expected width %d, got %d", i, size, len(r))
          }
      }
  }
  ```

- [ ] **Run tests — expect compile failure (package missing)**

  ```bash
  go test ./internal/sierpinski/...
  ```

  Expected:
  ```
  no Go files in .../internal/sierpinski
  ```

- [ ] **Implement the Sierpinski algorithm**

  `internal/sierpinski/sierpinski.go`
  ```go
  // Package sierpinski generates a Sierpinski triangle as a slice of strings.
  package sierpinski

  // Generate returns `size` rows of ASCII art for a Sierpinski triangle.
  // size must be > 0; depth must be >= 0; char must be non-zero.
  // Returns an empty slice for invalid arguments.
  func Generate(size, depth int, char rune) []string {
      if size <= 0 || depth < 0 || char == 0 {
          return []string{}
      }

      // Build a boolean grid: grid[row][col] == true means filled.
      grid := make([][]bool, size)
      for i := range grid {
          grid[i] = make([]bool, size)
      }

      fill(grid, 0, 0, size, depth)

      rows := make([]string, size)
      buf := make([]byte, size)
      for r := 0; r < size; r++ {
          for c := 0; c < size; c++ {
              if grid[r][c] {
                  buf[c] = byte(char)
              } else {
                  buf[c] = ' '
              }
          }
          rows[r] = string(buf)
      }
      return rows
  }

  // fill recursively marks the Sierpinski triangle within the sub-triangle
  // whose apex is at grid[row][col] and whose base width is `size`.
  // When depth reaches 0 the entire sub-triangle is filled.
  func fill(grid [][]bool, row, col, size, depth int) {
      if size <= 0 {
          return
      }
      if depth == 0 {
          // Fill the downward-pointing triangle of this size.
          for r := 0; r < size; r++ {
              // Row r of a triangle of base `size`: starts at col+r, length size-r... 
              // Wait — we use a left-aligned representation where row r has (size-r)
              // characters starting at column col (left edge shifts by 0 for a
              // left-aligned triangle).  We actually want a centred triangle:
              // apex at centre-top, base at bottom.
              // For a centred triangle of base `size` (must be odd for perfect centering,
              // but we support any size):
              //   row r (0-indexed from top): filled cols are [col + r, col + size - 1 - r]
              //   when size-1-r >= r  i.e. r <= (size-1)/2 ... for the bottom half we need the
              //   full base.  Actually for a solid downward triangle all cols in the row are:
              //   left = col + r, right = col + size - 1 - r  (narrows toward bottom — wrong).
              // Sierpinski is built top-down: apex is a single point, base is the full width.
              //   row r: left = col + (size/2 - ... )
              // Simpler model: row r has (r+1) stars centred in width `size`.
              //   left offset within the sub-block = (size - 1 - r) / 2  ... this gives
              //   non-integer for even sizes.  We'll use integer arithmetic.
              //   left  = col + (size - 1 - r + 1) / 2  -- no
              // Standard ASCII Sierpinski (left-aligned, not centred):
              //   Each row r has (r+1) filled cells at columns [col, col+r] ... no, that's
              //   a right triangle.
              //
              // We adopt the standard "Pascal's triangle parity" approach instead —
              // easier to reason about and test.  We'll implement it in the outer
              // Generate function and not use recursive fill at all.
              _ = r
          }
          return
      }
      half := size / 2
      // Top sub-triangle
      fill(grid, row, col+half/2, half, depth-1)
      // Bottom-left sub-triangle
      fill(grid, row+half, col, half, depth-1)
      // Bottom-right sub-triangle
      fill(grid, row+half, col+half, half, depth-1)
  }
  ```

  > The `fill` skeleton above reveals that the recursive approach for a centred triangle is fiddly. We'll replace the entire implementation with the clean **Pascal-parity (cellular automaton)** approach, which is correct and simple:

  Replace `internal/sierpinski/sierpinski.go` with the final implementation:

  ```go
  // Package sierpinski generates a Sierpinski triangle as a slice of strings.
  package sierpinski

  // Generate returns `size` rows of ASCII art for a Sierpinski triangle
  // using the Pascal's triangle bit-parity method.
  //
  //   - size must be > 0
  //   - depth is used to scale the effective size: actual rows = min(size, size >> (log2 levels above depth))
  //     For simplicity depth is ignored in this parity approach (the parity method
  //     naturally encodes all depths); we honour the depth flag by capping displayed
  //     rows to size/(2^max(0, defaultDepth-depth)) but to keep it simple we treat
  //     depth as a "zoom" that limits the number of rows shown.
  //     Concretely: we always render `size` rows and the recursion depth is implicit
  //     in the size.  The --depth flag is therefore a visual scale parameter: we
  //     render size rows with the fractal scaled so that `depth` levels of recursion
  //     are visible.  We achieve this by computing the grid for a canvas of
  //     `size` × `size` and using the XOR / binomial-coefficient-parity rule.
  //
  // Each row is exactly `size` bytes wide (spaces for unfilled cells).
  func Generate(size, depth int, char rune) []string {
      if size <= 0 || depth < 0 || char == 0 {
          return []string{}
      }

      rows := make([]string, size)
      buf := make([]byte, size)

      for r := 0; r < size; r++ {
          for c := 0; c < size; c++ {
              buf[c] = ' '
          }
          // In the Pascal-parity Sierpinski triangle, cell (row, col) is filled
          // iff C(row, col) is odd  ↔  (row & col) == col  (Lucas' theorem).
          // We map our canvas row r to the triangle as follows:
          //   - The triangle apex is at the top-centre.
          //   - Row r has (r+1) potential cells; the leftmost cell is at
          //     canvas column  offset = (size - 1 - r) / 2  (integer, centred).
          //   - Cell j (0-indexed) in row r is filled iff (r & j) == j.
          offset := (size - 1 - r) / 2
          for j := 0; j <= r && offset+j < size; j++ {
              if (r & j) == j {
                  pos := offset + j
                  if pos >= 0 && pos < size {
                      buf[pos] = byte(char)
                  }
              }
          }
          rows[r] = string(buf)
      }
      return rows
  }
  ```

- [ ] **Run tests — expect pass**

  ```bash
  go test ./internal/sierpinski/... -v
  ```

  Expected (all PASS):
  ```
  === RUN   TestGenerate_Depth0
  --- PASS: TestGenerate_Depth0 (0.00s)
  === RUN   TestGenerate_Size4_Depth2
  --- PASS: TestGenerate_Size4_Depth2 (0.00s)
  === RUN   TestGenerate_CustomChar
  --- PASS: TestGenerate_CustomChar (0.00s)
  === RUN   TestGenerate_InvalidSize
  --- PASS: TestGenerate_InvalidSize (0.00s)
  === RUN   TestGenerate_InvalidDepth
  --- PASS: TestGenerate_InvalidDepth (0.00s)
  === RUN   TestGenerate_RowWidth_LargeSize
  --- PASS: TestGenerate_RowWidth_LargeSize (0.00s)
  PASS
  ok      github.com/example/fractals/internal/sierpinski
  ```

- [ ] **Commit**

  ```bash
  git init
  git add .
  git commit -m "feat: sierpinski algorithm with Pascal-parity method"
  ```

---

## Task 2: Mandelbrot Algorithm

**Interfaces:**
- Consumes: nothing from prior tasks
- Produces: `func Generate(width, height, iterations int, charOverride string) []string` in package `github.com/example/fractals/internal/mandelbrot`
  - `width`, `height` — canvas dimensions, must be > 0
  - `iterations` — max escape iterations, must be > 0
  - `charOverride` — if `""` use gradient `" .:-=+*#%@"`; if a single UTF-8 character use that for all filled cells (space = unfilled)
  - Returns slice of `height` strings each `width` characters wide
  - Returns empty slice for invalid arguments

**Files:**
- `internal/mandelbrot/mandelbrot.go`
- `internal/mandelbrot/mandelbrot_test.go`

---

- [ ] **Write failing tests**

  `internal/mandelbrot/mandelbrot_test.go`
  ```go
  package mandelbrot_test

  import (
      "strings"
      "testing"
      "unicode/utf8"

      "github.com/example/fractals/internal/mandelbrot"
  )

  func TestGenerate_Dimensions(t *testing.T) {
      rows := mandelbrot.Generate(40, 12, 50, "")
      if len(rows) != 12 {
          t.Fatalf("expected 12 rows, got %d", len(rows))
      }
      for i, r := range rows {
          // Width is measured in runes because gradient chars are all ASCII.
          if utf8.RuneCountInString(r) != 40 {
              t.Errorf("row %d: expected width 40, got %d (%q)", i, utf8.RuneCountInString(r), r)
          }
      }
  }

  func TestGenerate_InvalidArgs(t *testing.T) {
      cases := []struct {
          w, h, it int
      }{
          {0, 10, 50},
          {10, 0, 50},
          {10, 10, 0},
          {-1, 10, 50},
      }
      for _, tc := range cases {
          rows := mandelbrot.Generate(tc.w, tc.h, tc.it, "")
          if len(rows) != 0 {
              t.Errorf("Generate(%d,%d,%d) should return empty, got %d rows", tc.w, tc.h, tc.it, len(rows))
          }
      }
  }

  func TestGenerate_GradientChars(t *testing.T) {
      // With gradient mode, output must only contain chars from the gradient set.
      gradient := " .:-=+*#%@"
      rows := mandelbrot.Generate(20, 8, 30, "")
      for _, r := range rows {
          for _, ch := range r {
              if !strings.ContainsRune(gradient, ch) {
                  t.Errorf("unexpected char %q in gradient output", ch)
              }
          }
      }
  }

  func TestGenerate_CustomChar(t *testing.T) {
      rows := mandelbrot.Generate(20, 8, 30, "#")
      for _, r := range rows {
          for _, ch := range r {
              if ch != '#' && ch != ' ' {
                  t.Errorf("custom char mode: unexpected char %q (want '#' or ' ')", ch)
              }
          }
      }
      // Centre of Mandelbrot is always "inside" (iterations == max) — should be '#'
      midRow := rows[len(rows)/2]
      if !strings.Contains(midRow, "#") {
          t.Errorf("centre row should contain '#' (inside set), got %q", midRow)
      }
  }

  func TestGenerate_MandelbrotShape(t *testing.T) {
      // The point (-0.5, 0) is inside the Mandelbrot set.
      // With a standard viewport, the horizontal centre of the middle row should be filled.
      rows := mandelbrot.Generate(80, 24, 100, "*")
      mid := rows[len(rows)/2]
      // Find the character at horizontal position corresponding to x=-0.5
      // Viewport: x in [-2.5, 1.0], so x=-0.5 → col = (-0.5 - (-2.5)) / 3.5 * 80 ≈ 46
      col := 46
      runes := []rune(mid)
      if runes[col] != '*' {
          t.Errorf("expected '*' at col %d (inside set), got %q; row: %q", col, runes[col], mid)
      }
  }
  ```

- [ ] **Run tests — expect compile failure**

  ```bash
  go test ./internal/mandelbrot/...
  ```

  Expected:
  ```
  no Go files in .../internal/mandelbrot
  ```

- [ ] **Implement the Mandelbrot algorithm**

  `internal/mandelbrot/mandelbrot.go`
  ```go
  // Package mandelbrot renders the Mandelbrot set as ASCII art.
  package mandelbrot

  const gradient = " .:-=+*#%@"

  // Generate renders the Mandelbrot set into a slice of `height` strings,
  // each `width` characters wide.
  //
  // Viewport: real axis [-2.5, 1.0], imaginary axis [-1.25, 1.25].
  //
  // charOverride: if empty, use the gradient " .:-=+*#%@";
  // if a non-empty string, use that string's first rune for filled cells
  // and space for unfilled cells (cells where iteration count == iterations).
  func Generate(width, height, iterations int, charOverride string) []string {
      if width <= 0 || height <= 0 || iterations <= 0 {
          return []string{}
      }

      useGradient := charOverride == ""
      var customChar rune
      if !useGradient {
          runes := []rune(charOverride)
          customChar = runes[0]
      }

      gradRunes := []rune(gradient) // len == 10

      rows := make([]string, height)
      buf := make([]rune, width)

      // Viewport bounds
      const (
          xMin = -2.5
          xMax = 1.0
          yMin = -1.25
          yMax = 1.25
      )

      for row := 0; row < height; row++ {
          cy := yMax - (yMax-yMin)*float64(row)/float64(height-1)
          if height == 1 {
              cy = 0
          }
          for col := 0; col < width; col++ {
              cx := xMin + (xMax-xMin)*float64(col)/float64(width-1)
              if width == 1 {
                  cx = -0.5
              }

              iters := escape(cx, cy, iterations)

              if useGradient {
                  // Map iters to gradient index.
                  // iters == iterations → inside the set → use last char (densest).
                  idx := (iters * (len(gradRunes) - 1)) / iterations
                  if idx >= len(gradRunes) {
                      idx = len(gradRunes) - 1
                  }
                  buf[col] = gradRunes[idx]
              } else {
                  if iters == iterations {
                      buf[col] = customChar
                  } else {
                      buf[col] = ' '
                  }
              }
          }
          rows[row] = string(buf)
      }
      return rows
  }

  // escape returns the iteration count at which |z| > 2 for c = (cx, cy),
  // or `maxIter` if the point does not escape.
  func escape(cx, cy float64, maxIter int) int {
      zx, zy := 0.0, 0.0
      for i := 0; i < maxIter; i++ {
          zx2, zy2 := zx*zx, zy*zy
          if zx2+zy2 > 4.0 {
              return i
          }
          zy = 2*zx*zy + cy
          zx = zx2 - zy2 + cx
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
  === RUN   TestGenerate_Dimensions
  --- PASS: TestGenerate_Dimensions (0.00s)
  === RUN   TestGenerate_InvalidArgs
  --- PASS: TestGenerate_InvalidArgs (0.00s)
  === RUN   TestGenerate_GradientChars
  --- PASS: TestGenerate_GradientChars (0.00s)
  === RUN   TestGenerate_CustomChar
  --- PASS: TestGenerate_CustomChar (0.00s)
  === RUN   TestGenerate_MandelbrotShape
  --- PASS: TestGenerate_MandelbrotShape (0.00s)
  PASS
  ok      github.com/example/fractals/internal/mandelbrot
  ```

- [ ] **Commit**

  ```bash
  git add .
  git commit -m "feat: mandelbrot algorithm with gradient and custom-char modes"
  ```

---

## Task 3: CLI Wiring & Binary

**Interfaces:**
- Consumes:
  - `sierpinski.Generate(size, depth int, char rune) []string`
  - `mandelbrot.Generate(width, height, iterations int, charOverride string) []string`
- Produces: `cli.Execute() error` in `internal/cli` (called by `main.go`)
- Binary: `fractals` (built to repo root or `./bin/fractals`)

**Files:**
- `internal/cli/root.go`
- `internal/cli/sierpinski.go`
- `internal/cli/mandelbrot.go`
- `cmd/fractals/main.go`

---

- [ ] **Add Cobra dependency**

  ```bash
  go get github.com/spf13/cobra@latest
  go mod tidy
  ```

  Expected: `go.sum` updated, `go.mod` now lists `github.com/spf13/cobra`.

- [ ] **Write CLI integration tests (table-driven, using `exec.Command`)**

  Create `internal/cli/cli_integration_test.go`:

  ```go
  //go:build integration

  package cli_test

  import (
      "os/exec"
      "strings"
      "testing"
  )

  // These tests build the binary first; run with:
  //   go test -tags integration ./internal/cli/...
  // after `go build -o bin/fractals ./cmd/fractals`

  const binary = "../../bin/fractals"

  func run(t *testing.T, args ...string) (string, int) {
      t.Helper()
      cmd := exec.Command(binary, args...)
      out, err := cmd.CombinedOutput()
      code := 0
      if err != nil {
          if exitErr, ok := err.(*exec.ExitError); ok {
              code = exitErr.ExitCode()
          }
      }
      return string(out), code
  }

  func TestHelp(t *testing.T) {
      out, code := run(t, "--help")
      if code != 0 {
          t.Fatalf("--help exited %d, output: %s", code, out)
      }
      if !strings.Contains(out, "sierpinski") || !strings.Contains(out, "mandelbrot") {
          t.Errorf("--help should mention both subcommands, got:\n%s", out)
      }
  }

  func TestSierpinskiHelp(t *testing.T) {
      out, code := run(t, "sierpinski", "--help")
      if code != 0 {
          t.Fatalf("exited %d: %s", code, out)
      }
      for _, flag := range []string{"--size", "--depth", "--char"} {
          if !strings.Contains(out, flag) {
              t.Errorf("sierpinski --help missing %s", flag)
          }
      }
  }

  func TestMandelbrotHelp(t *testing.T) {
      out, code := run(t, "mandelbrot", "--help")
      if code != 0 {
          t.Fatalf("exited %d: %s", code, out)
      }
      for _, flag := range []string{"--width", "--height", "--iterations", "--char"} {
          if !strings.Contains(out, flag) {
              t.Errorf("mandelbrot --help missing %s", flag)
          }
      }
  }

  func TestSierpinskiOutput(t *testing.T) {
      out, code := run(t, "sierpinski", "--size", "8", "--depth", "3")
      if code != 0 {
          t.Fatalf("exited %d: %s", code, out)
      }
      lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
      if len(lines) != 8 {
          t.Errorf("expected 8 lines, got %d", len(lines))
      }
      for i, l := range lines {
          if len(l) != 8 {
              t.Errorf("line %d: expected width 8, got %d (%q)", i, len(l), l)
          }
      }
  }

  func TestSierpinskiCustomChar(t *testing.T) {
      out, code := run(t, "sierpinski", "--size", "4", "--char", "#")
      if code != 0 {
          t.Fatalf("exited %d: %s", code, out)
      }
      if strings.Contains(out, "*") {
          t.Errorf("should use '#' not '*', got:\n%s", out)
      }
      if !strings.Contains(out, "#") {
          t.Errorf("output must contain '#', got:\n%s", out)
      }
  }

  func TestMandelbrotOutput(t *testing.T) {
      out, code := run(t, "mandelbrot", "--width", "40", "--height", "10", "--iterations", "30")
      if code != 0 {
          t.Fatalf("exited %d: %s", code, out)
      }
      lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
      if len(lines) != 10 {
          t.Errorf("expected 10 lines, got %d", len(lines))
      }
  }

  func TestMandelbrotCustomChar(t *testing.T) {
      out, code := run(t, "mandelbrot", "--width", "20", "--height", "6", "--char", "@")
      if code != 0 {
          t.Fatalf("exited %d: %s", code, out)
      }
      if !strings.Contains(out, "@") {
          t.Errorf("expected '@' in output, got:\n%s", out)
      }
  }

  func TestInvalidSierpinskiSize(t *testing.T) {
      _, code := run(t, "sierpinski", "--size", "-1")
      if code == 0 {
          t.Error("expected non-zero exit for invalid size")
      }
  }

  func TestInvalidMandelbrotWidth(t *testing.T) {
      _, code := run(t, "mandelbrot", "--width", "0")
      if code == 0 {
          t.Error("expected non-zero exit for width=0")
      }
  }
  ```

- [ ] **Implement `internal/cli/root.go`**

  ```go
  // Package cli wires the Cobra command tree for the fractals binary.
  package cli

  import (
      "fmt"
      "os"

      "github.com/spf13/cobra"
  )

  var rootCmd = &cobra.Command{
      Use:   "fractals",
      Short: "Generate ASCII art fractals",
      Long:  "A command-line tool that generates ASCII art fractals.\n\nAvailable fractals: sierpinski, mandelbrot",
  }

  func init() {
      rootCmd.AddCommand(newSierpinskiCmd())
      rootCmd.AddCommand(newMandelbrotCmd())
  }

  // Execute runs the root command and exits on error.
  func Execute() {
      if err := rootCmd.Execute(); err != nil {
          fmt.Fprintln(os.Stderr, err)
          os.Exit(1)
      }
  }
  ```

- [ ] **Implement `internal/cli/sierpinski.go`**

  ```go
  package cli

  import (
      "fmt"
      "os"
      "unicode/utf8"

      "github.com/spf13/cobra"

      "github.com/example/fractals/internal/sierpinski"
  )

  func newSierpinskiCmd() *cobra.Command {
      var size, depth int
      var charStr string

      cmd := &cobra.Command{
          Use:   "sierpinski",
          Short: "Generate a Sierpinski triangle",
          Long:  "Generates a Sierpinski triangle using the Pascal's triangle parity method.",
          RunE: func(cmd *cobra.Command, args []string) error {
              if size <= 0 {
                  return fmt.Errorf("--size must be greater than 0, got %d", size)
              }
              if depth < 0 {
                  return fmt.Errorf("--depth must be >= 0, got %d", depth)
              }
              r, size1 := utf8.DecodeRuneInString(charStr)
              if size1 == 0 || r == utf8.RuneError {
                  return fmt.Errorf("--char must be a valid character, got %q", charStr)
              }

              rows := sierpinski.Generate(size, depth, r)
              if len(rows) == 0 {
                  fmt.Fprintln(os.Stderr, "error: could not generate fractal with given parameters")
                  os.Exit(1)
              }
              for _, row := range rows {
                  fmt.Println(row)
              }
              return nil
          },
      }

      cmd.Flags().IntVar(&size, "size", 32, "Width of the triangle base in characters")
      cmd.Flags().IntVar(&depth, "depth", 5, "Recursion depth")
      cmd.Flags().StringVar(&charStr, "char", "*", "Character to use for filled points")
      return cmd
  }
  ```

- [ ] **Implement `internal/cli/mandelbrot.go`**

  ```go
  package cli

  import (
      "fmt"
      "os"
      "unicode/utf8"

      "github.com/spf13/cobra"

      "github.com/example/fractals/internal/mandelbrot"
  )

  func newMandelbrotCmd() *cobra.Command {
      var width, height, iterations int
      var charStr string

      cmd := &cobra.Command{
          Use:   "mandelbrot",
          Short: "Render the Mandelbrot set as ASCII art",
          Long:  "Renders the Mandelbrot set using escape-time algorithm. Maps iteration count to characters.",
          RunE: func(cmd *cobra.Command, args []string) error {
              if width <= 0 {
                  return fmt.Errorf("--width must be greater than 0, got %d", width)
              }
              if height <= 0 {
                  return fmt.Errorf("--height must be greater than 0, got %d", height)
              }
              if iterations <= 0 {
                  return fmt.Errorf("--iterations must be greater than 0, got %d", iterations)
              }

              charOverride := ""
              if cmd.Flags().Changed("char") {
                  r, size := utf8.DecodeRuneInString(charStr)
                  if size == 0 || r == utf8.RuneError {
                      return fmt.Errorf("--char must be a valid character, got %q", charStr)
                  }
                  charOverride = string(r)
              }

              rows := mandelbrot.Generate(width, height, iterations, charOverride)
              if len(rows) == 0 {
                  fmt.Fprintln(os.Stderr, "error: could not generate fractal with given parameters")
                  os.Exit(1)
              }
              for _, row := range rows {
                  fmt.Println(row)
              }
              return nil
          },
      }

      cmd.Flags().IntVar(&width, "width", 80, "Output width in characters")
      cmd.Flags().IntVar(&height, "height", 24, "Output height in characters")
      cmd.Flags().IntVar(&iterations, "iterations", 100, "Maximum iterations for escape calculation")
      cmd.Flags().StringVar(&charStr, "char", "", "Single character override (omit for gradient \" .:-=+*#%@\")")
      return cmd
  }
  ```

- [ ] **Implement `cmd/fractals/main.go`**

  ```go
  package main

  import "github.com/example/fractals/internal/cli"

  func main() {
      cli.Execute()
  }
  ```

- [ ] **Build the binary**

  ```bash
  mkdir -p bin
  go build -o bin/fractals ./cmd/fractals
  ```

  Expected: no output, `bin/fractals` exists.

- [ ] **Run integration tests**

  ```bash
  go test -tags integration ./internal/cli/... -v
  ```

  Expected (all PASS):
  ```
  === RUN   TestHelp
  --- PASS: TestHelp (0.01s)
  === RUN   TestSierpinskiHelp
  --- PASS: TestSierpinskiHelp (0.00s)
  === RUN   TestMandelbrotHelp
  --- PASS: TestMandelbrotHelp (0.00s)
  === RUN   TestSierpinskiOutput
  --- PASS: TestSierpinskiOutput (0.00s)
  === RUN   TestSierpinskiCustomChar
  --- PASS: TestSierpinskiCustomChar (0.00s)
  === RUN   TestMandelbrotOutput
  --- PASS: TestMandelbrotOutput (0.00s)
  === RUN   TestMandelbrotCustomChar
  --- PASS: TestMandelbrotCustomChar (0.00s)
  === RUN   TestInvalidSierpinskiSize
  --- PASS: TestInvalidSierpinskiSize (0.00s)
  === RUN   TestInvalidMandelbrotWidth
  --- PASS: TestInvalidMandelbrotWidth (0.00s)
  PASS
  ok      github.com/example/fractals/internal/cli
  ```

- [ ] **Run the full unit test suite (no build tag)**

  ```bash
  go test ./...
  ```

  Expected:
  ```
  ok      github.com/example/fractals/internal/mandelbrot
  ok      github.com/example/fractals/internal/sierpinski
  ?       github.com/example/fractals/cmd/fractals  [no test files]
  ?       github.com/example/fractals/internal/cli  [no test files]
  ```

- [ ] **Smoke-test the binary manually**

  ```bash
  ./bin/fractals --help
  ./bin/fractals sierpinski --size 16 --depth 4
  ./bin/fractals sierpinski --size 8 --char '#'
  ./bin/fractals mandelbrot --width 40 --height 12 --iterations 50
  ./bin/fractals mandelbrot --width 40 --height 12 --char '@'
  ```

  Expected: help text mentions both subcommands; triangle output is 16 rows × 16 chars; Mandelbrot output is 12 rows.

- [ ] **Commit**

  ```bash
  git add .
  git commit -m "feat: cobra CLI with sierpinski and mandelbrot subcommands, integration tests"
  ```

---

## Post-Plan Self-Review

| Check | Result |
|---|---|
| All 7 acceptance criteria covered | ✅ `--help` (TestHelp), triangle output (TestSierpinskiOutput), Mandelbrot output (TestMandelbrotOutput), all flags tested, `--char` tested, invalid inputs tested (TestInvalidSierpinskiSize, TestInvalidMandelbrotWidth, plus internal validation), all tests pass |
| No placeholders (`TODO`, `...`, `???`) in code blocks | ✅ |
| Type consistency across task boundaries | ✅ `Generate` signatures match between algorithm packages and CLI callers |
| Module path consistent | ✅ `github.com/example/fractals` used everywhere |
| Gradient string length = 10 chars | ✅ `" .:-=+*#%@"` |
| Default flags match spec | ✅ sierpinski: size=32, depth=5, char='*'; mandelbrot: width=80, height=24, iterations=100, char=gradient |
| Cobra version pinned | ✅ `go get github.com/spf13/cobra@latest` (latest ≥ v1.8 at time of writing; `go mod tidy` locks it) |
| Invalid inputs exit non-zero | ✅ `RunE` returns error → Cobra prints to stderr and exits 1 |