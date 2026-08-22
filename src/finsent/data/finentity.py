"""FinEntity, the entity-level source that carries the multi-target rows.

This is the set the aspect claim rests on. FiQA counted zero sentences whose
targets disagree, so without a source that has them the headline number in
`PRODUCT.html` cannot be measured at all. FinEntity is also the only human
source in the plan with a permissive licence, which matters for the release.

One document carries several annotated entity spans, each with its own
polarity. A document becomes one row per distinct target string, so a document
naming three companies produces three rows that share a `sentence_id`.

Warning. 70 of the 2,131 published spans carry offsets that do not match their
own value string. The drift is one to five characters and it is always forward,
so it reads like an encoding artefact rather than a labelling error. Every one
of them is repaired by a search for the value nearest the recorded offset. None
is unrecoverable, and `audit` reports the repair count so the number stays
visible rather than becoming a silent fix.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

REPO = "yixuantt/FinEntity"
FILE = "FinEntity.json"
LICENCE = "ODC-BY-1.0"
CODEBOOK = "finentity-v1"

LABEL_MAP = {"Positive": "positive", "Negative": "negative", "Neutral": "neutral"}


@dataclass
class Target:
    """One (document, target) pair. The unit the model is scored on."""

    sentence_id: str
    text: str
    target: str
    label: str
    target_start: int
    target_end: int


@dataclass
class Audit:
    """What the source holds, and whether it can carry the aspect claim."""

    n_documents: int
    n_spans: int
    n_targets: int
    n_repaired_offsets: int
    n_unrepairable: int
    n_duplicate_documents: int
    n_multi_target: int
    n_multi_label: int
    n_polar_opposite: int
    n_self_conflicting: int
    targets_from_multi_label: int
    label_counts: dict[str, int] = field(default_factory=dict)

    @property
    def multi_label_rate(self) -> float:
        return self.n_multi_label / self.n_documents if self.n_documents else 0.0


def _locate(content: str, value: str, start: int) -> int | None:
    """The recorded offset, or the occurrence of `value` nearest to it."""
    if content[start : start + len(value)] == value:
        return start
    best, found = None, content.find(value)
    while found != -1:
        if best is None or abs(found - start) < abs(best - start):
            best = found
        found = content.find(value, found + 1)
    return best


def _read() -> list[dict]:
    import json

    from huggingface_hub import hf_hub_download

    with open(hf_hub_download(REPO, FILE, repo_type="dataset")) as handle:
        return json.load(handle)


def parse(documents: list[dict]) -> tuple[list[Target], Audit]:
    """Turn the published documents into target rows, and count what is there.

    A document contributes one row per distinct target string. Where the same
    string is annotated twice in one document with different polarities, the
    document is counted as self-conflicting and every one of its rows is
    dropped, because that target has no single right answer.
    """
    from .schema import make_id

    n_spans = repaired = unrepairable = 0
    self_conflicting = multi_target = multi_label = polar_opposite = 0
    targets_from_multi_label = 0
    label_counts: dict[str, int] = {}
    seen_documents: set[str] = set()
    n_duplicate = 0
    rows: list[Target] = []

    for document in documents:
        content = document["content"].strip()
        if content in seen_documents:
            n_duplicate += 1
            continue
        seen_documents.add(content)
        sentence_id = make_id("finentity", content)

        spans: dict[str, list[tuple[str, int, int]]] = defaultdict(list)
        for span in document["annotations"]:
            n_spans += 1
            value = span["value"].strip()
            label = LABEL_MAP[span["label"]]
            label_counts[label] = label_counts.get(label, 0) + 1
            start = _locate(document["content"], span["value"], span["start"])
            if start is None:
                unrepairable += 1
                continue
            if start != span["start"]:
                repaired += 1
            spans[value].append((label, start, start + len(span["value"])))

        if any(len({label for label, _, _ in hits}) > 1 for hits in spans.values()):
            self_conflicting += 1
            continue

        labels = {hits[0][0] for hits in spans.values()}
        if len(spans) >= 2:
            multi_target += 1
            if len(labels) >= 2:
                multi_label += 1
                targets_from_multi_label += len(spans)
            if "positive" in labels and "negative" in labels:
                polar_opposite += 1

        for value, hits in spans.items():
            label, start, end = hits[0]
            rows.append(
                Target(
                    sentence_id=sentence_id,
                    text=content,
                    target=value,
                    label=label,
                    target_start=start,
                    target_end=end,
                )
            )

    audit = Audit(
        n_documents=len(seen_documents),
        n_spans=n_spans,
        n_targets=len(rows),
        n_repaired_offsets=repaired,
        n_unrepairable=unrepairable,
        n_duplicate_documents=n_duplicate,
        n_multi_target=multi_target,
        n_multi_label=multi_label,
        n_polar_opposite=polar_opposite,
        n_self_conflicting=self_conflicting,
        targets_from_multi_label=targets_from_multi_label,
        label_counts=dict(sorted(label_counts.items())),
    )
    return rows, audit


def load() -> tuple[list[Target], Audit]:
    """Pull the source and parse it. Needs network."""
    return parse(_read())
