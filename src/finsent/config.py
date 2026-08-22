"""Settings resolution and hashing.

A run is defined by its resolved settings. The resolved settings are hashed, and
that hash is what the registry records, so a default can never change a run's
meaning without changing its identity.

The defaults live in `settings.py`, not in a YAML file. The four HTML plan
documents at the repository root are the plan of record.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .settings import load as _load_defaults


def resolve() -> dict[str, Any]:
    """The resolved settings, before any override is folded in."""
    return _load_defaults()


def _parse_value(text: str) -> Any:
    """Read an override value. JSON first, then the bare string.

    This keeps `--set eval.bootstrap=2000` an integer and
    `--set licence.redistribute_text=false` a boolean, while a plain word such
    as `--set task_input.null_target=overall` stays a string.
    """
    lowered = text.strip().lower()
    if lowered in ("true", "false"):
        return lowered == "true"
    if lowered in ("null", "none", "~", ""):
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def apply_overrides(config: dict, overrides: list[str]) -> dict:
    """Fold `a.b=value` strings into resolved settings, before they are hashed."""
    out = json.loads(json.dumps(config))
    for item in overrides:
        if "=" not in item:
            raise ValueError(f"override must be key=value, got {item!r}")
        dotted, _, value = item.partition("=")
        node = out
        parts = dotted.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = _parse_value(value)
    return out


def config_hash(config: dict) -> str:
    """A stable hash of resolved settings. Key order never changes the result."""
    blob = json.dumps(config, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(blob.encode()).hexdigest()


def file_hash(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()
