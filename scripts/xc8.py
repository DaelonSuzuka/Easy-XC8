from pathlib import Path
import subprocess
from dependencies import scan_dependencies


class Xc8:
    def __init__(self, project, env, sources):
        self.command = ['xc8']
        flag = self.command.append

        flag(f"--CHIP={env.processor}")  # specify the processor
        flag(f"-O{project.build_dir}/{project.name}")  # location of final results
        flag(f"--OBJDIR={project.obj_dir}")  # intermediate file directory

        flag("--STACK=hybrid:auto:auto:auto")  # specify stack parameters
        flag("--FILL=0xffff")  # fill empty space in the hexfile with a pattern
        flag("--FLOAT=32")  # set floats to 32 bits
        flag("--DOUBLE=32")  # set doubles to 32 bits
        flag("--TIME")  # display compiler profiling information

        # flag("--STD=C89")

        # flag("--WARN=-9")
        # flag("--MSGDISABLE=373:off")  # implicit signed -> unsigned conversion
        # flag("--MSGDISABLE=752:off")  # conversion to shorter data type
        # flag("--MSGDISABLE=520:off")  # function is never called
        # flag("--MSGDISABLE=362:off")  # redundant &

        flag("-q")  # suppress the play-by-play of the compiler output

        # symbol definitions
        defines = [
            '__XC8_C89__',
            # '__XC8_C99__',
            # '__XC8_CC_C99__',
            '_XC_H_', # silence the header file warning telling me to include xc.h
            f'__PRODUCT_NAME__={project.name}',
            f'__PRODUCT_VERSION__={project.git_hash}',
            f'__PROCESSOR__={env.processor}',
            *env.defines,
        ]
        for symbol in defines:
            flag(f'-D{symbol}')

        # include paths
        includes = [
            project.src_dir,
            *[d.as_posix() for d in Path(project.src_dir).rglob("*") if d.is_dir()]
        ]
        for path in includes:
            flag(f'-I{path}')
        
        # source files
        sources = scan_dependencies(project, env, sources)
        for s in sources:
            flag(s)

    def run(self):
        cmd = ' '.join(self.command)
        return subprocess.call(cmd, shell=True)