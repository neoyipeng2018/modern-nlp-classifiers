"""The harness refuses bad input rather than warning about it."""

from __future__ import annotations

import pytest

from finsent.data import dedup
from finsent.data.splits import cut, freeze
from finsent.eval.harness import score


class Always:
    evidence_grade = "supported"

    def __init__(self, label: str, name: str = "always", short: bool = False) -> None:
        self.label, self.name, self.short = label, name, short

    def predict(self, texts):
        out = [self.label] * len(texts)
        return out[:-1] if self.short else out


@pytest.fixture
def frozen(tmp_path, rows):
    dedup.apply(rows)
    cut(rows, n_test=12, n_dev=6, seed=1)
    manifest = freeze(rows, tmp_path)
    return tmp_path, manifest


def test_a_wrong_split_hash_aborts(frozen):
    path, _ = frozen
    with pytest.raises(AssertionError, match="hash mismatch"):
        score(Always("neutral"), path / "test.jsonl", expected_hash="sha256:" + "0" * 64)


def test_the_correct_hash_is_accepted(frozen):
    path, manifest = frozen
    report = score(
        Always("neutral"), path / "test.jsonl", expected_hash=manifest["hashes"]["test"], bootstrap=50
    )
    assert report.n == 12
    assert 0.0 <= report.macro_f1["value"] <= 1.0


def test_a_non_human_label_in_the_split_aborts(tmp_path, frozen):
    path, manifest = frozen
    lines = (path / "test.jsonl").read_text().replace('"human"', '"weak"')
    bad = tmp_path / "weak.jsonl"
    bad.write_text(lines)
    with pytest.raises(AssertionError, match="non-human labels"):
        score(Always("neutral"), bad)


def test_missing_predictions_abort(frozen):
    path, manifest = frozen
    with pytest.raises(AssertionError, match="predictions for"):
        score(Always("neutral", short=True), path / "test.jsonl")


def test_a_paired_comparison_is_reported(frozen):
    path, manifest = frozen
    from finsent.data.splits import load_split

    rows = load_split(path / "test.jsonl")
    perfect = [r.label for r in rows]
    report = score(
        Always("neutral"),
        path / "test.jsonl",
        expected_hash=manifest["hashes"]["test"],
        comparators={"perfect": perfect},
        bootstrap=100,
    )
    assert report.vs["perfect"]["delta"] < 0
