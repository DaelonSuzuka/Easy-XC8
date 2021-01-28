from pathlib import Path


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

    # pass flags to compiler
    [flag(cflag) for cflag in project.compiler_flags]
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