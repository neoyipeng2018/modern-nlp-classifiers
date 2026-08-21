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
