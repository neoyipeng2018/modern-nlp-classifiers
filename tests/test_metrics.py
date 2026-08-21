import pytest

from finsent.eval import metrics


def test_macro_f1_against_a_hand_computed_case():
    gold = ["positive", "positive", "negative", "neutral"]
    pred = ["positive", "negative", "negative", "neutral"]
    # positive: p=1.0 r=0.5 f1=2/3 | negative: p=0.5 r=1.0 f1=2/3 | neutral: f1=1.0
    assert metrics.macro_f1(gold, pred) == pytest.approx((2 / 3 + 2 / 3 + 1.0) / 3)


def test_perfect_and_empty_cases():
    gold = ["positive", "negative", "neutral"]
    assert metrics.macro_f1(gold, gold) == pytest.approx(1.0)
    assert metrics.accuracy([], []) == 0.0


def test_macro_f1_punishes_a_majority_only_model():
    gold = ["neutral"] * 90 + ["positive"] * 10
    pred = ["neutral"] * 100
    assert metrics.accuracy(gold, pred) == pytest.approx(0.9)
    assert metrics.macro_f1(gold, pred) < 0.35, "this is why accuracy is not the primary metric"


def test_confusion_rows_sum_to_support():
    gold = ["positive"] * 4 + ["neutral"] * 2
    pred = ["positive", "neutral", "positive", "negative", "neutral", "neutral"]
    table = metrics.confusion(gold, pred)
    assert sum(table["positive"].values()) == 4
    assert sum(table["neutral"].values()) == 2


def test_paired_bootstrap_separates_a_real_gap():
    gold = ["positive", "negative", "neutral"] * 40
    good = list(gold)
    bad = ["neutral"] * len(gold)
    result = metrics.paired_bootstrap(gold, good, bad, n=400, seed=1)
    assert result.delta > 0 and result.separated


def test_paired_bootstrap_declines_to_separate_identical_systems():
    gold = ["positive", "negative", "neutral"] * 40
    same = ["neutral"] * len(gold)
    result = metrics.paired_bootstrap(gold, same, list(same), n=400, seed=1)
    assert result.delta == pytest.approx(0.0)
    assert not result.separated


def test_holm_is_stricter_than_the_raw_threshold():
    raw = {"a": 0.001, "b": 0.02, "c": 0.04, "d": 0.30}
    out = metrics.holm(raw, alpha=0.05)
    assert out["a"]["significant"]
    assert not out["d"]["significant"]
    # b would pass an uncorrected 0.05 test and does not survive the family.
    assert raw["b"] < 0.05 and not out["b"]["significant"]
