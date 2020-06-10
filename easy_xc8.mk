# **************************************************************************** #
# General Make configuration

MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --warn-undefined-variables

.ONESHELL:

# select shell 
ifeq ($(OS),Windows_NT)
SHELL = cmd
else
SHELL = bash
endif

# **************************************************************************** #
# Groundwork

# make sure the end user has told us the toolchain directory
ifndef TOOLCHAIN_DIR
$(error TOOLCHAIN_DIR is not set)
endif

# project settings are contained in PROJECT_FILE
PROJECT_FILE = project.yaml

# make sure PROJECT_FILE exists
ifeq (,$(wildcard ./$(PROJECT_FILE)))
$(warning $(PROJECT_FILE) does not exist! Run "make configure" to create it.)
endif

# run configuration wizard
config: venv
	$(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/configure.py	

# **************************************************************************** #
# include the other makefile pieces

# always include the venv helper file
include $(TOOLCHAIN_DIR)/makefiles/venv.mk

# only include the other makefiles if the PROJECT_FILE file exists
ifneq (,$(wildcard ./$(PROJECT_FILE)))
include $(TOOLCHAIN_DIR)/makefiles/variables.mk
include $(TOOLCHAIN_DIR)/makefiles/targets.mk
else
$(warning Makefile targets are disabled because $(PROJECT_FILE) doesn't exist!)
endif
