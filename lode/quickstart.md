# Toolchain Quickstart

Load this file first when working with the toolchain submodule.

## What It Is

Custom Python build system wrapping Microchip XC8. Make for orchestration, Python for build logic, cog for code generation.

## Key Rules

- **Always use `make` targets** — never run Python scripts directly
- **`make compile`** to build, **`make release`** for production
- **`project.yaml`** is the source of truth for build config
- **Skip rules** can exclude files per build profile (dev and release both support them)
- **Codegen lives in the project** — toolchain provides helpers, project owns `pinmap.py` and `cogfiles.txt`

## Make Targets

| Target | Purpose |
|--------|---------|
| `make compile` | Build development hex |
| `make upload` | Flash to device |
| `make release` | Build release hex |
| `make program` | Program release hex |
| `make clean` | Remove build artifacts |
| `make lint` | cppcheck static analysis |
| `make config` | Interactive project.yaml wizard |

## Project.yaml Structure

```yaml
name: MC-200
build_settings:
  development:
    processor: 18F16Q41
    float_size: 24
    defines: [DEVELOPMENT, SHELL_ENABLED, ...]
    skip_rules: [src/peripherals/src/spi.c, ...]
  release:
    defines: [RELEASE]
    skip_rules: [src/shellcommands/*, ...]
```

## Lode Index

- [summary.md](summary.md) — full build system overview
- [configure.md](configure.md) — project.yaml wizard
- [codegen.md](codegen.md) — cog code generation
- [reports.md](reports.md) — post-build memory analysis
- [variables.md](variables.md) — build variable system
