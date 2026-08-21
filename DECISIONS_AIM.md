# Decisions taken against the aim review

One entry per gap in `REVIEW_AIM.md`, plus the scope change that came out of the walk-through.
Written 21 August 2026.

An entry here is the authority. When a plan document disagrees with an entry here, the plan
document is wrong and gets edited.

---

## SCOPE CHANGE — one task, not three

**The project drops forward-looking detection and fact versus opinion. It builds a financial
sentiment classifier and nothing else.**

Why the change happened. The walk-through reached the fact-versus-opinion fork and looked at
real rows from the candidate benchmark. `gtfintechlab/Numclaim` splits on **time**, not on
**checkability**, so it is a second forward-looking set and not a fact-versus-opinion set at
all. One row settles it:

> "reasons to buy: dte energy's share price gained 17.7% in the last one year, outperforming
> the zacks categorized utility-electric power industry's 0.8% gain, **backed by its focus on
> improving its cost structure**" → labelled `OUTOFCLAIM`

That is a causal, evaluative analyst judgement. The codebook in `PRODUCT.html` calls it opinion
outright. NumClaim calls it out-of-claim because it describes the past. With NumClaim adopted,
tasks 1 and 3 would both split on time, and the thesis of three independent labels would not
survive its own overlap analysis.

Rather than resolve the fork, the scope narrowed. Simpler is the point.

### What the project is now

| | |
|---|---|
| **Task** | Sentence-level financial sentiment. Three classes: positive, negative, neutral. |
| **Input** | One sentence. No aspect. No target span. No passage. |
| **Primary benchmark** | `takala/financial_phrasebank`. 4,840 sentences, agreement tiers, financial news. |
| **Secondary benchmark** | `pauri32/fiqa-2018`. 1,213 rows, tweets and headlines. The out-of-domain read. |
| **Models shipped** | Two. One small, one large. See entry A. |
| **Best means** | Wins on both benchmarks, not one. |

### What this deletes from the plans

- Forward-looking detection, its codebook, its three classes and its whole slice.
- Fact versus opinion, its codebook, the fork, FinArg and NumClaim.
- `FinanceMTEB/FLS` entirely.
- The aspect input, the FiQA aspect taxonomy, the score mapping decision and the multi-aspect
  diagnostic.
- The target span, the marker tokens, the passage builder and the trimming rules.
- Slices 1, 3 and most of 2. Four slices become one.
- The name. "ModernFin Triad" describes a thing that no longer exists.

### Warning, and it needs a decision before Slice 1

FiQA's labels are **aspect-conditioned**. A sentence-level model cannot be scored honestly on a
row whose two aspects carry opposite polarity, because there is no single right answer for the
sentence. Before adopting FiQA as the secondary set, count those rows. Drop them and say how
many, or report them as a separate line. Do not average them away.

---

## A. Size tiers and the bench roster

**Ship two models: one small, one large.** Originally six, over three tasks. With one task it is
two. The medium tier still runs in the bench and its numbers are published, but nothing ships
from it. Most callers want the cheapest model or the best one.

**Tier limits, by parameter count.**

| Tier | Limit | Checkpoints that land there |
|---|---|---|
| Small | 70M or less | Ettin 17M, Ettin 32M, DeBERTa-v3-small 44M, Ettin 68M |
| Medium | 71M to 260M | Ettin 150M, ModernBERT-base 150M, DeBERTa-v3-base 184M, NeoBERT 250M |
| Large | 350M or more | ModernBERT-large 395M, Ettin 400M, Ettin 1B |

The limits follow the real gaps in the roster. No boundary sits on top of a checkpoint.

**Eleven checkpoints in the bench.** `jhu-clsp/ettin-encoder-17m` and `jhu-clsp/ettin-encoder-1b`
join the nine already planned. At three seeds that is 33 runs. Ettin then gives six sizes on one
recipe, so the bench prints one clean accuracy-against-size curve.

**One thing the narrowing makes easier.** The bench ran on one task before and the other two
inherited the winner. There is only one task now, so that inheritance rule and its re-open
condition both disappear.

---

## B. State of the art

**State of the art means the best published number on the same benchmark.** Financial
PhraseBank is heavily published, so this is a real and checkable target. It replaces the rule in
`PRODUCT.html` that makes beating published work "not a gate", and the rule in
`PROGRAM_DESIGN.html` that bans the words from the write-up.

**Published numbers go in the tables, with a protocol note beside each one.**

**Warning. This is the exact comparison that forced the last retraction.** Three rules come with
the decision.

1. Every quoted number carries its protocol difference in the same row. A number with no note
   is not publishable.
2. Where the other system is downloadable, re-run it on this project's split instead of quoting
   it. A re-run is paired. A quote is not.
3. A quoted number is graded **Reported**, never **Supported**.

**Financial PhraseBank makes rule 2 easy and rule 1 essential.** `ProsusAI/finbert` and
`yiyanghkust/finbert-tone` are both downloadable and both were built for this exact task, so
they get re-run rather than quoted. But published FPB numbers come from several different
agreement subsets — 50%, 66%, 75% and all-agree — and from different splits. A score on the
all-agree subset is not comparable to a score on the 50% subset. Record the subset in every row.

**New work this creates.**

- A survey step before the bench: collect published FPB and FiQA scores, their subsets, their
  splits, their metrics and their citations. Put them in the config, not in prose.
- A re-run step for `ProsusAI/finbert` and `yiyanghkust/finbert-tone` on this project's split.

---

## C. Data boost becomes Track D

**Augmentation is a first-class data track**, with its own `label_source` value, its own split
and its own provenance. This reverses the non-goal in `PRODUCT.html`.

**Two methods get built.** The third, counterfactual aspect pairs, is dropped with the aspect
input.

| Method | What it does | Prior evidence |
|---|---|---|
| Error-targeted paraphrase | Paraphrase the rows the model gets wrong, keep the label | +2.92 accuracy, +7.84 macro-F1 in `learnings.html` |
| Verbalized Sampling | One call returns several distinct variants with stated probabilities | None. Its gain over plain paraphrase is untested |

Class-balanced generation was considered and dropped.

**Track D is now the largest single lever in the project.** Domain pretraining is out, the
aspect work is out, and two of three tasks are out. What remains is a bench, a set of weak
labels, and this. The prior numbers came from this exact task on this exact dataset, so they
transfer directly rather than by analogy.

**Warning. The error set must not come from the split that picks the model.** `learnings.html`
records the leak: both augmented sets came from validation errors, and reusing that validation
set for selection made every validation estimate optimistic. Three rules stop it.

1. Errors are collected on a training-side fold, never on the development split and never on
   the validation split used for checkpoint selection.
2. A paraphrase and its original always land in the same split. The split key is the family,
   not the row.
3. A CI check fails the build when a family straddles two splits.

**The experiment that settles it.** One grouped, multi-seed factorial with equal sample counts:

- Arm 1: no augmentation.
- Arm 2: plain targeted paraphrase.
- Arm 3: Verbalized Sampling.

Three seeds each. One variable. `learnings.html` already names this experiment and never ran it.
Verbalized Sampling must beat plain paraphrase with a confidence interval, or the write-up keeps
the simpler conclusion that targeted augmentation helps.

**Every model is reported twice.** With Track D and without it, on the same frozen rows.

---

## D. Domain pretraining

**No domain pretrain run. The gap stays open on purpose.** No masked language modelling step
enters the plans.

**What this costs, stated plainly.** The bench answers "which general encoder wins on this
task". It does not answer "which is the best encoder for financial text". The write-up must say
which one it answered, and the card cannot claim a finance speciality that no step trained for.

**The narrowing sharpens this.** `ProsusAI/finbert` and `yiyanghkust/finbert-tone` are both
domain-pretrained models on this exact task. They are now baselines under entry B. If a
domain-pretrained BERT beats every general encoder in the bench, that is the answer to the
question this entry declined to ask, and it arrives for free.

**If reopened, the scope is set.** One run, on the bench winner only, against the same
fine-tune from the public checkpoint. One variable, three seeds. It needs a decision-log entry.

---

## E. Weak supervision widens to five methods

The routed-model pipeline stays as planned. Four methods join it.

| Method | What it buys |
|---|---|
| Distillation from the large model | The small model learns the large model's judgement |
| Self-training on unlabelled financial news | Extra training rows for no API money |
| Intermediate task fine-tune | Public data the plans list and never use |
| Label noise cleaning | The borrowed labels are known to be imperfect |

**Distillation is load-bearing, not optional.** Entry A ships a small model and a large model.
Without distillation the two train the same way from the same rows, and the small tier gets
nothing from the large tier. The order is fixed by that: train large, then distil.

**Intermediate task source.** FiQA, SemEval-2017 Task 5, or the FPB 50%-agreement subset used to
warm up a model that then trains on the all-agree subset. The last of these is free and is the
obvious first try.

**Self-training corpus.** Financial news sentences, not EDGAR. EDGAR is filing prose and this
task is news sentiment. The corpus has to match the task, and the narrowing changed which
corpus that is.

**Warning. The ablation count exceeds the bench.** One variable per experiment is the rule.
Run them in this order and stop when the curve flattens.

1. The Track D factorial. Three arms, the largest expected gain.
2. Distillation. Required by the two-tier release, so it runs whatever the result.
3. Intermediate fine-tune. Cheapest, no new data to buy.
4. Self-training. GPU time only.
5. Label noise cleaning. **Fix its position before the first ablation starts.** It changes the
   training set under everything above it, so it runs first or last, never in the middle.
   Cleaning after the other ablations invalidates them.

---

## F. Finance lexicon baselines

**Add all of them.** One lexicon runner, the same interface as every other baseline.

- Loughran-McDonald word lists. The standard finance sentiment dictionary.
- The Henry word list. The two disagree often enough to be worth both.
- The heuristic labelling functions, scored on the test split as baselines in their own right.
  They already exist in the design and nothing scores them. That measurement is free.

Forward-looking keyword rules are dropped with the forward-looking task.

**The narrowing raises the stakes here.** Loughran-McDonald is *the* baseline for financial
sentiment. It is not an optional extra on this task, it is the number every reader checks
first. An encoder result with no word-list score beside it invites exactly the question the
release exists to answer.

**It is also the first number this repository can print.** No GPU, no labelling spend, no open
decision. See entry K.

---

## G. Benchmarks, and the Financial PhraseBank subsets

**Primary: `takala/financial_phrasebank`. Secondary: `pauri32/fiqa-2018`.** A model that wins on
both is the one this project calls best. FiQA is news and social text against FPB's news
sentences, so it doubles as the out-of-domain read the release checklist promises.

**All four agreement subsets are reported.** 50%, 66%, 75% and all-agree. One table, four rows.
It shows how the score tracks annotator agreement, which is the closest thing this task has to a
human ceiling.

**Warning. The four subsets are nested, so they cannot each have their own test split.** Every
all-agree row is also a 50%-agree row. Cutting four independent test splits is impossible, and
cutting four overlapping ones leaks. One rule fixes it:

1. Cut **one** test split from the 50%-agree superset, and freeze it.
2. Record the agreement tier of every row in that split.
3. Report macro-F1 on the whole split, then as a breakdown by tier.

That gives four comparable numbers from one frozen set, with no leakage and no re-splitting.
The all-agree number stays comparable to MTEB, which benchmarks on that subset at 2,264 rows.

**Warning. FiQA labels are aspect-conditioned.** A sentence-level model cannot be scored
honestly on a row whose two aspects carry opposite polarity. Count those rows before adopting
the set. Drop them and say how many, or report them on a separate line. Do not average them
away.

---

## H. The bench pick reads human labels, through grouped k-fold

**Five-fold grouped cross-validation over the human rows that are not in the test split.** Every
human row is used for training and for picking, at different times. The frozen test split is
never opened for the bench.

This removes the fault outright. The old plan picked the backbone on validation rows carrying
router labels, which is the same machine-written-key problem the project removed from its
headline.

**Warning. Financial PhraseBank ships no document identifier, so "grouped" has no natural key.**
The sentences come from news articles and the article is not recorded. Without a key, grouped
k-fold is plain k-fold wearing a different name. Two keys are available and both are used:

1. **Paraphrase family.** Required by Track D. An original and every variant of it share one
   fold. This is the key that matters most, because it is the leak `learnings.html` recorded.
2. **Near-duplicate cluster.** Computed on full text before folding. FPB repeats boilerplate
   phrasings across sentences, so this catches what the missing article id would have caught.

The model card must state that article-level grouping was not possible, rather than implying a
grouped split that never happened.

**Cost.** Eleven checkpoints, three seeds, five folds. 165 short runs, against 33 for the plain
version. Price it at the smoke check before committing.

---

## I. Holm correction across the bench

**Every candidate is tested against the incumbent leader, and the family of eleven tests is
Holm-adjusted.** The rule goes into the config before the bench runs, not after the table is
read.

**Warning. This makes a declared tie the likely outcome, and that is accepted.** Holm plus
eleven candidates plus modern encoders of similar size on one classification task points one
way: no separation. The plans already treat a flat bench as a finding rather than a failure, and
the tie-break rule already exists — the cheaper checkpoint ships and the card says the pick was
made on cost.

Two things follow, and they are not optional.

1. Do not add seeds hunting for a separation the correction removed. The plans forbid it
   already. With 165 runs the temptation is larger, because the marginal run looks cheap.
2. The write-up leads with the tie if there is one. "The backbone did not matter at this data
   scale, so pick on cost" is a useful result for a reader, and it is the honest reading of a
   corrected flat bench.
