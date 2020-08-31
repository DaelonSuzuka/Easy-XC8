#!/usr/bin/env python3

import os
import sys
import yaml
from dotmap import DotMap
from pathlib import Path
from build import xc8, xc8_cc



def main(project):
    if project.compiler == 'xc8-cc':
        command = xc8_cc(project)
    else:
        command = xc8(project)

    try:
        result = os.system(command)
    except KeyboardInterrupt:
        result = 1
    sys.exit(result)


if __name__ == "__main__":
    project = DotMap(yaml.full_load(open("project.yaml").read()))

    print(project.release_processors)

    main(project)
