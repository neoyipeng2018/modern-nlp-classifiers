"""Baselines. Every one implements the same interface as a model.

The harness cannot tell a word list from a fine-tuned encoder, which is the
point. A weak baseline makes a weak result look strong.
"""

from .lexicon import LexiconBaseline
from .majority import MajorityBaseline
from .tfidf import TfidfBaseline

__all__ = ["LexiconBaseline", "MajorityBaseline", "TfidfBaseline"]
