# Configuration Wizard

Interactive wizard for creating `project.yaml` configuration files.

## Running the Wizard

```bash
make config
```

Or directly:

```bash
python toolchain/scripts/configure.py
```

## Wizard Flow

The wizard prompts for:

1. **Project name** - Must be non-empty, no spaces
2. **Processor family** - K42 or Q43
3. **Processor** - Specific chip from the family (shows RAM/ROM)
4. **Programmer** - Selected from `upload.json`
5. **Feature toggles** - Checkboxes for common defines

## Processor Families

```
K42 Family:
  18F24K42 - 20 pins, 1K RAM, 16K ROM
  18F25K42 - 20 pins, 2K RAM, 32K ROM
  18F26K42 - 20 pins, 4K RAM, 64K ROM
  18F27K42 - 20 pins, 8K RAM, 128K ROM
  18F45K42 - 40 pins, 2K RAM, 32K ROM
  18F46K42 - 40 pins, 4K RAM, 64K ROM
  18F47K42 - 40 pins, 8K RAM, 128K ROM
  18F55K42 - 48 pins, 2K RAM, 32K ROM
  18F56K42 - 48 pins, 4K RAM, 64K ROM
  18F57K42 - 48 pins, 8K RAM, 128K ROM

Q43 Family:
  18F24Q43 - 20 pins, 1K RAM, 16K ROM
  18F25Q43 - 20 pins, 2K RAM, 32K ROM
  18F26Q43 - 20 pins, 4K RAM, 64K ROM
  18F27Q43 - 20 pins, 8K RAM, 128K ROM
  ... (same pin counts as K42)
```

## Feature Toggles

The wizard offers checkboxes for:

| Option | Define | Default |
|--------|--------|---------|
| DEVELOPMENT | `DEVELOPMENT` | On |
| LOGGING_ENABLED | `LOGGING_ENABLED` | On |
| SHELL_ENABLED | `SHELL_ENABLED` | On |
| SHELL_HISTORY_ENABLED | `SHELL_HISTORY_ENABLED` | On |
| USB_ENABLED | `USB_ENABLED` | Off |

Checked options are added to the `development.defines` list only.

## Generated project.yaml

```yaml
name: MyProject
hw_version: '0.0.1'
sw_version: '0.0.1'
build_settings:
  toolchain_options:
  - USE_DEP_SCANNER
  development:
    processor: 18F27K42
    programmer: Pickit4
    defines:
    - DEVELOPMENT
    - SHELL_ENABLED
    - LOGGING_ENABLED
  release:
    processor: 18F27K42
    programmer: Pickit4
    defines: []
```

## Programmers

`project.yaml` names the **family** only (same on every OS). Host platform
selects the command at upload/program time via `scripts/programmers.py`.

Defined in `toolchain/scripts/upload.json`:

| Family | Windows command | Posix command |
|--------|-----------------|---------------|
| Pickit3 | `pk3cmd` | `pk3cmd` |
| Pickit4 | `ipecmd` | `ipecmd.sh` |
| Pickit5 | `ipecmd` | `ipecmd.sh` |
| ICD-U80 | `ccsloader` | `ccsloader` (flags differ) |

Legacy aliases still work: `Pickit4-linux` → `Pickit4`, `Pickit5-linux` →
`Pickit5`, `ICD-U80-win` / `ICD-U80-linux` → `ICD-U80`. Prefer family names in
new configs.

```yaml
programmer: Pickit4   # not Pickit4-linux
```

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

Platform overlay may also override `flags`, `target`, `source`, or `garbage`
when those differ by OS.

## Extending Feature Toggles

Edit `configure.py` to add new feature options:

```python
# In new_config_file_questions
Choice("MY_FEATURE", name="MY_FEATURE", enabled=False),
```

Then handle the selection:

```python
# In project_config_wizard()
if 'MY_FEATURE' in config['options']:
    dev('MY_FEATURE')
```