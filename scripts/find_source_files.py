#!/usr/bin/env python3

import sys
from pathlib import Path

# ------------------------------------------------------------------------------

if len(sys.argv):
    print(" ".join([str(f) for f in Path(sys.argv[1]).rglob("*.[hc]")]))
    sys.exit(0)

sys.exit(1)
