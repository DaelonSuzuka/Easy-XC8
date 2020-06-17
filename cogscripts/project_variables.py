import os
import sys
import yaml
from dotmap import DotMap
from pathlib import Path

# ------------------------------------------------------------------------------

def read_vars():

    project = DotMap(yaml.full_load(open("project.yaml").read()))
