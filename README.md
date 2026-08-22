# finsent

Aspect-based financial sentiment, benched in the open.

One task. Every row is a text and a target inside it, and the model says whether
the text is positive, negative or neutral **about that target**. When the caller
has no target, the target is the literal `overall`, and the task is plain
sentence sentiment. One model, one input format, one head. Two models will ship,
one small and one large.

Every number is measured on a frozen human-labelled split, through one harness,
against a floor set by finance word lists, with `gpt-5.6-sol` scored on the same
rows and its cost on the same table.

There is no config directory. The four HTML documents at the root are the plan
of record, and `src/finsent/settings.py` is the machine-readable copy of every
value the code reads. See `ARCHITECTURE.html`, the settings section.

The plans are the four HTML documents at the root: [`PRODUCT.html`](PRODUCT.html),
[`PROGRAM_DESIGN.html`](PROGRAM_DESIGN.html), [`ARCHITECTURE.html`](ARCHITECTURE.html)
and [`VERTICAL_SLICES.html`](VERTICAL_SLICES.html). Edit them directly; they are
no longer generated from fragments. The decision record is
[`DECISIONS_AIM.md`](DECISIONS_AIM.md), and the open gaps are in
[`GAPS_AIM_2.md`](GAPS_AIM_2.md) and [`GAPS_AIM_3.md`](GAPS_AIM_3.md). The reviews that produced them are in
[`REVIEW_AIM.md`](REVIEW_AIM.md) and [`REVIEW.md`](REVIEW.md). What the previous
project learned the hard way is in `learnings.html`.

## Reproduce the numbers

```bash
pip install -e ".[dev,lexicon]" nltk
finsent build-data     # pull, deduplicate, split, freeze, hash
finsent baselines      # score the floor on the development split
finsent aspect-audit   # count the multi-target rows the aspect claim needs
finsent registry       # every run that happened, with its evidence grade
```

`build-data` downloads Financial PhraseBank and FiQA, so it needs network. The
test suite does not: it runs on synthetic rows, which is what lets CI check the
data invariants without credentials.

## Where the numbers stand

Development split, 500 rows. Every baseline is fitted on the 3,336-row train
split and scored on dev. The test split has not been opened.

| System | macro-F1 | 95% interval | accuracy | grade |
|---|---:|---|---:|---|
| majority class | 0.2546 | 0.2431 – 0.2651 | 0.6180 | supported |
| Loughran-McDonald word list | 0.4426 | 0.3941 – 0.4907 | 0.5580 | supported |
| Henry word list | 0.5896 | 0.5349 – 0.6416 | 0.6760 | reported |

The two word lists fit nothing. The rule is the sign of positive hits minus
negative hits, and a tie is neutral. Read them beside their abstention rate:
Loughran-McDonald is silent on 65% of dev rows and Henry on 66%. Every silent
row is called neutral, so most of their "neutral" is the absence of a decision
rather than a decision.
| TF-IDF + logistic regression | 0.7385 | 0.6885 – 0.7848 | 0.7980 | supported |

Two things to read from that table.

The majority baseline scores 0.62 accuracy and 0.25 macro-F1. That gap is why
macro-F1 is the primary metric and accuracy is marked secondary.

Henry beats Loughran-McDonald by fourteen points here. Loughran-McDonald was
built from 10-K filings and this benchmark is financial news, so the gap is
plausible. It is also graded **reported**, not supported, because the Henry list
in this repository is transcribed from published reproductions and has not been
checked against the original paper. See the header of
`src/finsent/lexicons/data/henry_2008.txt`.

Nothing is fitted on the rows it is scored against. Majority class and TF-IDF
learn from train; the word lists learn nothing anywhere.

Henry beats Loughran-McDonald by fourteen points, and the word counts explain
most of it. Loughran-McDonald carries 140 positive stems against 893 negative
ones, because it was built to catch risk language in 10-K filings. On news it
over-calls negative and under-calls positive. Henry is balanced at 83 and 72,
and its predicted class rates track the gold rates closely.

## What the data build found

Financial PhraseBank ships 4,846 lines in its widest file. They are not 4,846
clean sentences.

- 8 sentences appear more than once. Repeats with one consistent label are
  collapsed to a single row.
- 2 sentences carry contradicting labels between their copies. They have no
  defensible label, so they are dropped and named in the build output. Letting
  the last read win would pick a label by file ordering.
- 4,836 usable sentences remain, of which 2,259 reach all-agree.
- 59 rows fall into a near-duplicate cluster with another row.

The four published subsets are nested, so cutting four test splits is impossible
and cutting four overlapping ones leaks. One test split is cut from the 50%-agree
superset, every row keeps the strongest tier it reached, and the four subsets are
read back as breakdowns of that one frozen split.

FiQA's labels are aspect-conditioned. Under the old sentence-level scope a
sentence carrying two aspects with opposite polarity could not be scored, and the
build counted those rows so they could be dropped. The scope changed on 21 August
2026 and those rows are now kept: they are the rows that separate an aspect model
from a sentence model. The count still matters, because it is the size of the
effect this project claims. On FiQA it is **zero** of 1,111 sentences, which is
why FinEntity had to be loaded before the claim could be measured at all.

FinEntity was audited on 22 August 2026 and the gate passed. Reproduce it with
`finsent aspect-audit`. Of 968 kept documents, 542 name two or more targets and
**119 give those targets different labels**, over 323 target rows. Thirty hold a
positive target and a negative one at once. See `VERTICAL_SLICES.html`, slice 2.

## Licence, and what is not in this repository

Financial PhraseBank is CC BY-NC-SA 3.0. **Non-commercial.** This project
redistributes none of its text and none of its labels. What is committed is the
manifest of hashes and `split_assignments.csv`, which carries row identifiers and
split assignments only. `finsent build-data` rebuilds the exact splits by joining
on `example_id`, which is a hash of the sentence.

The licence position for released weights is recorded in `DECISIONS_AIM.md`
entry J. It is a position, not a settled question.

## Layout

```
src/finsent/
  settings.py      every default the code reads. No YAML file
  config.py        resolution, overrides, hashing
  registry.py      append-only run rows. No row, no number
  data/            loaders, near-duplicate clustering, splitting, freezing
  lexicons/        Loughran-McDonald and Henry, and the tone scorer
  baselines/       majority, word lists, TF-IDF. One interface each
  eval/            metrics, paired bootstrap, Holm, the harness
tests/             the data invariant checks and the metric fixtures
```

## Rules the code enforces rather than asks for

- The harness refuses a split whose hash does not match the settings.
- The harness refuses any evaluation split holding a non-human label.
- The harness refuses a system that returns fewer predictions than rows.
- A near-duplicate group never straddles two splits.
- A paraphrase and its original never straddle two splits.
- A registry row without a hypothesis is refused.
- An unknown evidence grade is refused.
