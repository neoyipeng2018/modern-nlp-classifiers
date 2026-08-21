"""Finance word lists, and the scorer that turns one into a classifier.

These are the baselines a finance reader checks first. Loughran-McDonald is the
standard dictionary for financial text, and Henry is the second one, which
disagrees with it often enough to be worth running as well.
"""

from .scorer import HENRY, LOUGHRAN_MCDONALD, Lexicon, load_henry, load_loughran_mcdonald

__all__ = ["Lexicon", "HENRY", "LOUGHRAN_MCDONALD", "load_henry", "load_loughran_mcdonald"]
