#!/usr/bin/env python3

import os
import sys
import yaml
from dotmap import DotMap
from pathlib import Path
import subprocess


# ------------------------------------------------------------------------------


def xc8_cc(project, standard="C99"):
    """Builds the firmware using xc8-cc command in c99 mode."""
    command = ["xc8-cc"]
    flag = command.append

    flag(f"-mcpu={project.processor}")
    flag(f"-std={standard}")
    flag(f"-o {project.build_dir}/{project.name}.hex")

    # define macros to allow checking compiler version in code
    if standard == "C99":
        flag("-D__XC8_CC_C99__")
    else:
        flag("-D__XC8_CC_C89__")

    # pass flags to the linker
    [flag(f"-Wl,{link_flag}") for link_flag in project.linker_flags]
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


def xc8(project, files):
    """Builds the firmware using xc8 command in c89 mode."""
    command = ["xc8"]
    flag = command.append

    flag(f"--CHIP={project.processor}")  # specify the processor
    flag(f"-O{project.build_dir}/{project.name}")  # location of final results
    flag(f"--OBJDIR={project.obj_dir}")  # intermediate file directory

    # define macro to allow checking compiler version in code
    flag("-D__XC8_CC_C89__")

    # define macro to check the project name
    flag(f'-D__PRODUCT_NAME__={project.name}')

    # define macro to get which commit this code came from
    flag(f'-D__PRODUCT_VERSION__={project.git_hash}')

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
    [flag(f) for f in files]

    return " ".join(command)

def scan_deps(files):
    deps = {f: [] for f in files}

    def strip_name(name):
        return name.split('/')[-1][:-2]

    names = {strip_name(f): f for f in files}

    for f in files:
        with open(f) as file:
            for line in file.readlines():
                if line.startswith('#include "'):
                    name = strip_name(line[len('#include "'): -2])
                    deps[f].append(name)

    # walk the dependency tree
    def check_deps(file):
        used = [strip_name(file)]
        # print(file, deps[file])
        for dep in deps[file]:
            used.append(dep)
            if dep != strip_name(file) and dep in names:
                used.extend(check_deps(names[dep]))
        # print(used)
        return used

    used_files = check_deps('src/main.c')

    # special cases
    if 'uart' in used_files:
        used_files.append('uart1')
        used_files.append('uart2')

    return [names[f] for f in set(used_files) if f in names]


def main(project):
    # get the short hash and other status info of the repo
    cmd = 'git describe --always --long --dirty --tags'
    git_hash = subprocess.run(cmd, stdout=subprocess.PIPE)
    project.git_hash = git_hash.stdout.decode().replace('\n', '').replace('-', ':')

    files = [f.as_posix() for f in Path(project.src_dir).rglob("*.c")]
    deps = scan_deps(files)

    if project.compiler == 'xc8-cc':
        command = xc8_cc(project)
    else:
        command = xc8(project, deps)

    try:
        result = os.system(command)
    except KeyboardInterrupt:
        result = 1
    sys.exit(result)


if __name__ == "__main__":
    project = DotMap(yaml.full_load(open("project.yaml").read()))

    main(project)
