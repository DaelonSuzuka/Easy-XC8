#!/usr/bin/env python3

import os
import sys
import yaml
from dotmap import DotMap
from build import xc8, xc8_cc


def main(project):
    for processor in project.release_processors:
        project.processor = processor

        if project.compiler == 'xc8-cc':
            command = xc8_cc(project)
        else:
            command = xc8(project)

        try:
            os.system(command)
        except KeyboardInterrupt:
            sys.exit(1)
        
        hexfile = f"{project.build_dir}/{project.name}"
        old_name = f'{hexfile}.hex'
        new_name = f'{hexfile}_v{project.sw_version}_{processor}.hex'

        os.rename(old_name, new_name)

    sys.exit(0)


if __name__ == "__main__":
    project = DotMap(yaml.full_load(open("project.yaml").read()))

    main(project)