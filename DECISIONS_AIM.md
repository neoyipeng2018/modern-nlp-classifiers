# Decisions taken against the aim review

One entry per gap in `REVIEW_AIM.md`. Written as the decisions were made, 21 August 2026.
Each entry gives the choice and the reason. An entry here is the authority. When a plan
document disagrees with an entry here, the plan document is wrong and gets edited.

---

## A. Size tiers and the bench roster

**Ship six models, not nine and not three.** Small and large, for each of the three tasks.
The medium tier still runs in the bench, and its numbers are published, but no medium model
ships. Most callers want the cheapest model or the best one. The middle tier rarely wins on
either count.

**Tier limits, by parameter count.**

| Tier | Limit | Checkpoints that land there |
|---|---|---|
| Small | 70M or less | Ettin 17M, Ettin 32M, DeBERTa-v3-small 44M, Ettin 68M |
| Medium | 71M to 260M | Ettin 150M, ModernBERT-base 150M, DeBERTa-v3-base 184M, NeoBERT 250M |
| Large | 350M or more | ModernBERT-large 395M, Ettin 400M, Ettin 1B |

The limits follow the real gaps in the roster. No boundary sits on top of a checkpoint.

**Add both missing Ettin sizes.** `jhu-clsp/ettin-encoder-17m` and `jhu-clsp/ettin-encoder-1b`
join the bench. The roster goes from nine checkpoints to eleven. At three seeds that is six
more short runs. Ettin then gives six sizes on one recipe, so the bench prints one clean
accuracy-against-size curve.

**What this changes in the plans.**

1. `PRODUCT.html` "three small encoders" becomes six models over two tiers.
2. The decision-log row "Model size" is replaced by the table above.
3. The bench roster goes to eleven checkpoints in `ARCHITECTURE.html` and `VERTICAL_SLICES.html`.
4. Every task needs two released models, so the release checklist runs twice per task.

---

## B. State of the art

**State of the art means the best published number on the same benchmark.** The target is to
beat the highest score anyone published on FLS, on FiQA 2018 Task 1, and on the fact-versus-
opinion set. This replaces the rule in `PRODUCT.html` that makes beating published work "not a
gate", and the rule in `PROGRAM_DESIGN.html` that bans the words from the write-up.

**Published numbers go in the tables, with a protocol note beside each one.** Every results
table gains two columns: the published score, and a plain statement of how that protocol
differed from this one.

**Warning. This is the exact comparison that forced the last retraction.** The previous project
compared across protocols and had to withdraw the numbers. The decision stands, and three rules
come with it so the failure does not repeat.

1. Every quoted number carries its protocol difference in the same row. A number with no note
   is not publishable.
2. Where the other system is downloadable, re-run it on this project's split instead of quoting
   it. A re-run is a paired comparison. A quote is not.
3. A quoted number is graded **Reported**, never **Supported**. Only a number this project
   measured on its own frozen split can carry the headline.

**New work this creates.**

- A survey step per task, before the bench: collect the published scores, their splits, their
  metrics and their citations. Put them in the config, not in prose.
- A re-run step for every downloadable comparator, starting with `yiyanghkust/finbert-fls`.
- A row in the write-up naming which comparisons are paired and which are quoted.

---

## C. Data boost becomes Track D

**Augmentation is a first-class data track.** It gets its own `label_source` value, its own
split, its own provenance fields, and its own row in the data program. This reverses the
non-goal in `PRODUCT.html` that reads "synthetic data is out of the default plan".

**Three methods get built.**

| Method | What it does | Tasks | Prior evidence |
|---|---|---|---|
| Error-targeted paraphrase | Paraphrase the rows the model gets wrong, keep the label | All three | +2.92 accuracy, +7.84 macro-F1 in `learnings.html` |
| Verbalized Sampling | One call returns several distinct variants with stated probabilities | All three | None. Its gain over plain paraphrase is untested |
| Counterfactual aspect pairs | One sentence, two aspects, opposite labels | ABSA only | None. It also feeds the Slice 2 multi-aspect diagnostic |

Class-balanced generation is **not** built. It stays on the list of things considered and
dropped.

**Warning. The error set must not come from the split that picks the model.** `learnings.html`
records the leak: both augmented sets came from validation errors, and reusing that validation
set for selection made every validation estimate optimistic. Three rules stop it here.

1. Errors are collected on a training-side fold, never on the development split and never on
   the validation split used for checkpoint selection.
2. A paraphrase and its original always land in the same split. The split key is the family,
   not the row.
3. A CI check fails the build when a family straddles two splits.

**The experiment that settles it.** One grouped, multi-seed factorial per task, with equal
sample counts in every arm:

- Arm 1: no augmentation.
- Arm 2: plain targeted paraphrase.
- Arm 3: Verbalized Sampling.

Three seeds each. One variable. This is the experiment `learnings.html` already names and
never ran. Verbalized Sampling must beat plain paraphrase with a confidence interval, or the
write-up keeps the simpler conclusion that targeted augmentation helps.

**Every model is reported twice more.** With Track D and without it, on the same frozen rows.

---

## D. Domain pretraining

**No domain pretrain run. The gap stays open on purpose.** EDGAR remains a sample pool for the
labelling run and nothing else. No masked language modelling step enters the plans.

**What this costs, stated plainly.** The bench answers "which general encoder wins on this
task". It does not answer "which is the best encoder for financial text". Those are different
questions, and the write-up must say which one it answered. The card cannot claim a finance
speciality that no step trained for.

**If this is reopened, the scope is already set.** One run, on the bench winner only, against
the same fine-tune from the public checkpoint. One variable, three seeds. That is the cheapest
honest test, and it needs a decision-log entry to start.

---

## E. Weak supervision widens to five methods

The routed-model pipeline stays exactly as planned. Four methods join it.

| Method | What it buys | Runs on |
|---|---|---|
| Distillation from the large model | The small model learns the large model's judgement | Every task |
| Self-training on EDGAR | Extra training rows for no API money | Every task |
| Intermediate task fine-tune | Public data the plans list and never use | Every task |
| Label noise cleaning | The borrowed labels are known to be imperfect | Every task |

**Distillation is now load-bearing, not optional.** Gap A ships a small model and a large model
for each task. Without distillation the two train the same way from the same rows, and the
small tier gets nothing from the large tier at all. The order is fixed by that: train large,
then distil.

**Intermediate task sources.** Financial PhraseBank for ABSA. NumClaim for forward-looking and
for fact versus opinion. Both are public and both already appear in the plans as candidates
that nothing uses.

**Warning. The ablation count now exceeds the bench.** One variable per experiment is the rule,
and there are now nine things to vary over two shipped tiers and three tasks. Run them in this
order, and stop when the curve flattens.

1. The Track D factorial. Three arms, the largest expected gain.
2. Distillation. Required by the two-tier release, so it runs whatever the result.
3. Intermediate fine-tune. Cheapest of the four, no new data to buy.
4. Self-training. Costs GPU time only.
5. Label noise cleaning. Smallest expected effect, and it changes the training set for
   everything above it, so it runs last or first, never in the middle.

Point 5 matters. Cleaning the labels after the other ablations invalidates them. Either clean
first and run everything on the cleaned set, or clean last and report it as a separate result.
Pick one before the first ablation starts.

---

## F. Finance lexicon baselines

**Add all of them.** One lexicon runner, the same interface as every other baseline.

- Loughran-McDonald word lists, for the sentiment task.
- The Henry word list, beside it. The two disagree often enough to be worth both.
- Forward-looking keyword rules from the accounting literature, for the FLS task.
- The heuristic labelling functions, scored on the test split as baselines in their own right.
  They already exist in the design and nothing scores them. That measurement is free.

**Why this matters more than its cost.** It runs on a laptop, and it sets the floor a finance
reader looks for first. An encoder result with no word-list number beside it invites the
question the whole release is meant to answer.

**It is also the first number this repository can print.** It needs no GPU, no labelling spend
and no open decision. See gap K.
