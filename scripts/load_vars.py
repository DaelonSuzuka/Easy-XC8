#!/usr/bin/env python3

import sys

# ------------------------------------------------------------------------------

# the name of the variable we're looking for
key = sys.argv[1]

# look for the variable in project.yaml
# this is a fairly gross hack to not to have to import yaml
if len(sys.argv):
    with open("project.yaml") as f:
        project = f.readlines()

        for line in project:
            if line.startswith(key + ":"):
                print(line.split(":")[1].strip())
                sys.exit(0)

# if we get here, then the variable wasn't in project.yaml
optional_vars = {
    'src_dir': 'src',
    'build_dir': 'build',
    'obj_dir': 'obj',
}
if key in optional_vars:
    print(optional_vars[key])
    sys.exit(0)

# if we get here, it wasn't in optional_vars either
sys.exit(1)
