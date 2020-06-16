#!/usr/bin/env python3

import os
import re
import sys
from pathlib import Path
import yaml
from dotmap import DotMap

# ------------------------------------------------------------------------------

project = DotMap(yaml.full_load(open('project.yaml').read()))

end_comment = '*/'
start_comment = '/*'

def subdirs_of(search_dir):
    """Recursively finds every subdirectory of 'search_dir'"""
    return [d.as_posix() for d in [x for x in Path(search_dir).rglob('*') if x.is_dir()]]


def all_files(dir, pattern):
    """Recursively finds every file in 'dir' whose name matches 'pattern'."""
    return [f.as_posix() for f in [x for x in Path(dir).rglob(pattern)]]


def search(files, pattern):
    """Searches in 'files' for regex results matching 'pattern'."""
    results = []
    if isinstance(files, str):
        with open(files, 'r') as f:
            [results.append(m) for m in re.findall(pattern, f.read())]
    elif isinstance(files, list):
        for file in files:
            with open(file, 'r') as f:
                [results.append(m) for m in re.findall(pattern, f.read())]
    return results


def lines_containing(files, string):
    """Searches in 'files' for regex results matching 'pattern'."""
    lines = []
    for file in files:
        with open(file, 'r') as f:
            [lines.append(line.rstrip('\n')) for line in f if string in line]

    return lines
