from pathlib import Path

import pytest

from finsent.config import apply_overrides, config_hash, resolve


def write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(body)
    return path


def test_inheritance_merges_deeply(tmp_path):
    write(tmp_path, "base.yaml", "a: 1\nnested:\n  x: 1\n  y: 2\n")
    child = write(tmp_path, "child.yaml", "inherits: base.yaml\nnested:\n  y: 99\n")
    assert resolve(child) == {"a": 1, "nested": {"x": 1, "y": 99}}


def test_inheritance_loop_is_an_error(tmp_path):
    write(tmp_path, "a.yaml", "inherits: b.yaml\n")
    write(tmp_path, "b.yaml", "inherits: a.yaml\n")
    with pytest.raises(ValueError, match="loop"):
        resolve(tmp_path / "a.yaml")


def test_hash_is_stable_across_key_order():
    assert config_hash({"a": 1, "b": {"c": 2}}) == config_hash({"b": {"c": 2}, "a": 1})


def test_hash_changes_when_a_value_changes():
    assert config_hash({"a": 1}) != config_hash({"a": 2})


def test_overrides_are_folded_in_before_hashing():
    base = {"eval": {"bootstrap": 10}}
    out = apply_overrides(base, ["eval.bootstrap=50", "seed=7"])
    assert out == {"eval": {"bootstrap": 50}, "seed": 7}
    assert base == {"eval": {"bootstrap": 10}}, "the input config must not be mutated"
