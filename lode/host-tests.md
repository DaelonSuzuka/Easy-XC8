# Host unit tests

How to write and run pure-module tests on the development machine. This is the
canonical how-to; projects and other submodules should link here rather than
duplicating rules.

## Why

Some firmware logic is a **pure decision table** (classify this frame, map this
value, debounce FSM step). That logic can fail silently on the chip. Host tests
lock the table without XC8, a programmer, or mocks.

Impure code (UART, SFRs, ISRs, full `radio_update`) stays on-device: shell,
inject, logs. Do not mock hardware to “test” drivers.

## Commands

From any project that uses this toolchain:

```bash
make venv                    # project Python deps only (not Zig)
uv tool install ziglang      # once per machine — shared Zig (~400MB unpacked)
make test                    # discover, compile, run all *_test.c
```

Zig is **not** in the project venv (that would duplicate ~400MB per clone). Prefer
a single machine-wide install via uv.

### Compiler resolution (`host_test.py`)

First match wins:

1. `HOST_CC` — e.g. `HOST_CC=gcc make test`
2. `python-zig` on `PATH` — from `uv tool install ziglang`
3. `zig` on `PATH` — system Zig (`zig cc`)
4. `uvx --from ziglang python-zig` — on-demand / cache, no permanent tool
5. `python -m ziglang` — only if ziglang happens to be in the active env

## Convention

| Rule | Detail |
|------|--------|
| Name | `foo_test.c` next to `foo.c` (same directory) |
| Link | Runner links `foo_test.c` + `foo.c` only (stem match) |
| Entry | `main` returns `0` on success, nonzero on failure |
| Firmware | XC8 **always skips** `*_test.c` (`scripts/skip.py` builtin) |
| Output | Binaries under `build/host/` (gitignored with `build/`) |

Optional helpers: `#include "check.h"` from `toolchain/host/` (`CHECK`,
`CHECK_MSG`). Plain `printf` + a failure counter is fine — see product examples.

## What to test (and what not to)

**Yes — pure islands**

- Protocol classifiers / address filters
- BCD or table lookup with golden vectors
- Debounce or chase math with no pin I/O
- Hash, string, or packing helpers with no UART

**No**

- Full drivers (`uart.c`, PPS, ADC registers)
- Anything that needs a mock PIC or fake bus
- “Almost pure” code that still needs timers and SFRs — keep that on-device

If writing the test requires inventing a fake hardware layer, stop. Wrong layer.

## How to add a test (checklist)

1. **Extract or write a pure module** — `foo.c` / `foo.h` with no `pic_header`,
   no SFRs, no project-only globals required to call the function under test.
2. **Add `foo_test.c` beside it** with `main`.
3. **Assert contracts** — golden vectors, invariants (“only DIRECTED completes
   a poll”), edge cases (null, short length).
4. **Run** `make test` from the project root.
5. **Confirm skip** — `make compile` must not link `foo_test.c` (it appears in
   `build/skipped_files.txt` when skip rules run).

### Minimal skeleton

```c
/* foo_test.c — co-located with foo.c; run via: make test */
#include "foo.h"
#include <stdio.h>

int main(void) {
    int failures = 0;

    if (foo_classify(0) != FOO_OK) {
        printf("FAIL  classify(0)\n");
        failures++;
    } else {
        printf("ok    classify(0)\n");
    }

    if (failures) {
        printf("%d FAILURE(S)\n", failures);
        return 1;
    }
    printf("all passed\n");
    return 0;
}
```

With optional check macros:

```c
#include "foo.h"
#include "check.h"

int main(void) {
    CHECK(foo_classify(0) == FOO_OK);
    CHECK(foo_classify(1) == FOO_BAD);
    return 0;
}
```

### Multi-file pure modules

Default is one companion `.c`. If a later island needs more sources, extend the
runner (or a `// host-sources:` line) — do not invent that until a second real
case appears.

## Delivery / propagation

| Layer | Role |
|-------|------|
| **toolchain** (this doc + `make test`) | Runner, zig, skip rule — bump submodule |
| **os / peripherals** | Pure helpers + `*_test.c` when islands live there |
| **product** | Product tables (e.g. CI-V classify) + `*_test.c` |

After a toolchain bump in any PIC project:

```bash
git submodule update
make venv
uv tool install ziglang   # if not already on this machine
make test
```

## Reference implementation

In projects that already use this: look for `*_test.c` next to pure modules
(e.g. MC-7300 `src/civ_frame_test.c`).

## Related toolchain files

- `scripts/host_test.py` — discovery and runner
- `scripts/skip.py` — builtin `.*_test\.c$` for firmware
- `host/check.h` — optional assert macros
- `makefiles/targets.mk` — `test` target
