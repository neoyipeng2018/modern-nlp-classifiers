"""Financial sentence sentiment: data, baselines and the evaluation harness."""

__version__ = "0.1.0"

LABELS = ("negative", "neutral", "positive")
LABEL_TO_ID = {name: i for i, name in enumerate(LABELS)}
