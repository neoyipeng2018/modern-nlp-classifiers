"""FiQA 2018 Task 1, used as the secondary out-of-domain set.

Warning, and it is the reason this module counts before it converts. FiQA's
labels are aspect-conditioned: one row is one (sentence, target) pair, and the
same sentence can appear several times with different targets and opposite
scores. A sentence-level model cannot be scored honestly on such a sentence,
because there is no single right answer for it.

So `load` splits the data in two. Rows whose sentence carries one consistent
polarity are usable. Rows whose sentence carries conflicting polarities are
returned separately, counted, and never quietly averaged into the score.
"""

from __future__ import annotations

from dataclasses import dataclass

from .schema import Row, make_id

REPO = "pauri32/fiqa-2018"
FILES = ("train.csv", "validation.csv", "test.csv")
LICENCE = "unknown-verify-before-redistribution"
CODEBOOK = "fiqa-v1"

# FiQA ships a continuous score in [-1, 1]. These cuts follow the source's own
# mapped class, and the choice is published with the results either way.
NEGATIVE_BELOW = -0.1
POSITIVE_ABOVE = 0.1


@dataclass
class FiqaLoad:
    usable: list[Row]
    conflicted: list[Row]
    n_sentences: int
    n_conflicted_sentences: int

    @property
    def conflict_rate(self) -> float:
        return self.n_conflicted_sentences / self.n_sentences if self.n_sentences else 0.0


def score_to_label(score: float) -> str:
    if score < NEGATIVE_BELOW:
        return "negative"
    if score > POSITIVE_ABOVE:
        return "positive"
    return "neutral"


def load() -> FiqaLoad:
    import pandas as pd
    from huggingface_hub import hf_hub_download

    frames = [pd.read_csv(hf_hub_download(REPO, name, repo_type="dataset")) for name in FILES]
    table = pd.concat(frames, ignore_index=True)

    labels_by_sentence: dict[str, set[str]] = {}
    for sentence, score in zip(table["sentence"], table["sentiment_score"]):
        labels_by_sentence.setdefault(str(sentence), set()).add(score_to_label(float(score)))

    usable, conflicted = [], []
    for sentence, labels in labels_by_sentence.items():
        row = Row(
            example_id=make_id("fiqa", sentence),
            text=sentence,
            label=sorted(labels)[0] if len(labels) == 1 else sorted(labels)[0],
            label_source="human",
            source_dataset=REPO,
            source_licence=LICENCE,
            codebook_version=CODEBOOK,
            borrowed_row_id=make_id("fiqa", sentence),
        )
        row.validate()
        (usable if len(labels) == 1 else conflicted).append(row)

    return FiqaLoad(
        usable=usable,
        conflicted=conflicted,
        n_sentences=len(labels_by_sentence),
        n_conflicted_sentences=len(conflicted),
    )
