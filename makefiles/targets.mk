# **************************************************************************** #
# Primary targets
	
# Build the project
compile: venv $(PROJECT_HEX)

# Upload the hex file to the target device
upload: venv $(PROJECT_HEX) 
	$(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/upload.py

# Build the release binaries
release: venv
	$(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/release.py

# Scrape the compiler outputs for data about the build
reports: venv $(PROJECT_HEX) 
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

# generate doxygen output
docs:
	doxygen Doxyfile
	
# run cppcheck
lint: venv
	$(VENV_PYTHON) $(TOOLCHAIN_DIR)/scripts/cppcheck.py	