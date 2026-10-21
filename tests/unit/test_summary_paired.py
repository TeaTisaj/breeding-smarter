"""paired_vs keeps its columns when there is nothing to pair (E10 has no reference arm)."""

import pandas as pd

from breeding_smarter.experiments.summary import paired_vs


def test_paired_vs_empty_keeps_columns():
    per_gen = pd.DataFrame(
        {"breed": ["SYN_M"], "strategy": ["S3q-gain010-c050"], "adoption": [0.5],
         "replicate": [0], "generation": [10], "metric": ["M2_realised_ibd"], "value": [0.1]}
    )  # fmt: skip
    out = paired_vs(per_gen, ref="S1")
    assert out.empty and {"breed", "metric", "diff_mean"} <= set(out.columns)
