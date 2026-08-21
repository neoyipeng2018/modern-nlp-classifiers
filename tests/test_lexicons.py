from finsent.baselines import LexiconBaseline
from finsent.lexicons import load_henry
from finsent.lexicons.scorer import Lexicon
from tests.conftest import row

LEX = Lexicon("t", frozenset({"strong", "gain"}), frozenset({"weak", "loss"}), "test")


def test_the_henry_list_loads_and_is_graded_reported():
    henry = load_henry()
    assert len(henry.positive) > 50 and len(henry.negative) > 50
    assert henry.evidence_grade == "reported", (
        "the Henry list is transcribed and unverified, so anything it produces "
        "must not be graded supported"
    )


def test_the_score_is_a_plain_count_difference():
    assert LEX.score("strong gain") == 2
    assert LEX.score("weak loss") == -2
    assert LEX.score("strong loss") == 0
    assert LEX.score("results were reported") == 0


def test_length_never_changes_the_answer():
    short = "a strong quarter"
    padded = short + " " + " ".join(["the company said"] * 20)
    assert LEX.score(short) == LEX.score(padded)
    assert LEX.classify(short) == LEX.classify(padded) == "positive"


def test_negation_flips_the_sign():
    assert LEX.score("results were not strong") == -1
    assert LEX.score("results were strong") == 1
    assert LEX.classify("results were not strong") == "negative"


def test_a_tie_is_neutral_and_so_is_silence():
    assert LEX.classify("strong loss") == "neutral", "one hit each way cancels"
    assert LEX.classify("the meeting is on tuesday") == "neutral", "no hit at all"


def test_the_baseline_fits_nothing():
    baseline = LexiconBaseline(LEX)
    assert not hasattr(baseline, "fit"), (
        "the word lists are published and the rule is the sign of a count. "
        "A fit method here would imply a tuned parameter that does not exist."
    )
    assert baseline.predict(["strong gain", "weak loss", "quiet day"]) == [
        "positive",
        "negative",
        "neutral",
    ]


def test_the_abstention_rate_counts_silent_rows():
    rows = [
        row("a strong quarter", "positive"),
        row("a weak quarter", "negative"),
        row("the meeting is on tuesday", "neutral"),
        row("revenue was four billion", "neutral"),
    ]
    assert LexiconBaseline(LEX).abstention_rate(rows) == 0.5
    assert LexiconBaseline(LEX).abstention_rate([]) == 0.0
