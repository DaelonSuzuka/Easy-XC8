#!/usr/bin/env python3

import os
import sys
import json
import yaml
import argparse
from dotmap import DotMap
from pathlib import Path

# ------------------------------------------------------------------------------


def assemble_upload_command(programmer, args):
    command = []
    add = command.append

    add(programmer.command)
    add(programmer.target + args.target)
    add(programmer.source + args.source)

    for flag in programmer.flags:
        add(flag)

    return " ".join(command)


def main(programmer, args):
    command = assemble_upload_command(programmer, args)

    exit_code = os.system(command)

    # clean up temp files
    for f in programmer.garbage:
        try:
            os.remove(f)
        except:
            pass

    sys.exit(exit_code)


if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "upload.json")

    programmers = DotMap(json.loads(open(file_path).read()))

    parser = argparse.ArgumentParser()
    arg = parser.add_argument
    try:
        project = DotMap(yaml.full_load(open("project.yaml").read()))
        source = f"{project['build_dir']}/{project.name}.hex"
        arg("-t", "--target", default=project.target)
        arg("-s", "--source", default=source)
        arg("-p", "--programmer", default=project.programmer)
    except:
        arg("-t", "--target", required=True)
        arg("-s", "--source", required=True)
        arg("-p", "--programmer", default=programmers.default)

    args = parser.parse_args()

    main(programmers[args.programmer], args)
