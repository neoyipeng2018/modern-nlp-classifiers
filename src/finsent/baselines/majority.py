"""The floor. If a model is near this, something is broken."""

from __future__ import annotations

from collections import Counter

from ..data.schema import Row


class MajorityBaseline:
    name = "majority"
    evidence_grade = "supported"

    def __init__(self) -> None:
        self.label = "neutral"

    def fit(self, rows: list[Row]) -> "MajorityBaseline":
        self.label = Counter(r.label for r in rows).most_common(1)[0][0]
        return self

    def predict(self, texts: list[str]) -> list[str]:
        return [self.label] * len(texts)
