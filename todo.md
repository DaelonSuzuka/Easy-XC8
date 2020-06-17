# TODO List


`build.py`
 - all compiler options are currently hardcoded
   - refactor to provide sane defaults
   - load compiler options from project.yaml to override defaults

`configure.py`
 - add ability to edit existing project.yaml
 - add ability to populate `c_cpp_properties.json` with correct xc8 information
   - read path to find possible xc8 installations
   - add correct defines

pin configuration  
 - some script can copy the empty `pins.c`, `pins.h`, and `pins.csv` to where they belong
 - gui editor for pins.csv?
   - would require adding a gui framework to the venv
 - needs more documentation of features
   - list of all pin tags from `pins.csv`
