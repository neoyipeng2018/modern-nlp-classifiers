"""Command line entry points.

    finsent build-data   pull, deduplicate, split, freeze and hash
    finsent baselines    score majority, the word lists and TF-IDF
    finsent registry     print the run registry
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import registry
from .config import apply_overrides, resolve


def _build_data(config: dict) -> int:
    from .data import dedup, fiqa, fpb
    from .data.splits import cut, freeze

    settings = config["data"]
    print("Reading Financial PhraseBank ...")
    loaded_fpb = fpb.load_detailed()
    rows = loaded_fpb.rows
    tiers = {}
    for row in rows:
        tiers[row.agreement_tier] = tiers.get(row.agreement_tier, 0) + 1
    print(f"  {loaded_fpb.n_lines} lines in the 50%-agree file")
    print(f"  {loaded_fpb.n_repeated_texts} sentences appear more than once and were collapsed")
    print(f"  {loaded_fpb.n_dropped} dropped: their copies carry contradicting labels")
    for item in loaded_fpb.dropped_conflicting:
        print(f"    {item['labels']} :: {item['text'][:88]}")
    print(f"  {len(rows)} usable sentences, strongest tier reached: {dict(sorted(tiers.items()))}")
    for tier in fpb.TIER_ORDER:
        print(f"  tier >= {tier:>3}: {len(fpb.tier_at_least(rows, tier)):5d} rows")

    print("Clustering near-duplicates, which is the split key ...")
    dedup.apply(rows, threshold=settings["dedup_threshold"])
    groups = len({r.dup_group for r in rows})
    print(f"  {groups} groups over {len(rows)} rows ({len(rows) - groups} rows share a group)")

    print("Cutting and freezing the splits ...")
    cut(rows, n_test=settings["n_test"], n_dev=settings["n_dev"], seed=config["seed"])
    manifest = freeze(rows, settings["out_dir"])
    for name, block in manifest["stats"].items():
        print(f"  {name:5s} n={block['n']:5d} labels={block['labels']} groups={block['groups']}")
    for name, digest in manifest["hashes"].items():
        print(f"  {name:5s} {digest}")

    print("Reading FiQA, and counting the rows a sentence-level model cannot score ...")
    loaded = fiqa.load()
    print(
        f"  {loaded.n_sentences} sentences, {loaded.n_conflicted_sentences} carry conflicting "
        f"polarity across their aspects ({loaded.conflict_rate:.1%})"
    )
    print("  Those rows are held out of the score and reported separately, never averaged away.")

    fiqa_dir = Path(settings["out_dir"]).parent / "fiqa"
    fiqa_dir.mkdir(parents=True, exist_ok=True)
    for name, subset in (("usable", loaded.usable), ("conflicted", loaded.conflicted)):
        path = fiqa_dir / f"{name}.jsonl"
        with path.open("w") as handle:
            for row in sorted(subset, key=lambda r: r.example_id):
                row.split = "test"
                handle.write(json.dumps(row.as_dict(), sort_keys=True) + "\n")
        print(f"  wrote {path} ({len(subset)} rows)")
    return 0


def _baselines(config: dict) -> int:
    from .baselines import LexiconBaseline, MajorityBaseline, TfidfBaseline
    from .data.splits import load_split
    from .eval.harness import score, write_report
    from .lexicons import load_henry, load_loughran_mcdonald

    out_dir = Path(config["data"]["out_dir"])
    manifest = json.loads((out_dir / "manifest.json").read_text())
    train = load_split(out_dir / "train.jsonl")
    dev = load_split(out_dir / "dev.jsonl")

    # The fitted baselines learn from train and are scored on dev. The lexicon
    # baselines fit nothing at all: the word lists are published and the rule is
    # the sign of positive hits minus negative hits.
    systems = [
        MajorityBaseline().fit(train),
        LexiconBaseline(load_loughran_mcdonald()),
        LexiconBaseline(load_henry()),
        TfidfBaseline(seed=config["seed"]).fit(train),
    ]

    print(f"{'system':26s} {'macro-F1':>9s} {'95% interval':>18s}  {'acc':>6s}  grade")
    print("-" * 78)
    rows_out = []
    for system in systems:
        report = score(
            system,
            out_dir / "dev.jsonl",
            expected_hash=manifest["hashes"]["dev"],
            bootstrap=config["eval"]["bootstrap"],
            seed=config["seed"],
        )
        write_report(report, "runs/reports")
        block = report.macro_f1
        print(
            f"{system.name:26s} {block['value']:9.4f} "
            f"[{block['ci95'][0]:.4f}, {block['ci95'][1]:.4f}]  "
            f"{report.accuracy:6.4f}  {report.evidence_grade}"
        )
        if isinstance(system, LexiconBaseline):
            print(f"{'':26s} {'':9s} {'':18s}  silent on {system.abstention_rate(dev):.0%} of rows")
        rows_out.append((system.name, report))

        row = registry.start(
            kind="baseline",
            hypothesis=f"{system.name} sets a floor for financial sentence sentiment",
            config=config,
            variable="baseline system",
            seed=config["seed"],
            dev_hash=report.split_hash,
        )
        row.metrics = {"macro_f1": block["value"], "ci95": block["ci95"], "accuracy": report.accuracy}
        row.evidence_grade = report.evidence_grade
        row.notes = f"system={system.name}"
        registry.append(row)

    print()
    print("Warning. These are development-split numbers. The test split stays shut")
    print("until the bench is done and the success bar is written into the config.")
    return 0


def _registry(config: dict) -> int:
    rows = registry.read()
    if not rows:
        print("The registry is empty. No run has happened.")
        return 0
    for row in rows:
        print(
            f"{row['run_id']:38s} {row['kind']:10s} {row['evidence_grade']:11s} "
            f"{json.dumps(row.get('metrics', {}))}"
        )
    return 0


COMMANDS = {"build-data": _build_data, "baselines": _baselines, "registry": _registry}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="finsent", description=__doc__)
    parser.add_argument("command", choices=sorted(COMMANDS))
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--set", dest="overrides", action="append", default=[])
    args = parser.parse_args(argv)

    config = apply_overrides(resolve(args.config), args.overrides)
    return COMMANDS[args.command](config)


if __name__ == "__main__":
    sys.exit(main())
