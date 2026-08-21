import pytest

from finsent import registry


def test_a_run_without_a_hypothesis_is_refused(tmp_path):
    row = registry.start("baseline", "", {"a": 1})
    with pytest.raises(ValueError, match="hypothesis"):
        registry.append(row, tmp_path / "r.jsonl")


def test_an_unknown_evidence_grade_is_refused(tmp_path):
    row = registry.start("baseline", "tests the floor", {"a": 1})
    row.evidence_grade = "excellent"
    with pytest.raises(ValueError, match="evidence grade"):
        registry.append(row, tmp_path / "r.jsonl")


def test_rows_append_and_read_back(tmp_path):
    path = tmp_path / "r.jsonl"
    for i in range(3):
        row = registry.start("baseline", f"run {i}", {"seed": i})
        row.evidence_grade = "supported"
        registry.append(row, path)
    read = registry.read(path)
    assert [r["hypothesis"] for r in read] == ["run 0", "run 1", "run 2"]
    assert all(r["finished_at"] for r in read)


def test_run_id_tracks_the_config_hash():
    a = registry.start("bench", "h", {"seed": 1})
    b = registry.start("bench", "h", {"seed": 2})
    assert a.config_hash != b.config_hash
    assert a.run_id.split("-")[1] != b.run_id.split("-")[1]
