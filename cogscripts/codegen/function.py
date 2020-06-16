class Function():
    def __init__(self,
                 name='func',
                 return_type='void',
                 params='void',
                 body=None,
                 extern=False,
                 static=False,
                 ):
        self.name = name
        self.return_type = return_type
        if isinstance(params, str):
            self.params = params
        else:
            self.params = ', '.join(params)

        self.body = body
        self.extern = extern
        self.static = static

    def signature(self):
        if self.extern and self.static :
            raise Exception(f'conflicting options provided')

        signature = ''
        if self.extern:
            signature += 'extern '
        if self.static:
            signature += 'static '
        signature += f'{self.return_type} {self.name} ({self.params})'

        return signature

    def assemble(self):
        function = [self.signature()]
        if self.body and not self.extern:
            function.append('{')
            [function.append(line) for line in body]
            function.append('}')
        else:
            function.append(';')

        return function

    def declaration(self):
        return self.signature() + ';'

    def definition(self):
        function = [self.signature()]

        if self.body:
            function.append('{')
            [function.append(line) for line in body]
            function.append('}')
        return function

    def call(self, arguments):
        return f'{self.name}({",".join(arguments)})'

    def from_text(self, text):
        pass