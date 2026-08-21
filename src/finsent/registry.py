"""The run registry.

One append-only JSONL row per run. If a number has no row here, it did not
happen and it cannot be quoted. The row is written at the start, so a job that
dies still leaves evidence that it was attempted.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path("runs/registry.jsonl")

GRADES = ("supported", "reported", "compromised", "not_run")


@dataclass
class RunRow:
    run_id: str
    kind: str
    hypothesis: str
    config_hash: str
    started_at: str
    variable: str = ""
    parent_run_id: str = ""
    data_revision: dict[str, str] = field(default_factory=dict)
    test_hash: str = ""
    dev_hash: str = ""
    seed: int | None = None
    env: dict[str, str] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    artifact_path: str = ""
    evidence_grade: str = "not_run"
    cost_usd: float = 0.0
    finished_at: str = ""
    notes: str = ""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_run_id(kind: str, config_hash: str) -> str:
    short = config_hash.split(":")[-1][:6]
    return f"{kind}-{short}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"


def environment() -> dict[str, str]:
    import platform
    import sys

    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "hostname": platform.node(),
        "ci": os.environ.get("CI", ""),
    }


def start(kind: str, hypothesis: str, config: dict, **kwargs: Any) -> RunRow:
    from .config import config_hash as hash_config

    digest = hash_config(config)
    return RunRow(
        run_id=new_run_id(kind, digest),
        kind=kind,
        hypothesis=hypothesis,
        config_hash=digest,
        started_at=_now(),
        env=environment(),
        **kwargs,
    )


def append(row: RunRow, path: str | Path = DEFAULT_PATH) -> Path:
    if row.evidence_grade not in GRADES:
        raise ValueError(f"unknown evidence grade {row.evidence_grade!r}, expected one of {GRADES}")
    if not row.hypothesis.strip():
        raise ValueError("a run needs a hypothesis written before it starts")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not row.finished_at:
        row.finished_at = _now()
    with path.open("a") as handle:
        handle.write(json.dumps(asdict(row), sort_keys=True) + "\n")
    return path


def read(path: str | Path = DEFAULT_PATH) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open() as handle:
        return [json.loads(line) for line in handle if line.strip()]
