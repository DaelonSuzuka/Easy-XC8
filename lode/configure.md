# Creating a project.yaml

`project.yaml` is the source of truth for a project's build configuration. There is no wizard — create the file by hand or with an AI agent. The [JSON schema](../schemas/project.schema.json) provides validation and autocomplete when referenced via the `$schema` key.

## Minimal Config

```yaml
$schema: toolchain/schemas/project.schema.json
name: MyProject

hw_version: 0.0.1
sw_version: 0.0.1

build_settings:
  programmer: Pickit4
  development:
    processor: 18F16Q41
    defines: [DEVELOPMENT, SHELL_ENABLED, LOGGING_ENABLED]
  release:
    processor: 18F16Q41
    defines: [RELEASE]
```

## Required Keys

- `name` — project name (no spaces)
- `build_settings.development.processor` — PIC18 part (e.g. `18F16Q41`)
- `build_settings.release.processor` — same or different

Everything else has defaults. See [variables.md](variables.md) for the full key reference, defaults, and the inheritance system.

## Common Defines

| Define | Effect |
|--------|--------|
| `DEVELOPMENT` | Enables dev-only code paths, shell commands |
| `SHELL_ENABLED` | Interactive shell on debug UART |
| `SHELL_HISTORY_ENABLED` | Command history in shell |
| `LOGGING_ENABLED` | Runtime log levels, `logedit` TUI |
| `RELEASE` | Production build flag |

Add defines to `development.defines` or `release.defines` as a list.

## Skip Rules

Exclude source files from compilation per-profile with glob patterns:

```yaml
  development:
    skip_rules:
      - src/os/json/*
      - src/usb/*
  release:
    skip_rules:
      - src/os/shell/*
      - src/os/json/*
      - src/usb/*
```

## Programmers

`project.yaml` names the **family** only (same on every OS). Host platform
selects the command at upload/program time via `scripts/programmers.py`.

| Family | Windows | Posix |
|--------|---------|-------|
| Pickit3 | `pk3cmd` | `pk3cmd` |
| Pickit4 | `ipecmd` | `ipecmd.sh` |
| Pickit5 | `ipecmd` | `ipecmd.sh` |
| ICD-U80 | `ccsloader` | `ccsloader` (flags differ) |

Legacy aliases (`Pickit4-linux`, etc.) still work but prefer family names.

## Extending Programmers

Add a family to `upload.json` with shared fields and a `platforms` map:

```json
{
  "MyProgrammer": {
    "target": "-p",
    "source": "-f",
    "flags": ["-v"],
    "garbage": ["*.log"],
    "platforms": {
      "windows": { "command": "myprog.exe" },
      "posix": { "command": "myprog" }
    }
  }
}
```

Platform overlay may also override `flags`, `target`, `source`, or `garbage`.

## Adding New Config Keys

To add a new env-level key that profiles inherit:

1. Add an `inherit('new_key', default)` call inside `fix_env()` in `project.py`.
2. Add the key to the table in [variables.md](variables.md) with its default.
3. Add the key to `schemas/project.schema.json`.

If you forget step 1, the key will be silently absent from the profile dicts.