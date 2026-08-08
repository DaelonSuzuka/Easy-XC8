# Project Variables

Accessing configuration values from Make and scripts.

## load_vars.py

The `load_vars.py` script extracts values from `project.yaml` for use in Makefiles or other scripts.

### Usage

```bash
python toolchain/scripts/load_vars.py <key>
```

### Simple Keys

```bash
# Get project name
python toolchain/scripts/load_vars.py name
# Output: MC-200

# Get source directory
python toolchain/scripts/load_vars.py src_dir
# Output: src

# Get build directory
python toolchain/scripts/load_vars.py build_dir
# Output: build
```

### Compound Keys

Use dot notation for nested values:

```bash
# Get development processor
python toolchain/scripts/load_vars.py development.processor
# Output: 18F16Q41

# Get release programmer (family name; OS resolved at upload)
python toolchain/scripts/load_vars.py release.programmer
# Output: Pickit4
```

## Use in Makefiles

The Makefile includes `variables.mk` which uses `load_vars.py`:

```makefile
# In variables.mk
NAME := $(shell $(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/load_vars.py name)
SRC_DIR := $(shell $(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/load_vars.py src_dir)
BUILD_DIR := $(shell $(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/load_vars.py build_dir)
OBJ_DIR := $(shell $(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/load_vars.py obj_dir)

PROCESSOR := $(shell $(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/load_vars.py development.processor)
PROGRAMMER := $(shell $(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/load_vars.py development.programmer)
```

## Available Variables

### Top-Level

| Variable | Example |
|----------|---------|
| `name` | `MC-200` |
| `hw_version` | `0.1` |
| `sw_version` | `0.1` |
| `src_dir` | `src` |
| `obj_dir` | `obj` |
| `build_dir` | `build` |
| `compiler_version` | `2.45` |
| `git_hash` | `abc123` |

### Profile Variables

Both `development` and `release` profiles inherit the same keys via `fix_env()`. Access with dot notation: `development.processor`, `release.processor`, etc.

| Key | Example | Default |
|-----|---------|---------|
| `processor` | `18F16Q41` | *(required)* |
| `programmer` | `Pickit4` | Family name (`Pickit4`, not `Pickit4-linux`); default `Pickit4` |
| `compiler` | `legacy` | `legacy` |
| `standard` | `c89` | `c89` |
| `float_size` | `24` | `32` |
| `double_size` | `24` | `32` |
| `defines` | `[DEVELOPMENT, SHELL_ENABLED]` | `[]` |
| `skip_rules` | `[src/os/shell/*]` | `[]` |

## Key Resolution and Inheritance

`project.py:fix_project()` normalizes `project.yaml` into a flat dict that
consumers (Makefiles, build scripts) can access without knowing the YAML
structure. The transform has two phases:

1. **Flatten `build_settings`** — keys under `build_settings` (e.g.
   `programmer`, `toolchain_options`, `development`, `release`) are hoisted
   to the top level, then `build_settings` is removed.

2. **Inherit into each profile** — `fix_env()` runs for both `development`
   and `release`. For each inheritable key, if the key is not set in the
   profile, it falls through to the top-level value, then to a hardcoded
   default. After both profiles are fixed, inheritable keys are stripped from
   the top level (via `pop_list`) so only the two profile dicts hold them.

### Which keys are project-level vs env-level

| Scope | Keys | Set by |
|-------|------|--------|
| Project-level | `name`, `src_dir`, `obj_dir`, `build_dir`, `compiler` | `set_default()` — never inherited, never popped |
| Env-level (inheritable) | `processor`, `programmer`, `toolchain_options`, `defines`, `skip_rules`, `compiler`, `standard`, `float_size`, `double_size` | `inherit()` inside `fix_env()` |

Project-level keys are always available at the top level. Env-level keys
live only in `development` and `release` after normalization.

### Adding a new env-level key

1. Add an `inherit('new_key', default)` call inside `fix_env()` in `project.py`.
2. Add the key to the table in `variables.md` with its default.
3. If the key should appear in the wizard output, add it to `configure.py`.

If you forget step 1, the key will be silently absent from the profile dicts
and any code accessing `env.new_key` will get `None` (or a `DotMap` AttributeError
under the `DotMap` wrapper used by `compile.py` / `release.py`).

## Default Values

The `project.py` module applies defaults for optional values:

```python
# From project.py
set_default('src_dir', 'src')
set_default('obj_dir', 'obj')
set_default('build_dir', 'build')
set_default('compiler', 'legacy')
set_default('compiler_version', None)  # desired XC8 version; None = use newest
set_default('standard', 'c89')
set_default('float_size', 32)
set_default('double_size', 32)
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Key found, value printed |
| 1 | Key not found |

Use in shell scripts:

```bash
PROC=$(python toolchain/scripts/load_vars.py development.processor)
if [ $? -eq 0 ]; then
    echo "Processor: $PROC"
else
    echo "Key not found"
fi
```