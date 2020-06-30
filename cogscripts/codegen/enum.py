class Enum:
    def __init__(self,
                 name='',
                 values=[],
                 prefix='',
                 postfix='',
                 explicit=False,
                 typedef=False):
        self.name = name
        self.values = values
        self.prefix = prefix
        self.postfix = postfix
        self.explicit = explicit
        self.typedef = typedef

    def assemble(self):
        enum = []

        if self.typedef:
            enum.append('typedef enum {')
        else:
            enum.append(f'enum {self.name} {{')

        if isinstance(self.values, list):
            if self.explicit:
                [
                    enum.append(f'{self.prefix}{v}{self.postfix} = {i},')
                    for i, v
                    in enumerate(self.values)
                ]
            else:
                [
                    enum.append(f'{self.prefix}{v}{self.postfix},')
                    for v
                    in self.values
                ]
        elif isinstance(self.values, dict):
            [
                enum.append(
                    f'{self.prefix}{v}{self.postfix} = {self.values[v]},')
                for v
                in self.values
            ]

        if self.typedef:
            enum.append(f'}} {self.name};')
        else:
            enum.append('};')

        return enum
