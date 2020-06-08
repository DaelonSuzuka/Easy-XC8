# **************************************************************************** #
# General Make configuration

MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --warn-undefined-variables

# select shell 
ifeq ($(OS),Windows_NT)
SHELL = cmd
else
SHELL = bash
endif

# **************************************************************************** #
# Groudwork

# make sure the end user has told us the toolchain directory
ifndef TOOLCHAIN_DIR
$(error TOOLCHAIN_DIR is not set)
endif

# project settings are contained in PROJECT_FILE
PROJECT_FILE = project.yaml

# make sure PROJECT_FILE exists
ifeq (,$(wildcard ./project.yaml))
$(error $(PROJECT_FILE) does not exist! Please create a $(PROJECT_FILE))
endif

# **************************************************************************** #
# include the other makefile pieces

include toolchain/venv.mk
include toolchain/variables.mk
include toolchain/targets.mk
