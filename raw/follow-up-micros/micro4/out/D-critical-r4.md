# Go Fractals CLI - Implementation Plan

A command-line tool generating ASCII art fractals (Sierpinski triangle and Mandelbrot set) built with Go and cobra.

## Global Constraints

- Go 1.21+ (set in `go.mod` as `go 1.21`)
- CLI library: `github.com/spf13/cobra`
- Module path: `github.com/example/fractals`
- Binary name: `fractals`
- Mandelbrot default gradient (exact, 10 chars including leading space): `" .:-=+*#%@"`
- Sierpinski default char: `*`; default size `32`; default depth `5`
- Mandelbrot defaults: width `80`, height `24`, iterations `100`
- Invalid inputs must produce clear error messages and a non-zero exit code
- Each fractal algorithm lives in `internal/` and is independently testable without cobra

## File Structure

| File | Responsibility |
|------|----------------|
| `go.mod` | Module definition, Go version, cobra dependency |
| `internal/sierpinski/sierpinski.go` | Pure Sierpinski generation algorithm returning `[]string` |
| `internal/sierpinski/sierpinski_test.go` | Tests pinning Sierpinski output behavior and validation |
| `internal/mandelbrot/mandelbrot.go` | Pure Mandelbrot generation algorithm returning `[]string` |
| `internal/mandelbrot/mandelbrot_test.go` | Tests pinning Mandelbrot output behavior and validation |
| `internal/cli/root.go` | Root cobra command + help wiring |
| `internal/cli/sierpinski.go` | `sierpinski` subcommand: flags → algorithm → stdout |
| `internal/cli/mandelbrot.go` | `mandelbrot` subcommand: flags → algorithm → stdout |
| `internal/cli/root_test.go` | Smoke tests executing commands and asserting output |
| `cmd/fractals/main.go` | Entry point calling `cli.Execute()` |

---

### Task 1: Module setup and Sierpinski algorithm

**Files:**
- `go.mod`
- `internal/sierpinski/sierpinski.go`
- `internal/sierpinski/sierpinski_test.go`

**Interfaces:**
- Produces: `func Generate(size, depth int, char rune) ([]string, error)`
  - Returns one string per row; row `r` (0-indexed from top) corresponds to triangle apex at top.
  - Returns an error for `size < 1`, `depth < 0`, or `size > 4096` (sanity bound).

**Algorithm note (non-obvious):** Use the bitwise AND test for the Sierpinski triangle. For a triangle of height `n = 2^depth` rows, a cell at row `y` (0 at apex) and column `x` is filled iff `(x & y) == 0`, where `x` ranges over positions within that row. Lay out rows centered so each line is left-padded with spaces. The base width is `n` cells. `size` controls the rendered base width by scaling: render at the natural `2^depth` resolution but clamp the number of rows so the base does not exceed `size` columns — specifically the effective height `rows = min(1<<depth, size)`. Each output row has length equal to `rows` (apex centered with leading spaces).

Use this exact layout: for `y` in `0..rows-1`, build a string. Leading spaces count = `rows - 1 - y`. Then for `x` in `0..y`, append `char` if `(x & y) == 0` else a space, separated by a single space between cells.

- [ ] Run `go mod init github.com/example/fractals` and set `go 1.21` in `go.mod`.
- [ ] Write failing test in `sierpinski_test.go`:

```go
package sierpinski

import (
	"reflect"
	"testing"
)

func TestGenerateDepth1(t *testing.T) {
	got, err := Generate(32, 1, '*')
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	// depth 1 => rows = min(2, 32) = 2
	want := []string{
		" *",
		"* *",
	}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("got %#v, want %#v", got, want)
	}
}

func TestGenerateCustomChar(t *testing.T) {
	got, _ := Generate(32, 1, '#')
	if got[1] != "# #" {
		t.Errorf("got %q, want %q", got[1], "# #")
	}
}

func TestGenerateInvalidSize(t *testing.T) {
	if _, err := Generate(0, 5, '*'); err == nil {
		t.Error("expected error for size 0")
	}
}

func TestGenerateInvalidDepth(t *testing.T) {
	if _, err := Generate(32, -1, '*'); err == nil {
		t.Error("expected error for negative depth")
	}
}
```

- [ ] Run `go test ./internal/sierpinski/` and confirm it fails to compile (no `Generate`).
- [ ] Implement `Generate` in `sierpinski.go` per the algorithm note: validate inputs, compute `rows = min(1<<depth, size)`, build each row with leading spaces and space-separated cells using `(x & y) == 0`.
- [ ] Run `go test ./internal/sierpinski/` and confirm all tests pass.
- [ ] Commit: `git commit -am "Add Sierpinski algorithm"`

---

### Task 2: Mandelbrot algorithm

**Files:**
- `internal/mandelbrot/mandelbrot.go`
- `internal/mandelbrot/mandelbrot_test.go`

**Interfaces:**
- Produces: `func Generate(width, height, iterations int, gradient []rune) ([]string, error)`
  - Maps the complex plane region real `[-2.5, 1.0]`, imaginary `[-1.25, 1.25]` onto the `width × height` grid.
  - For each cell, run escape iteration up to `iterations`; map escape count to a gradient index.
  - Returns one string per row, each of length `width`.
  - Errors for `width < 1`, `height < 1`, `iterations < 1`, or empty `gradient`.

**Algorithm note (non-obvious):** For pixel `(px, py)`:
- `x0 = -2.5 + (px / (width-1)) * (1.0 - (-2.5))` (guard `width==1` → use `px=0` mapping to left edge)
- `y0 = -1.25 + (py / (height-1)) * (1.25 - (-1.25))`
- Iterate `x, y` from 0: `xtemp = x*x - y*y + x0; y = 2*x*y + y0; x = xtemp` while `x*x+y*y <= 4` and `iter < iterations`.
- Gradient index: points that never escape (`iter == iterations`) map to the **last** gradient char (densest). Otherwise index = `iter * (len(gradient)-1) / iterations`. This makes the interior solid and the exterior fade — matching gradient `" .:-=+*#%@"` where `@` is interior.

- [ ] Write failing test in `mandelbrot_test.go`:

```go
package mandelbrot

import (
	"strings"
	"testing"
)

var defaultGradient = []rune(" .:-=+*#%@")

func TestGenerateDimensions(t *testing.T) {
	rows, err := Generate(80, 24, 100, defaultGradient)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(rows) != 24 {
		t.Fatalf("got %d rows, want 24", len(rows))
	}
	for i, r := range rows {
		if len([]rune(r)) != 80 {
			t.Errorf("row %d width %d, want 80", i, len([]rune(r)))
		}
	}
}

func TestInteriorIsDensest(t *testing.T) {
	// The point near (-0.5, 0) is inside the set and should map to the last gradient rune.
	rows, _ := Generate(80, 24, 100, defaultGradient)
	joined := strings.Join(rows, "\n")
	if !strings.ContainsRune(joined, '@') {
		t.Error("expected interior '@' character in output")
	}
}

func TestSingleChar(t *testing.T) {
	rows, _ := Generate(40, 12, 50, []rune{'#'})
	for _, r := range rows {
		for _, c := range r {
			if c != '#' {
				t.Errorf("expected only '#', got %q", c)
			}
		}
	}
}

func TestInvalidWidth(t *testing.T) {
	if _, err := Generate(0, 24, 100, defaultGradient); err == nil {
		t.Error("expected error for width 0")
	}
}

func TestEmptyGradient(t *testing.T) {
	if _, err := Generate(80, 24, 100, []rune{}); err == nil {
		t.Error("expected error for empty gradient")
	}
}
```

- [ ] Run `go test ./internal/mandelbrot/` and confirm compile failure (no `Generate`).
- [ ] Implement `Generate` per the algorithm note, including validation and the interior-maps-to-last-char rule.
- [ ] Run `go test ./internal/mandelbrot/` and confirm all tests pass.
- [ ] Commit: `git commit -am "Add Mandelbrot algorithm"`

---

### Task 3: CLI commands and entry point

**Files:**
- `internal/cli/root.go`
- `internal/cli/sierpinski.go`
- `internal/cli/mandelbrot.go`
- `internal/cli/root_test.go`
- `cmd/fractals/main.go`
- `go.mod` (cobra dependency added)

**Interfaces:**
- Consumes: `sierpinski.Generate(size, depth int, char rune) ([]string, error)`, `mandelbrot.Generate(width, height, iterations int, gradient []rune) ([]string, error)`
- Produces:
  - `func Execute() error` in `internal/cli` — builds root command and runs it.
  - Root command writes output to `cmd.OutOrStdout()` so tests can capture it.

**`--char` handling (non-obvious):**
- Sierpinski: `--char` is a string flag defaulting to `"*"`. Validate it is exactly one rune; error otherwise. Pass the rune to `Generate`.
- Mandelbrot: `--char` is a string flag defaulting to `""` (empty). If empty, use gradient `[]rune(" .:-=+*#%@")`. If non-empty, validate exactly one rune and use `[]rune{r}` as the gradient.

- [ ] Add cobra: run `go get github.com/spf13/cobra@latest`, then `go mod tidy`.
- [ ] Write failing smoke test in `root_test.go`:

```go
package cli

import (
	"bytes"
	"strings"
	"testing"
)

func run(args ...string) (string, error) {
	cmd := newRootCmd()
	buf := &bytes.Buffer{}
	cmd.SetOut(buf)
	cmd.SetErr(buf)
	cmd.SetArgs(args)
	err := cmd.Execute()
	return buf.String(), err
}

func TestHelp(t *testing.T) {
	out, err := run("--help")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "sierpinski") || !strings.Contains(out, "mandelbrot") {
		t.Errorf("help missing subcommands: %s", out)
	}
}

func TestSierpinskiRuns(t *testing.T) {
	out, err := run("sierpinski", "--size", "16", "--depth", "3", "--char", "#")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(out, "#") {
		t.Errorf("expected '#' in output: %s", out)
	}
}

func TestMandelbrotRuns(t *testing.T) {
	out, err := run("mandelbrot", "--width", "40", "--height", "12")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.ContainsRune(out, '@') {
		t.Errorf("expected '@' in output: %s", out)
	}
}

func TestSierpinskiMultiCharError(t *testing.T) {
	_, err := run("sierpinski", "--char", "ab")
	if err == nil {
		t.Error("expected error for multi-char --char")
	}
}
```

- [ ] Run `go test ./internal/cli/` and confirm compile failure (no `newRootCmd`).
- [ ] Implement `root.go`: `newRootCmd()` returns root `*cobra.Command` (Use: `fractals`, short description), adds the two subcommands; `Execute()` calls `newRootCmd().Execute()`.
- [ ] Implement `sierpinski.go`: subcommand with `--size`, `--depth`, `--char` flags; `RunE` validates the single-rune char, calls `sierpinski.Generate`, prints rows to `cmd.OutOrStdout()` one per line.
- [ ] Implement `mandelbrot.go`: subcommand with `--width`, `--height`, `--iterations`, `--char` flags; `RunE` resolves gradient per the `--char` rule, calls `mandelbrot.Generate`, prints rows.
- [ ] Run `go test ./internal/cli/` and confirm all tests pass.
- [ ] Implement `cmd/fractals/main.go`:

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

- [ ] Run `go build ./...` and confirm no errors.
- [ ] Run `go run ./cmd/fractals sierpinski --size 16 --depth 4` and confirm a recognizable triangle prints.
- [ ] Run `go run ./cmd/fractals mandelbrot` and confirm a recognizable Mandelbrot set prints.
- [ ] Run `go test ./...` and confirm all packages pass.
- [ ] Commit: `git commit -am "Add CLI commands and entry point"`

---

## Self-Review

- **Spec coverage:** sierpinski (`--size/--depth/--char`) ✓ Task 1 + 3; mandelbrot (`--width/--height/--iterations/--char`) ✓ Task 2 + 3; help ✓ Task 3 (`TestHelp`); custom char ✓ both; invalid input errors ✓ (validation in Tasks 1–3, `TestSierpinskiMultiCharError`, `TestInvalidWidth`, `TestEmptyGradient`); all tests pass ✓ final step. Architecture file layout matches spec exactly.
- **Acceptance criteria:** 1–7 each mapped to a step or test above.
- **Placeholder scan:** No TODOs or stubs; all interfaces have concrete signatures.
- **Type consistency:** `Generate` signatures referenced identically in Interfaces and tests; `char` passed as `rune` to sierpinski, gradient as `[]rune` to mandelbrot; CLI resolves string flags to those types. Module path `github.com/example/fractals` consistent across `main.go` import and `go.mod`.
- **Gradient verbatim:** `" .:-=+*#%@"` used identically in spec, mandelbrot test, and CLI default.

One correction applied inline: the mandelbrot `--char` default is an empty string (not the gradient string) so the CLI can distinguish "use gradient" from "user supplied one char"; this is documented in the `--char` handling note in Task 3.