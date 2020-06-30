from pathlib import Path
from .utils import hrule, fmt


class SourceFile:
    def __init__(self, name='', contents=[], includes=[]):
        self.contents = []
        self.includes = []
        self.name = name
        self.add_contents(contents)
        self.add_includes(includes)

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
        text = []

        if self.includes:
            text.extend(self.includes)

            text.extend([
                hrule(),
                '',
            ])

        text.extend(self.contents)

        return fmt(text)

    def write(self):
        with open(self.name, 'w') as f:
            f.write(self.assemble())