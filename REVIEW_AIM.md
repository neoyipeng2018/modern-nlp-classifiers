# Plan review against the stated aim

Reviewed 2026-08-21 against `PRODUCT.html`, `PROGRAM_DESIGN.html`, `ARCHITECTURE.html`,
`VERTICAL_SLICES.html` and `learnings.html`.

`REVIEW.md` asked one question. Is there a benchmark to climb? This file asks a different one.
Do the plans build what the aim says?

## The aim, as stated

1. Build the best small, medium and large encoders or classifiers for financial text.
2. Cover three tasks: sentiment, forward-looking, and fact versus opinion.
3. Explore the different models that are available.
4. Explore data boost methods.
5. Explore weak supervision and other methods that work.
6. Compare against lexical baselines.
7. Release the models, the data method and everything else in public, at the state of the art.

## Summary

The plans cover part 2, part 3 in one narrow sense, part 5 in one narrow sense, and part 7 minus
the last two words. The plans do not cover part 1, part 4, or the state-of-the-art goal. Two of
the seven parts are written into the documents as things the project must **not** do.

| Aim | Plan status |
|---|---|
| Small, medium and large | **Missing.** The plans build small only. Large is out. |
| Three tasks | Covered. Task 3 has no name yet. |
| Different models | Partly. Nine general checkpoints. No finance encoder. No 17M. No 1B. |
| Data boost | **Banned.** Synthetic data is a non-goal. |
| Weak supervision | Partly. One method of six is planned. |
| Lexical baselines | Partly. TF-IDF only. No finance word list. |
| Public release | Covered, but four open items block it. |
| State of the art | **Banned.** The write-up rules forbid the words. |

The rest of this file gives one section per gap. Sections A to F are the aim gaps. Sections G to
K are faults that the aim change makes worse. Section L lists stale text.

---

## A. The plans build small models only

`PRODUCT.html` says "Three small encoders, one per task". The decision log says:

> Model size: Small and medium first, roughly 32M to 250M parameters. The 400M and large
> checkpoints run only if the medium tier looks capped.

So the large tier is conditional, and the condition is a result that does not exist yet. The aim
makes the large tier a deliverable. These are different projects.

Three more things are absent.

- No definition of small, medium and large. Nothing says where each tier starts and stops.
- No count of released models. Three tiers times three tasks is nine models, not three.
- No per-tier release path. There is one model card template and one success bar per task.

The Ettin family ships six sizes. The bench uses four. `jhu-clsp/ettin-encoder-17m` and
`jhu-clsp/ettin-encoder-1b` are both public, both MIT, and both absent from the roster. With those
two added, one family gives a size curve over six points from 17M to 1B. That curve is the direct
answer to the size question, and it costs six more short runs.

**Do this.**

1. Write the three tier limits into the decision log as parameter counts.
2. Add `ettin-encoder-17m` and `ettin-encoder-1b` to the bench.
3. Ship one model per tier per task. State the bar per tier.
4. Publish one accuracy-against-parameters curve per task.

---

## B. The plans forbid a state-of-the-art claim

`PRODUCT.html`, under "What is deliberately not a gate":

> Beating published state of the art. Prior benchmark protocols are not comparable to this one,
> and forcing the comparison is how the last project produced numbers it had to retract.

`PROGRAM_DESIGN.html`, under "Rules for the text":

> The word "state of the art" does not appear.

The aim says "but SOTA". The plans say the opposite. One of the two must change.

The caution behind the rule is correct. The previous project withdrew numbers because the protocol
moved. But the rule as written also removes every route to the aim:

- No document holds the published scores for FLS, FiQA or FinArg.
- No step submits a result to a leaderboard. FinanceMTEB and FLARE both carry these tasks.
- No table has a column for somebody else's number.

**Do this.**

1. Decide what state of the art means here. A leaderboard rank, or the best score under one
   honest protocol. Write the choice in the decision log.
2. Add a "published number" column to every results table.
3. Write the protocol difference beside each published number.
4. Add a leaderboard submission step to Slice 4.

A protocol note next to a borrowed number is honest. Silence about the number is not.

---

## C. Data boost is a non-goal, and the one measured gain sits in the learnings file

`PRODUCT.html` lists this countermeasure under "Known traps":

> Synthetic data is out of the default plan. If it is added, it runs as a controlled A/B on one
> task with everything else fixed.

The aim names data boost as a main line of work. The plans keep it out of the default plan.

This is the most expensive gap, because the previous project already measured a gain here.
`learnings.html` records it:

- Targeted paraphrases of 82 validation errors gave +2.92 accuracy and +7.84 macro-F1 points.
- A second augmented set gave +4.15 accuracy and +10.40 macro-F1 points.
- Both sets came from validation errors, so the validation estimate is contaminated.
- The learnings file names the fix: a grouped, multi-seed factorial with equal sample counts.

That experiment is written down, priced, and not in any plan. You also hold a
`verbalized-sampling-augment` skill built for exactly this task, and no document mentions it.

Methods that no document names:

| Method | What it buys | Cost |
|---|---|---|
| Error-targeted paraphrase | The measured +7.84 F1 from last time, done cleanly | Low |
| Verbalized Sampling generation | Wider cover of the label space than one paraphrase prompt | Low |
| Class-balanced generation | Rows for `specific_fls` and for `negative`, the thin classes | Low |
| Counterfactual aspect pairs | Two aspects, opposite labels, in one sentence | Medium |
| Back translation | Cheap surface variety, no model bill | Low |
| Span perturbation | Number and date swaps that keep the label | Low |

**Do this.**

1. Make augmentation Track D. Give it its own `label_source` value and its own split.
2. Group paraphrase families in the split. `learnings.html` records a leak of this exact shape.
3. Run one factorial per task: none, standard paraphrase, Verbalized Sampling. Equal counts.
   Three seeds. One variable.
4. Publish the ablation whichever way it comes out.

---

## D. No plan trains on financial text before the task

Nine benched checkpoints are general encoders. The plans use EDGAR as a sample pool for the
labelling run, and nothing else. No step runs masked language modelling on financial text.

That is the largest known lever for a domain encoder, and the field already shows it works.
`yiyanghkust/finbert-pretrain` exists for this reason. The bench as planned answers the question
"which general encoder wins on this task". The aim asks "which is the best encoder for financial
text". Those are different questions.

The gap also removes the natural use for EDGAR. The project holds a public-domain corpus of the
exact target text type and never learns from it.

**Do this.**

1. Add one continued-pretrain run on the bench winner. Masked language modelling on EDGAR
   management discussion text plus transcripts.
2. Fine-tune from that checkpoint. Compare against the same fine-tune from the public checkpoint.
   One variable, three seeds.
3. Release the domain checkpoint as an artifact of its own. It is useful to other people even
   when the classifier is not.

---

## E. Weak supervision covers one method out of six

What the plans cover is good and complete: k routed models, heuristic functions, a label matrix,
Snorkel's label model, plain majority vote as the control, and a pilot before the spend. Keep all
of it.

The aim says "weak supervision and any other viable ideas". Five other methods are absent.

1. **Self-training.** Label unlabelled EDGAR rows with the student, keep the confident ones,
   retrain. No API bill at all. The plans buy every extra label from a router.
2. **Distillation from a large encoder.** Train the 1B model, then train the 17M model on its
   soft outputs. This is the bridge between the size tiers the aim asks for, and the plans have
   no bridge. Today the small model and the large model train the same way from the same rows.
3. **Label noise cleaning.** Confident learning over the borrowed train split. The plans already
   found four rows of identical text across the FLS train and test splits, so the borrowed labels
   are known to be imperfect.
4. **Active learning.** Choose which rows go to the router. The plans buy labels at random, then
   stop when a curve flattens. A selection rule buys the same quality for fewer dollars.
5. **Intermediate task fine-tune.** Train on Financial PhraseBank or NumClaim first, then on the
   target task. Cheap, and it uses public data the plans already list and then never use.

**Do this.** Name each method. Price each one. Rank them. Run the top two as single-variable
ablations on the bench winner.

---

## F. The lexical baselines are not the finance ones

The plans run majority class and TF-IDF plus logistic regression. Both are correct, and neither is
the baseline a finance reader looks for.

Missing:

- **Loughran-McDonald word lists.** The standard finance sentiment dictionary. Any sentiment
  result without it invites the question.
- **The Henry word list.** The second standard, and it disagrees with Loughran-McDonald often
  enough to be worth both.
- **Forward-looking keyword rules.** The accounting literature measured forward-looking text with
  word rules for years before neural models. That is the number the FLS result must beat.
- **A plain rule set.** The plans already define heuristic labelling functions for all three
  tasks. Nothing scores them on the test split. That measurement is free.
- **Character n-gram SVM.** One more classical point, and it catches boilerplate.

**Do this.** Add a lexicon runner beside the classical runner. It takes the same interface. Score
every word list on every task. Publish the number. It tells a reader how much the encoder buys
over a word list, and that is the honest floor for this domain.

---

## G. One benchmark per task, and two of them are small

FLS ships 1,000 test rows. FiQA is re-split to 500. FinArg is re-split to 600. A claim that a model
is the best rests on one small set per task.

The release checklist promises out-of-domain results. No slice builds an out-of-domain set.

Three public human-labelled sets fit the three tasks and appear in no document. All three were
checked on the hub on 2026-08-21.

| Dataset | Rows | Labels | Fits | Licence |
|---|---:|---|---|---|
| `gtfintechlab/Numclaim` | 2,678 | `INCLAIM` / `OUTOFCLAIM` | Fact versus opinion, and forward-looking | Not declared |
| `gtfintechlab/all_annotated_sentences_25000` | 25,000 | `stance_label`, `time_label`, `certain_label` | `time_label` is forward-looking. `certain_label` is near fact versus opinion | CC-BY-NC-SA-4.0 |
| `takala/financial_phrasebank` | 4,840 | 3-class sentiment, with agreement tiers | Sentiment, out of domain against FiQA | CC-BY-NC-SA-3.0 |

NumClaim matters most. It labels analyst reports and earnings-call sentences as a forward-looking
or speculative claim, or as a statement of past or present fact. That is close to the
fact-versus-opinion codebook, and closer than FinArg's premise-versus-claim rule. It gives Slice 3
a second option, and the fork in `PROGRAM_DESIGN.html` lists only two.

The central bank family matters for a different reason. It carries a forward-looking label on a
text type that is not 10-K prose. That is the out-of-domain test the release checklist promises.

Both licences are non-commercial. Use them to score. Do not redistribute them.

**Do this.** For each task, adopt one primary set and one secondary set of a different text type.
Report both. A model that wins on both is one you can call best.

---

## H. The backbone bench is decided on machine-written labels

`ARCHITECTURE.html` and `VERTICAL_SLICES.html` both say the bench is "decided on validation
macro-F1". The data schema says:

> Validation comes from the same tracks as training.

Training tracks are Track A, which is public labels mapped to the codebook, and Track C, which is
weak labels from routed models. The 200-row human development set is reserved for prompts,
thresholds and label-model choice.

So the pick of the encoder for the whole project rests on labels that models wrote. That is the
fault the project removed from the headline. It survives at the point where the decision is made.

Gate 5 has the same shape. It reads "clearly beats TF-IDF plus logistic regression on validation".

**Do this.** Score the bench on the human development set as well, and pick on that number. If the
development set is too small to separate nine candidates, say so and grow it. Or state plainly in
the card that the pick was made against weak labels.

---

## I. Nine candidates need a rule the plans do not have

The plans pick on a paired bootstrap against the incumbent leader, over three seeds, and give the
tie to the cheaper checkpoint. That is a good rule and it is the right shape.

Two things are missing.

- **No control for multiple comparison.** Nine tests at 95% give roughly a one-in-three chance of
  one false separation. Adding the 17M and 1B checkpoints makes eleven.
- **No cross-validation.** One 200-row development split cannot separate nine close models.
  `learnings.html` records the same wall: a 1.09-point gap did not reach significance at p=.093.

**Do this.** Write the multiple-comparison rule into the config before the bench runs. Use grouped
k-fold over train plus development for the pick. Keep the test split for the final number only.

---

## J. Four open items block the public release

The aim puts public release in the goal. Four decision-log items still read Open or Reopened, and
each one blocks part of the release.

| Item | Why it blocks |
|---|---|
| Repository licence | Open. Nothing can be uploaded under an undecided licence. |
| Labelling budget | Open. It gates the first real spend, so it gates Slice 1 step 12. |
| Fact-versus-opinion fork | Reopened. One of the three products has no name and no benchmark. |
| Source licences | FinanceMTEB/FLS declares no licence on the hub. |

A new licence fact from section G: Financial PhraseBank is CC-BY-NC-SA-3.0, and the gtfintechlab
sets are CC-BY-NC-SA-4.0. Both are non-commercial. A model trained on non-commercial rows cannot
carry a permissive licence without a statement. Decide the training use and the licence together,
not in that order.

**Do this.** Close all four before Slice 1 step 9. They cost hours now. They cost a retraction
later.

---

## K. Nothing is built, and the aim makes the programme larger

`REVIEW.md` closed finding 1 by decision: the plans come first, and a repository of documents is
the expected state. That was right for one small encoder per task.

The aim is now nine models, over three tasks, with several data methods and several weak-
supervision methods. The plans still describe one serial path of four slices, and slice 1 alone
carries about half the work.

Three steps need no money and no open decision. Build them now.

1. Slice 1 step 1, the repository skeleton, the config hash and the registry.
2. Slice 1 step 5, the token length profile. It is the first number the project can print.
3. The lexical baselines from section F. They run on a laptop and they set the floor.

---

## L. Stale text left by the scope change

The 2026-08-20 change removed the length ladder, the reference set and the reconstruction gate.
Text from all three survives.

| File | Where | What it says |
|---|---|---|
| `PRODUCT.html` | Decision log | "Passage reconstruction bar: 60% ... Assumed". Two rows above, reconstruction is "no longer a gate. Decided". |
| `PRODUCT.html` | Model contracts | "all three read up to 8,192 tokens". The bench cap is 512 and `max_length` is per task. |
| `PROGRAM_DESIGN.html` | Registry fields | `control_run_id`: "The 512-token run this one is compared against". No control run exists. |
| `PROGRAM_DESIGN.html` | Risk register | "Reconstruction fails and the long-context claim dies", with the 60% bar. Both are removed. |
| `PROGRAM_DESIGN.html` | Write-up rules | "'Long context helps' is never written without ... the evidence-distance split". No such split exists. |
| `ARCHITECTURE.html` | Report card note | "8,192 against the 512 control on the far half". No ladder, no far half. |
| `ARCHITECTURE.html` | Demo | "A toggle that reruns the same input through the 512-token control". |
| `ARCHITECTURE.html` | CI checks | "a passage length that matches the rung being trained ... a run that finds two different validation keys stops". No rungs. |
| `ARCHITECTURE.html` | Choices and rejections | "Four families benched at 512, then the winner climbs the ladder". |
| `VERTICAL_SLICES.html` | Slice 3, reused | "The binary metric setup from Slice 1". Slice 1 is three-class. |
| `VERTICAL_SLICES.html` | Slice 3, step 5 | "The headline is stated against the ensemble either way". `REVIEW.md` finding 13 asked for the deletion. |
| `VERTICAL_SLICES.html` | Slice 3 | The step numbers go 0, 1a, 1b, 3. Step 2 is absent. |

---

## M. Smaller gaps, one line each

- No comparison of the classification head. CLS pooling against mean pooling is one config line.
- No temperature scaling, although the report card carries a calibration error field.
- No seed ensemble and no model soup. The bench already pays for three seeds per candidate.
- FiQA ships a continuous score from −1 to 1. The plans map it to a class and discard the score.
  A regression head with published thresholds usually scores higher on this set.
- No error analysis step. The report card holds a confusion matrix and nothing reads it.
- No inference cost story for the large tier, although CPU cost is planned for the small tier.
- No cross-task transfer between the three tasks, because the plans forbid a shared trunk. A
  shared trunk is correctly rejected. An intermediate fine-tune is not the same thing and is not
  rejected anywhere.

---

## The smallest change that makes the plans match the aim

In order. The first three cost nothing.

1. Decide the state-of-the-art question in section B. It changes what every table must carry.
2. Write the three size tiers into the decision log, and add `ettin-encoder-17m` and
   `ettin-encoder-1b` to the bench. Section A.
3. Add the lexicon baselines. Section F. They run on a laptop.
4. Move augmentation from the non-goals to Track D, with the factorial the learnings file already
   specifies. Section C.
5. Add the domain pretrain run. Section D.
6. Adopt a second benchmark per task from section G. NumClaim first, because it also resolves the
   Slice 3 fork.
7. Fix the bench pick so it reads human labels. Section H.
8. Close the four open items. Section J.
9. Build the skeleton, the length profile and the lexical baselines. Section K.
10. Clean the stale text. Section L.

Items 1 and 2 are the ones without which the plans build a different product from the one the aim
describes.

---

## Method

Dataset facts were read from the Hugging Face hub on 2026-08-21. `gtfintechlab/Numclaim` reports
2,141 train rows and 537 test rows over two columns. `gtfintechlab/federal_reserve_system` reports
1,000 sentences over three label columns, in three seed splits.
`gtfintechlab/all_annotated_sentences_25000` is the pooled set for that family.
`takala/financial_phrasebank` reports CC-BY-NC-SA-3.0 and 4,840 sentences.
`jhu-clsp/ettin-encoder-17m` and `jhu-clsp/ettin-encoder-1b` are both public under MIT.
`yiyanghkust/finbert-pretrain` and `yiyanghkust/finbert-fls` are both public.

Prior-project numbers in section C were read from `learnings.html` in this repository. Stale text
in section L was found by search across the four plan documents.
