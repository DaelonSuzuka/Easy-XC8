#!/usr/bin/env python3

import os
import sys
import yaml
from dotmap import DotMap
from pathlib import Path


# ------------------------------------------------------------------------------

"""
# Linter(s)
# Linting and static analysis are very important tools for maintaining code
# quality. If we have access to any of these tools that work on our target code,
# we should run them automatically on every build.

# Cppcheck is a free C/C++ static analysis tool.
# http://cppcheck.sourceforge.net/
"""

def cpp_check(project):
    command = ["cppcheck"]
    flag = command.append

    # Tell cppcheck which C standard to check against
    flag("--std=c89")
    
    # Tell cppcheck to run all test categories 
    flag("--enable=all")

    # tell cppcheck where to look for includes
    flag("-I C:/Microchip/xc8/v2.20/pic/include")
    flag("-I C:/Microchip/xc8/v2.20/pic/include/c90")
    flag("-I C:/Microchip/xc8/v2.20/pic/include/proc")

    # specify include directories
    flag(f"-I{project.src_dir}")
    [flag(f"-I{d.as_posix()}") for d in Path(project.src_dir).rglob("*") if d.is_dir()]

    # Allow that Cppcheck reports even though the analysis is inconclusive.
    flag("--inconclusive")
    # Force checking of all #ifdef configurations. This takes significantly longer!
    flag("--force")
    # Enable inline suppressions in the source 
    flag("--inline-suppr")
    # 8bit AVR is the most similar platform to PIC18
    flag("--platform=avr8")
    # Do not show progress reports
    flag("-q")
    
    # Specify the number of threads to use
    # Enabling multithreading disables unusedFunction check.
    flag("-j 6")

    # Check cppcheck configuration. The normal code analysis is disabled.
    # This option can be used to confirm that cppcheck sees every header file.
    # flag("--check-config")

    # Add the list of files
    [flag(f.as_posix()) for f in Path(project.src_dir).rglob("*.c")]
    
    return " ".join(command)

def main(project):
    command = cpp_check(project)

    try:
        result = os.system(command)
    except KeyboardInterrupt:
        result = 1
    sys.exit(result)


if __name__ == "__main__":
    project = DotMap(yaml.full_load(open("project.yaml").read()))

    main(project)