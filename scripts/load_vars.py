#!/usr/bin/env python3

import sys

# ------------------------------------------------------------------------------

if len(sys.argv):
    with open("project.yaml") as f:
        project = f.readlines()

        for line in project:
            if sys.argv[1] + ":" in line:
                print(line.split(":")[1].strip())
                sys.exit(0)

sys.exit(1)
