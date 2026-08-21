# Gap review, second pass, against the full aim

Written 21 August 2026. This review reads the aim as the owner stated it, and it
reads every plan document and every source file in the repository against that
aim.

## The aim, as stated

Build the best small, medium and large encoders or classifiers for financial
text. Cover aspect based sentiment and plain sentiment. Explore the models that
exist. Explore data boost methods. Explore weak supervision and other methods.
Compare against lexical baselines. Release the models, the data method and
everything else in public, at the state of the art.

## What the repository holds today

The skeleton runs. The data build runs. Four baselines have real numbers on a
frozen development split. `DECISIONS_AIM.md` holds thirteen decisions. Those
decisions answer the first aim review well.

The four HTML plan documents are older than those decisions. They still describe
three tasks, an aspect input and a passage builder. `DECISIONS_AIM.md` entry L
orders one new document. Nobody wrote it.

## What the 21 August plan rewrite closed

The owner answered gaps 1, 2 and 5 on 21 August 2026, and the four HTML plan
documents were rewritten to match. Gap 10 closed with them.

| # | Gap | What was decided |
|---|---|---|
| 1 | Aspect based sentiment | Put back. It is the whole task now. Plain sentence sentiment is the null-target case, so vanilla comes free. |
| 2 | The medium model | Two tiers ship, small and large. The medium tier stays in the bench as points on the size curve and leaves the corrected test family, which buys statistical power. |
| 5 | The frontier baseline | `gpt-5.6-sol` at medium reasoning effort. It was already pinned in the plans. It is now in `configs/base.yaml` as well, so it is a value and not prose. The cost table is specified. |
| 10 | The stale plan documents | All four rewritten. `assets/src` and `assets/build.py` were deleted, because the fragments were older than the root files and the build would have overwritten the newer text. |

The other thirteen gaps stay open and the text below is unchanged.

## Summary

Seventeen gaps. Gap 1 to gap 5 change the shape of the project. Gap 6 to gap 12
change the result. Gap 13 to gap 17 are hygiene, and they are cheap.

| # | Gap | Size |
|---|---|---|
| 1 | Aspect based sentiment is deleted from the plans | Large |
| 2 | The medium model does not ship | Medium |
| 3 | The primary data set is non-commercial, so the public release cannot hold it | Large |
| 4 | No state of the art target number is written down | Large |
| 5 | No large language model baseline, and no cost measure | Large |
| 6 | Weak supervision names no corpus, no label model and no budget | Large |
| 7 | Data boost names no generator, so the generated rows have no licence | Medium |
| 8 | No power calculation, so a flat bench has no meaning | Medium |
| 9 | No robustness test and no time drift test | Medium |
| 10 | The four HTML plan documents are stale | Medium |
| 11 | The release artefacts do not exist | Medium |
| 12 | The lexical baseline set is incomplete | Small |
| 13 | Nobody checked the labels of the frozen test split | Small |
| 14 | No learning curve, so the data spend has no guide | Small |
| 15 | The development split has no reuse limit | Small |
| 16 | Three decision log items stay open | Small |
| 17 | No compute budget and no plan of record | Small |

---

## 1. Aspect based sentiment is deleted from the plans

**What the plans say.** The scope change in `DECISIONS_AIM.md` deletes the aspect
input, the FiQA aspect taxonomy, the target span and the marker tokens. The
project became one sentence-level task with three classes.

**What the aim says.** Cover aspect based sentiment and plain sentiment.

**The conflict is direct.** The plans cannot meet the aim. One of the two must
change, and only the owner can decide which.

**The delete was correct for the reason given.** The walk-through deleted the
aspect work together with two other tasks. It deleted three things because one
of them, fact against opinion, had a broken benchmark. Aspect sentiment did not
have that problem. It went out with the rest.

**What aspect based sentiment costs, if you put it back.**

- A second label schema. One row carries a text, a target, and a polarity for
  that target.
- A second model contract. The input is a pair, not a sentence.
- A second metric. Score each target, then average over targets, not over rows.
- A second benchmark. FiQA 2018 Task 1 carries aspects. `yixuantt/FinEntity`
  carries entity-level sentiment and its licence is ODC-BY, which is permissive.
- A second baseline. A word list near the target span is the honest floor.

**What it buys.** Real users ask about one company in a sentence that names
three. A sentence-level model cannot answer that. This is the difference
between a demonstration and a tool.

**Do this.** Decide the scope in one line, and record it in `DECISIONS_AIM.md`.
Choose one of three:

1. Plain sentiment only. Then correct the aim, and say the aspect work is out.
2. Plain sentiment first, aspect second, as a phase two with its own gate.
3. Both from the start. Then the bench doubles, and the timeline doubles.

Option 2 is the smallest change that keeps the aim true.

---

## 2. The medium model does not ship

**What the plans say.** `DECISIONS_AIM.md` entry A ships two models, one small
and one large. The medium tier runs in the bench, and its numbers are published,
but nothing ships from it.

**What the aim says.** Small, medium and large.

**The reason in entry A is thin.** It says most callers want the cheapest model
or the best one. That is true for a product. It is not true for a public
release. The medium tier is where ModernBERT-base and DeBERTa-v3-base sit, and
those are the two checkpoints most readers will compare against.

**The cost of the fix is near zero.** The bench already trains the medium tier at
three seeds. To ship the medium winner you add one distillation run and one
model card.

**Do this.** Change entry A to three tiers. Ship the winner of each tier.

---

## 3. The primary data set is non-commercial, so the public release cannot hold it

**What the plans say.** Entry J takes the position that trained weights are not a
derivative work of the training text. It forbids the redistribution of any
Financial PhraseBank text. It publishes row identifiers and split assignments
only. That position is careful, and the code follows it.

**What is still missing.** The aim says release the data method and everything
else. Under entry J the benchmark itself stays behind a non-commercial licence.
A reader can rebuild the split, but only if the source stays available and
unchanged. The release has no evaluation set that you own.

**This is the largest risk to the release.** Every headline number rests on one
data set from 2014 that you may not redistribute.

**Do this. Build a test set that you own.**

1. Collect financial news sentences from a source with a permissive licence.
2. Label 1,000 to 2,000 sentences with the same three classes.
3. Use two or three annotators, and record the agreement.
4. Publish the text, the labels and the codebook under CC-BY.

**This one step fixes four problems at once.** It gives the release a data set.
It gives the project a modern test set, so gap 9 closes. It gives a second
benchmark that no published model has seen, so contamination stops being a
worry. It gives a real human agreement number, which is the ceiling the encoder
scores are read against.

**Warning. Do not skip the agreement measurement.** A single-annotator set has
no ceiling, and a score above it means nothing.

---

## 4. No state of the art target number is written down

**What the plans say.** Entry B defines the state of the art as the best
published number on the same benchmark. It asks for a survey step before the
bench. It sets three rules for every quoted number.

**What is missing.** The survey did not happen. No file holds a published
Financial PhraseBank score, its agreement subset, its split, its metric or its
citation. Entry B says to put them in the config. The config holds none.

**Why this blocks work, not just the write-up.** You cannot design a bench that
beats a target you never wrote down. The target also sets the size of the test
split, because a small gap needs many rows. See gap 8.

**Do this, before the first GPU run.**

1. Collect ten to twenty published Financial PhraseBank results.
2. Record the agreement subset for each one. The 50 percent subset and the
   all-agree subset are not comparable.
3. Record the split, the metric, the seed count and the citation.
4. Put the table in `configs/published.yaml`, not in prose.
5. Re-run every model that you can download, on your own split.

**Two re-runs are already named.** `ProsusAI/finbert` and
`yiyanghkust/finbert-tone`. Add `FinanceInc/auditor_sentiment` and any recent
finance encoder that has weights on the Hub.

---

## 5. No large language model baseline, and no cost measure

**What the plans say.** Nothing. The bench holds eleven encoders, four
baselines, and two FinBERT re-runs.

**The first question every reader asks.** "Why not prompt a large language
model?" The release exists to answer that question, and it has no number for it.

**The second question.** "How much cheaper is the small model?" Entry I says the
tie-break rule picks the cheaper checkpoint. No file defines cheaper.

**Do this.**

1. Add a zero-shot large language model baseline on the frozen split. Use one
   open-weight model and one hosted model.
2. Add a few-shot version of the same prompt.
3. Record the prompt, the model version and the date in the registry.
4. Measure cost for every system. Record latency at batch size 1, throughput at
   batch size 32, peak memory, and parameter count, on one stated machine.
5. Print one table of macro-F1 against cost. That table is the argument for a
   small encoder, and it is the most useful thing the release can publish.

**Warning. A hosted model changes under its own name.** Record the exact model
version and the run date, or the number is not reproducible.

---

## 6. Weak supervision names no corpus, no label model and no budget

**What the plans say.** Entry E lists five methods. Distillation from the large
model. Self-training on unlabelled financial news. Intermediate task fine-tune.
Label noise cleaning. The routed-model pipeline from the older plans.

**Three things are missing, and each one blocks the work.**

**The corpus has no name.** Entry E says financial news sentences, not EDGAR.
That is a direction, not a data set. Self-training needs a real corpus with a
real licence and a real hash. Name it. Check that it does not overlap the test
split.

**The label model has no name.** The older plans describe heuristic label rules
and a routed model. No document says how you combine several weak labels into
one. Majority vote and a learned label model give different answers. Choose one,
and write it down.

**The weak label quality has no measure.** Weak labels are only useful if you
know how wrong they are. Score every weak label source against the human labels
on a held-out human slice. Publish that table.

**The budget stays open.** Entry J says the labelling budget still gates the
first router spend. No number exists. Set a cap in dollars before the first
call.

**One more thing is missing.** No experiment varies the mix of weak rows and
human rows. That ratio is the main knob in weak supervision. Add one sweep. Use
0, 1, 3 and 10 weak rows for each human row.

---

## 7. Data boost names no generator, so the generated rows have no licence

**What the plans say.** Entry C makes augmentation Track D. It builds
error-targeted paraphrase and Verbalized Sampling. It sets three anti-leak rules,
and the code already enforces the family rule.

**The leak rules are good. The licence rule is missing.** Entry C never says
which model writes the paraphrases. That choice decides whether you can release
the generated rows and the weights that train on them. Some hosted model terms
restrict the use of their output. Some do not.

**Do this, before the first generation run.**

1. Choose the generator model, and record its name and its terms.
2. Prefer an open-weight generator. It keeps the release clean.
3. Warning. Check the terms before the run, not after. A rerun costs money
   twice.

**A second check is missing.** Nothing compares a generated row against the
frozen test split. A paraphrase that lands near a test row is a leak by another
route. Add a near-duplicate check between every generated row and the test
split. Fail the build on a hit.

**A third gap.** Track D grows synthetic rows only. Several permissive human
data sets exist and the plans use none of them. Real rows beat synthetic rows.
Add a step that pulls permissive human data before the synthetic step.

---

## 8. No power calculation, so a flat bench has no meaning

**What the plans say.** Entry I applies the Holm correction across eleven
candidates. It accepts a declared tie as the likely outcome. Entry H prices 165
runs.

**The missing step.** Nobody computed the smallest gap that a 1,000-row test
split can detect, after the Holm correction, across eleven candidates. Without
that number a tie has two readings. Either the backbones are equal, or the test
split is too small to tell. Those are different findings.

**Do this, before you spend the 165 runs.**

1. Compute the minimum detectable effect. Use the observed class balance and the
   bootstrap already in `src/finsent/eval/`.
2. If the minimum detectable effect is larger than the gaps in the published
   literature, the bench cannot answer its own question.
3. Then choose. Grow the test split, or cut the candidate count, or state up
   front that the bench measures a tie.

**Cutting the candidate list is the cheapest fix.** Eleven candidates cost power.
Six candidates on the same rows detect a smaller gap.

---

## 9. No robustness test and no time drift test

**What the plans say.** Entry M adds an error analysis step. That step reads the
confusion matrix, and it feeds Track D.

**Error analysis is not a robustness test.** It looks at the rows the model got
wrong on one split. It does not probe the failures that matter in finance.

**Four probes are missing, and each one is cheap.**

1. Negation. "Profit did not fall" against "profit fell".
2. Numbers. Change 5 percent to 50 percent, and check that the label moves.
3. Company names. Swap the company name, and check that the label holds.
4. Direction words. Swap rose and fell, and check that the label flips.

**Build these by hand.** Two hundred pairs are enough. Publish them. A behaviour
test set is a real contribution, and it costs one afternoon.

**Time drift has no test at all.** Financial PhraseBank holds news from about
2014. Nothing measures the model on 2026 text. The permissive test set in gap 3
closes this. Label recent news, and report the score beside the old score.

---

## 10. The four HTML plan documents are stale

**What the plans say.** Entry L orders one document to replace the four. It lists
what to keep and what to drop.

**Nobody wrote it.** `PRODUCT.html`, `PROGRAM_DESIGN.html`, `ARCHITECTURE.html`
and `VERTICAL_SLICES.html` still describe three tasks, an aspect input, a
passage builder and a length ladder. Together they hold over two hundred
mentions of deleted work.

**This is a real risk, not untidiness.** A new reader opens `PRODUCT.html` first,
because its name says product. That file is wrong on the first page. A future
agent will build the wrong thing from it.

**Do this now. It needs no decision and no money.**

1. Write one `PLAN.md` from entry L.
2. Delete the four HTML files, or move them under `archive/` with a header that
   says they are superseded.
3. Fix the repository name and the project name in one pass.

---

## 11. The release artefacts do not exist

**What the plans say.** `PRODUCT.html` holds a release checklist. Entry J sets
three licence rules for the model card.

**What is missing, item by item.**

- No model card template.
- No dataset card for the split assignments that you do publish.
- No script that a third party runs to reproduce a number end to end.
- No version policy. A model card without a version cannot be corrected later.
- No Hugging Face organisation name, and no reserved model names.
- No demo, so a reader cannot try the model before they download it.
- No rule for outside submissions, so the benchmark cannot grow.

**Do this.** Write the model card template now, and fill it as the numbers
arrive. An empty card with the right sections stops a rushed card at the end.

---

## 12. The lexical baseline set is incomplete

**What is done, and done well.** Loughran-McDonald and Henry both run.
TF-IDF with logistic regression runs. The abstention rates are reported, and the
README reads them honestly.

**Four items are missing.**

1. **The word lists are under-sold.** The rule is the sign of positive hits minus
   negative hits. That throws away the count. Add one hybrid baseline. Feed the
   word list counts into logistic regression. This is the fair lexical baseline,
   and any encoder must beat it.
2. **VADER is missing.** It is the baseline a non-finance reader expects.
3. **The answered-only score is missing.** The word lists are silent on about 65
   percent of rows, and every silent row becomes neutral. Report the macro-F1 on
   the answered rows beside the full score. Two numbers tell the true story.
4. **The FinBERT re-runs are not built.** Entry B names them. They are the
   nearest published competitor, and they need no training.

**One open item.** The Henry word list in the repository comes from published
reproductions. Nobody checked it against the original paper. Its grade is
reported, which is honest. Check it, or drop it.

---

## 13. Nobody checked the labels of the frozen test split

**What the plans say.** The harness refuses any evaluation split that holds a
non-human label. That rule is good, and the code enforces it.

**A human label is not a correct label.** Financial PhraseBank has known label
noise. The 50 percent agreement subset holds rows where half the annotators
disagreed. Your test split is cut from that superset.

**Why this caps the project.** If five percent of the test labels are wrong, no
model can score above 95 percent, and the gaps near the top are noise.

**Do this.** Re-check a sample of 200 test rows by hand. Report the error rate.
That single number sets the ceiling for every claim in the release.

**Warning. Do not correct the test labels quietly.** A corrected split is a new
split with a new hash. Publish both, and say which one each number used.

---

## 14. No learning curve, so the data spend has no guide

**What is missing.** No experiment varies the size of the training set.

**Why it matters more than it looks.** The project plans to spend money on weak
labels and on generated rows. A learning curve tells you whether more rows help
at all. If the curve is flat at 3,000 rows, then Track D and weak supervision
both fail before they start, and you save the spend.

**Do this. It is cheap.** Train the bench winner on 10, 25, 50 and 100 percent of
the training rows, at three seeds. Plot macro-F1 against row count. Run it
directly after the bench, and before Track D.

---

## 15. The development split has no reuse limit

**What the plans say.** Entry H picks the backbone with grouped five-fold
cross-validation. The frozen test split stays closed. That is correct.

**The development split carries too much.** It has 500 rows. The plans use it for
the baselines, the temperature scaling, the head and pooling comparison, the
error analysis and the Track D arms. Every decision that reads it makes the
final development number more optimistic.

**Do this. Choose one.**

1. Cut a second development split, and hold it closed until the end.
2. Or count the decisions that read the development split, publish the count,
   and treat every development number as optimistic.

Option 1 costs 500 rows. Option 2 costs nothing but honesty.

---

## 16. Three decision log items stay open

Entry E, point 5 says to fix the position of label noise cleaning before the
first ablation starts. It is not fixed. Cleaning changes the training set under
every other ablation. Put it first or last. Write it down.

Entry J says the labelling budget stays open and gates the first router spend.
Set the cap.

Entry F and the README both flag the Henry word list source. Check it against
the paper, or drop the list.

---

## 17. No compute budget and no plan of record

**What is missing.** No document says how many GPU hours the project has, what
they cost, or in what order the runs happen.

**The run count is already large.** Entry H prices 165 runs for the bench alone.
Entry C adds a three-arm factorial at three seeds. Entry E adds five methods.
The learning curve in gap 14 adds twelve more runs. Nothing counts the total.

**Do this.**

1. Count every planned run, and multiply by the measured cost of one smoke run.
2. Set a cap.
3. Order the work, and name the gate that stops each step.

**The order that entry E gives is good, and it should apply to the whole
project.** Run the largest expected gain first. Stop when the curve flattens.

---

## The smallest change that makes the plans match the aim

Six steps, in order. The first three need a decision from the owner. The rest
need work, not money.

1. Decide the aspect scope. Gap 1.
2. Decide the tier count. Gap 2.
3. Decide the licence route for the released benchmark. Gap 3.
4. Write the published-number survey into the config. Gap 4.
5. Write one plan document, and archive the four stale ones. Gap 10.
6. Add the large language model baseline and the cost table. Gap 5.

Steps 4, 5 and 6 need no GPU and no spend. Start them today.

## Method

I read `README.md`, `DECISIONS_AIM.md`, `REVIEW_AIM.md`, `REVIEW.md`, the four
HTML plan documents, `configs/base.yaml`, every file under `src/finsent/`, the
tests, and `runs/registry.jsonl`. I searched the Hugging Face Hub for the data
sets named in this review, and I checked their licences on the Hub.
