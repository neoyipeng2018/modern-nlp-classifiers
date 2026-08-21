"""A finance word list, scored as a classifier.

This is the number a finance reader looks for first, and it is the honest floor
for this task. The deadband that separates neutral from the other two classes is
fitted on the development split, never on test.
"""

from __future__ import annotations

import numpy as np

from ..data.schema import Row
from ..eval.metrics import macro_f1
from ..lexicons import Lexicon


class LexiconBaseline:
    def __init__(self, lexicon: Lexicon, deadband: float = 0.0) -> None:
        self.lexicon = lexicon
        self.deadband = deadband
        self.name = f"lexicon-{lexicon.name}"
        self.evidence_grade = lexicon.evidence_grade

    def fit(self, rows: list[Row], grid: int = 40) -> "LexiconBaseline":
        """Pick the deadband on development rows. One tuned number, recorded."""
        scores = [self.lexicon.score(r.text) for r in rows]
        gold = [r.label for r in rows]
        spread = max((abs(s) for s in scores), default=0.0)
        best, best_score = 0.0, -1.0
        for candidate in np.linspace(0.0, spread, grid):
            pred = [
                "positive" if s > candidate else "negative" if s < -candidate else "neutral"
                for s in scores
            ]
            value = macro_f1(gold, pred)
            if value > best_score:
                best, best_score = float(candidate), value
        self.deadband = best
        return self

    def predict(self, texts: list[str]) -> list[str]:
        return [self.lexicon.classify(text, self.deadband) for text in texts]
