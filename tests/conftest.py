"""Fixtures. No test in this suite touches the network.

CI has no credentials and no GPU, so everything here runs on synthetic rows.
The dataset loaders are exercised by `finsent build-data`, not by CI.
"""

from __future__ import annotations

import pytest

from finsent.data.schema import Row, make_id


def row(text: str, label: str, **kwargs) -> Row:
    defaults = dict(
        example_id=make_id("t", text),
        text=text,
        label=label,
        label_source="human",
        source_dataset="test",
        source_licence="CC0",
        codebook_version="v0",
    )
    defaults.update(kwargs)
    return Row(**defaults)


@pytest.fixture
def rows() -> list[Row]:
    made = []
    for i in range(60):
        label = ("negative", "neutral", "positive")[i % 3]
        made.append(row(f"the company reported a result number {i} for the quarter", label))
    return made
