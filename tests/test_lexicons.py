from finsent.lexicons import load_henry
from finsent.lexicons.scorer import Lexicon


def test_the_henry_list_loads_and_is_graded_reported():
    henry = load_henry()
    assert len(henry.positive) > 50 and len(henry.negative) > 50
    assert henry.evidence_grade == "reported", (
        "the Henry list is transcribed and unverified, so anything it produces "
        "must not be graded supported"
    )


def test_scoring_direction():
    lex = Lexicon("t", frozenset({"strong"}), frozenset({"weak"}), "test")
    assert lex.score("results were strong") > 0
    assert lex.score("results were weak") < 0
    assert lex.score("results were reported") == 0.0


def test_negation_flips_the_sign():
    lex = Lexicon("t", frozenset({"strong"}), frozenset({"weak"}), "test")
    assert lex.score("results were not strong") < 0
    assert lex.score("results were strong") > 0


def test_classify_respects_the_deadband():
    lex = Lexicon("t", frozenset({"strong"}), frozenset({"weak"}), "test")
    assert lex.classify("results were strong", deadband=0.0) == "positive"
    assert lex.classify("results were strong", deadband=0.9) == "neutral"
