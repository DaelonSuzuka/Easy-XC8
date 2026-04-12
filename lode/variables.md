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

# Get release programmer
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
| `git_hash` | `abc123` |

### Development Profile

| Variable | Example |
|----------|---------|
| `development.processor` | `18F16Q41` |
| `development.programmer` | `Pickit4` |
| `development.compiler` | `legacy` |
| `development.standard` | `c89` |

### Release Profile

| Variable | Example |
|----------|---------|
| `release.processor` | `18F16Q41` |
| `release.programmer` | `Pickit4` |
| `release.compiler` | `legacy` |

## Default Values

The `project.py` module applies defaults for optional values:

```python
# From project.py
set_default('src_dir', 'src')
set_default('obj_dir', 'obj')
set_default('build_dir', 'build')
set_default('compiler', 'legacy')
set_default('standard', 'c89')
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