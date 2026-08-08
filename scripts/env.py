#!/usr/bin/env python3
"""Generate .vscode/c_cpp_properties.json from project.yaml.

Discovers the XC8 installation, validates the compiler version (if a
desired version is set in project.yaml), and writes IntelliSense config
for both development and release profiles.

Usage:
    make env
    python toolchain/scripts/env.py
"""

from __future__ import annotations

import json
import os
import platform
import re
import sys
from pathlib import Path

# --- toolchain imports (run from project root) ---------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
from project import load_project


# --- XC8 discovery -------------------------------------------------------------

def xc8_search_roots() -> list[Path]:
    """Directories that may contain xc8/v<version>/ installs."""
    roots: list[Path] = []
    if platform.system() == "Windows" or os.name == "nt":
        for drive_base in ("C:/", "D:/"):
            for prefix in ("Program Files", "Microchip", ""):
                roots.append(Path(drive_base + prefix + "/Microchip/xc8"))
        # MPLAB X bundled
        roots.append(Path("C:/Program Files/Microchip/xc8"))
        roots.append(Path("C:/Microchip/xc8"))
    else:
        roots.append(Path("/opt/microchip/xc8"))
        # Home-local installs
        home = Path.home()
        roots.append(home / ".microchip/xc8")
    return roots


def find_xc8_installations() -> list[dict]:
    """Return list of {path, version, bin} for each XC8 found."""
    installs = []
    seen = set()

    for root in xc8_search_roots():
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            if child.name in seen:
                continue
            # Expect directory named v<version> e.g. v2.45
            if not re.match(r"^v\d+\.\d+$", child.name):
                continue
            bin_dir = child / "bin"
            if not bin_dir.is_dir():
                continue
            version = child.name[1:]  # strip 'v'
            installs.append({
                "path": child,
                "version": version,
                "bin": bin_dir,
            })
            seen.add(child.name)

    # Also check xc8 on PATH (resolve backward to install root)
    from shutil import which
    xc8_on_path = which("xc8")
    if xc8_on_path:
        real = Path(xc8_on_path).resolve()
        # bin/xc8 -> parent is bin, parent.parent is v<version>, parent.parent.parent is xc8/
        if real.name in ("xc8", "xc8.exe") and real.parent.name == "bin":
            version_dir = real.parent.parent
            if version_dir.name not in seen and re.match(r"^v\d+\.\d+$", version_dir.name):
                installs.append({
                    "path": version_dir,
                    "version": version_dir.name[1:],
                    "bin": real.parent,
                })
                seen.add(version_dir.name)

    return installs


def select_xc8(installs: list[dict], desired: str | None) -> dict | None:
    """Pick the best XC8 installation, warn on version mismatch."""
    if not installs:
        return None

    if desired:
        for inst in installs:
            if inst["version"] == desired:
                return inst
        available = ", ".join(i["version"] for i in installs)
        print(
            f"warning: desired compiler version {desired} not found.\n"
            f"  available: {available}",
            file=sys.stderr,
        )
        # Fall back to newest
        return max(installs, key=lambda i: i["version"])

    # No preference: pick newest
    return max(installs, key=lambda i: i["version"])


# --- Include path resolution (version-branchable) -------------------------------

def xc8_include_dirs(xc8: dict, standard: str) -> list[str]:
    """Return XC8 system include directories for the given C standard.

    XC8 v2.x layout:
        pic/include/          — core headers (xc.h, pic.h, etc.)
        pic/include/c90/      — c90 standard library
        pic/include/c99/      — c99 standard library
        pic/include/proc/     — per-device headers
        pic/include/legacy/   — HI-TECH legacy headers

    If the internal layout changes in a future version, branch here on
    xc8['version'].
    """
    base = xc8["path"] / "pic" / "include"
    std_dir = "c90" if standard == "c89" else "c99"

    dirs = [
        base,
        base / std_dir,
        base / "proc",
    ]
    # Only include if they exist (graceful for stripped installs)
    return [d.as_posix() for d in dirs if d.is_dir()]


def project_include_dirs(src_dir: str) -> list[str]:
    """Project source tree + all subdirectories."""
    root = Path(src_dir)
    dirs = [root.as_posix()]
    for d in sorted(root.rglob("*")):
        if d.is_dir():
            dirs.append(d.as_posix())
    return dirs


# --- c_cpp_properties.json generation ------------------------------------------

def build_config(project: dict, env_name: str, xc8: dict) -> dict:
    """Build a single c_cpp_properties.json configuration entry."""
    env = project[env_name]

    # Chip-select macro: XC8 defines _18F16Q41 internally from -mcpu.
    # IntelliSense can't probe xc8 for this, so we inject it explicitly.
    # pic18_chip_select.h uses #ifdef _18F<chip> to include the device header.
    chip_select = "_" + env["processor"]

    # Defines from project.yaml + compiler-injected symbols
    defines = [
        chip_select,
        f"__XC8_{env['standard'].upper()}__",
        f"__XC8_VERSION={xc8['version'].replace('.', '')}",
        "_XC_H_",
        f"__PROCESSOR__={env['processor']}",
        f"__PRODUCT_NAME__={project['name']}",
    ]
    # Add profile defines
    defines.extend(env.get("defines", []))

    # Include paths: project first, then XC8 system
    includes = project_include_dirs(project["src_dir"])
    includes.extend(xc8_include_dirs(xc8, env["standard"]))

    # C standard for IntelliSense
    c_standard = "c89" if env["standard"] == "c89" else "c99"

    # Compiler path: the C/C++ extension needs a real clang/gcc it can probe
    # for built-in defines and standard headers. XC8 bundles clang on Windows
    # (clang.exe in bin/). On Linux there's no bundled clang, so we look for
    # a system clang as fallback. The explicit defines/includePath above
    # handle all PIC-specific resolution regardless of which clang is probed.
    is_windows = platform.system() == "Windows" or os.name == "nt"
    from shutil import which
    candidates = []
    if is_windows:
        candidates.append(xc8["bin"] / "clang.exe")
    # System clang/gcc as fallback (Linux, or Windows without bundled clang)
    for name in ("clang", "gcc"):
        path = which(name)
        if path:
            candidates.append(Path(path))
    compiler_path = None
    for c in candidates:
        if c.exists():
            compiler_path = c.resolve().as_posix()
            break
    # IntelliSense shim: neutralizes XC8 language extensions (__interrupt, irq,
 # etc.) that the C/C++ extension can't parse. Never included by real builds.
    shim = (Path(__file__).resolve().parent.parent / "host" / "intellisense.h").as_posix()
    return {
        "name": env_name,
        "includePath": includes,
        "defines": defines,
        "cStandard": c_standard,
        "compilerPath": compiler_path,
        "intelliSenseMode": "gcc-x64",
        "forcedInclude": [shim],
    }


def generate(project: dict, xc8: dict, output: Path) -> None:
    """Write .vscode/c_cpp_properties.json with dev + release configs."""
    configs = [
        build_config(project, "development", xc8),
        build_config(project, "release", xc8),
    ]

    properties = {
        "version": 4,
        "configurations": configs,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(properties, indent=4) + "\n")
    print(f"wrote {output}")
    for c in configs:
        print(f"  [{c['name']}] {len(c['includePath'])} include paths, {len(c['defines'])} defines")


# --- main ----------------------------------------------------------------------

def main() -> int:
    project = load_project()

    # Desired compiler version (optional, top-level in build_settings)
    desired_version = project.get("compiler_version")

    installs = find_xc8_installations()

    if not installs:
        print(
            "!!! No XC8 installation found !!!\n"
            "\n"
            "  Searched:\n"
            + "\n".join(f"    {r}" for r in xc8_search_roots())
            + "\n"
            "\n"
            "  Install Microchip XC8 from:\n"
            "    https://www.microchip.com/en-us/tools/programmers-compiler/xc8\n"
            "\n"
            "  Or set the install location on PATH and re-run:\n"
            "    make env\n",
            file=sys.stderr,
        )
        return 1

    xc8 = select_xc8(installs, desired_version)

    if desired_version and xc8["version"] != desired_version:
        print(f"using XC8 v{xc8['version']} (desired: v{desired_version})", file=sys.stderr)
    else:
        print(f"using XC8 v{xc8['version']}")

    output = Path(".vscode/c_cpp_properties.json")
    generate(project, xc8, output)
    return 0


if __name__ == "__main__":
    sys.exit(main())