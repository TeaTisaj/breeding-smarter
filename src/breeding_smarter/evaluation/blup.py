"""Pedigree BLUP for HD on registry data only (P4 task 4.6).

Model per breed: `y = birth_year_group + sex + animal + e`, with `y` the FCI grade scored
A=1 .. E=5 (a linear model on the categorical score, the common practical simplification).
`lambda = sigma_e^2 / sigma_a^2 = (1 - h2) / h2` uses the simulation's true h2 (a real
evaluation would estimate variance components). A-inverse by Henderson's rules with
inbreeding (D from the P2 engine). Mixed model equations solved by conjugate gradients with a
Jacobi preconditioner (fallback: sparse direct solve).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.sparse.linalg import cg, spsolve

from breeding_smarter.config.models import GeneticsConfig
from breeding_smarter.io.parquet import read_table, write_table
from breeding_smarter.pedigree import Pedigree, inbreeding
from breeding_smarter.pedigree.core import FloatArray, IntArray
from breeding_smarter.schema.tables import ANIMALS, EBV, HEALTH_TESTS

log = logging.getLogger(__name__)
GRADE_SCORE = {"A": 1.0, "B": 2.0, "C": 3.0, "D": 4.0, "E": 5.0}
CG_TOL = 1e-8


def henderson_ainv(sire: IntArray, dam: IntArray, D: FloatArray) -> sp.csr_matrix:
    """A-inverse by Henderson's rules with inbreeding.

    For animal i with `b = 1/D_i`: add `b` to (i,i); `-b/2` to (i,p) and (p,i) for each known
    parent p; `b/4` to (p,q) for every pair of known parents (including p = q).
    """
    n = sire.shape[0]
    b = 1.0 / D
    i = np.arange(n)
    rows: list[IntArray] = [i]
    cols: list[IntArray] = [i]
    vals: list[FloatArray] = [b]
    parents = [(sire >= 0, sire), (dam >= 0, dam)]
    for known, p in parents:
        k = np.flatnonzero(known)
        rows += [k, p[k]]
        cols += [p[k], k]
        vals += [-b[k] / 2, -b[k] / 2]
    for kp, p in parents:
        for kq, q in parents:
            k = np.flatnonzero(kp & kq)
            rows.append(p[k])
            cols.append(q[k])
            vals.append(b[k] / 4)
    return sp.coo_matrix(
        (np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n)
    ).tocsr()


@dataclass
class BlupResult:
    ebv: FloatArray
    accuracy: FloatArray
    fixed: FloatArray
    converged: bool
    n_records: int


def solve_mme(
    ped: Pedigree,
    D: FloatArray,
    rec_idx: IntArray,
    y: FloatArray,
    X: sp.csr_matrix,
    lam: float,
) -> tuple[FloatArray, FloatArray, bool]:
    """Solve `[X'X X'Z; Z'X Z'Z + lam Ainv] [b; u] = [X'y; Z'y]`; returns (b, u, converged)."""
    n = ped.n
    nr = rec_idx.size
    Z = sp.csr_matrix((np.ones(nr), (np.arange(nr), rec_idx)), shape=(nr, n))
    Ainv = henderson_ainv(ped.sire, ped.dam, D)
    C = sp.bmat([[X.T @ X, X.T @ Z], [Z.T @ X, Z.T @ Z + lam * Ainv]], format="csr")
    rhs = np.concatenate([X.T @ y, Z.T @ y])
    diag = C.diagonal()
    M = sp.diags(1.0 / np.where(diag > 0, diag, 1.0))
    sol, info = cg(C, rhs, rtol=CG_TOL, maxiter=5000, M=M)
    ok = info == 0
    if not ok:
        log.warning("CG did not converge (info=%s); falling back to spsolve", info)
        sol = spsolve(C.tocsc(), rhs)
    nf = X.shape[1]
    return sol[:nf], sol[nf:], ok


def reliability(ped: Pedigree, has_record: np.ndarray, h2: float) -> FloatArray:
    """Approximate reliability (documented approximation, not exact PEV).

    `r2_own = h2` with an own record; `r2_prog = n_p / (n_p + (4 - h2) / h2)` for `n_p`
    progeny with records; `r2_par = (r2_sire + r2_dam) / 4` from a first pass with own and
    progeny information; `r2 = 1 - (1 - r2_own)(1 - r2_prog)(1 - r2_par)`.
    """
    n = ped.n
    own = np.where(has_record, h2, 0.0)
    n_prog = np.zeros(n)
    for par in (ped.sire, ped.dam):
        k = (par >= 0) & has_record
        np.add.at(n_prog, par[k], 1.0)
    prog = n_prog / (n_prog + (4.0 - h2) / h2)
    first = 1.0 - (1.0 - own) * (1.0 - prog)
    rs = np.where(ped.sire >= 0, first[np.maximum(ped.sire, 0)], 0.0)
    rd = np.where(ped.dam >= 0, first[np.maximum(ped.dam, 0)], 0.0)
    r_par = 0.25 * (rs + rd)
    return np.asarray(1.0 - (1.0 - own) * (1.0 - prog) * (1.0 - r_par))


def evaluate_arrays(
    ped: Pedigree,
    D: FloatArray,
    rec_idx: IntArray,
    y: FloatArray,
    h2: float,
    group_years: int = 5,
) -> BlupResult:
    """BLUP from arrays: records `y` (grade scores) on animals `rec_idx` of `ped`; fixed
    effects birth-year group and sex (as in `evaluate_breed`)."""
    nr = rec_idx.size
    if nr == 0:
        z = np.zeros(ped.n)
        return BlupResult(z, z, np.zeros(0), True, 0)
    years = ped.birth_year[rec_idx].astype(np.int64)
    levels, g = np.unique((years // group_years) * group_years, return_inverse=True)
    male = (ped.sex[rec_idx] == 1).astype(float)
    X = sp.hstack(
        [
            sp.csr_matrix((np.ones(nr), (np.arange(nr), g)), shape=(nr, levels.size)),
            sp.csr_matrix(male[:, None]),
        ],
        format="csr",
    )
    b, u, ok = solve_mme(ped, D, rec_idx, y, X, (1.0 - h2) / h2)
    has = np.zeros(ped.n, bool)
    has[rec_idx] = True
    return BlupResult(u, np.sqrt(reliability(ped, has, h2)), b, ok, nr)


def evaluate_breed(
    animals: pd.DataFrame,
    health: pd.DataFrame,
    breed_id: str,
    h2: float,
    group_years: int = 5,
) -> tuple[IntArray, BlupResult]:
    """EBVs (grade-score scale, higher = worse hips) for one breed. Returns registry idx and
    the result for the breed sub-pedigree (breed animals plus ancestors)."""
    full = Pedigree.from_registry(animals)
    sub, old_to_new = full.prune(full.breed_mask(breed_id))
    kept = np.flatnonzero(old_to_new >= 0)
    _, D = inbreeding(sub)
    hd = health[health["test_type"] == "HD"].sort_values("test_date").groupby("idx").tail(1)
    hd = hd[hd["idx"].isin(kept)]
    rec = old_to_new[hd["idx"].to_numpy(np.int64)]
    y = np.asarray(hd["result"].map(GRADE_SCORE).to_numpy(float), dtype=np.float64)
    years = sub.birth_year[rec].astype(np.int64)
    grp = (years // group_years) * group_years
    levels, g = np.unique(grp, return_inverse=True)
    male = (sub.sex[rec] == 1).astype(float)
    nr = rec.size
    X = sp.hstack(
        [
            sp.csr_matrix((np.ones(nr), (np.arange(nr), g)), shape=(nr, levels.size)),
            sp.csr_matrix(male[:, None]),
        ],
        format="csr",
    )
    if nr == 0:
        z = np.zeros(sub.n)
        return sub.ids, BlupResult(z, z, np.zeros(0), True, 0)
    lam = (1.0 - h2) / h2
    b, u, ok = solve_mme(sub, D, rec, y, X, lam)
    has = np.zeros(sub.n, bool)
    has[rec] = True
    acc = np.sqrt(reliability(sub, has, h2))
    return sub.ids, BlupResult(u, acc, b, ok, nr)


def to_index(ebv: FloatArray, recent: np.ndarray) -> FloatArray:
    """Breed index: mean 100 and SD 10 among recent animals, higher is better (SKK).

    `index = 100 - 10 (ebv - mean_recent) / sd_recent` (the grade-score EBV is higher = worse).
    """
    ref = ebv[recent] if recent.any() else ebv
    sd = float(ref.std()) or 1.0
    return np.asarray(100.0 - 10.0 * (ebv - ref.mean()) / sd)


def evaluate_tables(
    animals: pd.DataFrame,
    health: pd.DataFrame,
    h2: float,
    evaluation_date: str,
    group_years: int = 5,
    sd_window_years: int = 5,
) -> pd.DataFrame:
    """EBV table rows for every registered non-stub animal of every breed."""
    eval_date = pd.Timestamp(evaluation_date)
    frames = []
    for breed_id in sorted(animals["breed_id"].unique()):
        ids, res = evaluate_breed(animals, health, breed_id, h2, group_years)
        sub = animals.set_index("idx").loc[ids]
        keep = (sub["breed_id"] == breed_id).to_numpy() & (sub["studbook"] != "FOREIGN").to_numpy()
        by = sub["birth_date"].dt.year.to_numpy()
        recent = keep & (by > eval_date.year - sd_window_years)
        index = to_index(res.ebv, recent)
        frames.append(
            pd.DataFrame(
                {
                    "idx": ids[keep],
                    "trait": "HD",
                    "ebv_index": index[keep],
                    "accuracy": res.accuracy[keep],
                    "evaluation_date": eval_date,
                }
            )
        )
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=EBV.columns)
    return out.sort_values("idx", kind="stable").reset_index(drop=True)


def evaluate_run(run_root: Path, h2: float, cfg: GeneticsConfig) -> Path:
    """Read registry tables of a run, evaluate every breed and write `registry/ebv.parquet`."""
    run_root = Path(run_root)
    animals = read_table(run_root / ANIMALS.filename, ANIMALS)
    health = read_table(run_root / HEALTH_TESTS.filename, HEALTH_TESTS)
    ebv = evaluate_tables(
        animals,
        health,
        h2,
        cfg.evaluation_date,
        cfg.ebv_birth_year_group_years.value,
        cfg.ebv_index_sd_window_years.value,
    )
    return write_table(ebv, EBV, run_root / EBV.filename)
