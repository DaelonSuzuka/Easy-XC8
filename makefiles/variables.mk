# **************************************************************************** #

# Project name 
PROJECT := $(shell $(PYTHON) $(TOOLCHAIN_DIR)/scripts/load_vars.py name)

# Source file directory
SRC_DIR := $(shell $(PYTHON) $(TOOLCHAIN_DIR)/scripts/load_vars.py src_dir)

# Output directories
BUILD_DIR := $(shell $(PYTHON) $(TOOLCHAIN_DIR)/scripts/load_vars.py build_dir)
OBJ_DIR := $(shell $(PYTHON) $(TOOLCHAIN_DIR)/scripts/load_vars.py obj_dir)

# Every C source file and header
PROJECT_FILES := $(shell $(PYTHON) $(TOOLCHAIN_DIR)/scripts/find_source_files.py $(SRC_DIR))

# The project config file
PROJECT_FILES += $(PROJECT_FILE)

# The build script
PROJECT_FILES += $(TOOLCHAIN_DIR)/scripts/build.py

# **************************************************************************** #

# The hex file we're trying to end up with 
PROJECT_HEX = $(BUILD_DIR)/$(PROJECT).hex 

# The build rules for the hex file
$(PROJECT_HEX): $(PROJECT_FILES) | $(OBJ_DIR) $(BUILD_DIR)
	$(VENV_PYTHON) -m cogapp -I$(TOOLCHAIN_DIR)/cogscripts -p "import cogutils as utils" @cogfiles.txt
	$(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/build.py

# **************************************************************************** #
# creates output directories if they're missing

ifeq ($(OS),Windows_NT)
MK_DIR := -md
else
MK_DIR := mkdir -p
endif

$(OBJ_DIR):
	$(MK_DIR) $(OBJ_DIR)

$(BUILD_DIR):
	$(MK_DIR) $(BUILD_DIR)