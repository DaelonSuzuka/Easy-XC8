# Host unit tests

Pure-module tests run on the development machine with `zig cc` (via the
`ziglang` PyPI package in the toolchain venv). No XC8, no PIC, no mocks.

## Commands

```bash
make test          # discover, compile, run all *_test.c
make venv          # installs ziglang among other deps
```

Optional: `HOST_CC=gcc make test` to use a system compiler instead of zig.

## Convention

- Co-locate `foo_test.c` next to `foo.c`.
- One binary per test file; `main` returns 0 on success.
- `foo_test.c` links `foo.c` in the same directory (stem match).
- Firmware builds **always skip** `*_test.c` (`skip.py` builtin rule).

Optional helpers: `toolchain/host/check.h` (`CHECK`, `CHECK_MSG`).

## What belongs here

Decision tables, decode/map, protocol classifiers, pure math — islands with no
SFR/UART dependency. Do not host-test drivers by mocking hardware.

## Delivery

Shipped in the **toolchain** submodule. Projects get `make test` by bumping
toolchain and running `make venv`. Pure modules and their `*_test.c` files may
live in product code, `os`, or `peripherals`.
