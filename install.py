#!/usr/bin/env python3

from pathlib import Path


makefile_body = """# **************************************************************************** #
# General Make configuration

# This suppresses make's command echoing. This suppression produces a cleaner output. 
# If you need to see the full commands being issued by make, comment this out.
MAKEFLAGS += -s

# **************************************************************************** #
# Include toolchain

# define the toolchain directory
TOOLCHAIN_DIR = toolchain

# include the toolchain makefile
include $(TOOLCHAIN_DIR)/easy_xc8.mk"""

project_path = Path(__file__).absolute().parent.parent

# check if the Makefile exists
makefile_path = Path(project_path, "Makefile")
if not makefile_path.exists():
    print("Your project's Makefile is missing, creating one from template...")
    with open(makefile_path, 'w') as f:
        f.write(makefile_body)