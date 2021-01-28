#!/usr/bin/env python3

import os
from pathlib import Path
from xc8 import Xc8
from project import load_project


def release():
    project = load_project()
    env = project.release
    sources = [f.as_posix() for f in Path(project.src_dir).rglob("*.c")]

    command = Xc8(project, env, sources)
    command.run()

    # rename the hex file 
    hexfile = f"{project.build_dir}/{project.name}"
    old_name = f'{hexfile}.hex'
    new_name = f'{hexfile}_v{project.sw_version}_{env.processor}.hex'
    os.rename(old_name, new_name)


if __name__ == "__main__":
    release()