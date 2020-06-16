from pathlib import Path
from codegen.utils import hrule, fmt


class Header():
    name = ''
    guard_string = ''
    contents = []
    includes = []

    def __init__(self,
                 name='',
                 contents=[],
                 includes=[],
                 use_include_guard=True,
                 ):
        self.set_name(name)
        self.add_contents(contents)
        self.add_includes(includes)
        self.use_include_guard = use_include_guard

    def set_name(self, name):
        self.name = name
        self.guard_string = '_' + \
            Path(name).name.replace('.', '_').upper() + '_'

    def add_includes(self, includes=[]):
        if includes:
            if isinstance(includes, str):
                self.includes.append(f'#include {includes}')
            elif isinstance(includes, list):
                [self.includes.append(f'#include {i}') for i in includes]
            self.includes.append('')

    def add_contents(self, contents=[]):
        if isinstance(contents, str):
            self.contents.append(contents)
            return

        for c in contents:
            if isinstance(c, str):
                self.contents.append(c)
            else:
                for c2 in c:
                    if isinstance(c2, str):
                        self.contents.append(c2)

            self.contents.append('\n')

    def erase_contents(self):
        self.contents = []

    def assemble(self):
        header = []

        if self.use_include_guard:
            header.extend([
                f'#ifndef {self.guard_string}',
                f'#define {self.guard_string}',
                '',
            ])

        if self.includes:
            header.extend(self.includes)

        header.extend([
            hrule(),
            '',
        ])
        header.extend(self.contents)

        if self.use_include_guard:
            header.extend([
                '',
                f'#endif /* {self.guard_string} */',
            ])

        return fmt(header)

    def write(self):
        with open(self.name, 'w') as f:
            f.write(self.assemble())
