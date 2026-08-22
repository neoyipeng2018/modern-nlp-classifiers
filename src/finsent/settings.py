"""The runtime settings, and the only place the code reads a value from.

There is no YAML config file. The four HTML plan documents at the repository
root are the plan of record, and `ARCHITECTURE.html` carries this table in
readable form. This module is the machine-readable copy of it, and nothing else
in the package holds a default.

The rule that mattered about the old config file still holds. A run is defined
by its resolved settings, the resolved settings are hashed, and the registry
records that hash. A value cannot change a run's meaning without changing the
run's identity. `--set a.b=value` folds an override in before the hash is taken.

Warning. Change a value here and every later run gets a new `config_hash`. That
is the point. Do not reach around this module to hard-code a number somewhere
else, because a number the hash cannot see is a number the registry cannot
defend.
"""

from __future__ import annotations

import json
from typing import Any

DEFAULTS: dict[str, Any] = {
    "task": "financial-sentiment",
    "labels": ["negative", "neutral", "positive"],
    "seed": 20260821,
    "data": {
        "primary": "takala/financial_phrasebank",
        "secondary": "pauri32/fiqa-2018",
        "out_dir": "data/processed/fpb",
        "n_test": 1000,
        "n_dev": 500,
        "dedup_threshold": 0.5,
    },
    # Warning. Financial PhraseBank is CC BY-NC-SA 3.0, which is non-commercial.
    # This project never redistributes its text. Only row identifiers and split
    # assignments are published. See DECISIONS_AIM.md entry J.
    "licence": {
        "primary_data": "CC-BY-NC-SA-3.0",
        "redistribute_text": False,
    },
    "eval": {
        "primary_metric": "macro_f1",
        "bootstrap": 10000,
        "alpha": 0.05,
        "correction": "holm",
    },
    # The task is aspect-conditioned. Every row is a text and a target. A row
    # with no target carries the literal below, so plain sentence sentiment is
    # the null-target case of the same task and not a second code path.
    # See PRODUCT.html#input.
    "task_input": {
        "format": "pair",  # segment A is the text, segment B is the target
        "null_target": "overall",  # never an empty string: it would change the shape
    },
    # The frontier baseline. One model, one version, one effort setting. The
    # effort is part of the pin, not a tuning knob, because it changes the
    # answers and the bill. It writes no labels: it is scored against the human
    # key like any other system. Reasoning tokens are billed and are counted in
    # the cost table.
    "baselines": {
        "frontier": {
            "model": "gpt-5.6-sol",
            "effort": "medium",
            "prompts": ["zero_shot", "few_shot"],  # few-shot examples come from train only
            "cache_dir": "runs/cache/gpt-5.6-sol",
        },
    },
}


def load() -> dict[str, Any]:
    """A fresh copy of the defaults. The caller may edit it without side effects."""
    return json.loads(json.dumps(DEFAULTS))
