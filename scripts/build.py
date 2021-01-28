#!/usr/bin/env python3

from pathlib import Path
from xc8 import Xc8
from project import load_project


def compile():
    project = load_project()
    env = project.development
    sources = [f.as_posix() for f in Path(project.src_dir).rglob("*.c")]

    command = Xc8(project, env, sources)
    command.run()


if __name__ == "__main__":
    compile()