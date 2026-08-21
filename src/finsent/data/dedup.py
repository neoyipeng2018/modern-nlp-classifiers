"""Near-duplicate clustering, which supplies the split key.

Financial PhraseBank ships no article identifier, so grouped splitting has no
natural key. Without one, "grouped" k-fold is plain k-fold under another name.
Two keys stand in for the missing article id. This module supplies the first:
a near-duplicate cluster computed on the full text. Track D's paraphrase family
supplies the second.

The model card must say that article-level grouping was not possible, rather
than implying a grouped split that never happened.
"""

from __future__ import annotations

import re
from collections import defaultdict

from .schema import Row

_WORD = re.compile(r"[a-z0-9]+")


def shingles(text: str, size: int = 5) -> set[str]:
    words = _WORD.findall(text.lower())
    if len(words) < size:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i : i + size]) for i in range(len(words) - size + 1)}


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def cluster(rows: list[Row], threshold: float = 0.5, shingle_size: int = 5) -> dict[str, str]:
    """Map example_id to a cluster id. Two rows sharing a shingle are compared.

    Blocking on shared shingles keeps this near linear on this data size. An
    exhaustive pairwise pass over 4,846 rows would also finish, but the blocked
    version stays usable when Track D multiplies the row count.
    """
    prints = {row.example_id: shingles(row.text, shingle_size) for row in rows}

    buckets: dict[str, list[str]] = defaultdict(list)
    for example_id, prints_for_row in prints.items():
        for shingle in prints_for_row:
            buckets[shingle].append(example_id)

    parent: dict[str, str] = {row.example_id: row.example_id for row in rows}

    def find(node: str) -> str:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(a: str, b: str) -> None:
        root_a, root_b = find(a), find(b)
        if root_a != root_b:
            parent[max(root_a, root_b)] = min(root_a, root_b)

    seen: set[tuple[str, str]] = set()
    for members in buckets.values():
        if len(members) < 2 or len(members) > 200:
            continue  # a shingle shared by hundreds of rows is boilerplate, not a duplicate
        for i, left in enumerate(members):
            for right in members[i + 1 :]:
                pair = (left, right) if left < right else (right, left)
                if pair in seen:
                    continue
                seen.add(pair)
                if jaccard(prints[left], prints[right]) >= threshold:
                    union(left, right)

    return {row.example_id: find(row.example_id) for row in rows}


def apply(rows: list[Row], threshold: float = 0.5) -> list[Row]:
    groups = cluster(rows, threshold=threshold)
    for row in rows:
        row.dup_group = groups[row.example_id]
    return rows
