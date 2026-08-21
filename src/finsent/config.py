"""Config resolution and hashing.

A run is defined by its resolved config. The resolved config is hashed, and that
hash is what the registry records, so an inherited default can never change a
run's meaning without changing its identity.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

_INHERIT_KEY = "inherits"


def _deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def resolve(path: str | Path, _seen: tuple[Path, ...] = ()) -> dict[str, Any]:
    """Read a YAML config and fold in everything it inherits from.

    `inherits` may be a single path or a list, resolved relative to this file.
    Later entries win over earlier ones, and the file itself wins over all.
    """
    path = Path(path).resolve()
    if path in _seen:
        chain = " -> ".join(p.name for p in (*_seen, path))
        raise ValueError(f"config inheritance loop: {chain}")

    with path.open() as handle:
        raw = yaml.safe_load(handle) or {}
    if not isinstance(raw, dict):
        raise TypeError(f"{path} must contain a mapping, got {type(raw).__name__}")

    parents = raw.pop(_INHERIT_KEY, [])
    if isinstance(parents, str):
        parents = [parents]

    merged: dict[str, Any] = {}
    for parent in parents:
        merged = _deep_merge(merged, resolve(path.parent / parent, (*_seen, path)))
    return _deep_merge(merged, raw)


def apply_overrides(config: dict, overrides: list[str]) -> dict:
    """Fold `a.b=value` strings into a resolved config, before it is hashed."""
    out = json.loads(json.dumps(config))
    for item in overrides:
        if "=" not in item:
            raise ValueError(f"override must be key=value, got {item!r}")
        dotted, _, value = item.partition("=")
        node = out
        parts = dotted.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = yaml.safe_load(value)
    return out


def config_hash(config: dict) -> str:
    """A stable hash of a resolved config. Key order never changes the result."""
    blob = json.dumps(config, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(blob.encode()).hexdigest()


def file_hash(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()
