#!/usr/bin/env python3

import os
from subprocess import Popen, PIPE, check_output
from pathlib import Path
import codegen as code


# ------------------------------------------------------------------------------


class Gperf:
    def __init__(self,
                 strings=[],
                 struct=None,
                 # command line options
                 iterations=100,
                 random=True,
                 no_strlen=True,
                 # .gperf file declarations
                 omit_struct_type=False,
                 enum=False,
                 readonly_tables=True,
                 global_table=True,
                 ignore_case=False,
                 compare_strncmp=False,
                 # postprocessing options
                 remove_line_directives=True,
                 use_stdint=True,
                 remove_keywords=True,
                 struct_typedef=True,
                 ):
        self.strings = strings
        if struct:
            self.struct = struct

        # options used to call gperf
        self.iterations = iterations
        self.random = random
        self.no_strlen = no_strlen

        # declarations for the .gperf file
        self.declarations = []
        if struct:
            self.declarations.append('%struct-type')
        if omit_struct_type:
            self.declarations.append('%omit-struct-type')
        if enum:
            self.declarations.append('%enum')
        if readonly_tables:
            self.declarations.append('%readonly-tables')
        if global_table:
            self.declarations.append('%global-table')
        if ignore_case:
            self.declarations.append('%ignore-case')
        if compare_strncmp:
            self.declarations.append('%compare-strncmp')

        # postprocessing options
        self.remove_line_directives = remove_line_directives
        self.overwrite_list = {}
        if use_stdint:
            self.overwrite_list.update({
                'unsigned int': 'uint16_t',
                'unsigned char': 'uint8_t',
                'size_t': 'uint8_t',
            })
        if remove_keywords:
            self.overwrite_list.update({
                'register': '',
                '__inline': '',
                'inline': '',
            })

    def command(self, file):
        cmd = ['gperf']
        if self.iterations:
            cmd.append(f'-m {self.iterations}')
        if self.random:
            cmd.append('-r')
        if self.no_strlen:
            cmd.append('-n')
        cmd.append(file)
        return ' '.join(cmd)

    def create_temp_file(self):
        with open('strings.gperf', 'w') as f:
            def outl(string):
                f.write(string + '\n')

            outl('\n'.join(self.declarations))
            outl('\n'.join(self.struct))
            outl("%%")

            # finally, add the strings
            f.write("\n".join(self.strings))

    def remove_temp_file(self):
        os.remove('strings.gperf')

    def run(self):
        self.create_temp_file()
        result = check_output(self.command(file='strings.gperf')).decode()
        result = result.split('\r\n')
        self.remove_temp_file()

        if self.remove_line_directives:
            result = [x for x in result if '#line' not in x]

        def overwrite(s1, s2=''):
            return [x.replace(s1, s2) for x in result]

        for k in self.overwrite_list:
            result = overwrite(k, self.overwrite_list[k])

        result = code.fmt(result)
        result = result.replace('}};', '},};')
        result = code.fmt(result)

        return str(result)
