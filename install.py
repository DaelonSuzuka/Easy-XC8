#!/usr/bin/env python3

from pathlib import Path
import shutil

project_path = Path(__file__).absolute().parent.parent
templates_folder = Path(Path(__file__).absolute().parent, 'templates')

makefile_path = Path(project_path, "Makefile")
if not makefile_path.exists():
    shutil.copyfile(Path(templates_folder, 'Makefile'), makefile_path)