import subprocess
from pathlib import Path

from skip import apply_skip_rules


class Xc8CC:
    def __init__(self, project, env, sources):
        self.command = ['xc8-cc']
        # self.command = ['C:/Microchip/xc8/v3.10/bin/xc8-cc']
        flag = self.command.append

        flag(f'-mcpu={env.processor}')
        # flag(f'-mdfp="C:/Microchip/packs/Microchip.PIC18F-K_DFP.1.15.303/xc8"')

        flag(f'-std={env.standard}')
        flag(f'-o {project.build_dir}/{project.name}.hex')

        flag('-mstack=hybrid:auto:auto:auto')  # specify stack parameters

        flag('-O2')  # optimize for size

        # symbol definitions
        defines = [
            f'__XC8_CC_{env.standard.upper()}__',
            '_XC_H_',  # silence the header file warning telling me to include xc.h
            f'__PRODUCT_NAME__={project.name}',
            f'__PRODUCT_VERSION__={project.git_hash}',
            f'__PROCESSOR__={env.processor}',
            *env.defines,
        ]
        for symbol in defines:
            flag(f'-D{symbol}')

        # # pass flags to compiler
        # [flag(cflag) for cflag in project.compiler_flags]
        # # pass flags to the linker
        # [flag(f'-Wl,{link_flag}') for link_flag in project.linker_flags]

        # include paths
        includes = [
            project.src_dir,
            *[d.as_posix() for d in Path(project.src_dir).rglob('*') if d.is_dir()],
        ]
        for path in includes:
            flag(f'-I{path}')

        # source files
        sources = apply_skip_rules(project, env, sources)
        for s in sources:
            flag(s)

    def run(self):
        cmd = ' '.join(self.command)
        return subprocess.call(cmd, shell=True)
