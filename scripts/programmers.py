"""Programmer family resolution for upload/program.

project.yaml names the *family* (Pickit4, Pickit5, …). Host OS selects the
platform overlay from upload.json (windows | posix).

Legacy aliases (Pickit4-linux, ICD-U80-win, …) still resolve for old yamls.
"""

from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path

# Old project.yaml / wizard names → family key in upload.json
LEGACY_ALIASES = {
    "Pickit4-linux": "Pickit4",
    "Pickit5-linux": "Pickit5",
    "ICD-U80-win": "ICD-U80",
    "ICD-U80-linux": "ICD-U80",
}


def upload_json_path() -> Path:
    return Path(__file__).resolve().parent / "upload.json"


def load_programmers_table() -> dict:
    return json.loads(upload_json_path().read_text())


def host_platform_key() -> str:
    """Coarse host class matching upload.json platforms keys."""
    if platform.system() == "Windows" or os.name == "nt":
        return "windows"
    return "posix"


def list_programmer_families(table: dict | None = None) -> list[str]:
    """Names suitable for project.yaml / configure wizard (not aliases)."""
    table = table if table is not None else load_programmers_table()
    names = []
    for key, entry in table.items():
        if key == "default":
            continue
        if not isinstance(entry, dict):
            continue
        names.append(key)
    return sorted(names)


def canonical_programmer_name(name: str | None, table: dict | None = None) -> str:
    table = table if table is not None else load_programmers_table()
    if not name or name == "default":
        return table.get("default", "Pickit4")
    return LEGACY_ALIASES.get(name, name)


def resolve_programmer(name: str | None, table: dict | None = None) -> dict:
    """Return a flat programmer dict for the current host: command, target, …

    Shared fields live at the family root; platforms.<windows|posix> overlays
    command and any per-OS flags/target/source/garbage.
    """
    table = table if table is not None else load_programmers_table()
    family = canonical_programmer_name(name, table)

    if family not in table or not isinstance(table[family], dict):
        known = ", ".join(list_programmer_families(table))
        aliases = ", ".join(sorted(LEGACY_ALIASES))
        print(
            f"error: unknown programmer {name!r} (canonical {family!r})\n"
            f"  families: {known}\n"
            f"  legacy aliases: {aliases}",
            file=sys.stderr,
        )
        raise SystemExit(2)

    entry = table[family]
    plat = host_platform_key()

    # Base (OS-independent) fields
    out = {
        "name": family,
        "requested": name or family,
        "platform": plat,
        "target": entry.get("target", "-P"),
        "source": entry.get("source", "-F"),
        "flags": list(entry.get("flags") or []),
        "garbage": list(entry.get("garbage") or []),
        "command": entry.get("command"),
    }

    platforms = entry.get("platforms")
    if platforms:
        if plat not in platforms:
            print(
                f"error: programmer {family!r} has no platform {plat!r}\n"
                f"  defined platforms: {', '.join(sorted(platforms))}",
                file=sys.stderr,
            )
            raise SystemExit(2)
        overlay = platforms[plat] or {}
        for key in ("command", "target", "source", "flags", "garbage"):
            if key not in overlay:
                continue
            val = overlay[key]
            out[key] = list(val) if key in ("flags", "garbage") else val

    if not out.get("command"):
        print(
            f"error: programmer {family!r} has no command for platform {plat!r}\n"
            f"  fix platforms.{plat}.command in toolchain/scripts/upload.json",
            file=sys.stderr,
        )
        raise SystemExit(2)

    return out
