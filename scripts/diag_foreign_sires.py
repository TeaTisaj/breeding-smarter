"""Additional P12 diagnostic (not pre-registered).

CC-none-rand with domestic candidate sires only, SYN_S replicates 0 to 3, late-window dF.
Explains the gap between S0 (domestic sires only) and CC-none-rand (domestic plus registered
foreign sires). Usage: uv run python scripts/diag_foreign_sires.py
"""

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

import breeding_smarter.experiments.runner as rn
import breeding_smarter.experiments.strategies as stg
from breeding_smarter.experiments.runner import Part, load_experiment, run_part
from breeding_smarter.experiments.summary import ne_from_series

CONFIG = Path("configs/experiments/coordination.yaml")


class DomesticOnly(stg.Coordinated):
    def candidates(self, sires, yc):
        idx = self.obs.idx(np.asarray(sires, np.int64))
        return np.asarray(sires, np.int64), idx


def one(r: int) -> tuple[int, float]:
    rn.make_strategy = lambda s, p, sc: DomesticOnly(p, sc, "none", "random", name="dom")
    df = run_part(load_experiment(CONFIG), Part("SYN_S", "CC-none-rand", 1.0, r))
    g = df[(df.metric == "M2_realised_ibd") & (df.generation > 5)]
    return r, ne_from_series(g.generation.to_numpy(), g.value.to_numpy())[0]


if __name__ == "__main__":
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(one, range(4)))
    e5 = pd.read_csv("reports/experiments/E5_coordination/per_generation_replicates.csv.gz")
    late = e5[(e5.metric == "R_delta_f_late") & (e5.breed == "SYN_S") & (e5.replicate < 4)]
    late = late[late.strategy.isin(["S0", "CC-none-rand"])]
    table = late.pivot_table(index="replicate", columns="strategy", values="value")
    table["CC-none-rand, domestic sires only"] = pd.Series(dict(res))
    print(table)
