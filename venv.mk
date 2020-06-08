# **************************************************************************** #
# python venv settings
VENV_NAME := .venv

ifeq ($(OS),Windows_NT)
	VENV_DIR := $(TOOLCHAIN_DIR)\$(VENV_NAME)\$(OS)
	VENV := $(VENV_DIR)\Scripts
	PYTHON := python
	VENV_PYTHON := $(VENV)\$(PYTHON)
	VENV_MARKER := $(VENV)\.initialized-with-Makefile.venv
else
	VENV_DIR := $(TOOLCHAIN_DIR)/$(VENV_NAME)/$(OS)
	VENV := $(VENV_DIR)/bin
	PYTHON := python3
	VENV_PYTHON := $(VENV)/$(PYTHON)
	VENV_MARKER := $(VENV)/.initialized-with-Makefile.venv
endif

# Add this as a requirement to any make target that relies on the venv
.PHONY: venv
venv: $(VENV_DIR)

# Create the venv if it doesn't exist
$(VENV_DIR):
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r $(TOOLCHAIN_DIR)/requirements.txt

# deletes the venv
clean_venv:
ifeq ($(OS),Windows_NT)
	rd /s /q $(VENV_DIR)
else
	rm -rf $(VENV_DIR)
endif

# deletes the venv and rebuilds it
reset_venv: clean_venv venv