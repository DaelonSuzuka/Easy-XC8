# **************************************************************************** #
# Primary targets
	
# Build the project
compile: venv $(PROJECT_HEX)

# Upload the hex file to the target device
upload: venv
	$(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/upload.py

# Build the release binaries
release: venv
	$(VENV_PYTHON) -m cogapp --verbosity=1 -I$(TOOLCHAIN_DIR)/cogscripts -p "import cogutils as utils" @cogfiles.txt
	$(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/release.py

# program the release hex to a chip
program: venv
	$(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/program.py

# Scrape the compiler outputs for data about the build
reports: venv
	$(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/reports.py

# Remove the compiler outputs
clean:
ifeq ($(OS),Windows_NT)
	del /s /q $(BUILD_DIR)\* 1>nul
	del /s /q $(OBJ_DIR)\* 1>nul
else
	rm -rf $(BUILD_DIR)/*
	rm -rf $(OBJ_DIR)/*
endif
	
# run cppcheck
lint: venv
	$(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/cppcheck.py	

# 
project:
	$(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/project.py	