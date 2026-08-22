"""The FinEntity parse rules, on synthetic documents.

CI has no network, so these documents are written here rather than pulled. Each
one encodes a rule the real source needs: an offset that drifted off its own
value, a document that names one target twice with two labels, an exact repeat,
and the multi-target case the whole aspect claim rests on.
"""

from __future__ import annotations

from finsent.data import finentity


def document(content: str, spans: list[tuple[str, str, int]]) -> dict:
    return {
        "content": content,
        "annotations": [
            {"value": value, "label": label, "start": start, "end": start + len(value), "tag": label}
            for value, label, start in spans
        ],
    }


ONE_TARGET = document("Acme raised its dividend today.", [("Acme", "Positive", 0)])
TWO_TARGETS_TWO_LABELS = document(
    "Acme gained on the contract while Borex lost the bid.",
    [("Acme", "Positive", 0), ("Borex", "Negative", 33)],
)
TWO_TARGETS_ONE_LABEL = document(
    "Acme and Borex both closed flat.", [("Acme", "Neutral", 0), ("Borex", "Neutral", 9)]
)


def test_one_document_makes_one_row_per_distinct_target():
    rows, audit = finentity.parse([ONE_TARGET, TWO_TARGETS_TWO_LABELS])
    assert audit.n_documents == 2
    assert audit.n_targets == 3
    assert [r.target for r in rows] == ["Acme", "Acme", "Borex"]


def test_targets_of_one_document_share_a_sentence_id():
    rows, _ = finentity.parse([TWO_TARGETS_TWO_LABELS])
    assert len({r.sentence_id for r in rows}) == 1, "the sentence is the split key"


def test_labels_are_lowercased_into_the_codebook():
    rows, audit = finentity.parse([TWO_TARGETS_TWO_LABELS])
    assert sorted(r.label for r in rows) == ["negative", "positive"]
    assert audit.label_counts == {"negative": 1, "positive": 1}


def test_the_multi_label_count_is_the_gate():
    _, audit = finentity.parse([ONE_TARGET, TWO_TARGETS_ONE_LABEL, TWO_TARGETS_TWO_LABELS])
    assert audit.n_multi_target == 2, "two documents carry two targets"
    assert audit.n_multi_label == 1, "only one of them carries two different labels"
    assert audit.n_polar_opposite == 1
    assert audit.targets_from_multi_label == 2


def test_a_drifted_offset_is_repaired_and_counted():
    drifted = document("Acme raised its dividend today.", [("Acme", "Positive", 2)])
    rows, audit = finentity.parse([drifted])
    assert audit.n_repaired_offsets == 1
    assert audit.n_unrepairable == 0
    assert rows[0].target_start == 0
    assert rows[0].text[rows[0].target_start : rows[0].target_end] == "Acme"


def test_a_value_that_is_absent_is_counted_not_guessed():
    absent = document("Acme raised its dividend today.", [("Zeta", "Positive", 0)])
    rows, audit = finentity.parse([absent])
    assert audit.n_unrepairable == 1
    assert rows == []


def test_a_target_labelled_two_ways_drops_its_whole_document():
    conflicted = document(
        "Acme rose, then Acme fell.", [("Acme", "Positive", 0), ("Acme", "Negative", 16)]
    )
    rows, audit = finentity.parse([conflicted])
    assert audit.n_self_conflicting == 1
    assert rows == [], "that target has no single right answer, so nothing is kept"


def test_an_exact_repeat_of_a_document_is_dropped():
    _, audit = finentity.parse([ONE_TARGET, dict(ONE_TARGET)])
    assert audit.n_duplicate_documents == 1
    assert audit.n_documents == 1


def test_the_multi_label_rate_reads_against_kept_documents():
    _, audit = finentity.parse([ONE_TARGET, TWO_TARGETS_TWO_LABELS])
    assert audit.multi_label_rate == 0.5
