#!/usr/bin/env python3

import sys

from project import load_project

# ------------------------------------------------------------------------------


def walk_project(project: dict, parts: list[str]):
    if len(parts) == 1:
        return project.get(parts[0], None)

    return walk_project(project[parts[0]], parts[1:])


def main(key: str):
    project: dict = load_project()

    parts = key.split('.')

    if len(parts) == 1:
        if key in project:
            print(project[key])
            sys.exit(0)
    else:
        result = walk_project(project, parts)
        if result is not None:
            print(result)
            sys.exit(0)

    sys.exit(1)


if __name__ == '__main__':
    # the name of the desired variable is the first argument
    # e.g. name, src_dir, build_dir
    # compound variables are separated by a dot, e.g. release.compiler
    key = sys.argv[1]

    main(key)
