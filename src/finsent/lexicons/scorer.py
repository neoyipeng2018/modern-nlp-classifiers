"""Word-list tone scoring.

Both lists are matched on Porter stems, so "improving" and "improvement" both
hit "improv" without either being listed. Negation is handled with a short
window, because "not strong" is not a positive sentence and a bare word count
says it is.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

LOUGHRAN_MCDONALD = "loughran_mcdonald"
HENRY = "henry"

_WORD = re.compile(r"[a-z][a-z']*")
_NEGATORS = frozenset(
    {"not", "no", "never", "none", "cannot", "without", "nor", "neither", "hardly", "barely"}
)
_NEGATION_WINDOW = 3


def _stem(word: str) -> str:
    """Porter stem, matching how the packaged Loughran-McDonald list is stored."""
    from nltk.stem import PorterStemmer  # type: ignore

    return PorterStemmer().stem(word)


@dataclass(frozen=True)
class Lexicon:
    name: str
    positive: frozenset[str]
    negative: frozenset[str]
    source: str
    evidence_grade: str = "supported"

    def score(self, text: str) -> float:
        """Net tone, scaled by length. Positive means positive."""
        words = _WORD.findall(text.lower())
        stems = _stems(words)
        total = 0
        for index, stem in enumerate(stems):
            weight = 0
            if stem in self.positive:
                weight = 1
            elif stem in self.negative:
                weight = -1
            if weight == 0:
                continue
            window = words[max(0, index - _NEGATION_WINDOW) : index]
            if any(word in _NEGATORS for word in window):
                weight = -weight
            total += weight
        return total / len(words) if words else 0.0

    def classify(self, text: str, deadband: float = 0.0) -> str:
        value = self.score(text)
        if value > deadband:
            return "positive"
        if value < -deadband:
            return "negative"
        return "neutral"


_STEM_CACHE: dict[str, str] = {}


def _stems(words: list[str]) -> list[str]:
    missing = [w for w in words if w not in _STEM_CACHE]
    if missing:
        from nltk.stem import PorterStemmer  # type: ignore

        stemmer = PorterStemmer()
        for word in missing:
            _STEM_CACHE[word] = stemmer.stem(word)
    return [_STEM_CACHE[w] for w in words]


def load_loughran_mcdonald() -> Lexicon:
    """The packaged Loughran-McDonald dictionary, already Porter-stemmed."""
    import pysentiment2  # type: ignore

    lm = pysentiment2.LM()
    return Lexicon(
        name=LOUGHRAN_MCDONALD,
        positive=frozenset(lm._posset),
        negative=frozenset(lm._negset),
        source="Loughran & McDonald (2011), as packaged by pysentiment2",
        evidence_grade="supported",
    )


def load_henry(path: str | Path | None = None) -> Lexicon:
    """The Henry (2008) list. See the provenance warning in the data file."""
    path = Path(path) if path else Path(__file__).parent / "data" / "henry_2008.txt"
    buckets: dict[str, list[str]] = {"positive": [], "negative": []}
    current = None
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            continue
        if current in buckets:
            buckets[current].append(line.lower())
    return Lexicon(
        name=HENRY,
        positive=frozenset(_stems(buckets["positive"])),
        negative=frozenset(_stems(buckets["negative"])),
        source="Henry (2008), transcribed from published reproductions and NOT yet verified",
        evidence_grade="reported",
    )
