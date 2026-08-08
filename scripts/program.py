#!/usr/bin/env python3

import sys
import os
from pathlib import Path

from project import load_project
from programmers import resolve_programmer


def program():
    project = load_project()
    # Programs the release hex — named with version + processor for the shop
    # bulk programmer. For local dev board uploads use `make upload` (upload.py).
    env = project["release"]

    hexfile = f"{project['build_dir']}/{project['name']}"
    source = f"{hexfile}_v{project['sw_version']}_{env['processor']}.hex"

    name = env.get("programmer") or project.get("programmer")
    programmer = resolve_programmer(name)

    # Match upload.py: ipecmd on posix wants an absolute hex path
    source_arg = str(Path(source).absolute()) if os.name != "nt" else source

    command = [
        programmer["command"],
        programmer["target"] + env["processor"],
        programmer["source"] + source_arg,
        *programmer["flags"],
    ]

    print(f"program: {programmer['name']} ({programmer['platform']}) → {programmer['command']}")
    exit_code = os.system(" ".join(command))

    for f in programmer["garbage"]:
        try:
            os.remove(f)
        except OSError:
            pass

    sys.exit(exit_code)


if __name__ == "__main__":
    program()
