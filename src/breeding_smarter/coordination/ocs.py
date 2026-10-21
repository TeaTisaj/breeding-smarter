"""Optimum contribution selection for one breeding season (P12 task 12.3).

Sires are the decision; the season's mated dams are fixed (each has one litter). With `n` dams
and `l_i` expected litters for sire i, contributions are `s_i = l_i / (2n)` (sum 1/2) and
`d_j = 1 / (2n)`. The expected coancestry of the planned matings [meuwissen-1997]:

    C(c) = c'Kc = s'K_SS s + 2 s'K_SD d + d'K_DD d,      K = A / 2 (kinship).

Internally `x = l / n` (sums to 1), so `C = x'K_SS x / 4 + x'(K_SD d) + d'K_DD d`.

- conservation: `min C(c)` [pong-wong-woolliams-2007];
- gain: `max m'x` subject to `C(c) + tau(c) <= budget`, where `tau = (1/(2N)) sum_i c_i
  (1 - k_ii)` is the small-cohort term with N newborns [du-2025]. If the budget is below the
  conservation minimum the conservation solution is returned with `infeasible=True` (D7).

Constraints: `0 <= l_i <= cap_i`; `l_i >= fixed_i` (non-adopters' booked litters, D15); at least
one litter to each of the youngest `n_age_classes` non-empty age classes
[sonesson-meuwissen-2001]; contribution-weighted mean equivalent generations of the sires at
least their unweighted mean [wellmann-2019]; optionally (E8) a carrier limit per tested locus l,
`sum_i x_i t_il <= b_l` with `t_il` the probability that sire i transmits the risk allele
(`docs/research_coordination.md`: health goals as linear constraints; OCS alone keeps recessives
at heterozygous frequencies [de-cara-2013]). A constraint that makes the problem infeasible is
dropped (carrier first, then age classes, then depth) and reported in `relaxed`.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import cvxpy as cp
import numpy as np
from numpy.typing import NDArray

from breeding_smarter.pedigree.core import FloatArray, IntArray

TOL = 1e-9


@dataclass
class OCSProblem:
    K: FloatArray  # (m + n_d) square kinship matrix, sires first
    n_dams: int
    caps: FloatArray  # litters per sire (upper bounds), length m
    age_class: IntArray  # per sire (whole years); -1 = no class (e.g. fixed non-candidate)
    eqg: FloatArray  # per sire
    merit: FloatArray | None = None  # per sire (gain objective; higher is better)
    fixed_sire_litters: FloatArray | None = None  # booked litters (lower bounds)
    n_newborn: float = 0.0  # expected registered newborns (small-cohort term; 0 = off)
    n_age_classes: int = 2
    depth: bool = True
    carrier_t: FloatArray | None = None  # (m, L) risk-allele transmission per sire and locus
    carrier_bound: FloatArray | None = None  # (L,) upper bound of x't per locus

    @property
    def has_carrier(self) -> bool:
        return self.carrier_t is not None and self.carrier_bound is not None

    @property
    def m(self) -> int:
        return int(self.caps.size)


@dataclass
class OCSResult:
    litters: FloatArray  # continuous expected litters per sire (sums to n_dams)
    coancestry: float  # C(c) achieved (without the small-cohort term)
    objective: str  # "conservation" | "gain"
    target: float | None
    infeasible: bool
    status: str
    seconds: float
    relaxed: list[str] = field(default_factory=list)
    c_min: float | None = None  # conservation minimum (gain only)


def _psd(Q: FloatArray) -> FloatArray:
    """Symmetrise; lift the diagonal if round-off made the matrix slightly indefinite."""
    Q = 0.5 * (Q + Q.T)
    lam = float(np.linalg.eigvalsh(Q)[0]) if Q.size else 0.0
    if lam < 0:
        Q = Q + (abs(lam) + 1e-12) * np.eye(Q.shape[0])
    return Q


def _parts(p: OCSProblem) -> tuple[FloatArray, FloatArray, float]:
    """(K_SS, K_SD d, d'K_DD d) with dam contributions 1/(2n)."""
    m, n = p.m, p.n_dams
    K = np.asarray(p.K, dtype=float)
    d = np.full(n, 1.0 / (2 * n))
    return K[:m, :m], K[:m, m:] @ d, float(d @ K[m:, m:] @ d)


def expected_coancestry(K: FloatArray, sire_litters: FloatArray, n_dams: int) -> float:
    """`c'Kc` of `n_dams` matings with `sire_litters` litters per sire (sires first in K)."""
    m = int(np.asarray(sire_litters).size)
    c = np.r_[np.asarray(sire_litters, float) / (2 * n_dams), np.full(n_dams, 1.0 / (2 * n_dams))]
    assert K.shape == (m + n_dams, m + n_dams)
    return float(c @ K @ c)


def small_cohort_term(K: FloatArray, sire_litters: FloatArray, n_dams: int, n_new: float) -> float:
    """`(1/(2N)) sum_i c_i (1 - k_ii)` over all parents [du-2025]; 0 when `n_new` is 0."""
    if n_new <= 0:
        return 0.0
    c = np.r_[np.asarray(sire_litters, float) / (2 * n_dams), np.full(n_dams, 1.0 / (2 * n_dams))]
    return float(c @ (1.0 - np.diag(K))) / (2.0 * n_new)


def _bounds(p: OCSProblem) -> tuple[FloatArray, FloatArray]:
    lo = (
        np.zeros(p.m)
        if p.fixed_sire_litters is None
        else np.asarray(p.fixed_sire_litters, float).copy()
    )
    hi = np.maximum(np.asarray(p.caps, float), lo)
    return lo / p.n_dams, hi / p.n_dams


def _constraints(p: OCSProblem, x: cp.Variable, drop: set[str]) -> list[cp.Constraint]:
    lo, hi = _bounds(p)
    cons: list[cp.Constraint] = [cp.sum(x) == 1, x >= lo, x <= hi]
    if "age" not in drop and p.n_age_classes > 0:
        classes = np.unique(p.age_class[p.age_class >= 0])[: p.n_age_classes]
        for a in classes:
            idx = np.flatnonzero(p.age_class == a)
            cons.append(cp.sum(x[idx]) >= min(1.0, float(hi[idx].sum() * p.n_dams)) / p.n_dams)
    if "depth" not in drop and p.depth:
        cand = p.age_class >= 0
        if cand.any():
            target = float(np.mean(p.eqg[cand]))
            cons.append(x @ np.asarray(p.eqg, float) >= target)
    if "carrier" not in drop and p.has_carrier:
        t = np.asarray(p.carrier_t, float)
        cons.append(t.T @ x <= np.asarray(p.carrier_bound, float))
    return cons


def _solve(
    p: OCSProblem, build: object, solver: str
) -> tuple[NDArray[np.float64] | None, str, list[str]]:
    """Solve with all constraints; drop carrier, then age, then depth, on infeasibility."""
    ladder: list[list[str]] = [[], ["age"], ["age", "depth"]]
    if p.has_carrier:
        ladder = [[], *[["carrier", *d] for d in ladder]]
    for drop in ladder:
        x = cp.Variable(p.m)
        prob = build(x, _constraints(p, x, set(drop)))  # type: ignore[operator]
        try:
            prob.solve(solver=solver)
        except cp.SolverError:
            prob.solve(solver="SCS")
        if prob.status in ("optimal", "optimal_inaccurate") and x.value is not None:
            return np.asarray(x.value, float), str(prob.status), list(drop)
        last = str(prob.status)
    return None, last, ladder[-1]


def _finish(p: OCSProblem, x: NDArray[np.float64]) -> FloatArray:
    lo, hi = _bounds(p)
    x = np.clip(x, lo, hi)
    return np.asarray(x / x.sum() * p.n_dams, dtype=float)


def solve_conservation(p: OCSProblem, solver: str = "CLARABEL") -> OCSResult:
    """`min C(c)` (plus the small-cohort term, which is linear) under the constraints."""
    t0 = time.perf_counter()
    K_SS, k_sd, _ = _parts(p)
    Q = cp.psd_wrap(_psd(K_SS) / 4.0)
    lin = k_sd + _tau_lin(p)

    def build(x: cp.Variable, cons: list[cp.Constraint]) -> cp.Problem:
        return cp.Problem(cp.Minimize(cp.quad_form(x, Q) + lin @ x), cons)

    x, status, relaxed = _solve(p, build, solver)
    if x is None:
        raise RuntimeError(f"OCS conservation problem not solvable: {status}")
    lit = _finish(p, x)
    return OCSResult(
        litters=lit,
        coancestry=expected_coancestry(np.asarray(p.K, float), lit, p.n_dams),
        objective="conservation",
        target=None,
        infeasible=False,
        status=status,
        seconds=time.perf_counter() - t0,
        relaxed=relaxed,
    )


def _tau_lin(p: OCSProblem) -> FloatArray:
    """Sire part of the small-cohort term per unit of x (x = 2 s)."""
    if p.n_newborn <= 0:
        return np.zeros(p.m)
    k_ii = np.diag(np.asarray(p.K, float))[: p.m]
    return np.asarray((1.0 - k_ii) / 2.0 / (2.0 * p.n_newborn))


def _tau_const(p: OCSProblem) -> float:
    if p.n_newborn <= 0:
        return 0.0
    k_jj = np.diag(np.asarray(p.K, float))[p.m :]
    return float((1.0 - k_jj).sum() / (2 * p.n_dams) / (2.0 * p.n_newborn))


def solve_gain(p: OCSProblem, budget: float, solver: str = "CLARABEL") -> OCSResult:
    """`max merit'x` subject to `C(c) + tau(c) <= budget`; conservation fallback (D7)."""
    t0 = time.perf_counter()
    cons_res = solve_conservation(p, solver)
    K = np.asarray(p.K, float)
    c_min = cons_res.coancestry + small_cohort_term(K, cons_res.litters, p.n_dams, p.n_newborn)
    if p.merit is None or budget < c_min + TOL:
        cons_res.objective = "gain"
        cons_res.target = budget
        cons_res.infeasible = budget < c_min + TOL
        cons_res.c_min = c_min
        cons_res.seconds = time.perf_counter() - t0
        return cons_res
    K_SS, k_sd, c_dd = _parts(p)
    Q = cp.psd_wrap(_psd(K_SS) / 4.0)
    lin = k_sd + _tau_lin(p)
    const = c_dd + _tau_const(p)
    merit = np.nan_to_num(np.asarray(p.merit, float))

    def build(x: cp.Variable, cons: list[cp.Constraint]) -> cp.Problem:
        cons = [*cons, cp.quad_form(x, Q) + lin @ x + const <= budget]
        return cp.Problem(cp.Maximize(merit @ x), cons)

    x, status, relaxed = _solve(p, build, solver)
    if x is None:  # numerically infeasible at the boundary: keep the conservation solution
        cons_res.objective, cons_res.target, cons_res.infeasible = "gain", budget, True
        cons_res.c_min, cons_res.seconds = c_min, time.perf_counter() - t0
        return cons_res
    lit = _finish(p, x)
    return OCSResult(
        litters=lit,
        coancestry=expected_coancestry(K, lit, p.n_dams),
        objective="gain",
        target=budget,
        infeasible=False,
        status=status,
        seconds=time.perf_counter() - t0,
        relaxed=sorted(set(relaxed) | set(cons_res.relaxed)),
        c_min=c_min,
    )
