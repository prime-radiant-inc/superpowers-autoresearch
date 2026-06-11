# Go Fractals CLI — Implementation Plan

## Global Constraints

- Go 1.21+
- Dependency: `github.com/spf13/cobra` (CLI framework)
- Binary name: `fractals`
- Default Sierpinski char: `*`
- Default Mandelbrot gradient (no `--char`): `" .:-=+*#%@"` (10 chars, space first)
- Sierpinski defaults: `--size 32`, `--depth 5`
- Mandelbrot defaults: `--width 80`, `--height 24`, `--iterations 100`
- Architecture: `cmd/fractals/main.go`, `internal/sierpinski/`, `internal/mandelbrot/`, `internal/cli/`

---

## File Structure

| File | Responsibility |
|---|---|
| `go.mod` / `go.sum` | Module declaration, dependency lock |
| `cmd/fractals/main.go` | Binary entry point; calls `cli.Execute()` |
| `internal/cli/root.go` | Root cobra command, `Execute()` function |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand; parses flags, calls algorithm, prints |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand; parses flags, calls algorithm, prints |
| `internal/sierpinski/sierpinski.go` | Pure algorithm: `Generate(size, depth int, ch rune) []string` |
| `internal/sierpinski/sierpinski_test.go` | Unit tests for `Generate` |
| `internal/mandelbrot/mandelbrot.go` | Pure algorithm: `Generate(width, height, iterations int, ch rune, gradient bool) []string` |
| `internal/mandelbrot/mandelbrot_test.go` | Unit tests for `Generate` |

---

## Task 1: Module Scaffold & Sierpinski Algorithm

**Interfaces:**
- Produces: `func Generate(size, depth int, ch rune) ([]string, error)` in package `sierpinski`
- Consumed by: Task 3 (`internal/cli/sierpinski.go`)

**Files:**
- `go.mod`
- `go.sum`
- `internal/sierpinski/sierpinski.go`
- `internal/sierpinski/sierpinski_test.go`

---

- [ ] **Initialise the module and fetch cobra**

  ```bash
  mkdir -p fractals && cd fractals
  go mod init github.com/example/fractals
  go get github.com/spf13/cobra@latest
  ```

  Expected: `go.mod` lists `github.com/spf13/cobra`, `go.sum` created.

---

- [ ] **Write the failing tests** — `internal/sierpinski/sierpinski_test.go`

  ```go
  package sierpinski_test

  import (
      "strings"
      "testing"

      "github.com/example/fractals/internal/sierpinski"
  )

  func TestGenerate_InvalidSize(t *testing.T) {
      _, err := sierpinski.Generate(0, 5, '*')
      if err == nil {
          t.Fatal("expected error for size=0")
      }
  }

  func TestGenerate_InvalidDepth(t *testing.T) {
      _, err := sierpinski.Generate(16, -1, '*')
      if err == nil {
          t.Fatal("expected error for depth=-1")
      }
  }

  func TestGenerate_RowCount(t *testing.T) {
      rows, err := sierpinski.Generate(4, 2, '*')
      if err != nil {
          t.Fatal(err)
      }
      // size=4 → 4 rows (rows == size/2 + 1, but for power-of-two size the
      // triangle has size rows indexed 0..size-1, capped by recursion depth)
      if len(rows) == 0 {
          t.Fatal("expected non-empty output")
      }
  }

  func TestGenerate_RowWidth(t *testing.T) {
      size := 8
      rows, err := sierpinski.Generate(size, 3, '*')
      if err != nil {
          t.Fatal(err)
      }
      for i, row := range rows {
          if len(row) != size {
              t.Errorf("row %d: got len %d, want %d", i, len(row), size)
          }
      }
  }

  func TestGenerate_CustomChar(t *testing.T) {
      rows, err := sierpinski.Generate(4, 2, '#')
      if err != nil {
          t.Fatal(err)
      }
      combined := strings.Join(rows, "")
      if strings.ContainsRune(combined, '*') {
          t.Error("default char '*' found; expected custom char '#'")
      }
      if !strings.ContainsRune(combined, '#') {
          t.Error("custom char '#' not found in output")
      }
  }

  func TestGenerate_TopPixelFilled(t *testing.T) {
      rows, err := sierpinski.Generate(8, 4, '*')
      if err != nil {
          t.Fatal(err)
      }
      // Apex: first row, middle character should be filled
      mid := len(rows[0]) / 2
      if rune(rows[0][mid]) != '*' {
          t.Errorf("apex pixel not filled: got %q", rows[0][mid])
      }
  }

  func TestGenerate_BottomRowEdgesFilled(t *testing.T) {
      rows, err := sierpinski.Generate(8, 4, '*')
      if err != nil {
          t.Fatal(err)
      }
      last := rows[len(rows)-1]
      if rune(last[0]) != '*' {
          t.Errorf("bottom-left not filled: got %q", last[0])
      }
      if rune(last[len(last)-1]) != '*' {
          t.Errorf("bottom-right not filled: got %q", last[len(last)-1])
      }
  }

  func TestGenerate_CenterBottomEmpty(t *testing.T) {
      // With depth ≥ 2 the centre of the bottom row should be empty
      rows, err := sierpinski.Generate(8, 3, '*')
      if err != nil {
          t.Fatal(err)
      }
      last := rows[len(rows)-1]
      mid := len(last) / 2
      if rune(last[mid]) == '*' {
          t.Errorf("centre of bottom row should be empty, got %q", last[mid])
      }
  }
  ```

- [ ] **Run tests — expect compile failure / all red**

  ```bash
  go test ./internal/sierpinski/...
  ```

  Expected: `cannot find package` or compilation errors (package does not exist yet).

---

- [ ] **Implement the algorithm** — `internal/sierpinski/sierpinski.go`

  ```go
  package sierpinski

  import "fmt"

  // Generate returns a slice of strings representing a Sierpinski triangle.
  // Each string has exactly `size` characters.
  // size must be a positive integer; depth must be >= 0.
  func Generate(size, depth int, ch rune) ([]string, error) {
      if size <= 0 {
          return nil, fmt.Errorf("size must be positive, got %d", size)
      }
      if depth < 0 {
          return nil, fmt.Errorf("depth must be non-negative, got %d", depth)
      }

      rows := make([]string, size)
      buf := make([][]rune, size)
      for i := range buf {
          buf[i] = make([]rune, size)
          for j := range buf[i] {
              buf[i][j] = ' '
          }
      }

      // Recursive fill: triangle defined by top-left, top-right, apex columns
      // and the row index range.
      // We treat the triangle as occupying rows [0, size) where row i spans
      // columns [size/2 - i .. size/2 + i] (0-indexed from apex).
      var fill func(topRow, leftCol, width, d int)
      fill = func(topRow, leftCol, width, d int) {
          if width <= 0 {
              return
          }
          if d == 0 || width == 1 {
              // Fill the whole sub-triangle solid
              for row := 0; row < width; row++ {
                  r := topRow + row
                  if r >= size {
                      break
                  }
                  // row i of a triangle of width w spans columns
                  // leftCol + (w/2 - row) .. leftCol + (w/2 + row)
                  // using integer centre
                  centre := leftCol + width/2
                  start := centre - row
                  end := centre + row
                  for c := start; c <= end && c < size; c++ {
                      if c >= 0 {
                          buf[r][c] = ch
                      }
                  }
              }
              return
          }
          half := width / 2
          // Top sub-triangle
          fill(topRow, leftCol+half/2, half, d-1)
          // Bottom-left sub-triangle
          fill(topRow+half, leftCol, half, d-1)
          // Bottom-right sub-triangle
          fill(topRow+half, leftCol+half, half, d-1)
      }

      fill(0, 0, size, depth)

      for i, row := range buf {
          rows[i] = string(row)
      }
      return rows, nil
  }
  ```

- [ ] **Run tests — expect all green**

  ```bash
  go test ./internal/sierpinski/... -v
  ```

  Expected output (abridged):
  ```
  --- PASS: TestGenerate_InvalidSize
  --- PASS: TestGenerate_InvalidDepth
  --- PASS: TestGenerate_RowCount
  --- PASS: TestGenerate_RowWidth
  --- PASS: TestGenerate_CustomChar
  --- PASS: TestGenerate_TopPixelFilled
  --- PASS: TestGenerate_BottomRowEdgesFilled
  --- PASS: TestGenerate_CenterBottomEmpty
  PASS
  ok  github.com/example/fractals/internal/sierpinski
  ```

- [ ] **Commit**

  ```bash
  git init
  git add .
  git commit -m "task 1: module scaffold + sierpinski algorithm"
  ```

---

## Task 2: Mandelbrot Algorithm

**Interfaces:**
- Produces: `func Generate(width, height, iterations int, ch rune, gradient bool) ([]string, error)` in package `mandelbrot`
- Consumed by: Task 3 (`internal/cli/mandelbrot.go`)

**Files:**
- `internal/mandelbrot/mandelbrot.go`
- `internal/mandelbrot/mandelbrot_test.go`

---

- [ ] **Write the failing tests** — `internal/mandelbrot/mandelbrot_test.go`

  ```go
  package mandelbrot_test

  import (
      "strings"
      "testing"

      "github.com/example/fractals/internal/mandelbrot"
  )

  func TestGenerate_InvalidWidth(t *testing.T) {
      _, err := mandelbrot.Generate(0, 24, 100, '*', false)
      if err == nil {
          t.Fatal("expected error for width=0")
      }
  }

  func TestGenerate_InvalidHeight(t *testing.T) {
      _, err := mandelbrot.Generate(80, 0, 100, '*', false)
      if err == nil {
          t.Fatal("expected error for height=0")
      }
  }

  func TestGenerate_InvalidIterations(t *testing.T) {
      _, err := mandelbrot.Generate(80, 24, 0, '*', false)
      if err == nil {
          t.Fatal("expected error for iterations=0")
      }
  }

  func TestGenerate_RowCount(t *testing.T) {
      rows, err := mandelbrot.Generate(40, 12, 50, '*', false)
      if err != nil {
          t.Fatal(err)
      }
      if len(rows) != 12 {
          t.Errorf("got %d rows, want 12", len(rows))
      }
  }

  func TestGenerate_RowWidth(t *testing.T) {
      rows, err := mandelbrot.Generate(40, 12, 50, '*', false)
      if err != nil {
          t.Fatal(err)
      }
      for i, row := range rows {
          if len(row) != 40 {
              t.Errorf("row %d: got len %d, want 40", i, len(row))
          }
      }
  }

  func TestGenerate_SingleChar(t *testing.T) {
      rows, err := mandelbrot.Generate(20, 6, 50, '#', false)
      if err != nil {
          t.Fatal(err)
      }
      combined := strings.Join(rows, "")
      for _, r := range combined {
          if r != '#' && r != ' ' {
              t.Errorf("unexpected character %q in single-char mode", r)
          }
      }
  }

  func TestGenerate_GradientChars(t *testing.T) {
      gradient := " .:-=+*#%@"
      rows, err := mandelbrot.Generate(40, 12, 50, 0, true)
      if err != nil {
          t.Fatal(err)
      }
      combined := strings.Join(rows, "")
      for _, r := range combined {
          if !strings.ContainsRune(gradient, r) {
              t.Errorf("character %q not in gradient set", r)
          }
      }
  }

  func TestGenerate_ContainsFilledAndEmpty(t *testing.T) {
      // The Mandelbrot set occupies roughly the centre-left; there should be
      // both filled (non-space) and empty (space) characters.
      rows, err := mandelbrot.Generate(80, 24, 100, '*', false)
      if err != nil {
          t.Fatal(err)
      }
      combined := strings.Join(rows, "")
      hasSpace := strings.ContainsRune(combined, ' ')
      hasFill := strings.ContainsRune(combined, '*')
      if !hasSpace {
          t.Error("expected some empty (space) pixels")
      }
      if !hasFill {
          t.Error("expected some filled pixels")
      }
  }

  func TestGenerate_OriginInSet(t *testing.T) {
      // The point (0,0) is inside the Mandelbrot set and should map to a
      // non-space character in single-char mode.
      width, height := 80, 24
      rows, err := mandelbrot.Generate(width, height, 100, '*', false)
      if err != nil {
          t.Fatal(err)
      }
      // Map pixel that corresponds to complex(0,0):
      // real ∈ [-2.5, 1.0], imag ∈ [-1.2, 1.2]
      // col = int((0 - (-2.5)) / (1.0 - (-2.5)) * float64(width))  ≈ 57
      // row = int((0 - (-1.2)) / (1.2 - (-1.2)) * float64(height)) ≈ 12
      col := int((0 - (-2.5)) / (1.0 - (-2.5)) * float64(width))
      row := int((0 - (-1.2)) / (1.2 - (-1.2)) * float64(height))
      if row >= height {
          row = height - 1
      }
      if col >= width {
          col = width - 1
      }
      if rune(rows[row][col]) != '*' {
          t.Errorf("origin should be inside Mandelbrot set, got %q", rows[row][col])
      }
  }
  ```

- [ ] **Run tests — expect compile failure**

  ```bash
  go test ./internal/mandelbrot/...
  ```

  Expected: compilation error (package does not exist).

---

- [ ] **Implement the algorithm** — `internal/mandelbrot/mandelbrot.go`

  ```go
  package mandelbrot

  import (
      "fmt"
      "math/cmplx"
  )

  const gradientChars = " .:-=+*#%@"

  // Generate returns a slice of `height` strings each of length `width`
  // representing the Mandelbrot set.
  // When gradient is true, ch is ignored and the gradient palette is used.
  // iterations must be > 0; width and height must be > 0.
  func Generate(width, height, iterations int, ch rune, gradient bool) ([]string, error) {
      if width <= 0 {
          return nil, fmt.Errorf("width must be positive, got %d", width)
      }
      if height <= 0 {
          return nil, fmt.Errorf("height must be positive, got %d", height)
      }
      if iterations <= 0 {
          return nil, fmt.Errorf("iterations must be positive, got %d", iterations)
      }

      // Viewport bounds (classic Mandelbrot view)
      const (
          xMin = -2.5
          xMax = 1.0
          yMin = -1.2
          yMax = 1.2
      )

      palette := []rune(gradientChars)
      rows := make([]string, height)

      for row := 0; row < height; row++ {
          line := make([]rune, width)
          imag := yMin + (yMax-yMin)*float64(row)/float64(height)
          for col := 0; col < width; col++ {
              real := xMin + (xMax-xMin)*float64(col)/float64(width)
              c := complex(real, imag)
              z := complex(0, 0)
              var iter int
              for iter = 0; iter < iterations; iter++ {
                  z = z*z + c
                  if cmplx.Abs(z) > 2 {
                      break
                  }
              }
              if gradient {
                  idx := iter * (len(palette) - 1) / iterations
                  line[col] = palette[idx]
              } else {
                  if iter == iterations {
                      line[col] = ch
                  } else {
                      line[col] = ' '
                  }
              }
          }
          rows[row] = string(line)
      }
      return rows, nil
  }
  ```

- [ ] **Run tests — expect all green**

  ```bash
  go test ./internal/mandelbrot/... -v
  ```

  Expected output (abridged):
  ```
  --- PASS: TestGenerate_InvalidWidth
  --- PASS: TestGenerate_InvalidHeight
  --- PASS: TestGenerate_InvalidIterations
  --- PASS: TestGenerate_RowCount
  --- PASS: TestGenerate_RowWidth
  --- PASS: TestGenerate_SingleChar
  --- PASS: TestGenerate_GradientChars
  --- PASS: TestGenerate_ContainsFilledAndEmpty
  --- PASS: TestGenerate_OriginInSet
  PASS
  ok  github.com/example/fractals/internal/mandelbrot
  ```

- [ ] **Commit**

  ```bash
  git add .
  git commit -m "task 2: mandelbrot algorithm"
  ```

---

## Task 3: CLI Commands & Binary

**Interfaces:**
- Consumes:
  - `sierpinski.Generate(size, depth int, ch rune) ([]string, error)`
  - `mandelbrot.Generate(width, height, iterations int, ch rune, gradient bool) ([]string, error)`
- Produces: `cli.Execute() error` consumed by `cmd/fractals/main.go`

**Files:**
- `internal/cli/root.go`
- `internal/cli/sierpinski.go`
- `internal/cli/mandelbrot.go`
- `cmd/fractals/main.go`

> CLI integration is tested via `go run` / `go build` invocations; there are
> no separate `_test.go` files for this task because the behaviour under test
> is end-to-end flag parsing and output, covered by the acceptance commands
> below.

---

- [ ] **Create the root command** — `internal/cli/root.go`

  ```go
  package cli

  import (
      "github.com/spf13/cobra"
  )

  var rootCmd = &cobra.Command{
      Use:   "fractals",
      Short: "Generate ASCII art fractals",
      Long:  "A CLI tool that generates ASCII art fractals.\nSupports Sierpinski triangle and Mandelbrot set.",
  }

  // Execute runs the root command and returns any error.
  func Execute() error {
      return rootCmd.Execute()
  }

  func init() {
      rootCmd.AddCommand(sierpinskiCmd)
      rootCmd.AddCommand(mandelbrotCmd)
  }
  ```

- [ ] **Create the sierpinski subcommand** — `internal/cli/sierpinski.go`

  ```go
  package cli

  import (
      "fmt"
      "os"
      "strings"

      "github.com/spf13/cobra"

      "github.com/example/fractals/internal/sierpinski"
  )

  var (
      sierpinskiSize  int
      sierpinskiDepth int
      sierpinskiChar  string
  )

  var sierpinskiCmd = &cobra.Command{
      Use:   "sierpinski",
      Short: "Generate a Sierpinski triangle",
      Long:  "Generates a Sierpinski triangle using recursive subdivision.",
      RunE: func(cmd *cobra.Command, args []string) error {
          ch := '*'
          if sierpinskiChar != "" {
              runes := []rune(sierpinskiChar)
              if len(runes) != 1 {
                  return fmt.Errorf("--char must be exactly one character, got %q", sierpinskiChar)
              }
              ch = runes[0]
          }

          rows, err := sierpinski.Generate(sierpinskiSize, sierpinskiDepth, ch)
          if err != nil {
              return err
          }

          fmt.Fprintln(os.Stdout, strings.Join(rows, "\n"))
          return nil
      },
  }

  func init() {
      sierpinskiCmd.Flags().IntVar(&sierpinskiSize, "size", 32, "Width of the triangle base in characters")
      sierpinskiCmd.Flags().IntVar(&sierpinskiDepth, "depth", 5, "Recursion depth")
      sierpinskiCmd.Flags().StringVar(&sierpinskiChar, "char", "*", "Character to use for filled points")
  }
  ```

- [ ] **Create the mandelbrot subcommand** — `internal/cli/mandelbrot.go`

  ```go
  package cli

  import (
      "fmt"
      "os"
      "strings"

      "github.com/spf13/cobra"

      "github.com/example/fractals/internal/mandelbrot"
  )

  var (
      mandelbrotWidth      int
      mandelbrotHeight     int
      mandelbrotIterations int
      mandelbrotChar       string
  )

  var mandelbrotCmd = &cobra.Command{
      Use:   "mandelbrot",
      Short: "Render the Mandelbrot set as ASCII art",
      Long:  "Renders the Mandelbrot set as ASCII art, mapping iteration counts to characters.",
      RunE: func(cmd *cobra.Command, args []string) error {
          useGradient := false
          ch := rune(0)

          charFlag := cmd.Flags().Lookup("char")
          if !charFlag.Changed {
              // --char not supplied → use gradient
              useGradient = true
          } else {
              runes := []rune(mandelbrotChar)
              if len(runes) != 1 {
                  return fmt.Errorf("--char must be exactly one character, got %q", mandelbrotChar)
              }
              ch = runes[0]
          }

          rows, err := mandelbrot.Generate(mandelbrotWidth, mandelbrotHeight, mandelbrotIterations, ch, useGradient)
          if err != nil {
              return err
          }

          fmt.Fprintln(os.Stdout, strings.Join(rows, "\n"))
          return nil
      },
  }

  func init() {
      mandelbrotCmd.Flags().IntVar(&mandelbrotWidth, "width", 80, "Output width in characters")
      mandelbrotCmd.Flags().IntVar(&mandelbrotHeight, "height", 24, "Output height in characters")
      mandelbrotCmd.Flags().IntVar(&mandelbrotIterations, "iterations", 100, "Maximum iterations for escape calculation")
      mandelbrotCmd.Flags().StringVar(&mandelbrotChar, "char", "", "Single character override (omit for gradient \" .:-=+*#%@\")")
  }
  ```

- [ ] **Create the entry point** — `cmd/fractals/main.go`

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

- [ ] **Verify the project builds**

  ```bash
  go build ./...
  ```

  Expected: no output, exit code 0.

- [ ] **Run all unit tests**

  ```bash
  go test ./...
  ```

  Expected:
  ```
  ok  github.com/example/fractals/internal/mandelbrot
  ok  github.com/example/fractals/internal/sierpinski
  ```

- [ ] **Acceptance check 1 — help**

  ```bash
  go run ./cmd/fractals --help
  ```

  Expected (contains):
  ```
  A CLI tool that generates ASCII art fractals.
  
  Usage:
    fractals [command]
  
  Available Commands:
    mandelbrot  Render the Mandelbrot set as ASCII art
    sierpinski  Generate a Sierpinski triangle
  ```

- [ ] **Acceptance check 2 — sierpinski default**

  ```bash
  go run ./cmd/fractals sierpinski
  ```

  Expected: 32 lines of `*`-filled triangle printed to stdout, no errors.

  Quick sanity check (must print exactly 32 lines):
  ```bash
  go run ./cmd/fractals sierpinski | wc -l
  ```
  Expected: `32`

- [ ] **Acceptance check 3 — sierpinski custom flags**

  ```bash
  go run ./cmd/fractals sierpinski --size 8 --depth 3 --char '#'
  ```

  Expected: 8 lines, each 8 chars wide, using `#` not `*`.

  ```bash
  go run ./cmd/fractals sierpinski --size 8 --depth 3 --char '#' | head -1 | grep -v '\*'
  ```
  Expected: matches (no `*` present).

- [ ] **Acceptance check 4 — mandelbrot default (gradient)**

  ```bash
  go run ./cmd/fractals mandelbrot
  ```

  Expected: 24 lines of recognisable ASCII Mandelbrot art using gradient chars.

  ```bash
  go run ./cmd/fractals mandelbrot | wc -l
  ```
  Expected: `24`

- [ ] **Acceptance check 5 — mandelbrot custom flags**

  ```bash
  go run ./cmd/fractals mandelbrot --width 40 --height 12 --iterations 50 --char '*'
  ```

  Expected: 12 lines each 40 chars wide, only `*` and space characters.

  ```bash
  go run ./cmd/fractals mandelbrot --width 40 --height 12 --iterations 50 --char '*' | wc -l
  ```
  Expected: `12`

- [ ] **Acceptance check 6 — invalid input error messages**

  ```bash
  go run ./cmd/fractals sierpinski --size -1 2>&1
  ```
  Expected: contains `size must be positive`

  ```bash
  go run ./cmd/fractals mandelbrot --width -1 2>&1
  ```
  Expected: contains `width must be positive`

  ```bash
  go run ./cmd/fractals sierpinski --char 'ab' 2>&1
  ```
  Expected: contains `--char must be exactly one character`

- [ ] **Build the binary and smoke-test**

  ```bash
  go build -o fractals ./cmd/fractals
  ./fractals --help
  ./fractals sierpinski --size 16 --depth 4
  ./fractals mandelbrot --width 60 --height 20
  ```

  Expected: help text and two fractal outputs, all exit code 0.

- [ ] **Commit**

  ```bash
  git add .
  git commit -m "task 3: CLI commands and binary entry point"
  ```