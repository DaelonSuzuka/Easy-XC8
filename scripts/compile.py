#!/usr/bin/env python3

import sys
from pathlib import Path
from xc8 import Xc8
from xc8_cc import Xc8CC
from project import load_project
from dotmap import DotMap


def compile():
    project = DotMap(load_project())
    env = project.development
    sources = [f.as_posix() for f in Path(project.src_dir).rglob('*.c')]

    if env.compiler == 'legacy':
        command = Xc8(project, env, sources)
    else:
        command = Xc8CC(project, env, sources)

    result = command.run()

    # hexfile = f'{project.build_dir}/{project.name}.hex'
    # # add metadata to the hex file
    # contents = Path(hexfile).read_text()
    # contents = f';{env.processor}\n;{project.name}v{project.sw_version}\n;{project.git_hash}\n\n{contents}'
    # Path(hexfile).write_text(contents)

    sys.exit(result)


if __name__ == '__main__':
    compile()
