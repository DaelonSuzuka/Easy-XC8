#!/usr/bin/env python3

import sys
from pathlib import Path
from xc8 import Xc8
from project import load_project
from dotmap import DotMap


def release():
    project = DotMap(load_project())
    env = project.release
    sources = [f.as_posix() for f in Path(project.src_dir).rglob("*.c")]

    command = Xc8(project, env, sources)
    result = command.run()

    if result == 0:
        # rename the hex file 
        hexfile = f"{project.build_dir}/{project.name}"
        old_name = f'{hexfile}.hex'
        new_name = f'{hexfile}_v{project.sw_version}_{env.processor}.hex'
        Path(old_name).replace(new_name)

    sys.exit(result)


if __name__ == "__main__":
    release()