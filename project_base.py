import subprocess
import sys
import json
from hashlib import md5


class MyList(list):
    def __iadd__(self, x):
        if isinstance(x, list):
            self.extend(x)
        else:
            self.append(x)
        return self


# grab the hash and other status info of the repo
cmd = 'git describe --always --long --dirty --tags'
output = subprocess.check_output(cmd, shell=True)
git_hash = output.decode().replace('\n', '').replace('-', ':')


class Project:
    name = ''
    hw_version = '0.1'
    sw_version = '0.0.1'
    
    src_dir = 'src'
    obj_dir = 'obj'
    build_dir = 'build'

    dependencies = MyList()
    sources = MyList()

    programmer = 'Pickit4'
    processor = ''

    # compiler options
    compiler = 'xc8'
    c_standard = '89'
    cflags = MyList()
    defines = MyList()
    toolchain_options = MyList()
    prune_dependencies = False

    git_hash = git_hash

    def __init__(self, project=None):
        if isinstance(project, Project):
            self.__from_project__(project)

    def __from_project__(self, project):
        attributes = [a for a in dir(project) if not a.startswith('__')]
        for attribute in attributes:
            setattr(self, attribute, getattr(project, attribute))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


def main():
    frame = sys._getframe(1)

    if len(sys.argv) == 2:
        eval(f'{sys.argv[1]}()', frame.f_globals)
    if len(sys.argv) == 3:
        eval(f'{sys.argv[1]}("{sys.argv[2]}")', frame.f_globals)