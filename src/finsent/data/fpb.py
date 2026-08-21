"""Financial PhraseBank.

The canonical repo ships a loading script, which recent `datasets` releases
refuse to run, so the original archive is read directly instead. That archive
holds four files, and they are nested: every all-agree sentence also appears in
the 50%-agree file. So there is one pool of 4,846 lines, and each sentence
carries the strongest agreement tier it reached.

The nesting is not perfect and the loader says so rather than papering over it.
Measured on the shipped archive:

  * the 50%-agree file holds 4,846 lines over 4,838 unique sentences, so eight
    sentences appear twice;
  * two of those repeated sentences carry two different labels.

A repeated sentence with one consistent label is collapsed to one row. A
repeated sentence whose copies disagree has no defensible label, so it is
dropped and counted. Letting the last read win would pick a label by file
ordering, which is not a decision anybody made.

Licence: CC BY-NC-SA 3.0. Non-commercial. The text is never redistributed by
this project. Only row identifiers and split assignments are published.
"""

from __future__ import annotations

import zipfile
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .schema import Row, make_id

REPO = "takala/financial_phrasebank"
ARCHIVE = "data/FinancialPhraseBank-v1.0.zip"
LICENCE = "CC-BY-NC-SA-3.0"
CODEBOOK = "fpb-v1"

# Read widest first, so the tier finally recorded for a sentence is the
# narrowest file it reached, which is the strongest agreement it achieved.
SUBSETS = (
    ("50", "Sentences_50Agree.txt"),
    ("66", "Sentences_66Agree.txt"),
    ("75", "Sentences_75Agree.txt"),
    ("all", "Sentences_AllAgree.txt"),
)

TIER_ORDER = ("50", "66", "75", "all")


@dataclass
class FpbLoad:
    rows: list[Row]
    n_lines: int
    n_repeated_texts: int
    dropped_conflicting: list[dict] = field(default_factory=list)

    @property
    def n_dropped(self) -> int:
        return len(self.dropped_conflicting)


def _archive_path() -> Path:
    from huggingface_hub import hf_hub_download

    return Path(hf_hub_download(REPO, ARCHIVE, repo_type="dataset"))


def _read_subset(archive: zipfile.ZipFile, filename: str) -> list[tuple[str, str]]:
    member = next(n for n in archive.namelist() if n.endswith(filename) and "__MACOSX" not in n)
    pairs = []
    for line in archive.read(member).decode("latin-1").splitlines():
        line = line.strip()
        if not line:
            continue
        sentence, _, label = line.rpartition("@")
        pairs.append((sentence.strip(), label.strip()))
    return pairs


def load_detailed() -> FpbLoad:
    """Load the pool, with the counts of what was collapsed and what was dropped."""
    labels: dict[str, set[str]] = defaultdict(set)
    tier: dict[str, str] = {}
    n_lines = 0
    repeated: set[str] = set()

    with zipfile.ZipFile(_archive_path()) as archive:
        for tier_name, filename in SUBSETS:
            seen_in_file: set[str] = set()
            for sentence, label in _read_subset(archive, filename):
                n_lines += 1 if tier_name == "50" else 0
                if sentence in seen_in_file:
                    repeated.add(sentence)
                seen_in_file.add(sentence)
                labels[sentence].add(label)
                tier[sentence] = tier_name

    rows: list[Row] = []
    dropped: list[dict] = []
    for sentence, found in labels.items():
        if len(found) > 1:
            dropped.append({"text": sentence, "labels": sorted(found), "tier": tier[sentence]})
            continue
        row = Row(
            example_id=make_id("fpb", sentence),
            text=sentence,
            label=next(iter(found)),
            label_source="human",
            source_dataset=REPO,
            source_licence=LICENCE,
            codebook_version=CODEBOOK,
            agreement_tier=tier[sentence],
            borrowed_row_id=make_id("fpb", sentence),
        )
        row.validate()
        rows.append(row)

    rows.sort(key=lambda r: r.example_id)
    return FpbLoad(
        rows=rows,
        n_lines=n_lines,
        n_repeated_texts=len(repeated),
        dropped_conflicting=sorted(dropped, key=lambda d: d["text"]),
    )


def load() -> list[Row]:
    return load_detailed().rows


def tier_at_least(rows: list[Row], tier: str) -> list[Row]:
    """The rows that reached `tier` or better. This rebuilds a published subset."""
    if tier not in TIER_ORDER:
        raise ValueError(f"unknown tier {tier!r}, expected one of {TIER_ORDER}")
    floor = TIER_ORDER.index(tier)
    return [r for r in rows if TIER_ORDER.index(r.agreement_tier) >= floor]
