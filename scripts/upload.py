#!/usr/bin/env python3

import os
import sys
import argparse
from pathlib import Path

from project import load_project
from programmers import resolve_programmer

# ------------------------------------------------------------------------------


def assemble_upload_command(programmer, args):
    command = []
    add = command.append

    add(programmer["command"])
    add(programmer["target"] + args.target)

    # ipecmd on linux requires absolute path
    add(programmer["source"] + str(Path(args.source).absolute()))

    for flag in programmer["flags"]:
        add(flag)

    return " ".join(command)


def main(programmer, args):
    command = assemble_upload_command(programmer, args)
    print(f"upload: {programmer['name']} ({programmer['platform']}) → {programmer['command']}")

    exit_code = os.system(command)

    for f in programmer["garbage"]:
        try:
            os.remove(f)
        except OSError:
            pass

    sys.exit(exit_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    arg = parser.add_argument

    project = load_project()
    # Always uses development profile — upload is for local dev boards/interposers.
    # Release hexes go to the shop via `make program` (program.py, release profile).
    source = f"{project['build_dir']}/{project['name']}.hex"
    arg("-t", "--target", default=project["development"]["processor"])
    arg("-s", "--source", default=source)
    arg("-p", "--programmer", default=project["development"].get("programmer") or project.get("programmer"))

    args = parser.parse_args()
    main(resolve_programmer(args.programmer), args)
