# Code Generation with Cog

The build system uses [cog](https://nedbatchelder.com/code/cog/) to auto-generate C code from Python. Code generation runs during `make compile` before the compiler.

## Key Principle

**Project-specific codegen lives in the project, NOT in the toolchain.**

```
project-root/
├── project.yaml          # Build configuration
├── cogfiles.txt          # Files to process (project-specific)
├── pinmap.py            # Pin definitions (project-specific)
└── src/
    └── backlight.c      # Cog blocks for lookup tables
```

The toolchain provides helper modules in `cogscripts/codegen/` but your project owns its data and generation logic.

## Cogfiles

List files to process in `cogfiles.txt` at project root:

```
src/pins.h -r
src/pins.c -r
src/os/judi/hash.h -r
src/backlight.c -r
```

The `-r` flag means "replace generated code in place."

## Writing a Cog Block

Cog blocks live inside C/C++ comments with special markers:

```c
/* [[[cog
    # Python code here
    cog.outl("// Generated code")
]]] */

// Generated code appears here

// [[[end]]]
```

**How it works:**
1. `[[[cog` starts the Python block
2. Python runs during build
3. `cog.outl()` writes output
4. Output appears between `]]] */` and `// [[[end]]]`
5. `[[[end]]]` marks where generated code ends

## Example 1: Pin Generation

The `pinmap.py` file defines your hardware:

```python
# pinmap.py (in project root)
class Pin:
    button = ['input', 'gpio', 'button']
    uart_tx = ['output', 'pps']
    uart_rx = ['input', 'pps']
    analog_in = ['input', 'analog']

common = {
    'A2': ('BRIGHTNESS_PIN', Pin.analog_in),
    'B5': ('DEBUG_RX_PIN', Pin.uart_rx),
    'B7': ('DEBUG_TX_PIN', Pin.uart_tx),
    'C3': ('SCALE_BUTTON_PIN', Pin.button),
}

development = {}  # Dev-only pins
release = {}      # Release-only pins
```

Then in your C files, use cog to generate:

```c
/* pins.h */
/* [[[cog
    from codegen import fmt; import pins
    cog.outl(fmt(pins.pin_declarations()))
]]] */

// GPIO read functions
extern bool read_SCALE_BUTTON_PIN(void);
extern bool read_MODE_BUTTON_PIN(void);

// Button count
#define NUMBER_OF_BUTTONS 2
// [[[end]]]
```

```c
/* pins.c */
/* [[[cog
    from codegen import fmt; import pins
    cog.outl(fmt(pins.pins_init()))
]]] */

void pins_init(void) {
    // BRIGHTNESS_PIN
    TRISAbits.TRISA2 = 1;
    ANSELAbits.ANSELA2 = 1;
    // ... more pins
}
// [[[end]]]
```

## Example 2: Lookup Tables

Generate data tables at build time from Python calculations:

```c
/* backlight.c */

/* [[[cog
    # White temperature to RGB lookup table
    # Uses Tanner Helland's algorithm for Kelvin -> RGB
    
    import math
    
    TEMP_COOL_K = 6500.0
    TEMP_WARM_K = 2200.0
    TABLE_SIZE = 32
    
    def kelvin_to_rgb(temp_k):
        temp = temp_k / 100.0
        # ... algorithm here ...
        return (int(red), int(green), int(blue))
    
    cog.outl('// White temperature table: {r, g, b}')
    cog.outl('static const uint8_t white_table[][3] = {')
    for i in range(TABLE_SIZE):
        t = i / (TABLE_SIZE - 1)
        temp = TEMP_COOL_K - t * (TEMP_COOL_K - TEMP_WARM_K)
        r, g, b = kelvin_to_rgb(temp)
        cog.outl(f'    {{{r}, {g}, {b}}},  // {int(temp)}K')
    cog.outl('};')
]]] */

// White temperature table: {r, g, b}
static const uint8_t white_table[][3] = {
    {255, 199, 176},  // 6500K
    {255, 196, 183},  // 6367K
    // ... 32 entries ...
};
// [[[end]]]
```

**Why do this?** Complex calculations become compile-time constants. No runtime overhead.

## Example 3: Hash Enum Generation

Generate enums and hash tables from strings found in code:

```c
/* hash.h */
/* [[[cog
    import codegen as code
    from pathlib import Path
    
    # Find all hash_ keys in messages.c
    search_pattern = r'(?<=hash_).*?(?=[:)])'
    strings = utils.search('src/usb/messages.c', search_pattern)
    strings.append('message_id')
    
    # Build enum with hash_ prefix
    prefix = 'hash_'
    keys = [f'{prefix}{s}' for s in strings]
    
    enum = code.Enum('hash_value_t', values=keys, typedef=True, explicit=True)
    cog.outl(enum.declare())
]]] */

typedef enum {
    hash_message_id = 0,
    hash_type = 1,
    hash_value = 2,
    // ...
} hash_value_t;
// [[[end]]]
```

## Codegen Module Reference

The toolchain provides helper modules in `cogscripts/codegen/`:

### `from codegen import Enum`

Generate C enums from Python lists:

```python
from codegen import Enum

# Simple enum
e = Enum('color_t', values=['RED', 'GREEN', 'BLUE'], typedef=True)
cog.outl(e.assemble())
# typedef enum { RED, GREEN, BLUE, } color_t;

# Explicit values
e = Enum('state_t', values=['INIT', 'RUNNING', 'DONE'], 
         explicit=True, typedef=True)
cog.outl(e.assemble())
# typedef enum { INIT = 0, RUNNING = 1, DONE = 2, } state_t;

# Dict values
e = Enum('flags_t', values={'FLAG_A': 0x01, 'FLAG_B': 0x02}, typedef=True)
# typedef enum { FLAG_A = 0x01, FLAG_B = 0x02, } flags_t;
```

### `from codegen import Struct`

Generate C structs:

```python
from codegen import Struct

s = Struct('config_t', ['uint8_t id', 'char name[16]', 'uint32_t value'])
cog.outl(s.assemble())
# struct config_t { uint8_t id; char name[16]; uint32_t value; };
```

### `from codegen import Function`

Generate function declarations:

```python
from codegen import Function

f = Function('init', return_type='void', params='uart_config_t *cfg', 
             contents=['cfg->baud = 9600;', 'cfg->mode = 0;'])
cog.outl(f.declaration())  # void init(uart_config_t *cfg);
cog.outl(f.definition())   # void init(...) { ... }
```

### `from codegen import fmt`

Format output with clang-format:

```python
from codegen import fmt

code = ['int main(void) {', '    init();', '    return 0;', '}']
cog.outl(fmt(code))  # Formatted with proper indentation
```

## fmt() and clang-format

The `fmt()` function pipes output through `clang-format` for consistent formatting:

```python
from codegen import fmt
cog.outl(fmt(pins.pin_declarations()))
```

Ensure `clang-format` is in your PATH.

## Running Codegen

Codegen runs automatically during `make compile`:

```makefile
# In targets.mk
compile: venv $(PROJECT_HEX)

$(PROJECT_HEX): $(PROJECT_FILES)
    $(VENV_PYTHON) -m cogapp --verbosity=1 -I$(TOOLCHAIN_DIR)/cogscripts -p "import cogutils as utils" @cogfiles.txt
    $(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/compile.py
```

To run codegen only (no compile):
```bash
python -m cogapp -Itoolchain/cogscripts @cogfiles.txt
```

## Dev/Release Pin Variants

Pins can differ between development and production hardware:

```python
# pinmap.py
development = {
    'B5': ('DEBUG_RX_PIN', Pin.uart_rx),  # Dev board uses B5
}

release = {
    'C0': ('DEBUG_RX_PIN', Pin.uart_rx),  # Production uses C0
}
```

The codegen generates conditional initialization:

```c
void pins_init(void) {
    // DEBUG_RX_PIN
    #ifdef DEVELOPMENT
    TRISBbits.TRISB5 = 1;
    #endif
    #ifdef RELEASE
    TRISCbits.TRISC0 = 1;
    #endif
}
```