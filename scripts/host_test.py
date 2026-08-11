#!/usr/bin/env python3
"""Discover, build, and run host unit tests (*_test.c).

Compiler resolution (first match wins):
  1. HOST_CC env (space-separated), e.g. HOST_CC=gcc
  2. python-zig on PATH  —  uv tool install ziglang
  3. zig on PATH         —  system Zig (uses: zig cc)
  4. uvx --from ziglang python-zig
  5. python -m ziglang   —  only if ziglang is importable in this env

Zig is intentionally not a toolchain venv dependency (~400MB unpacked).
Install once per machine:  uv tool install ziglang

Convention:
  - Co-located: foo_test.c next to foo.c (same directory, stem match)
  - One binary per *_test.c; main returns 0 on success
  - Firmware builds skip *_test.c (see skip.py)

Usage (from project root via make):
  make test
  make test   # runs --check-cc first via Makefile
  python host_test.py --check-cc   # compiler only
"""

from __future__ import annotations

import argparse
import os
import shutil
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

# Resolved once per process: argv prefix that ends ready for cc flags
# e.g. ["python-zig", "cc"] or ["gcc"]
_cc_prefix: list[str] | None = None


def project_root() -> Path:
    return Path.cwd().resolve()


def toolchain_dir() -> Path:
    env = os.environ.get("TOOLCHAIN_DIR")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


def discover_tests(root: Path) -> list[Path]:
    tests: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
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
    stem = test_c.stem
    if not stem.endswith("_test"):
        return None
    base = stem[: -len("_test")]
    candidate = test_c.with_name(base + ".c")
    return candidate if candidate.is_file() else None


def log(msg: str = "") -> None:
    print(msg, flush=True)


def _probe(cmd: list[str]) -> bool:
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=120)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def resolve_cc() -> list[str]:
    """Return compiler argv prefix including the 'cc' mode for zig wrappers."""
    global _cc_prefix
    if _cc_prefix is not None:
        return _cc_prefix

    override = os.environ.get("HOST_CC")
    if override:
        _cc_prefix = override.split()
        log(f"host cc: HOST_CC ({' '.join(_cc_prefix)})")
        return _cc_prefix

    # uv tool install ziglang  →  python-zig on PATH
    python_zig = shutil.which("python-zig")
    if python_zig and _probe([python_zig, "version"]):
        _cc_prefix = [python_zig, "cc"]
        log(f"host cc: {python_zig} cc  (uv tool)")
        return _cc_prefix

    # System Zig
    zig = shutil.which("zig")
    if zig and _probe([zig, "version"]):
        _cc_prefix = [zig, "cc"]
        log(f"host cc: {zig} cc")
        return _cc_prefix

    # Ephemeral / cached via uvx (no permanent tool install)
    uv = shutil.which("uv")
    if uv and _probe([uv, "x", "--from", "ziglang", "python-zig", "version"]):
        _cc_prefix = [uv, "x", "--from", "ziglang", "python-zig", "cc"]
        log("host cc: uvx --from ziglang python-zig cc")
        return _cc_prefix

    # Optional: ziglang still installed in this Python env
    if _probe([sys.executable, "-m", "ziglang", "version"]):
        _cc_prefix = [sys.executable, "-m", "ziglang", "cc"]
        log("host cc: python -m ziglang cc  (venv/package)")
        return _cc_prefix

    print(
        "!!! Host C compiler not found !!!\n"
        "\n"
        "  Host tests are designed to run with zig cc (one-time setup, shared\n"
        "  across all projects on this machine):\n"
        "\n"
        "    uv tool install ziglang\n"
        "\n"
        "  Then re-run:\n"
        "\n"
        "    make test\n"
        "\n"
        "  Fallbacks (NOT recommended — zig cc is the supported path):\n"
        "    HOST_CC=gcc make test\n"
        "    HOST_CC=clang make test\n"
        "    # or install system zig so `zig` is on PATH\n",
        file=sys.stderr,
    )
    raise SystemExit(2)


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

    cmd = resolve_cc() + [
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Host unit tests for *_test.c")
    parser.add_argument(
        "--check-cc",
        action="store_true",
        help="only verify a host C compiler is available, then exit",
    )
    args = parser.parse_args(argv)

    resolve_cc()  # fail early with install hint
    if args.check_cc:
        return 0

    root = project_root()
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
