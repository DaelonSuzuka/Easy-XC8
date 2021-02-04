#!/usr/bin/env python3

import sys
import os
import json
from dotmap import DotMap
from project import load_project


current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "upload.json")
programmers = DotMap(json.loads(open(file_path).read()))


def program():
    project = load_project()
    env = project.release

    hexfile = f"{project.build_dir}/{project.name}"
    source = f'{hexfile}_v{project.sw_version}_{env.processor}.hex'

    programmer = programmers[env.programmer]
    command = [
        programmer['command'],
        programmer['target'] + env.processor,
        programmer['source'] + source,
        *programmer['flags']
    ]

    exit_code = os.system(" ".join(command))

    # clean up temp files
    for f in programmer.garbage:
        try:
            os.remove(f)
        except:
            pass

    sys.exit(exit_code)


if __name__ == "__main__":
    program()