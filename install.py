#!/usr/bin/env python3


import os
from pathlib import Path
import shutil
import json
import argparse


templates_folder = Path(Path(__file__).absolute().parent, 'templates')
template_files = json.load(open(Path(templates_folder, 'template.json')))


def copy_file(filename, dest):
    if d := os.path.dirname(dest):
        os.makedirs(d, exist_ok=True)
    shutil.copyfile(Path(templates_folder, filename), Path(dest))


def install():
    for name, path in template_files.items():
        if not Path(path).exists():
            copy_file(name, path)


def uninstall():
    for name, path in template_files.items():
        os.remove(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()

    if args.uninstall:
        uninstall()
    else:
        install()