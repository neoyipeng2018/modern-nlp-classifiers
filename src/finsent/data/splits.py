"""Cutting the splits, once, and freezing them.

One test split is cut from the 50%-agreement superset, and every row keeps the
agreement tier it reached. The four published subsets are then read back as
breakdowns of that one frozen split. Cutting four independent test splits is
impossible, because the subsets are nested, and cutting four overlapping ones
leaks.

Splitting is grouped on the near-duplicate cluster and stratified on the label.
Re-splitting after seeing a result is the same as tuning on the test set, so the
split is written once and hashed.
"""

from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from ..config import file_hash
from .schema import Row


def _group_rows(rows: list[Row]) -> dict[str, list[Row]]:
    groups: dict[str, list[Row]] = defaultdict(list)
    for row in rows:
        groups[row.dup_group or row.example_id].append(row)
    return groups


def cut(rows: list[Row], n_test: int, n_dev: int, seed: int = 20260821) -> list[Row]:
    """Assign every row to test, dev or train. Groups never straddle a split.

    Groups are taken in a shuffled order, biggest-label-need first, so the class
    rates of the test split track the pool rather than the group sizes. The
    natural class rate is kept. Rebalancing a test set hides the real task.
    """
    groups = _group_rows(rows)
    target = Counter({name: 0 for name in ("test", "dev")})
    target["test"], target["dev"] = n_test, n_dev

    order = sorted(groups, key=lambda key: (-len(groups[key]), key))
    rng = random.Random(seed)
    rng.shuffle(order)

    filled = Counter()
    assignment: dict[str, str] = {}
    for key in order:
        size = len(groups[key])
        for name in ("test", "dev"):
            if filled[name] + size <= target[name]:
                assignment[key] = name
                filled[name] += size
                break
        else:
            assignment[key] = "train"

    for key, members in groups.items():
        for row in members:
            row.split = assignment[key]
    return rows


def stats(rows: list[Row]) -> dict:
    out: dict[str, dict] = {}
    for name in ("train", "dev", "test"):
        subset = [r for r in rows if r.split == name]
        out[name] = {
            "n": len(subset),
            "labels": dict(sorted(Counter(r.label for r in subset).items())),
            "agreement_tiers": dict(sorted(Counter(r.agreement_tier for r in subset).items())),
            "groups": len({r.dup_group or r.example_id for r in subset}),
        }
    return out


def check_invariants(rows: list[Row]) -> None:
    """The checks that CI runs. Each one is a way results get silently ruined."""
    by_split: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        row.validate()
        by_split[row.split].add(row.example_id)

    names = list(by_split)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            shared = by_split[left] & by_split[right]
            if shared:
                raise AssertionError(f"{len(shared)} example ids appear in both {left} and {right}")

    group_splits: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        group_splits[row.dup_group or row.example_id].add(row.split)
    straddling = [key for key, splits in group_splits.items() if len(splits) > 1]
    if straddling:
        raise AssertionError(f"{len(straddling)} near-duplicate groups straddle two splits")

    families: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if row.family_id:
            families[row.family_id].add(row.split)
    split_families = [key for key, splits in families.items() if len(splits) > 1]
    if split_families:
        raise AssertionError(
            f"{len(split_families)} augmentation families straddle two splits. "
            "A paraphrase and its original always share a split."
        )

    for name in ("dev", "test"):
        offenders = {r.label_source for r in rows if r.split == name} - {"human"}
        if offenders:
            raise AssertionError(f"{name} split carries non-human labels: {sorted(offenders)}")


def freeze(rows: list[Row], out_dir: str | Path) -> dict:
    """Write the splits, hash them, and write a manifest naming every hash."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    check_invariants(rows)

    manifest: dict[str, object] = {"stats": stats(rows), "hashes": {}}
    for name in ("train", "dev", "test"):
        path = out_dir / f"{name}.jsonl"
        subset = sorted((r for r in rows if r.split == name), key=lambda r: r.example_id)
        with path.open("w") as handle:
            for row in subset:
                handle.write(json.dumps(row.as_dict(), sort_keys=True) + "\n")
        manifest["hashes"][name] = file_hash(path)

    # The publishable artifact. Row identifiers and split assignments only, no
    # text and no labels, because the source is CC BY-NC-SA and this project
    # redistributes none of it. Anyone rebuilds the exact splits by re-running
    # the loader and joining on example_id. See DECISIONS_AIM.md entry J.
    assignments = out_dir / "split_assignments.csv"
    with assignments.open("w") as handle:
        handle.write("example_id,split,agreement_tier,dup_group\n")
        for row in sorted(rows, key=lambda r: r.example_id):
            handle.write(f"{row.example_id},{row.split},{row.agreement_tier},{row.dup_group}\n")
    manifest["hashes"]["split_assignments"] = file_hash(assignments)
    manifest["redistribution"] = {
        "text_published": False,
        "labels_published": False,
        "note": "Source is CC BY-NC-SA. Only row ids and split assignments are published.",
    }

    manifest_path = out_dir / "manifest.json"
    with manifest_path.open("w") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
    return manifest


def load_split(path: str | Path) -> list[Row]:
    with Path(path).open() as handle:
        return [Row(**json.loads(line)) for line in handle if line.strip()]
