from pathlib import Path
import subprocess
import os
from .scan_deps import scan_dependencies


class CommandBuilder:
    def __init__(self, command):
        self.command = ['xc8']

    def flag(self, text):
        self.command.append(text)

    def add_define(self, symbol):
        self.flag(f'-D{symbol}')

    def add_include_path(self, path):
        self.flag(f'-I{path}')

    def assemble(self):
        return " ".join(self.command)

    def run(self):
        os.system(self.assemble())


class Xc8(CommandBuilder):
    def __init__(self, project):
        super().__init__('xc8')

        self.flag(f"--CHIP={project.processor}")  # specify the processor
        self.flag(f"-O{project.build_dir}/{project.name}")  # location of final results
        self.flag(f"--OBJDIR={project.obj_dir}")  # intermediate file directory
        
        self.flag("--STACK=hybrid:auto:auto:auto")  # specify stack parameters
        self.flag("--FILL=0xffff")  # fill empty space in the hexfile with a pattern
        self.flag("--FLOAT=32")  # set floats to 32 bits
        self.flag("--DOUBLE=32")  # set doubles to 32 bits
        self.flag("--TIME")  # display compiler profiling information

        # flag("--WARN=-9")
        # flag("--MSGDISABLE=373:off")  # implicit signed -> unsigned conversion
        # flag("--MSGDISABLE=752:off")  # conversion to shorter data type
        # flag("--MSGDISABLE=520:off")  # function is never called
        # flag("--MSGDISABLE=362:off")  # redundant &

        self.flag("-q")  # suppress the play-by-play of the compiler output

        defines = [
            '__XC8_CC_C89__',
            f'__PRODUCT_NAME__={project.name}',
            f'__PRODUCT_VERSION__={project.git_hash}',
            *project.defines,
        ]
        for d in defines:
            self.add_define(d)

        includes = [
            project.src_dir,
            *[d.as_posix() for d in Path(project.src_dir).rglob("*") if d.is_dir()]
        ]
        for i in includes:
            self.add_include_path(i)
        
        project.sources = [s for s in project.sources if s.endswith('.c')]

        if project.prune_dependencies:
            project.sources = scan_dependencies(project, project.sources)

        for s in project.sources:
            self.flag(s)