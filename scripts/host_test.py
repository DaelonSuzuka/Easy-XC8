#!/usr/bin/env python3
"""Discover, build, and run host unit tests (*_test.c) with zig cc.

Convention:
  - Co-located: foo_test.c next to foo.c (same directory, stem match)
  - One binary per *_test.c; main returns 0 on success
  - Firmware builds skip *_test.c (see skip.py)

Usage (from project root via make):
  make test
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# Directories never searched for host tests
EXCLUDE_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "build",
    "obj",
    "node_modules",
    "__pycache__",
}

# Top-level path segments to skip entirely (relative to project root)
EXCLUDE_TOP = {
    "toolchain",
}


def project_root() -> Path:
    return Path.cwd().resolve()


def toolchain_dir() -> Path:
    env = os.environ.get("TOOLCHAIN_DIR")
    if env:
        return Path(env).resolve()
    # scripts/ live in toolchain/scripts/
    return Path(__file__).resolve().parent.parent


def discover_tests(root: Path) -> list[Path]:
    tests: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # prune excluded dirs in-place
        rel = Path(dirpath).resolve().relative_to(root)
        parts = rel.parts
        if parts and parts[0] in EXCLUDE_TOP:
            dirnames.clear()
            continue
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_NAMES]

        for name in filenames:
            if name.endswith("_test.c"):
                tests.append(Path(dirpath) / name)
    return sorted(tests)


def companion_source(test_c: Path) -> Path | None:
    """foo_test.c -> foo.c in the same directory."""
    stem = test_c.stem  # foo_test
    if not stem.endswith("_test"):
        return None
    base = stem[: -len("_test")]
    candidate = test_c.with_name(base + ".c")
    return candidate if candidate.is_file() else None


def host_cc_cmd() -> list[str]:
    """Prefer venv ziglang; allow HOST_CC override (space-separated)."""
    override = os.environ.get("HOST_CC")
    if override:
        return override.split()
    return [sys.executable, "-m", "ziglang", "cc"]


def ensure_zig() -> None:
    if os.environ.get("HOST_CC"):
        return
    try:
        subprocess.run(
            [sys.executable, "-m", "ziglang", "version"],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(
            "error: ziglang not available in this Python env.\n"
            "  From the project: make venv   (toolchain must depend on ziglang)\n"
            "  Or set HOST_CC=gcc",
            file=sys.stderr,
        )
        raise SystemExit(2) from e


def build_and_run(test_c: Path, companion: Path, out_dir: Path, root: Path) -> int:
    name = test_c.stem
    out_bin = out_dir / name
    if sys.platform == "win32":
        out_bin = out_bin.with_suffix(".exe")

    include_dirs = {
        companion.parent,
        test_c.parent,
        root / "src",
        root,
        toolchain_dir() / "host",
    }

    cmd = host_cc_cmd() + [
        "-std=c99",
        "-Wall",
        "-Werror",
        "-o",
        str(out_bin),
    ]
    for inc in sorted(include_dirs, key=lambda p: str(p)):
        if inc.is_dir():
            cmd.extend(["-I", str(inc)])

    cmd.extend([str(test_c), str(companion)])

    log(f"  compile {name}")
    r = subprocess.run(cmd, cwd=root)
    if r.returncode != 0:
        log(f"FAIL  {name} (compile)")
        return 1

    log(f"  run     {name}")
    r = subprocess.run([str(out_bin)], cwd=root)
    if r.returncode != 0:
        log(f"FAIL  {name} (exit {r.returncode})")
        return 1

    log(f"ok    {name}")
    return 0


def log(msg: str = "") -> None:
    print(msg, flush=True)


def main() -> int:
    root = project_root()
    ensure_zig()

    tests = discover_tests(root)
    if not tests:
        log("no host tests (*_test.c)")
        return 0

    out_dir = root / "build" / "host"
    out_dir.mkdir(parents=True, exist_ok=True)

    log(f"host tests: {len(tests)} unit(s)")
    failed = 0
    skipped = 0

    for test_c in tests:
        rel = test_c.relative_to(root)
        companion = companion_source(test_c)
        if companion is None:
            log(f"SKIP  {rel}  (no companion {test_c.stem[: -len('_test')]}.c)")
            skipped += 1
            continue
        if build_and_run(test_c, companion, out_dir, root) != 0:
            failed += 1

    log()
    if failed:
        log(f"{failed} failed, {len(tests) - failed - skipped} passed, {skipped} skipped")
        return 1
    log(f"all passed ({len(tests) - skipped} run, {skipped} skipped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
