"""The one gatekeeper.

Everything that produces labels is scored here and nowhere else: the classical
baselines, the word lists, the fine-tuned encoders and any public model being
compared. The harness refuses input rather than warning about it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

from ..config import file_hash
from ..data.schema import EVAL_LABEL_SOURCES, Row
from . import metrics


class System(Protocol):
    name: str

    def predict(self, texts: list[str]) -> list[str]: ...


@dataclass
class Report:
    system: str
    split: str
    split_hash: str
    n: int
    macro_f1: dict
    accuracy: float
    per_class: dict
    confusion: dict
    by_agreement_tier: dict = field(default_factory=dict)
    vs: dict = field(default_factory=dict)
    evidence_grade: str = "supported"
    notes: str = ""

    def as_dict(self) -> dict:
        return {
            "system": self.system,
            "split": self.split,
            "split_hash": self.split_hash,
            "n": self.n,
            "macro_f1": self.macro_f1,
            "accuracy": self.accuracy,
            "per_class": self.per_class,
            "confusion": self.confusion,
            "by_agreement_tier": self.by_agreement_tier,
            "vs": self.vs,
            "evidence_grade": self.evidence_grade,
            "notes": self.notes,
        }


def _guard(rows: list[Row], split_path: Path, expected_hash: str | None) -> str:
    if not rows:
        raise ValueError("nothing to score")

    offenders = {r.label_source for r in rows} - set(EVAL_LABEL_SOURCES)
    if offenders:
        raise AssertionError(
            f"evaluation split carries non-human labels {sorted(offenders)}. "
            "A model scored against labels its own teachers wrote tells you nothing."
        )

    actual = file_hash(split_path)
    if expected_hash and actual != expected_hash:
        raise AssertionError(
            f"split hash mismatch for {split_path}.\n  expected {expected_hash}\n  found    {actual}\n"
            "The frozen split changed. Every number measured against it is not comparable."
        )
    return actual


def score(
    system: System,
    split_path: str | Path,
    expected_hash: str | None = None,
    comparators: dict[str, list[str]] | None = None,
    bootstrap: int = 2000,
    seed: int = 0,
) -> Report:
    """Score one system on one frozen split, and write nothing without a hash."""
    from ..data.splits import load_split

    split_path = Path(split_path)
    rows = load_split(split_path)
    split_hash = _guard(rows, split_path, expected_hash)

    gold = [r.label for r in rows]
    pred = system.predict([r.text for r in rows])
    if len(pred) != len(gold):
        raise AssertionError(
            f"{system.name} returned {len(pred)} predictions for {len(gold)} rows. "
            "Every row must get a prediction. Missing outputs are never dropped silently."
        )

    by_tier = {}
    tiers = sorted({r.agreement_tier for r in rows if r.agreement_tier})
    for tier in tiers:
        idx = [i for i, r in enumerate(rows) if r.agreement_tier == tier]
        by_tier[tier] = {
            "n": len(idx),
            "macro_f1": metrics.macro_f1([gold[i] for i in idx], [pred[i] for i in idx]),
        }

    # The published subsets are nested, so read them back cumulatively from the
    # one frozen split rather than cutting four splits that would overlap.
    order = ("50", "66", "75", "all")
    cumulative = {}
    for floor, tier in enumerate(order):
        idx = [i for i, r in enumerate(rows) if r.agreement_tier in order[floor:]]
        if idx:
            cumulative[f"{tier}agree"] = {
                "n": len(idx),
                "macro_f1": metrics.macro_f1([gold[i] for i in idx], [pred[i] for i in idx]),
            }

    vs = {}
    for name, other in (comparators or {}).items():
        vs[name] = metrics.paired_bootstrap(gold, pred, other, n=bootstrap, seed=seed).as_dict()

    return Report(
        system=system.name,
        split=split_path.stem,
        split_hash=split_hash,
        n=len(rows),
        macro_f1=metrics.bootstrap_macro_f1(gold, pred, n=bootstrap, seed=seed).as_dict(),
        accuracy=metrics.accuracy(gold, pred),
        per_class=metrics.per_class_f1(gold, pred),
        confusion=metrics.confusion(gold, pred),
        by_agreement_tier={"exact": by_tier, "cumulative": cumulative},
        vs=vs,
        evidence_grade=getattr(system, "evidence_grade", "supported"),
    )


def write_report(report: Report, out_dir: str | Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{report.system}.{report.split}.json"
    with path.open("w") as handle:
        json.dump(report.as_dict(), handle, indent=2, sort_keys=True)
    return path
