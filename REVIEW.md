# Plan review: can this repo improve itself?

Reviewed 2026-08-18 against `PRODUCT.html`, `PROGRAM_DESIGN.html`, `ARCHITECTURE.html`, `VERTICAL_SLICES.html`.

The question asked was narrow. Is there a valid benchmark to hill climb towards?
The answer is no, for six separate reasons. Four are design faults that can be fixed by editing
the plans. Two are facts about the borrowed data that the plans get wrong.

Findings are ordered by how much they block progress. Findings 3 and 4 were fixed in the plans
on 2026-08-18 and are kept here as the record of why. Finding 10 was added afterwards.

---

## 1. There is nothing to run

The repository holds five HTML files and one build script. That is all.

Every gate, assertion, CI check, registry, codebook, harness and test named in the plans is
described but does not exist. There is no `src/`, no `tests/`, no `configs/`, no
`runs/registry.jsonl`, no `docs/codebook/`.

So today the repo has no score of any kind. Not a bad score, no score. Self improvement needs
a starting number, and the first one only arrives after Slice 1 steps 1 through 21. Those steps
include buying LLM labels over three length rungs. That is thousands of dollars and weeks of
work before the first data point exists.

**Fix.** Bring the small, cheap parts of Slice 1 forward. Repo skeleton, config hashing,
registry, the TF-IDF baseline and a fixed dev harness can all be built and run before any money
is spent. See finding 8.

---

## 2. The headline metric is unreadable while you work

The headline is agreement with cached `gpt-5.6-sol` labels on a frozen 5,000 passage set.

Operating principle 4 forbids looking at the test set. Gate 6 opens it once per model, at the
end. So the single number that defines success is off limits during development.

What is left to steer by is validation macro-F1 against weak labels written by cheap teacher
models. That is a different target, produced by different models, at a different tier. Nothing
in the plan measures how well the validation number predicts the headline number.

That is the core problem. You cannot hill climb a hill you are not allowed to look at, using an
altimeter nobody has calibrated.

**Fix.** Carve a readable development slice out of the reference set. Take 500 of the 5,000
reference labelled passages, mark them as dev, and score them on every run. Publish the headline
on the remaining 4,500, which stays frozen and unopened.

This contradicts the current rule that the reference "touches the test split and nothing else".
Change that rule on purpose and write down why. The rule as written was meant to stop the
weak-to-strong result being engineered. Reserving a dev slice does not do that, as long as the
labelling functions and the label model are still tuned only on the borrowed human dev set.

---

## 3. The length ladder is measured against three different answer keys

> **Fixed 2026-08-18.** The plans now specify one answer key, written at full passage length,
> scored across all three rungs. See the Track R rules and the reference set section in
> `PROGRAM_DESIGN.html`, and step 6b in `VERTICAL_SLICES.html`. The per-rung reference passes were
> dropped rather than demoted, which also removes two of the three reference labelling runs.

Slice 1 step 6b says: run the reference over the sampled passages "once at each rung".
Program design repeats it. The reference reads 512 tokens for the 512 rung and 8,192 tokens
for the 8,192 rung.

That produces three different answer keys. Agreement at 512 is measured against a key the
reference wrote after reading 512 tokens. Agreement at 8,192 is measured against a different
key. A student scoring 95% at both rungs has told you nothing, because the two 95% figures
refer to different sets of labels.

The ladder is described as the project's actual contribution. As specified it cannot produce a
readable result.

**Fix.** One answer key for the whole ladder. The reference reads the full passage once, at the
longest rung the row supports. Every rung of the student is scored against that one key.

Keep the per-rung reference run, but demote it. It answers a genuinely interesting side
question, which is how much the reference's own answer moves when you give it more context.
That is a diagnostic, not the key.

---

## 4. The context-sensitivity probe cannot tell context from noise

> **Fixed 2026-08-18.** Three passes per condition, with a row counting as context sensitive only
> when the between-condition flip rate beats the within-condition rate. Both rates are published,
> and the report card carries a field for each. The reference is named as the model that runs the
> probe, resolving the contradiction with `PRODUCT.html`.

The plans define the long-evidence half as the rows where the model's answer changes between
the bare sentence and the full passage.

The same documents state, correctly, that a reasoning model asked the same question twice can
answer differently. Program design says so under Track R. Architecture repeats it.

So the probe compares one sample under condition A against one sample under condition B, and
attributes every difference to the condition. Some of those flips are just the model
disagreeing with itself. There is no self-consistency control anywhere in the design.

This matters more than it sounds. The probe defines the split that the entire long-context
claim is read on. If a chunk of that split is sampling noise, the flagship result is unsound
in a way no downstream care can repair.

**Fix.** Run each condition at least three times. Measure the within-condition flip rate. A row
counts as context sensitive only when the between-condition flip rate exceeds it. Publish both
rates side by side.

**Also.** The documents disagree about who runs the probe. `PRODUCT.html` says the teacher
ensemble does it. `PROGRAM_DESIGN.html` and `VERTICAL_SLICES.html` say the pinned reference does.
Those are different experiments with different contamination properties. Pick one.

---

## 5. Passage reconstruction is gated on the wrong statistic

Gate 2 requires that 60% of a task's test rows "recover a real passage". The plan calls FLS
recovery "entirely automatable" with a "Good" outlook.

Recovery is not the hard part. Uniqueness is, and the plan never measures it.

`FinanceMTEB/FLS` ships three columns: `text`, `label`, `label_text`. No CIK. No accession
number. No company. No filing year. To rebuild the passage you must find the sentence in EDGAR
and then decide which filing it came from. Nothing in the row helps you decide.

I measured this. 120 random rows from the 1,000 row FLS test split, queried against EDGAR
full-text search restricted to form 10-K. 105 queries returned cleanly.

| EDGAR 10-K filings containing the sentence | Rows | Share |
|---|---:|---:|
| 0, unrecoverable | 10 | 10% |
| exactly 1, unambiguous | 28 | 27% |
| 2 to 5 | 35 | 33% |
| 6 to 20 | 17 | 16% |
| more than 20 | 15 | 14% |

Gate 2 as written passes comfortably, at about 90%. But only 27% of rows resolve to one filing.
For the other 63% the pipeline picks a passage from between 2 and dozens of candidates, and the
passage it picks is probably not the one the annotator read.

The ambiguity is concentrated in the worst place. Median candidate count is 1 for specific FLS,
2 for not-FLS, and 5.5 for non-specific FLS. Non-specific FLS is the class the codebook calls
the hard boundary, and it is the class the long-context claim most needs to get right.

Scaling the unique-match share to the full test split gives roughly 270 usable rows. Apply the
plan's own rule that the context-sensitive half must be at least 10% of recovered rows, and the
long-evidence subset is around 27 rows. A paired bootstrap over 27 rows across three rungs and
three seeds cannot separate anything.

**Also.** EDGAR full-text search only indexes filings from 2001-05-04 onward. The FinBERT-FLS
annotation effort drew on older 10-Ks as well. Any pre-2001 row is invisible to this route
entirely, which is part of the 10% that returned nothing.

**Fix.** Gate 2 counts unique matches, not any match. Rows with more than one candidate filing
are marked ambiguous and are scored at sentence length, the same as rows that failed to match.
Then re-read the 60% bar against the real number, which is closer to 27%, and decide honestly
whether FLS has a long-context story at all.

This is the same failure shape as the previous project's truncated long-context data. The gate
passes, the data is silently wrong, and the conclusion drawn is about length when it is really
about the data.

---

## 6. No quality gate can fail

Gate 6 is the success bar. Its own text says: "If it fails: the model still ships." So it does
not gate anything.

Its two numeric conditions cannot fail either.

**The 95% agreement bar has nothing behind it.** No measurement, no reference point, no
argument. The risk register then says that if the teacher ensemble's ceiling turns out to be
below 95%, "either lower the bar and say why". A bar you plan to move when you miss it is not a
bar. On a three-class judgement task, two different frontier models typically agree well below
95%, so missing it is the likely outcome.

**The 50x cost bar is a tautology.** `gpt-5.6-sol` costs $5 per million input tokens and $30 per
million output tokens, plus billed reasoning tokens. A 150M encoder on rented GPU is cheaper by
something closer to three orders of magnitude. The gate cannot fail and therefore measures
nothing.

Of the seven gates, only 1, 2, 3, 4, 5 and 7 can actually stop work, and all six are about
process rather than model quality. There is no condition anywhere under which the plan says the
models are not good enough.

**Fix.** Set the agreement bar after step 10 measures the teacher ensemble's own agreement with
the reference, and write it into the config then. Make Gate 6 block the *claim*, not the
weights. Replace the 50x cost gate with the break-even volume figure the baseline program
already asks for, which is the number a reader actually needs.

---

## 7. Factual errors and leftovers

**The reference model id was wrong in all four documents.** *Fixed 2026-08-18, twelve occurrences.*
They said `gpt-sol-5.6`. The real API identifier is `gpt-5.6-sol`. Gate 1 exists to catch exactly this, but the wrong string is
already baked into the report card schema, the decision log and the slice steps. Worth noting
that `medium` is the model's default reasoning effort, so pinning it is right but is a weaker
statement than the documents imply.

**The labelling budget is marked Open and it decides whether Slice 1 can run at all.** At
published prices, 5,000 passages of 8,192 tokens is about 41M input tokens, roughly $205 per
rung before reasoning output. Three rungs, plus the probe run at least twice, plus the teacher
ensemble passes, puts the reference and probe spend in the low thousands of dollars before a
single encoder is trained. Price it at Gate 1, not at step 10.

**The report card carries a double-annotation field that no longer applies.**
`human_ceiling: {metric: "cohens_kappa", n_double: 300}` is a leftover from the version of the
plan where you annotated. Nobody annotates now. It sits two lines below
`referee.human_agreement: "not published by source"` and directly contradicts it. That is
exactly the shape of hole an invented number slips through.

**The top level `macro_f1` field is a fidelity number, not accuracy.** It is computed on the
reference set, where the labels were written by a model. Nothing in the schema marks that.
Rename it so a reader of the JSON cannot mistake it.

**The report card has one `test_hash` and the project has three frozen artifacts.** The
reference set, the referee set and the probe output all need their own hash field.

**NeoBERT's 4,096 ceiling fits two of the three rungs.** Slice 1 step 2 says it "fits none of
the three rungs". 512 and 2,048 both fit.

**The published FLS splits are not clean.** Four rows of identical text appear in both the
shipped train and test splits. The plan's dedup rule covers this. Just make sure dedup drops
from train, because the plan also promises to keep the 1,000 row test split unchanged.

**The FiQA re-split may not fit its own constraints.** The plan cuts 500 test and 200 dev from
1,213 rows, grouped by target company, while also keeping every aspect of a sentence in one
split. With a long-tail aspect taxonomy those constraints together will leave a thin and lumpy
training split. Check the real group sizes before committing to 500.

---

## 8. There is no cheap inner loop

Every measurement in the plan is a serverless GPU job, a three-seed comparison, or a paid
labelling run. The fastest thing described is the TF-IDF baseline, and it is listed as a data
canary rather than as the number you read every day.

The 200 row borrowed development set is the only small artifact, and it is reserved for prompt
and threshold tuning. At 200 rows over three classes, its interval is around seven points wide.
Nothing can be steered by it.

**Fix.** Before step 5, build a fixed dev harness that runs on CPU in seconds and prints one
number. It does not have to be the real metric. It has to move in the same direction as the real
metric and it has to be free to run. Without it, every iteration of this project costs money and
hours, which is why the plan has no iteration in it.

---

## 9. Every judgement that matters requires a human

The working-style section is explicit. An agent may not decide a number is good enough. Only you
can accept a borrowed benchmark, resolve the fact-versus-opinion fork, or make a licence call.

That is the right rule for anything that gets published. It also means the repo improves at the
speed of your attention rather than the agent's, and the plans never say which decisions an
agent may make alone. Right now the answer is none.

If autonomous improvement is a goal, name the decisions an agent can make on its own. Choosing
between two configs on validation data is an obvious candidate. Accepting a benchmark is not.

---

## 10. The backbone is picked at 512 and assumed to still win at 8,192

Raised after the first pass and worth recording.

The bench runs all nine checkpoints at 512, because DeBERTa-v3 ships a 512 config and that is the
only rung every candidate can run. The winner then inherits the length ladder and both later
slices. Nothing tests whether the 512 winner is still the right backbone at 8,192.

That assumption sits directly against the project's own thesis. If reading more of the document
changes what works, then the model that wins on one sentence is not automatically the model that
best uses a whole MD&A section. The plans never say this out loud.

**Dropping DeBERTa-v3 does not fix it.** The next ceiling is NeoBERT at 4,096, so removing
DeBERTa-v3 moves the bench to 4,096 and no further. Getting to 8,192 means dropping NeoBERT too,
which leaves four Ettin sizes plus ModernBERT base and large. All six share one architecture, so
the bench would then be measuring size and recipe rather than architecture, and the point of
benching four families is gone.

**Better fix, and it costs one extra ladder run.** Keep all nine at 512. Reclassify DeBERTa-v3
from candidate to control, since a 512-only model can never ship as the long model anyway. Its
job is to answer a genuinely useful question, which is whether the long-context families are
worth anything at short length. Then carry the top two or three long-capable checkpoints up the
ladder instead of the top one. That is 2x or 3x on one task's ladder, not 9x, and it is the only
version that tests the assumption rather than asserting it.

Not applied. Dropping or reclassifying a benched model changes what the bench claims, and the
decision log marks the backbone as "Bench decides".

---

## Smallest change that makes the repo climbable

In order.

1. ~~One answer key for the whole length ladder.~~ Done 2026-08-18.
2. ~~Add the self-consistency control to the context-sensitivity probe.~~ Done 2026-08-18.
3. ~~Fix `gpt-sol-5.6` to `gpt-5.6-sol` everywhere.~~ Done 2026-08-18.
4. Build the skeleton, the registry, the CI data checks and a fast CPU dev harness. No money
   spent, and the repo gains a number it can print.
5. Gate 2 counts unique matches, and the 60% bar is re-argued against the real figure.
6. Carve a readable 500 row dev slice out of the reference set.
7. Set the agreement bar after the reference self-agreement and the step 10 pilot are both known,
   and make Gate 6 block the claim rather than the weights.
8. Decide the backbone question in finding 10.

Item 5 costs nothing and is the one most likely to change what the project decides to build.

---

## Method

Dataset facts were checked directly against the Hugging Face dataset viewer for
`FinanceMTEB/FLS`, `pauri32/fiqa-2018` and `ChanceFocus/flare-finarg-ecc-auc`. All three exist
with the row counts the plans state, and FLS is confirmed three-class.

The reconstruction numbers in finding 5 come from 120 rows sampled from the FLS test parquet
with `random_state=1`, queried against `efts.sec.gov` with an exact phrase search restricted to
form 10-K. 105 of 120 queries returned cleanly. The remainder timed out and were dropped.

Model identifier, effort values and pricing were read from the OpenAI API model page for
`gpt-5.6-sol`.
