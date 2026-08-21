"""The row schema.

Every row carries where it came from, what licence it arrived under and how its
label was made. A row without provenance never enters a training set, and the
loader raises rather than defaulting a missing field quietly.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Literal

from .. import LABELS

LabelSource = Literal["human", "public", "weak", "augmented"]
LABEL_SOURCES = ("human", "public", "weak", "augmented")

# Only these may appear in an evaluation split. The harness enforces it.
EVAL_LABEL_SOURCES = ("human",)


@dataclass
class Row:
    example_id: str
    text: str
    label: str
    label_source: LabelSource
    source_dataset: str
    source_licence: str
    codebook_version: str
    agreement_tier: str = ""      # FPB only: all, 75, 66, 50
    borrowed_row_id: str = ""
    dup_group: str = ""           # near-duplicate cluster, the split key
    family_id: str = ""           # augmentation family, the other split key
    split: str = ""

    def validate(self) -> None:
        if self.label not in LABELS:
            raise ValueError(f"{self.example_id}: label {self.label!r} not in {LABELS}")
        if self.label_source not in LABEL_SOURCES:
            raise ValueError(f"{self.example_id}: bad label_source {self.label_source!r}")
        for field_name in ("text", "source_dataset", "source_licence", "codebook_version"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{self.example_id}: {field_name} is empty, which is never allowed")

    def as_dict(self) -> dict:
        return asdict(self)


def make_id(source: str, text: str) -> str:
    """A stable id. Rebuilding the dataset gives the same ids."""
    return f"{source}:{hashlib.sha256(text.encode()).hexdigest()[:16]}"
