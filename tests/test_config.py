import pytest

from finsent.config import apply_overrides, config_hash, resolve
from finsent.settings import DEFAULTS


def test_resolve_returns_the_defaults():
    assert resolve() == DEFAULTS


def test_resolve_returns_a_fresh_copy_every_time():
    first = resolve()
    first["seed"] = 1
    assert resolve()["seed"] == DEFAULTS["seed"]
    assert DEFAULTS["seed"] != 1


def test_the_defaults_hold_the_values_the_plans_name():
    # These four are named in PRODUCT.html and ARCHITECTURE.html. A silent edit
    # here changes what every run means, so the test states them out loud.
    assert DEFAULTS["task_input"]["format"] == "pair"
    assert DEFAULTS["task_input"]["null_target"] == "overall"
    assert DEFAULTS["baselines"]["frontier"]["model"] == "gpt-5.6-sol"
    assert DEFAULTS["licence"]["redistribute_text"] is False


def test_the_null_target_is_never_empty():
    assert DEFAULTS["task_input"]["null_target"].strip()


def test_hash_is_stable_across_key_order():
    assert config_hash({"a": 1, "b": {"c": 2}}) == config_hash({"b": {"c": 2}, "a": 1})


def test_hash_changes_when_a_value_changes():
    assert config_hash({"a": 1}) != config_hash({"a": 2})


def test_overrides_are_folded_in_before_hashing():
    base = {"eval": {"bootstrap": 10}}
    out = apply_overrides(base, ["eval.bootstrap=50", "seed=7"])
    assert out == {"eval": {"bootstrap": 50}, "seed": 7}
    assert base == {"eval": {"bootstrap": 10}}, "the input config must not be mutated"


def test_override_values_keep_their_type():
    out = apply_overrides(
        resolve(),
        [
            "eval.bootstrap=2000",
            "data.dedup_threshold=0.7",
            "licence.redistribute_text=false",
            "task_input.null_target=overall",
        ],
    )
    assert out["eval"]["bootstrap"] == 2000
    assert out["data"]["dedup_threshold"] == 0.7
    assert out["licence"]["redistribute_text"] is False
    assert out["task_input"]["null_target"] == "overall"


def test_an_override_without_an_equals_sign_is_an_error():
    with pytest.raises(ValueError, match="key=value"):
        apply_overrides(resolve(), ["seed"])


def test_an_override_changes_the_hash():
    base = resolve()
    assert config_hash(base) != config_hash(apply_overrides(base, ["seed=1"]))
