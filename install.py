#!/usr/bin/env python3


import os
from pathlib import Path
import shutil


templates_folder = Path(Path(__file__).absolute().parent, 'templates')


def copy_file(filename, dest):
    if d := os.path.dirname(dest):
        os.makedirs(d, exist_ok=True)
    shutil.copyfile(Path(templates_folder, filename), Path(dest))


files = {
    'Makefile': 'Makefile',
    'c_cpp_properties.json': '.vscode/c_cpp_properties.json',
    'cogfiles.txt': 'cogfiles.txt',
    'pins.csv': 'pins.csv',
    'pins.c': 'src/pins.c',
    'pins.h': 'src/pins.h',
    '.clang-format': '.clang-format',
    '.gitignore': '.gitignore',
}


for name, path in files.items():
    if not Path(path).exists():
        copy_file(name, path)