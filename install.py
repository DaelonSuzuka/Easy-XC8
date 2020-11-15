#!/usr/bin/env python3


import os
from pathlib import Path
import shutil
import json
import argparse


templates_folder = Path(Path(__file__).absolute().parent, 'templates')
template = Path(templates_folder, 'judi_example')
template_files = [x for x in template.rglob('*') if not x.is_dir()]


def copy_file(src):
    dest = Path(src).relative_to(template)
    
    if d := os.path.dirname(dest):
        os.makedirs(d, exist_ok=True)

    shutil.copyfile(Path(templates_folder, src), dest)


def install():
    for f in template_files:
        if not Path(f).relative_to(template).exists():
            copy_file(f)


# def uninstall():
#     for name, path in template_files.items():
#         os.remove(path)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--uninstall", action="store_true")
    # args = parser.parse_args()

    # if args.uninstall:
    #     uninstall()
    # else:
        # install()
        
    install()