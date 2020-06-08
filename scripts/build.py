#!/usr/bin/env python3

import os
import sys
import yaml
from dotmap import DotMap
from pathlib import Path

# ------------------------------------------------------------------------------


def xc8_cc(project, standard="C99"):
    """Builds the firmware using xc8-cc command in c99 mode."""
    command = ["xc8-cc"]
    flag = command.append

    flag(f"-mcpu={project.target}")
    flag(f"-std={standard}")
    flag(f"-o {project.build_dir}/{project.name}.hex")

    # pass flags to the linker
    [flag(f"-W1,{link_flag}") for link_flag in project.linker_flags]
    # tell the compiler to define preprocessor symbols
    [flag(f"-D{symbol}") for symbol in project.defines]
    # specify include directories
    flag(f"-I{project.src_dir}")
    [flag(f"-I{d.as_posix()}") for d in Path(project.src_dir).rglob("*") if d.is_dir()]

    flag("-mstack=hybrid:auto:auto:auto")  # specify stack parameters

    # this MUST be last
    # specify "*.c" as compilation targets
    files = [f.as_posix() for f in Path(project.src_dir).rglob("*.c")]
    # move main.c to the front of the list
    main = [f for f in files if "main.c" in f][0]
    files.insert(0, files.pop(files.index(main)))

    [flag(f) for f in files]

    return " ".join(command)


def xc8(project):
    """Builds the firmware using xc8 command in c89 mode."""
    command = ["xc8"]
    flag = command.append

    flag(f"--CHIP={project.target}")  # specify the processor
    flag(f"-O{project.build_dir}/{project.name}")  # location of final results
    flag(f"--OBJDIR={project.obj_dir}")  # intermediate file directory

    # pass flags to the linker
    [flag(f"-L{link_flag}") for link_flag in project.linker_flags]
    # tell the compiler to define preprocessor symbols
    [flag(f"-D{symbol}") for symbol in project.defines]
    # specify include directories
    flag(f"-I{project.src_dir}")
    [flag(f"-I{d.as_posix()}") for d in Path(project.src_dir).rglob("*") if d.is_dir()]

    flag("--STACK=hybrid:auto:auto:auto")  # specify stack parameters
    flag("--FILL=0xffff")  # fill empty space in the hexfile with a pattern
    flag("--FLOAT=32")  # set floats to 32 bits
    flag("--DOUBLE=32")  # set doubles to 32 bits
    flag("--TIME")  # display compiler profiling information

    # flag("--WARN=-9")
    # flag("--MSGDISABLE=373:off")  # implicit signed -> unsigned conversion
    # flag("--MSGDISABLE=752:off")  # conversion to shorter data type
    # flag("--MSGDISABLE=520:off")  # function is never called
    # flag("--MSGDISABLE=362:off")  # redundant &

    flag("-q")  # suppress the play-by-play of the compiler output

    # this MUST be last
    # specify "*.c" as compilation targets
    [flag(f.as_posix()) for f in Path(project.src_dir).rglob("*.c")]

    return " ".join(command)


def main(project):
    command = xc8(project)
    # command = xc8_cc(project)

    try:
        result = os.system(command)
    except KeyboardInterrupt:
        result = 1
    sys.exit(result)


if __name__ == "__main__":
    project = DotMap(yaml.full_load(open("project.yaml").read()))

    main(project)
