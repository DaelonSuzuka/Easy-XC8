#!/usr/bin/env python3


import os
from pathlib import Path
import shutil
import json
import argparse


templates_folder = Path(Path(__file__).absolute().parent, 'templates')


def copy_file(src, dest):
    if d := os.path.dirname(dest):
        os.makedirs(d, exist_ok=True)

    shutil.copyfile(Path(templates_folder, src), dest)


def install(template):
    count = 0
    for f in template.rglob('*'):
        if not Path(f).relative_to(template).exists():
            copy_file(f, Path(f).relative_to(template))
            count += 1

    return count

# def uninstall():
#     for name, path in template_files.items():
#         os.remove(path)

def main(args):
    available_templates = [t for t in templates_folder.iterdir()]
    full_template_names = {t.parts[-1]:t for t in available_templates}

    if args.list:
        print("Available templates: ")
        for t in available_templates:
            print(' -', t.parts[-1])
        return

    if args.install:
        print(f'Installing template: {args.template}')
        print('...')
        count = install(full_template_names[args.template])
        print(f'Installed {count} files')

    # if args.uninstall:
    #     uninstall()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", default=True, action="store_false")
    # parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--template", default='judi_example')
    args = parser.parse_args()

    main(args)