"""P12 H5 bug check (plan section 4): on a SYN_M season with true-pedigree kinship, verify
that equal contributions are feasible and that the conservation optimum is not worse than the
equal split. Usage: uv run python scripts/check_h5_oracle.py"""

import numpy as np

from breeding_smarter.coordination.config import load_coordination
from breeding_smarter.coordination.ocs import expected_coancestry
from breeding_smarter.coordination.planner import plan_season
from breeding_smarter.experiments.observed import ObservedRegistry
from breeding_smarter.experiments.runner import experiment_setup, prepared_state
from breeding_smarter.experiments.truth_kinship import TrueKinship
from breeding_smarter.io.datasets import resolve_dataset
from breeding_smarter.rules import day_number
from breeding_smarter.sim.demography import eligible
from breeding_smarter.sim.genetics import DogGenetics
from breeding_smarter.sim.state import DOMESTIC, FOREIGN, SimState

state, _ = SimState.load(prepared_state("v1", "SYN_M"))
b = state.breed_ids.index("SYN_M")
setup = experiment_setup(resolve_dataset("v1").root, b, 1.0)
g = DogGenetics.from_setup(setup)
g.load_arrays(state.extra)
obs = ObservedRegistry(state, g, setup, b)
year = state.year + 1
ctx = obs.context(state, year)
rng = np.random.default_rng(0)
dams = obs.idx(rng.choice(eligible(state, setup, b, DOMESTIC, year, 0, g), 150, replace=False))
dom = eligible(state, setup, b, DOMESTIC, year, 1, g)
foreign = [x for x in eligible(state, setup, b, FOREIGN, year, 1, g) if obs.has(int(x))]
tk = TrueKinship(state, b)
cfg = load_coordination()
for label, sires_gid in (("domestic + registered foreign", np.r_[dom, foreign]), ("domestic", dom)):
    sires = obs.idx(np.asarray(sires_gid, np.int64))

    def kin(idx):
        return tk.kinship(obs.gid[np.asarray(idx, np.int64)])

    plan = plan_season(ctx, "SYN_M", day_number(f"{year}-07-01"), dams, sires, cfg, "ocs", "mc1",
                       kin=kin)  # fmt: skip
    K = kin(np.r_[sires, dams])
    n, m = dams.size, sires.size
    equal = expected_coancestry(K, np.full(m, n / m), n)
    quota = expected_coancestry(K, plan.quotas.astype(float), n)
    print(
        f"{label}: m={m}, equal split feasible under caps: {n / m <= 5}; "
        f"C(OCS continuous)={plan.diagnostics['achieved_C']:.5f} "
        f"C(Sainte-Lague quotas)={quota:.5f} C(equal split)={equal:.5f}; "
        f"relaxed={plan.diagnostics['relaxed_constraints']!r}"
    )
