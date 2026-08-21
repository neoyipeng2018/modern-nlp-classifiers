"""Metrics.

Macro-F1 is the primary number. Accuracy is reported and marked secondary,
because on an imbalanced task it rewards ignoring the class you care about.

Every comparison is paired. Two systems are scored on the same rows and the
bootstrap runs over the per-row difference. That cancels the shared difficulty
of the rows and separates gaps far smaller than two overlapping intervals
suggest.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .. import LABELS


def confusion(gold: list[str], pred: list[str]) -> dict[str, dict[str, int]]:
    table = {g: {p: 0 for p in LABELS} for g in LABELS}
    for g, p in zip(gold, pred):
        table[g][p] += 1
    return table


def per_class_f1(gold: list[str], pred: list[str]) -> dict[str, dict[str, float]]:
    out = {}
    for label in LABELS:
        tp = sum(1 for g, p in zip(gold, pred) if g == label and p == label)
        fp = sum(1 for g, p in zip(gold, pred) if g != label and p == label)
        fn = sum(1 for g, p in zip(gold, pred) if g == label and p != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        out[label] = {"precision": precision, "recall": recall, "f1": f1, "support": tp + fn}
    return out


def macro_f1(gold: list[str], pred: list[str]) -> float:
    scores = per_class_f1(gold, pred)
    return sum(v["f1"] for v in scores.values()) / len(LABELS)


def accuracy(gold: list[str], pred: list[str]) -> float:
    return sum(1 for g, p in zip(gold, pred) if g == p) / len(gold) if gold else 0.0


@dataclass
class Interval:
    value: float
    low: float
    high: float
    method: str

    def as_dict(self) -> dict:
        return {"value": self.value, "ci95": [self.low, self.high], "method": self.method}


def bootstrap_macro_f1(gold: list[str], pred: list[str], n: int = 10000, seed: int = 0) -> Interval:
    rng = np.random.default_rng(seed)
    gold_arr, pred_arr = np.array(gold), np.array(pred)
    size = len(gold_arr)
    draws = np.empty(n)
    for i in range(n):
        idx = rng.integers(0, size, size)
        draws[i] = macro_f1(list(gold_arr[idx]), list(pred_arr[idx]))
    low, high = np.percentile(draws, [2.5, 97.5])
    return Interval(macro_f1(gold, pred), float(low), float(high), f"bootstrap-{n}")


@dataclass
class PairedResult:
    delta: float
    low: float
    high: float
    p_value: float
    separated: bool

    def as_dict(self) -> dict:
        return {
            "delta": self.delta,
            "ci95": [self.low, self.high],
            "p_value": self.p_value,
            "separated": self.separated,
        }


def paired_bootstrap(
    gold: list[str], pred_a: list[str], pred_b: list[str], n: int = 10000, seed: int = 0
) -> PairedResult:
    """Bootstrap the per-row difference in macro-F1 between A and B.

    Positive delta means A beats B. The two-sided p-value is the share of draws
    on the wrong side of zero, doubled.
    """
    rng = np.random.default_rng(seed)
    gold_arr = np.array(gold)
    a_arr, b_arr = np.array(pred_a), np.array(pred_b)
    size = len(gold_arr)
    draws = np.empty(n)
    for i in range(n):
        idx = rng.integers(0, size, size)
        g = list(gold_arr[idx])
        draws[i] = macro_f1(g, list(a_arr[idx])) - macro_f1(g, list(b_arr[idx]))
    low, high = np.percentile(draws, [2.5, 97.5])
    share_below = float((draws <= 0).mean())
    p_value = min(1.0, 2 * min(share_below, 1 - share_below))
    delta = macro_f1(gold, pred_a) - macro_f1(gold, pred_b)
    return PairedResult(delta, float(low), float(high), p_value, bool(low > 0 or high < 0))


def holm(p_values: dict[str, float], alpha: float = 0.05) -> dict[str, dict]:
    """Holm correction over a family of tests.

    The bench runs one test per candidate against the incumbent leader. Eleven
    tests at 95% give roughly a one-in-three chance of a false separation, so
    the family is corrected and the rule is fixed before the bench runs.
    """
    ordered = sorted(p_values.items(), key=lambda kv: kv[1])
    total = len(ordered)
    out: dict[str, dict] = {}
    still_rejecting = True
    for rank, (name, p) in enumerate(ordered):
        threshold = alpha / (total - rank)
        if p > threshold:
            still_rejecting = False
        out[name] = {
            "p_value": p,
            "threshold": threshold,
            "significant": bool(still_rejecting and p <= threshold),
        }
    return out
