# Go Fractals CLI - Implementation Plan

A command-line tool generating ASCII art fractals (Sierpinski triangle and Mandelbrot set) using Cobra.

## Global Constraints

- Go 1.21+ (set `go 1.21` in `go.mod`)
- Module path: `github.com/example/fractals`
- CLI library: `github.com/spf13/cobra` (latest compatible with Go 1.21)
- Binary name: `fractals`
- Mandelbrot default gradient (exact, 10 chars including leading space): `" .:-=+*#%@"`
- All output goes to stdout; errors to stderr with a clear message
- Invalid inputs (e.g. negative/zero sizes) produce a non-zero exit and a clear error message

## File Structure

```
go.mod                                  # Module definition, deps
go.sum                                  # Dependency checksums
cmd/fractals/main.go                    # Entry point: calls cli.Execute()
internal/sierpinski/sierpinski.go       # Generate([]string) algorithm
internal/sierpinski/sierpinski_test.go  # Algorithm tests
internal/mandelbrot/mandelbrot.go       # Render algorithm
internal/mandelbrot/mandelbrot_test.go  # Algorithm tests
internal/cli/root.go                    # Root cobra command + Execute()
internal/cli/sierpinski.go              # sierpinski subcommand wiring
internal/cli/mandelbrot.go              # mandelbrot subcommand wiring
```

Each package's pure algorithm (`sierpinski`, `mandelbrot`) knows nothing about Cobra. The `cli` package wires flags to those functions and handles I/O and validation.

---

### Task 1: Project scaffolding & module setup

**Files:** `go.mod`, `cmd/fractals/main.go`

**Interfaces:**
- Consumes: nothing.
- Produces: module `github.com/example/fractals`; `main()` entry point that will call `cli.Execute()` (stubbed until Task 4). For now `main` prints a placeholder so the binary builds.

- [ ] Create the module:
  ```bash
  go mod init github.com/example/fractals
  ```
  Edit `go.mod` to ensure the line `go 1.21` is present.
- [ ] Add Cobra dependency:
  ```bash
  go get github.com/spf13/cobra@latest
  ```
  Expected: `go.sum` created; `go.mod` lists `github.com/spf13/cobra`.
- [ ] Create `cmd/fractals/main.go` with a temporary body:
  ```go
  package main

  import "fmt"

  func main() {
      fmt.Println("fractals: not yet wired")
  }
  ```
- [ ] Build to verify:
  ```bash
  go build ./...
  ```
  Expected: no output, exit 0.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Scaffold fractals module and entry point"
  ```

---

### Task 2: Sierpinski algorithm

**Files:** `internal/sierpinski/sierpinski.go`, `internal/sierpinski/sierpinski_test.go`

**Interfaces:**
- Consumes: nothing.
- Produces:
  ```go
  // Generate returns the rows of a Sierpinski triangle.
  // size is the base width (number of columns at the bottom row).
  // depth controls recursion; char is the fill character.
  // Returns an error if size < 1 or depth < 0.
  func Generate(size, depth int, char rune) ([]string, error)
  ```

Use the classic bitwise rule: for the triangle of height `h`, a cell at `(row, col)` is filled iff `(col & row) == 0` when rows are arranged so the triangle points up. We derive height from `size` and clamp detail by `depth`. The simplest correct, testable approach: render a triangle of `n = min(size, 2^depth)` rows where row `r` (0-indexed from the top) has cells `c` in `[0, r]`, and cell is filled when `(r & c) == c` (equivalently `(r & c) == c`). Pin exact behavior with the tests below.

- [ ] Write failing test `sierpinski_test.go`:
  ```go
  package sierpinski

  import (
      "reflect"
      "testing"
  )

  func TestGenerateSmall(t *testing.T) {
      // depth 1 -> 2 rows. Bitwise Pascal mod 2 pattern.
      got, err := Generate(2, 1, '*')
      if err != nil {
          t.Fatalf("unexpected error: %v", err)
      }
      want := []string{
          "*",
          "**",
      }
      if !reflect.DeepEqual(got, want) {
          t.Fatalf("got %#v want %#v", got, want)
      }
  }

  func TestGenerateChar(t *testing.T) {
      got, _ := Generate(2, 1, '#')
      if got[1] != "##" {
          t.Fatalf("char not applied: %q", got[1])
      }
  }

  func TestGenerateInvalidSize(t *testing.T) {
      if _, err := Generate(0, 1, '*'); err == nil {
          t.Fatal("expected error for size 0")
      }
  }

  func TestGenerateInvalidDepth(t *testing.T) {
      if _, err := Generate(4, -1, '*'); err == nil {
          t.Fatal("expected error for negative depth")
      }
  }

  func TestGenerateRow4Pattern(t *testing.T) {
      // 4 rows: row index r, col c filled iff (r & c) == c
      got, _ := Generate(4, 2, '*')
      want := []string{
          "*",     // r0
          "**",    // r1
          "* *",   // r2: c0 filled, c1 NOT (2&1=0!=1), c2 filled
          "****",  // r3
      }
      if !reflect.DeepEqual(got, want) {
          t.Fatalf("got %#v want %#v", got, want)
      }
  }
  ```
- [ ] Run it, expect failure (package/function missing):
  ```bash
  go test ./internal/sierpinski/
  ```
  Expected: build/compile error referencing undefined `Generate`.
- [ ] Implement `sierpinski.go`:
  ```go
  package sierpinski

  import (
      "errors"
      "strings"
  )

  func Generate(size, depth int, char rune) ([]string, error) {
      if size < 1 {
          return nil, errors.New("size must be at least 1")
      }
      if depth < 0 {
          return nil, errors.New("depth must be non-negative")
      }
      n := size
      cap := 1 << depth // 2^depth rows max
      if n > cap {
          n = cap
      }
      rows := make([]string, 0, n)
      for r := 0; r < n; r++ {
          var b strings.Builder
          for c := 0; c <= r; c++ {
              if (r & c) == c {
                  b.WriteRune(char)
              } else {
                  b.WriteRune(' ')
              }
          }
          rows = append(rows, b.String())
      }
      return rows, nil
  }
  ```
- [ ] Run tests, expect pass:
  ```bash
  go test ./internal/sierpinski/
  ```
  Expected: `ok  github.com/example/fractals/internal/sierpinski`.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add Sierpinski triangle algorithm"
  ```

---

### Task 3: Mandelbrot algorithm

**Files:** `internal/mandelbrot/mandelbrot.go`, `internal/mandelbrot/mandelbrot_test.go`

**Interfaces:**
- Consumes: nothing.
- Produces:
  ```go
  // DefaultGradient is the iteration->char ramp.
  const DefaultGradient = " .:-=+*#%@"

  // Render returns `height` strings each of length `width`.
  // iterations is the escape ceiling.
  // If gradient is non-empty, iteration counts map across its runes.
  // If single != 0, that rune is used for in-set (non-escaping) points and ' ' otherwise.
  // Exactly one of gradient/single is used: pass single==0 to use gradient.
  // Errors if width<1, height<1, or iterations<1.
  func Render(width, height, iterations int, gradient string, single rune) ([]string, error)
  ```

Map the complex plane region real `[-2.5, 1.0]`, imag `[-1.0, 1.0]`. For each pixel compute escape iteration count `it`. Points that never escape (`it == iterations`) belong to the set.

- Gradient mode: index = `it * (len(runes)-1) / iterations`, clamped; in-set points (it==iterations) get the last gradient char (`@`).
- Single-char mode: in-set points get `single`, escaped points get `' '`.

- [ ] Write failing test `mandelbrot_test.go`:
  ```go
  package mandelbrot

  import "testing"

  func TestRenderDimensions(t *testing.T) {
      rows, err := Render(80, 24, 100, DefaultGradient, 0)
      if err != nil {
          t.Fatalf("unexpected error: %v", err)
      }
      if len(rows) != 24 {
          t.Fatalf("got %d rows want 24", len(rows))
      }
      for i, r := range rows {
          if len([]rune(r)) != 80 {
              t.Fatalf("row %d width %d want 80", i, len([]rune(r)))
          }
      }
  }

  func TestRenderHasSetPoints(t *testing.T) {
      // Center-ish of the cardioid is in-set; expect the in-set char '@' to appear.
      rows, _ := Render(80, 24, 100, DefaultGradient, 0)
      found := false
      for _, r := range rows {
          for _, c := range r {
              if c == '@' {
                  found = true
              }
          }
      }
      if !found {
          t.Fatal("expected at least one in-set '@' point")
      }
  }

  func TestRenderSingleChar(t *testing.T) {
      rows, _ := Render(40, 12, 50, "", '#')
      for _, r := range rows {
          for _, c := range r {
              if c != '#' && c != ' ' {
                  t.Fatalf("single mode produced unexpected rune %q", c)
              }
          }
      }
  }

  func TestRenderInvalid(t *testing.T) {
      cases := [][3]int{{0, 10, 10}, {10, 0, 10}, {10, 10, 0}}
      for _, c := range cases {
          if _, err := Render(c[0], c[1], c[2], DefaultGradient, 0); err == nil {
              t.Fatalf("expected error for %v", c)
          }
      }
  }
  ```
- [ ] Run, expect failure:
  ```bash
  go test ./internal/mandelbrot/
  ```
  Expected: undefined `Render` / `DefaultGradient`.
- [ ] Implement `mandelbrot.go`:
  ```go
  package mandelbrot

  import (
      "errors"
      "strings"
  )

  const DefaultGradient = " .:-=+*#%@"

  func Render(width, height, iterations int, gradient string, single rune) ([]string, error) {
      if width < 1 {
          return nil, errors.New("width must be at least 1")
      }
      if height < 1 {
          return nil, errors.New("height must be at least 1")
      }
      if iterations < 1 {
          return nil, errors.New("iterations must be at least 1")
      }

      const (
          rMin, rMax = -2.5, 1.0
          iMin, iMax = -1.0, 1.0
      )
      var ramp []rune
      if single == 0 {
          ramp = []rune(gradient)
          if len(ramp) == 0 {
              ramp = []rune(DefaultGradient)
          }
      }

      rows := make([]string, 0, height)
      for py := 0; py < height; py++ {
          var b strings.Builder
          ci := iMin + (iMax-iMin)*float64(py)/float64(height-1+boolToInt(height == 1))
          for px := 0; px < width; px++ {
              cr := rMin + (rMax-rMin)*float64(px)/float64(width-1+boolToInt(width == 1))
              it := escape(cr, ci, iterations)
              if single != 0 {
                  if it == iterations {
                      b.WriteRune(single)
                  } else {
                      b.WriteRune(' ')
                  }
                  continue
              }
              idx := it * (len(ramp) - 1) / iterations
              if idx >= len(ramp) {
                  idx = len(ramp) - 1
              }
              b.WriteRune(ramp[idx])
          }
          rows = append(rows, b.String())
      }
      return rows, nil
  }

  func escape(cr, ci float64, maxIter int) int {
      var zr, zi float64
      for it := 0; it < maxIter; it++ {
          zr2, zi2 := zr*zr, zi*zi
          if zr2+zi2 > 4.0 {
              return it
          }
          zi = 2*zr*zi + ci
          zr = zr2 - zi2 + cr
      }
      return maxIter
  }

  func boolToInt(b bool) int {
      if b {
          return 1
      }
      return 0
  }
  ```
  Note: the `boolToInt(... == 1)` guard avoids divide-by-zero when width or height is 1.
- [ ] Run tests, expect pass:
  ```bash
  go test ./internal/mandelbrot/
  ```
  Expected: `ok  github.com/example/fractals/internal/mandelbrot`.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add Mandelbrot rendering algorithm"
  ```

---

### Task 4: Root CLI command & Execute

**Files:** `internal/cli/root.go`, `cmd/fractals/main.go`

**Interfaces:**
- Consumes: nothing yet (subcommands attach in Tasks 5–6).
- Produces:
  ```go
  func RootCmd() *cobra.Command  // returns configured root, used by tests
  func Execute() error           // builds root, runs, returns error
  ```
  Root command `Use: "fractals"`, with a `Short` description so `--help` shows usage.

- [ ] Write failing test `internal/cli/root_test.go`:
  ```go
  package cli

  import (
      "bytes"
      "strings"
      "testing"
  )

  func TestRootHelp(t *testing.T) {
      cmd := RootCmd()
      var out bytes.Buffer
      cmd.SetOut(&out)
      cmd.SetArgs([]string{"--help"})
      if err := cmd.Execute(); err != nil {
          t.Fatalf("help returned error: %v", err)
      }
      if !strings.Contains(out.String(), "fractals") {
          t.Fatalf("help missing usage, got: %s", out.String())
      }
  }
  ```
- [ ] Run, expect failure (undefined `RootCmd`):
  ```bash
  go test ./internal/cli/
  ```
- [ ] Implement `root.go`: define `RootCmd()` returning `&cobra.Command{Use: "fractals", Short: "Generate ASCII art fractals"}`, and `Execute()` that calls `RootCmd().Execute()`. (Subcommands added in later tasks via `root.AddCommand(...)` inside `RootCmd`.)
- [ ] Run tests, expect pass:
  ```bash
  go test ./internal/cli/
  ```
- [ ] Update `cmd/fractals/main.go` to use the real entry point:
  ```go
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
- [ ] Build & run help:
  ```bash
  go build ./... && go run ./cmd/fractals --help
  ```
  Expected: usage text containing `fractals`.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add root CLI command and Execute wiring"
  ```

---

### Task 5: Sierpinski subcommand

**Files:** `internal/cli/sierpinski.go`, `internal/cli/sierpinski_test.go`, `internal/cli/root.go` (register)

**Interfaces:**
- Consumes: `sierpinski.Generate(size, depth int, char rune) ([]string, error)`; `RootCmd()`.
- Produces: `newSierpinskiCmd() *cobra.Command`, registered onto root.

Flags: `--size` (int, default 32), `--depth` (int, default 5), `--char` (string, default `"*"`). Validate `--char` is exactly one rune; convert to rune; call `Generate`; print rows to the command's stdout joined by `\n`.

- [ ] Write failing test `sierpinski_test.go`:
  ```go
  package cli

  import (
      "bytes"
      "strings"
      "testing"
  )

  func runRoot(t *testing.T, args ...string) (string, error) {
      t.Helper()
      cmd := RootCmd()
      var out bytes.Buffer
      cmd.SetOut(&out)
      cmd.SetErr(&out)
      cmd.SetArgs(args)
      err := cmd.Execute()
      return out.String(), err
  }

  func TestSierpinskiDefaultRuns(t *testing.T) {
      out, err := runRoot(t, "sierpinski", "--size", "4", "--depth", "2")
      if err != nil {
          t.Fatalf("err: %v", err)
      }
      if !strings.Contains(out, "*") {
          t.Fatalf("expected '*' in output: %q", out)
      }
  }

  func TestSierpinskiCustomChar(t *testing.T) {
      out, _ := runRoot(t, "sierpinski", "--size", "4", "--depth", "2", "--char", "#")
      if !strings.Contains(out, "#") || strings.Contains(out, "*") {
          t.Fatalf("char not applied: %q", out)
      }
  }

  func TestSierpinskiBadChar(t *testing.T) {
      _, err := runRoot(t, "sierpinski", "--char", "ab")
      if err == nil {
          t.Fatal("expected error for multi-char --char")
      }
  }

  func TestSierpinskiBadSize(t *testing.T) {
      _, err := runRoot(t, "sierpinski", "--size", "0")
      if err == nil {
          t.Fatal("expected error for size 0")
      }
  }
  ```
- [ ] Run, expect failure (no `sierpinski` subcommand):
  ```bash
  go test ./internal/cli/ -run Sierpinski
  ```
- [ ] Implement `newSierpinskiCmd()` in `sierpinski.go`. In `RunE`: validate `len([]rune(charFlag)) == 1` (else return error `--char must be a single character`); call `sierpinski.Generate`; on error return it; else `fmt.Fprintln(cmd.OutOrStdout(), strings.Join(rows, "\n"))`. Register it in `RootCmd()` via `root.AddCommand(newSierpinskiCmd())`.
- [ ] Run tests, expect pass:
  ```bash
  go test ./internal/cli/ -run Sierpinski
  ```
- [ ] Manual check:
  ```bash
  go run ./cmd/fractals sierpinski --size 16 --depth 4
  ```
  Expected: a triangle of `*` characters.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add sierpinski subcommand"
  ```

---

### Task 6: Mandelbrot subcommand

**Files:** `internal/cli/mandelbrot.go`, `internal/cli/mandelbrot_test.go`, `internal/cli/root.go` (register)

**Interfaces:**
- Consumes: `mandelbrot.Render(width, height, iterations int, gradient string, single rune) ([]string, error)`; `RootCmd()`.
- Produces: `newMandelbrotCmd() *cobra.Command`, registered onto root.

Flags: `--width` (int, default 80), `--height` (int, default 24), `--iterations` (int, default 100), `--char` (string, default `""`). When `--char` is empty → gradient mode (`Render(..., DefaultGradient, 0)`). When `--char` set, must be exactly one rune → single-char mode (`Render(..., "", r)`).

- [ ] Write failing test `mandelbrot_test.go` (reuses `runRoot` from Task 5's file):
  ```go
  package cli

  import (
      "strings"
      "testing"
  )

  func TestMandelbrotDefaultRuns(t *testing.T) {
      out, err := runRoot(t, "mandelbrot", "--width", "40", "--height", "12")
      if err != nil {
          t.Fatalf("err: %v", err)
      }
      if !strings.Contains(out, "@") {
          t.Fatalf("expected in-set '@': %q", out)
      }
  }

  func TestMandelbrotSingleChar(t *testing.T) {
      out, _ := runRoot(t, "mandelbrot", "--width", "40", "--height", "12", "--char", "X")
      if !strings.Contains(out, "X") {
          t.Fatalf("expected 'X' in output: %q", out)
      }
  }

  func TestMandelbrotBadChar(t *testing.T) {
      _, err := runRoot(t, "mandelbrot", "--char", "ab")
      if err == nil {
          t.Fatal("expected error for multi-char --char")
      }
  }

  func TestMandelbrotBadWidth(t *testing.T) {
      _, err := runRoot(t, "mandelbrot", "--width", "0")
      if err == nil {
          t.Fatal("expected error for width 0")
      }
  }
  ```
- [ ] Run, expect failure:
  ```bash
  go test ./internal/cli/ -run Mandelbrot
  ```
- [ ] Implement `newMandelbrotCmd()` in `mandelbrot.go`. In `RunE`: if `charFlag == ""` call `Render(w, h, iter, mandelbrot.DefaultGradient, 0)`; else validate single rune (error `--char must be a single character`) and call `Render(w, h, iter, "", r)`; on error return it; print rows joined by `\n`. Register via `root.AddCommand(newMandelbrotCmd())` in `RootCmd()`.
- [ ] Run tests, expect pass:
  ```bash
  go test ./internal/cli/ -run Mandelbrot
  ```
- [ ] Manual check:
  ```bash
  go run ./cmd/fractals mandelbrot --width 80 --height 24
  ```
  Expected: recognizable Mandelbrot shape with gradient characters.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add mandelbrot subcommand"
  ```

---

### Task 7: Full integration verification

**Files:** none new (verification only).

**Interfaces:** consumes the built `fractals` binary.

- [ ] Run the whole suite:
  ```bash
  go test ./...
  ```
  Expected: all packages `ok`.
- [ ] Vet:
  ```bash
  go vet ./...
  ```
  Expected: no output.
- [ ] Verify each acceptance criterion manually:
  ```bash
  go run ./cmd/fractals --help
  go run ./cmd/fractals sierpinski --help
  go run ./cmd/fractals sierpinski
  go run ./cmd/fractals mandelbrot
  go run ./cmd/fractals sierpinski --size 16 --char '#'
  go run ./cmd/fractals mandelbrot --width 60 --height 20 --iterations 200
  go run ./cmd/fractals sierpinski --size 0; echo "exit=$?"
  ```
  Expected: help texts show usage; triangle and Mandelbrot render; custom char works; the last command prints `error: size must be at least 1` to stderr and `exit=1`.
- [ ] Commit (if any tidy-ups were needed):
  ```bash
  git add -A && git commit -m "Final integration verification" --allow-empty
  ```

---

## Self-Review

- **Spec coverage:**
  - AC1 `--help` → Task 4 + Task 7. ✓
  - AC2 sierpinski triangle → Tasks 2, 5. ✓
  - AC3 mandelbrot set → Tasks 3, 6. ✓
  - AC4 size/width/height/depth/iterations flags → Tasks 5, 6. ✓
  - AC5 `--char` customization (both commands, gradient default for mandelbrot) → Tasks 5, 6. ✓
  - AC6 invalid input clear errors → validation in algorithms (Tasks 2, 3) surfaced via `RunE` returning errors and `main` printing to stderr with exit 1 (Task 4); tested in Tasks 5, 6, 7. ✓
  - AC7 all tests pass → Task 7. ✓
  - Architecture file layout matches spec exactly. ✓
  - Dependencies (Go 1.21+, cobra) → Task 1 / Global Constraints. ✓
  - Mandelbrot default gradient `" .:-=+*#%@"` verbatim → Task 3. ✓
- **Placeholder scan:** no `TODO`/`FIXME`/`...` left in code blocks; the only temporary stub (Task 1 `main`) is explicitly replaced in Task 4.
- **Type consistency:** `Generate(int, int, rune) ([]string, error)` and `Render(int, int, int, string, rune) ([]string, error)` signatures are identical across their Interfaces blocks and call sites in Tasks 5 and 6. `runRoot` helper defined once (Task 5) and reused (Task 6) within the same `cli` package — no redefinition.
- **Edge case checked:** divide-by-zero when `width==1`/`height==1` handled via `boolToInt` guard in Task 3.