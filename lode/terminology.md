# Terminology

Domain-specific terms used in the build system.

## Compiler Terms

- **XC8** - Microchip's C compiler for PIC18 architecture
- **Legacy compiler** - XC8 v2.x using `xc8` command
- **Clang compiler** - XC8 v3.x using `xc8-cc` command

## Build Terms

- **Development Build** - Firmware with full debugging features (shell, logging, JUDI)
- **Release Build** - Production firmware with minimal features
- **Skip Rules** - Regex patterns to exclude files from release builds

## Code Generation Terms

- **Cog** - Python code generator ([nedbatchelder.com/code/cog](https://nedbatchelder.com/code/cog/))
- **Cogfile** - File processed by cog; listed in `cogfiles.txt`
- **pinmap.py** - Python file defining pin assignments
- **PPS_INPUT/PPS_OUTPUT** - Macros for peripheral pin selection

## Configuration Terms

- **project.yaml** - Project configuration file (name, version, build settings)
- **upload.json** - Programmer command mappings