class Function():
    def __init__(self,
                 name='func',
                 return_type='void',
                 params='void',
                 contents=None,
                 extern=False,
                 static=False,
                 ):
        self.name = name
        self.return_type = return_type
        if isinstance(params, str):
            self.params = params
        else:
            self.params = ', '.join(params)

        self.contents = []
        self.add_contents(contents)

        self.extern = extern
        self.static = static

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

    def signature(self):
        if self.extern and self.static :
            raise Exception(f'conflicting options provided')

        signature = ''
        if self.static:
            signature += 'static '
        signature += f'{self.return_type} {self.name} ({self.params})'

        return signature

    def assemble(self):
        function = [self.signature()]
        if self.contents and not self.extern:
            function.append('{')
            [function.append(line) for line in self.contents]
            function.append('}')
        else:
            function.append(';')

        return function

    def declaration(self, extern=False):
        declaration = ""
        if self.extern:
            declaration += 'extern '

        declaration += self.signature() + ';'

        return declaration

    def definition(self):
        function = [self.signature()]

        if self.contents:
            function.append('{')
            [function.append(line) for line in self.contents]
            function.append('}')
        return function

    def call(self, arguments):
        return f'{self.name}({",".join(arguments)})'

    def from_text(self, text):
        pass