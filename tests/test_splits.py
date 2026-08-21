"""The data invariant checks. These are the failures that silently ruin results."""

from __future__ import annotations

import pytest

from finsent.data import dedup
from finsent.data.splits import check_invariants, cut, freeze, load_split, stats
from tests.conftest import row


def test_cut_fills_the_requested_sizes(rows):
    dedup.apply(rows)
    cut(rows, n_test=12, n_dev=6, seed=1)
    counts = {name: block["n"] for name, block in stats(rows).items()}
    assert counts["test"] == 12
    assert counts["dev"] == 6
    assert counts["train"] == len(rows) - 18


def test_no_example_id_appears_in_two_splits(rows):
    dedup.apply(rows)
    cut(rows, n_test=12, n_dev=6, seed=1)
    check_invariants(rows)


def test_a_near_duplicate_group_never_straddles_a_split(rows):
    twin_a = row("the quarterly dividend was raised to forty two cents per share today", "positive")
    twin_b = row("the quarterly dividend was raised to forty two cents per share today now", "positive")
    pool = rows + [twin_a, twin_b]
    dedup.apply(pool)
    assert twin_a.dup_group == twin_b.dup_group, "the two twins should cluster together"
    cut(pool, n_test=12, n_dev=6, seed=1)
    assert twin_a.split == twin_b.split
    check_invariants(pool)


def test_a_straddling_group_makes_the_check_fail(rows):
    dedup.apply(rows)
    cut(rows, n_test=12, n_dev=6, seed=1)
    shared = rows[0].dup_group
    rows[0].dup_group = shared
    rows[1].dup_group = shared
    rows[0].split, rows[1].split = "train", "test"
    with pytest.raises(AssertionError, match="straddle"):
        check_invariants(rows)


def test_a_split_paraphrase_family_makes_the_check_fail(rows):
    dedup.apply(rows)
    cut(rows, n_test=12, n_dev=6, seed=1)
    rows[0].family_id = rows[1].family_id = "family-1"
    rows[0].split, rows[1].split = "train", "test"
    with pytest.raises(AssertionError, match="families straddle"):
        check_invariants(rows)


def test_a_weak_label_in_an_evaluation_split_makes_the_check_fail(rows):
    dedup.apply(rows)
    cut(rows, n_test=12, n_dev=6, seed=1)
    offender = next(r for r in rows if r.split == "test")
    offender.label_source = "weak"
    with pytest.raises(AssertionError, match="non-human labels"):
        check_invariants(rows)


def test_freeze_writes_hashes_and_reloads_identically(tmp_path, rows):
    dedup.apply(rows)
    cut(rows, n_test=12, n_dev=6, seed=1)
    manifest = freeze(rows, tmp_path)
    assert set(manifest["hashes"]) == {"train", "dev", "test", "split_assignments"}
    assert manifest["redistribution"]["text_published"] is False
    assert all(v.startswith("sha256:") for v in manifest["hashes"].values())
    assert len(load_split(tmp_path / "test.jsonl")) == 12


def test_freezing_twice_gives_the_same_hash(tmp_path, rows):
    dedup.apply(rows)
    cut(rows, n_test=12, n_dev=6, seed=1)
    first = freeze(rows, tmp_path / "a")["hashes"]
    second = freeze(rows, tmp_path / "b")["hashes"]
    assert first == second, "a frozen split must be reproducible byte for byte"


def test_cutting_is_deterministic_for_one_seed(rows):
    import copy

    other = copy.deepcopy(rows)
    dedup.apply(rows)
    dedup.apply(other)
    cut(rows, n_test=12, n_dev=6, seed=7)
    cut(other, n_test=12, n_dev=6, seed=7)
    assert [r.split for r in rows] == [r.split for r in other]
