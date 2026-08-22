# Gap review, third pass, against the full aim

Written 22 August 2026. This review reads the four plan documents, the decision
record, `GAPS_AIM_2.md`, the settings and every source file in `src/finsent/`.

`GAPS_AIM_2.md` holds seventeen gaps. This file holds only the gaps that are
**not** in that list. A gap that the second pass already names does not appear
here again.

## The aim, as the owner states it

Build the best small, medium and large encoders or classifiers for financial
text. Cover aspect based sentiment and plain sentiment. Explore the models that
exist. Explore data boost methods. Explore weak supervision and other methods.
Compare against lexical baselines. Release the models, the data method and
everything else in public, at the state of the art.

## What the plans already do well

Give the plans credit before the list. Six things are strong.

- One task, one input format, one head. Plain sentiment falls out of the aspect
  task for free. This is the right shape.
- The harness refuses bad input. It does not warn about it.
- Three split keys stop three different leaks, and CI checks them.
- The registry keeps the runs that failed.
- The word-list floor is real, and the abstention rates sit beside it.
- The aspect gate ran before the GPU spend, and it passed.

The rest of this file is what is still absent.

## Summary

Eighteen new gaps. Gap 1 to gap 4 change what the bench measures. Gap 5 to gap
11 change the data spend. Gap 12 to gap 18 decide whether the release can claim
the state of the art at all.

| # | Gap | Aim point | Size |
|---|---|---|---|
| 1 | The roster holds encoders only, and the aim says classifiers | Models | Large |
| 2 | FinBERT runs zero-shot only, so the domain comparison is unfair | Models | Large |
| 3 | No candidate checkpoint carries a recorded licence | Models | Medium |
| 4 | The large tier puts 395M and 1B in one corrected family | Models | Small |
| 5 | No permissive human data set is named | Data boost | Large |
| 6 | Nothing checks whether a generated row keeps its label | Data boost | Large |
| 7 | No cap on generated rows, and no class balance rule | Data boost | Medium |
| 8 | No cheap control arm below the paraphrase arm | Data boost | Small |
| 9 | No market reaction weak label | Weak supervision | Medium |
| 10 | Self-training has no confidence threshold and no stop rule | Weak supervision | Medium |
| 11 | Every weak method writes a sentence label, not a target label | Weak supervision | Large |
| 12 | The aspect sources have no human agreement number | Measurement | Large |
| 13 | The project cuts its own split, so no published number joins to it | State of the art | Large |
| 14 | No aspect test split exists, and two plan statements disagree | Measurement | Large |
| 15 | `data_revision` stays empty, and no Hub revision is pinned | Release | Medium |
| 16 | The cost table names no serving format | Release | Medium |
| 17 | The negative class holds 136 test rows | Measurement | Medium |
| 18 | No rule settles a split decision across the three breakdowns | Measurement | Small |

---

## Models

### 1. The roster holds encoders only, and the aim says classifiers

**What the plans say.** `PROGRAM_DESIGN.html` lists eleven checkpoints. All
eleven are masked language model encoders. Ettin, ModernBERT, DeBERTa-v3 and
NeoBERT.

**What the aim says.** "The best small, medium and large encoders **or
classifiers**."

**Two families are absent, and both are cheap.**

1. A small decoder with a classification head. A 0.5B or 1B decoder with a
   linear head is a normal classifier in 2026. It fits the small tier and the
   large tier. It needs no new data and no new harness.
2. A frozen text embedding plus logistic regression. Take an off-the-shelf
   embedding model, freeze it, and fit a linear model on top. It costs one
   forward pass per row and no fine-tune at all.

**Why this matters more than it looks.** The second family is the true floor
above TF-IDF. If a frozen embedding plus logistic regression reaches the
fine-tuned encoder, the whole bench collapses to one line. That is a cheap
finding and the project has no plan to look for it.

**Do this.**

- Add one frozen embedding baseline. Run it in slice 2, beside TF-IDF. No GPU
  fine-tune is needed.
- Add one small decoder with a classification head to each shipped tier. Mark it
  in the roster as a separate architecture family.
- Or state in the product spec that the aim narrowed to encoders, and say why.

### 2. FinBERT runs zero-shot only, so the domain comparison is unfair

**What the plans say.** Slice 3 step 8 re-runs `ProsusAI/finbert` and
`yiyanghkust/finbert-tone` on this project's split. `PRODUCT.html` makes domain
pretraining a non-goal.

**The comparison is not paired.** The project fine-tunes ModernBERT on 3,336
train rows. It runs FinBERT with the weights that came in the box. A win over
FinBERT then measures the fine-tune, not the backbone.

**One extra run fixes it.** Fine-tune FinBERT on the same train rows, with the
same recipe and the same seeds. It is one more candidate in the same family.

**What it buys.** It answers the question the non-goal leaves open. Domain
pretraining is out of scope as a step this project performs. It is not out of
scope as a checkpoint this project measures. The card can then say whether
finance pretraining still helps in 2026, which is a publishable result on its
own.

**Warning.** Do not claim "we beat FinBERT" from a zero-shot FinBERT number. A
reviewer will find that in one minute, and the whole release loses trust.

### 3. No candidate checkpoint carries a recorded licence

**What the plans say.** The row schema carries `source_licence` for data. Entry J
settles the data licence. Nothing records the licence of a model checkpoint.

**The risk is direct.** You can bench a checkpoint and then find that you cannot
ship a model derived from it. The bench then wasted its runs.

**One checkpoint carries a second risk.** NeoBERT loads with remote code. A
model that needs remote code is harder to release, harder to serve and harder to
audit. Price that before it enters the family.

**Do this.**

- Add a `licence` field for each candidate in the roster settings.
- Check every licence before the smoke check, not after the bench.
- Record which checkpoints need remote code.

### 4. The large tier puts 395M and 1B in one corrected family

**What the plans say.** The large tier is 350M or more. It holds ModernBERT-large
at 395M, Ettin at 400M and Ettin at 1B.

**A 1B encoder is a different product.** It costs about two and a half times the
compute of the 395M models. The tier limits came from the gaps in the checkpoint
roster. They did not come from what a caller will pay to serve.

**Do this.** Either move Ettin 1B out of the corrected family and run it once as
a point on the size curve, the same way the medium tier runs. Or split the large
tier at 500M and say which half ships. Both choices cost one line.

---

## Data boost

### 5. No permissive human data set is named

**What the plans say.** `GAPS_AIM_2.md` gap 7 asks for a step that pulls
permissive human data before the synthetic step. Nobody wrote that step, and no
document names a data set.

**Real rows beat synthetic rows, and permissive rows fix the release.** Several
sets sit on the Hub under MIT today.

| Set | Rows | Licence | What it adds |
|---|---|---|---|
| `zeroshot/twitter-financial-news-sentiment` | about 12,000 | MIT | Microblog text, three classes |
| `TimKoornstra/financial-tweets-sentiment` | about 38,000 | MIT | A larger microblog pool |
| `Jean-Baptiste/financial_news_sentiment` | about 2,000 | MIT | News articles, checked by hand |

**Warning.** Check each set for overlap against the frozen splits before it
enters the train pool. Check each codebook against the codebook in
`PRODUCT.html`. A tweet set labelled to a different rule adds noise, not rows.

**Do this.** Add one step to slice 4, before the Track D factorial. Pull the
permissive sets, map them, measure the disagreement rate on 100 rows each, and
report the model with them and without them.

### 6. Nothing checks whether a generated row keeps its label

**What the plans say.** Track D paraphrases the rows the model gets wrong and
**keeps the label**. Two rules protect the split. One rule fails the build when a
generated row lands near a test row.

**The missing rule is about truth, not about leaks.** A paraphrase can change the
sentiment and keep the old label. "Profit fell less than feared" and "profit
fell" are close in text and different in label. Track D writes noise into the
train pool and no gate sees it.

**Do this.**

- Score every generated row with a second model, or with the teacher.
- Drop a generated row when the second opinion disagrees with the kept label.
- Check 100 generated rows by hand and publish the flip rate.
- Add the flip rate to the Track D report. A track with a 10% flip rate is a
  different track from one with a 1% flip rate.

### 7. No cap on generated rows, and no class balance rule

**What the plans say.** "Equal sample counts" across the three arms. Nothing
says how many variants come from one original row.

**Two things move without a decision.** The class prior moves, because the errors
are not spread evenly across the three classes. The effective weight of one
original row moves, because ten variants of one row make that row ten times
louder.

**Do this.** Set a cap of variants per original row in `settings.py`. State whether
the generated pool is balanced across the three classes or matched to the train
prior. Hash both numbers with the config.

### 8. No cheap control arm below the paraphrase arm

**What the plans say.** Three arms. No augmentation, error-targeted paraphrase,
and Verbalized Sampling.

**The control is too far below.** "No augmentation" tests whether extra rows
help. It does not test whether a **model** must write them. Back-translation and
word swap cost no API money and no terms check.

**Do this.** Add a fourth arm that uses back-translation. If the model-written
paraphrase does not beat back-translation with an interval, the write-up keeps
the cheaper conclusion and the release keeps a clean licence.

---

## Weak supervision

### 9. No market reaction weak label

**What the plans say.** Five methods. Distillation, intermediate fine-tune,
self-training, label rules with a routed model, and noise cleaning.

**The one finance-native signal is absent.** The price move of the named company
after the news is a distant label for sentiment. It is free, it scales to every
row in the news corpus, and it needs no model and no API spend.

**It is noisy, and that is manageable.** Use it as a weak source with a measured
error rate, like every other weak source. Score it against the human labels on a
held-out human slice, the same way the plans already require.

**It is also the aspect signal.** The price move belongs to one company. That
makes it a **target-level** label, which is what gap 11 says the project has none
of.

**Warning.** A price move needs a date, a ticker and a market window. Financial
PhraseBank ships none of the three. This method only works on a news corpus that
carries dates and tickers. Name that corpus first.

### 10. Self-training has no confidence threshold and no stop rule

**What the plans say.** "Self-training on unlabelled news." That is the whole
specification.

**Three numbers decide the result and none is written.** The confidence
threshold above which a pseudo-label is kept. The number of rounds. The rule that
stops a round. Self-training below a good threshold amplifies the model's own
errors, and the plan has no guard against it.

**Do this.** Write the threshold, the round count and the stop rule into the
config before the first round. Report the pseudo-label accuracy on a held-out
human slice after each round.

### 11. Every weak method writes a sentence label, not a target label

**What the plans say.** The task is aspect-conditioned. Every row is a text and a
target. The five weak methods all describe a label for a piece of text.

**The gap is structural.** A weak row must carry a target string, or it cannot
join the train pool. The row schema makes an empty target raise. So a weak
sentence label has nowhere to go except the null-target case.

**What that costs.** All the weak supervision spend then improves the easy half
of the task. The aspect half, which is the whole claim of the project, gets
nothing from it.

**Do this.** State for each of the five methods how it writes a target.

- Distillation is safe. The teacher already reads a pair.
- Self-training needs a target on every unlabelled row. Run an entity finder
  over the corpus first, or accept the null target and say so.
- The label rules need a window around a target span, not a sentence count. The
  designed `lexicon-window` baseline is exactly that rule. Reuse it.
- The market reaction label in gap 9 is target-level by construction.

---

## Measurement and the state of the art

### 12. The aspect sources have no human agreement number

**What the plans say.** Financial PhraseBank ships four agreement tiers. The
report card breaks the score down by tier. That tier breakdown is called the
closest thing this task has to a human ceiling.

**The aspect sources ship no tiers.** FinEntity and FiQA give one label per
target and no agreement measure. So the headline number of this project, the
multi-target discrimination rate, has no ceiling above it.

**Why this is not a small thing.** A model that reaches 0.70 on the aspect rows
means one thing if people agree 0.95 of the time. It means something else if
people agree 0.72 of the time.

**Do this.** Re-label 200 aspect rows with two or three annotators. Publish the
agreement. This is the same afternoon of work as the 200 test rows in gap 13 of
the second pass, and it should run beside it.

### 13. The project cuts its own split, so no published number joins to it

**What the plans say.** Entry B defines the state of the art as the best
published number on the same benchmark and the same agreement subset. Slice 3
step 1 fills the survey table in `PROGRAM_DESIGN.html`.

**The survey will not join to this project's numbers.** This project cuts one
test split of 1,000 rows from the 50%-agreement superset. The published papers
use their own splits, and many use ten-fold cross-validation over a subset. Two
numbers on two different splits are not comparable, and the second pass says so
about the subsets already.

**Re-runs fix half of it.** The plans re-run the downloadable models on this
split. That is the right move and it is already there.

**The other half needs one more run.** The shipped models must also run on the
protocol the papers use. One extra evaluation of the final checkpoint, on the
common published protocol, joined to the survey table.

**Do this.**

- Record the exact protocol of each published number in
  the survey table in `PROGRAM_DESIGN.html`, including the fold count.
- Add one run of each shipped model on the most common published protocol.
- Grade that run supported, and mark the protocol difference in the same row.
- Or drop the phrase "state of the art" from the release and say the project
  publishes a new benchmark instead. That is an honest position, and it is
  cheaper.

### 14. No aspect test split exists, and two plan statements disagree

**What the plans say.** `settings.py` sets `data.n_test` to 1,000, and that split
comes from Financial PhraseBank alone. `VERTICAL_SLICES.html` says to pool the
aspect rows with the null-target rows for the headline macro-F1. It also says not
to cut a third split for the aspect rows.

**The two statements cannot both hold.** An aspect row cannot appear in a pooled
headline test number unless an aspect test split exists. Today there is no
aspect test split, no aspect split hash and no aspect row count in the manifest.

**This blocks slice 2, not slice 4.** The definition of done rests on a number
that has no split under it.

**Do this. Choose one and record it.**

1. Cut aspect test rows from FinEntity and FiQA on the `sentence_id` key, freeze
   them, hash them and add them to the manifest. The headline is then a pooled
   number over both kinds of row.
2. Or keep the headline on Financial PhraseBank only, and report every aspect
   number as a named secondary table.

Option 1 matches the product spec. Option 2 matches the config today.

### 15. `data_revision` stays empty, and no Hub revision is pinned

**What the plans say.** The README says `finsent build-data` rebuilds the exact
splits by a join on `example_id`. The registry row carries a `data_revision`
field.

**The field is empty in all eight registry rows.** No loader pins a Hub revision.
`src/finsent/data/` holds no revision string at all.

**Why the hash does not save you.** The split hash proves that the rows this
project used did not change. It cannot rebuild those rows if the source changes
on the Hub. The published `split_assignments.csv` then joins to nothing, and the
release stops being reproducible by a third party. That is the exact promise the
README makes.

**Do this.**

- Pin a Hub revision for every source data set in `settings.py`.
- Pass the revision to every loader.
- Fill `data_revision` on every registry row.
- Add a CI check that fails an empty `data_revision` on a run of kind `bench`.

### 16. The cost table names no serving format

**What the plans say.** Latency at batch size 1, throughput at batch size 32,
peak memory and parameter count, on one stated machine. The definition of done
asks the small model to cost an order of magnitude less than the frontier model
per thousand rows.

**The format decides the number.** A small encoder in plain PyTorch and the same
encoder as a quantised ONNX graph differ by several times on CPU. The cost table
is the argument the release exists to print. It must not use the slowest setting
by accident.

**Do this.**

- State the serving format in `settings.py`: framework, precision and device.
- Report the small model twice, in the plain format and in the served format.
- Publish the served artefact, so a reader reproduces the cost as well as the
  score.

### 17. The negative class holds 136 test rows

**What the plans say.** The primary metric is macro-F1 over three classes. Gap 8
of the second pass asks for a minimum detectable effect on a 1,000-row split.

**The binding number is smaller than 1,000.** The frozen test split holds 136
negative rows, 300 positive rows and 564 neutral rows. Macro-F1 weights the three
class scores equally, so the negative class alone drives one third of the metric
from 136 rows.

**Do the power calculation on the negative class, not on the split size.** A
minimum detectable effect computed from 1,000 rows will be too optimistic. Say
so in the same step, and report the per-class interval beside the macro-F1
interval.

### 18. No rule settles a split decision across the three breakdowns

**What the plans say.** The report gives macro-F1 three ways. All rows,
null-target rows and aspect rows. The definition of done holds six conditions.

**No rule covers the likely case.** One candidate wins on the aspect rows and
loses on the null-target rows. Nothing says which one ships.

**Do this.** Write the tie-break into `settings.py` before the bench runs. State the
order: the pooled macro-F1 first, then the aspect macro-F1, then cost. A rule
written after the table is read is not a rule.

---

## What to do first

Five items. None costs money. Three of them block slice 2, which is the next
slice.

1. Settle the aspect test split. Gap 14. Slice 2 cannot finish without it.
2. Pin the data revisions and fill `data_revision`. Gap 15. It is one config
   change and one CI check.
3. Add the frozen embedding baseline. Gap 1. It runs beside TF-IDF and it can
   change the shape of the whole bench.
4. Record a licence for every candidate checkpoint. Gap 3. Do it before the
   smoke check.
5. Decide the position on the state of the art. Gap 13. Either add the published
   protocol run, or drop the claim.

Two more items block slice 4 and cost nothing today. Write the generated-row
quality gate, gap 6. Write how each weak method produces a target, gap 11.

## Method

I read `README.md`, `DECISIONS_AIM.md`, `GAPS_AIM_2.md`, `REVIEW_AIM.md`, the
four HTML plan documents, the settings, `runs/registry.jsonl`,
`data/processed/fpb/manifest.json` and every file under `src/finsent/`. I checked
the licence and the parameter count of the named checkpoints on the Hugging Face
Hub. I searched the Hub for permissive financial sentiment data sets. I dropped
every finding that `GAPS_AIM_2.md` already names.

I also dropped one finding after I read the code. The word-list scorer looks
like a bare word count in the plan text. It is not. `src/finsent/lexicons/scorer.py`
applies a three-word negation window, and the docstring explains it. The lexical
floor is fairer than the plans make it sound.
