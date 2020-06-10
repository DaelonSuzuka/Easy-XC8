# What is this?
Easy-XC8 is a hybrid python/makefile build system for working with 8-bit PIC microcontrollers from Microchip. This was developed for use with PIC18s, particularly the K42 family, but there's no reason it can't work with any chip supported by XC8.

# Requirements
Programs:

- GNU Make >3.8.2 (other makes may work, but I'm not going to test them)
- xc8 compiler (`xc8` must be on your path)
- mplabx IPE (`ipecmd` or `ipecmd.sh` must be on your path)
- python3 > 3.6
- python3-venv (not installed on ubuntu by default)
- python3-pip (not installed on ubuntu by default)

# Getting Started

This project is designed to be included in your project as a git "submodule", which will cause a copy of this repo to be downloaded into your project so it can be compiled like normal, but it doesn't add those files to your project's source control. This makes it easier to keep a common set of code in sync between multiple projects without error-prone copy/pasting.

In your repository, run:

```
git submodule add https://github.com/DaelonSuzuka/XC8-Toolchain.git toolchain
python toolchain/install.py
make config
```

This will:
 - add the submodule to your git repository, and download this repo to `./toolchain`. 
 - create the minimum usable `Makefile` in the root directory of your project
 - create `project.yaml` using the project configuration wizard

You should now be ready to use the Easy-XC8 toolchain.

# Make targets

## Build targets

Build your project with
> $ make compile

Take the resulting hex and upload it to your target hardware with
> $ make upload

Remove all your build artifacts to start over
> $ make clean 

## Other targets

Generate documentation with Doxygen
> $ make docs

Run the linter to check for errors
> $ make lint

This is a suprise tool that will help us later:
> $ make cog 

## venv targets

Hopefully, you won't have to use these on your own

Create the venv and install python packages in, but only runs if the venv if missing
> $ make venv

Delete the venv
> $ make clean_venv

Delete the venv, the recreate it
> $ make reset_venv


# Scripts 

## `build.py`

This script wraps the xc8 compiler in (what I find to be) a more readable way than calling it directly from make. `build.py` automagically pulls the following information from `project.yaml` and feeds it to the compiler:

- location of source files
- location of output files
- desired C standard(C90 vs C99)
- list of preprocessor symbols to be defined
- list of flags to be passed to the linker

Additional features:

- recursively searches the source directory to build the list of files it passes to `xc8`. 
- designates the source directory and any subdirectories as 'include' directories(location the compiler will search for header files)

Planned features:

- scan for a git repository(you _are_ using version control, aren't you?), grabs the current branch, commit hash, maybe some other data, and makes that information available as preprocessor symbols in your source code.
- grab the version numbers from `project.yaml` and make them available as preprocessor symbols

## `upload.py`

This script has an accompanying file(`upload.json`) that tells it how to interact with a variety of usb pic programmers. I've gotten it to work in linux by selecting `Pickit4-linux` as your programmer in project.yaml. Unfortunately, before this would work, I had to fix Microchip's `ipecmd.sh` that was supposed to be edited during installation with the path of MPLABX's local jvm. This was a pain.


# venvs

In order to avoid polluting your system python environment, the scripts that do all the heavy lifting are run from a
virtual environment. This is an interesting topic all on its own and warrants a much more in-depth explanation than this one. 

Fortunately, the makefile is _supposed_ to handle the entire venv process for you. If the venv is missing when you run a make target that needs it, it will automatically create the venv and install the necessary python packages into the venv, then run the make target. If the venv is already there, it just uses it without you having to do anything.

# Future goals:

- Include VS Code default settings and extension recommendations
- Figure out how to explain wtf cog is
- how to customize build.py
- how to customize upload.py