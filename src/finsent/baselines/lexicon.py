"""A finance word list, scored as a classifier.

This is the number a finance reader looks for first, and it is the honest floor
for this task. There is nothing to fit: the word lists are published, and the
rule is the sign of positive hits minus negative hits.

Read the abstention rate beside the score. Both lists stay silent on roughly two
thirds of the rows, and every silent row is called neutral. So "neutral" here is
mostly the absence of a decision rather than a decision.
"""

from __future__ import annotations

from ..data.schema import Row
from ..lexicons import Lexicon


class LexiconBaseline:
    def __init__(self, lexicon: Lexicon) -> None:
        self.lexicon = lexicon
        self.name = f"lexicon-{lexicon.name}"
        self.evidence_grade = lexicon.evidence_grade

    def predict(self, texts: list[str]) -> list[str]:
        return [self.lexicon.classify(text) for text in texts]

    def abstention_rate(self, rows: list[Row]) -> float:
        """Share of rows where neither list fires, so the answer is neutral by
        default. Reported next to the score, never hidden inside it."""
        if not rows:
            return 0.0
        silent = sum(1 for r in rows if self.lexicon.score(r.text) == 0)
        return silent / len(rows)
