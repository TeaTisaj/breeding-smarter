"""Dog genetics model and observations (P4): neutral gene drop (true IBD), Mendelian disease
loci with DNA testing, a polygenic HD liability trait with FCI screening, and table output.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import norm

from breeding_smarter.config.loader import load_genetics, load_loci
from breeding_smarter.config.models import GeneticsConfig, LociConfig
from breeding_smarter.schema.tables import ANIMALS_TRUTH, DNA_TESTS, GENOTYPES_TRUTH, HEALTH_TESTS
from breeding_smarter.sim.interfaces import SimSetup
from breeding_smarter.sim.state import DOMESTIC, SimState

GRADES = ("A", "B", "C", "D", "E")
GENOTYPE_NAMES = ("clear", "carrier", "affected")
NO_GRADE = -1


def _grow(arr: np.ndarray, n: int, fill: Any) -> np.ndarray:
    if arr.shape[0] >= n:
        return arr
    new = np.full((max(n, 2 * arr.shape[0], 1024), *arr.shape[1:]), fill, dtype=arr.dtype)
    new[: arr.shape[0]] = arr
    return new


def _frac_dates(t: np.ndarray) -> np.ndarray:
    """Fractional years -> datetime64[D]."""
    year = np.floor(t).astype(np.int64)
    doy = np.clip(np.floor((t - year) * 365.0).astype(np.int64), 0, 364)
    base = (year - 1970).astype("datetime64[Y]").astype("datetime64[D]")
    return base + doy.astype("timedelta64[D]")


class DogGenetics:
    """Implements `GeneticsModel` for dogs. All randomness comes from the passed generators."""

    def __init__(self, setup: SimSetup, cfg: GeneticsConfig, loci: LociConfig):
        self.setup = setup
        self.cfg = cfg
        self.loci = loci
        self.L = cfg.n_neutral_loci.value
        self.K = len(loci.loci)
        self.h2 = cfg.hd_heritability.value
        self.penetrance = np.array([x.penetrance.value for x in loci.loci])
        self.avail = np.array(
            [x.test_available_from.value if x.test_available_from else 99999 for x in loci.loci]
        )
        self.base_q = np.array(
            [
                [loci.base_allele_frequency.value[b.breed_id][lid] for lid in loci.ids]
                for b in setup.breeds
            ]
        )
        # liability thresholds per breed (phenotypic variance 1 in the base population)
        self.thresholds = np.array(
            [
                norm.ppf(np.cumsum([b.health.hd_base_distribution.value[g] for g in GRADES[:-1]]))
                for b in setup.breeds
            ]
        )
        self.exclude = [
            np.array([GRADES.index(g) for g in b.health.hd_exclude_grades.value])
            for b in setup.breeds
        ]
        self.exclude_known_carriers = False  # E3 policy (c); never used for the history
        self.n = 0
        self.tbv = np.zeros(0)
        self.u_excl = np.zeros(0)
        self.liability = np.zeros(0)
        self.grade = np.zeros(0, np.int8)
        self.screen_t = np.zeros(0)
        self.screen_decided = np.zeros(0, bool)
        self.geno = np.zeros((0, self.K), np.int8)
        self.tested = np.zeros((0, self.K), bool)
        self.test_t = np.zeros((0, self.K))
        self.test_lab = np.zeros((0, self.K), np.int8)
        self.neutral = np.zeros((0, self.L, 2), np.uint16)
        self.row_of = np.zeros(0, np.int64)
        self.n_rows = 0

    @classmethod
    def from_setup(cls, setup: SimSetup) -> DogGenetics:
        return cls(setup, load_genetics(setup.sim.genetics), load_loci(setup.sim.loci))

    # ------------------------------------------------------------------ storage
    def _ensure(self, n: int) -> None:
        self.tbv = _grow(self.tbv, n, 0.0)
        self.u_excl = _grow(self.u_excl, n, 1.0)
        self.liability = _grow(self.liability, n, np.nan)
        self.grade = _grow(self.grade, n, NO_GRADE)
        self.screen_t = _grow(self.screen_t, n, np.nan)
        self.screen_decided = _grow(self.screen_decided, n, False)
        self.geno = _grow(self.geno, n, 0)
        self.tested = _grow(self.tested, n, False)
        self.test_t = _grow(self.test_t, n, np.nan)
        self.test_lab = _grow(self.test_lab, n, 0)
        self.row_of = _grow(self.row_of, n, -1)
        self.n = max(self.n, n)

    def _add_rows(self, gids: np.ndarray, alleles: np.ndarray) -> None:
        self.neutral = _grow(self.neutral, self.n_rows + gids.size, 0)
        self.neutral[self.n_rows : self.n_rows + gids.size] = alleles
        self.row_of[gids] = np.arange(self.n_rows, self.n_rows + gids.size)
        self.n_rows += gids.size

    def compact(self, state: SimState, year: int) -> None:
        """Drop neutral alleles of animals that are dead by the end of `year`."""
        holders = np.flatnonzero(self.row_of[: self.n] >= 0)
        alive = holders[state.animals.death_year[holders] > year]
        rows = self.row_of[alive]
        self.neutral[: alive.size] = self.neutral[rows]
        self.row_of[holders] = -1
        self.row_of[alive] = np.arange(alive.size)
        self.n_rows = alive.size
        if self.neutral.shape[0] > 2 * max(self.n_rows, 1024):
            self.neutral = self.neutral[: max(int(1.25 * self.n_rows), 1024)].copy()

    @property
    def n_holders(self) -> int:
        return int((self.row_of[: self.n] >= 0).sum())

    # ------------------------------------------------------------------ hooks
    def init_founders(self, state: SimState, gids: np.ndarray, rng: np.random.Generator) -> None:
        self._ensure(state.n)
        n = gids.size
        if (2 * gids + 1).max(initial=0) > np.iinfo(np.uint16).max:
            raise ValueError("founder allele ids exceed uint16; founders must have small gids")
        base = (2 * gids).astype(np.uint16)
        alleles = np.stack(
            [np.repeat(base[:, None], self.L, 1), np.repeat(base[:, None] + 1, self.L, 1)], axis=2
        )
        self._add_rows(gids, alleles)
        q = self.base_q[state.animals.breed[gids]]
        self.geno[gids] = rng.binomial(2, q).astype(np.int8)
        self.tbv[gids] = rng.normal(0.0, np.sqrt(self.h2), n)
        self.u_excl[gids] = rng.random(n)
        state.animals.data["f_true"][gids] = 0.0

    def make_offspring(
        self,
        state: SimState,
        sire: np.ndarray,
        dam: np.ndarray,
        child_gids: np.ndarray,
        rng: np.random.Generator,
    ) -> None:
        """Gene drop (one random allele per parent and locus), Mendelian transmission at the
        disease loci and the infinitesimal model with inbreeding-adjusted Mendelian sampling:
        `tbv = (tbv_s + tbv_d) / 2 + N(0, 0.5 (1 - (F_s + F_d) / 2) sigma_a^2)`."""
        self._ensure(state.n)
        n = child_gids.size
        rs, rd = self.row_of[sire], self.row_of[dam]
        if (rs < 0).any() or (rd < 0).any():
            raise RuntimeError("a parent has no neutral alleles (dead or never initialised)")
        loci = np.arange(self.L)
        ps = rng.integers(0, 2, (n, self.L), dtype=np.uint8)
        pd_ = rng.integers(0, 2, (n, self.L), dtype=np.uint8)
        a_s = self.neutral[rs[:, None], loci[None, :], ps]
        a_d = self.neutral[rd[:, None], loci[None, :], pd_]
        state.animals.data["f_true"][child_gids] = (a_s == a_d).mean(axis=1)
        self._add_rows(child_gids, np.stack([a_s, a_d], axis=2))
        gs, gd = self.geno[sire], self.geno[dam]
        ts = rng.random((n, self.K)) < gs / 2.0
        td = rng.random((n, self.K)) < gd / 2.0
        self.geno[child_gids] = ts.astype(np.int8) + td.astype(np.int8)
        f = state.animals.f_true
        var = 0.5 * (1.0 - 0.5 * (f[sire] + f[dam])) * self.h2
        self.tbv[child_gids] = 0.5 * (self.tbv[sire] + self.tbv[dam]) + rng.normal(
            0.0, np.sqrt(np.maximum(var, 0.0))
        )
        self.u_excl[child_gids] = rng.random(n)

    def known_affected(self, gids: np.ndarray) -> np.ndarray:
        return (self.tested[gids] & (self.geno[gids] == 2)).any(axis=1)

    def is_eligible(self, state: SimState, gids: np.ndarray, year: int) -> np.ndarray:
        """Excluded: an HD grade in the breed's exclusion list (hks-pravilnik), or a known
        affected genotype with probability `affected_exclusion_prob` (fixed per animal)."""
        breed = state.animals.breed[gids]
        g = self.grade[gids]
        bad = np.zeros(gids.size, bool)
        for b, excl in enumerate(self.exclude):
            m = breed == b
            bad[m] = np.isin(g[m], excl)
        p = self.cfg.affected_exclusion_prob.value
        bad |= self.known_affected(gids) & (self.u_excl[gids] < p)
        if self.exclude_known_carriers:  # experiment E3 policy (c)
            testable = np.array([lc.testable for lc in self.loci.loci])
            bad |= (self.tested[gids][:, testable] & (self.geno[gids][:, testable] >= 1)).any(1)
        return ~bad

    def pair_avoid(
        self, state: SimState, dams: np.ndarray, sires: np.ndarray, rng: np.random.Generator
    ) -> np.ndarray:
        """Known carrier (or affected) x known carrier at the same locus, resampled w.p. 0.9."""
        risky = (
            self.tested[dams]
            & self.tested[sires]
            & (self.geno[dams] >= 1)
            & (self.geno[sires] >= 1)
        ).any(axis=1)
        return np.asarray(
            risky & (rng.random(dams.size) < self.cfg.carrier_pair_resample_prob.value)
        )

    def _test(self, gids: np.ndarray, k: int, t: np.ndarray, rng: np.random.Generator) -> None:
        self.tested[gids, k] = True
        self.test_t[gids, k] = t
        self.test_lab[gids, k] = rng.integers(0, len(self.cfg.labs), gids.size)

    def dna_rate(self, k: int, breed: int, year: int) -> float:
        a = self.avail[k]
        end = self.cfg.dna_test_rate_ramp_end_year.value
        r0 = self.cfg.dna_test_rate_initial.value
        r1 = self.setup.breeds[breed].health.dna_test_rate_2026.value
        w = np.clip((year - a) / max(1, end - a), 0.0, 1.0)
        return float(r0 + (r1 - r0) * w)

    def on_import(
        self, state: SimState, gids: np.ndarray, year: int, rng: np.random.Generator
    ) -> None:
        """Imports and foreign AI sires are DNA tested on entry with probability 0.7."""
        p = self.cfg.import_dna_test_prob.value
        for k in range(self.K):
            if self.avail[k] > year:
                continue
            g = gids[~self.tested[gids, k]]
            g = g[rng.random(g.size) < p]
            self._test(g, k, year + rng.random(g.size) * 0.99, rng)

    def on_year_end(self, state: SimState, year: int, rng: np.random.Generator) -> None:
        a = state.animals
        self._ensure(state.n)
        # DNA testing of living domestic breeding candidates older than 12 months
        min_age = self.cfg.dna_test_min_age_months.value / 12.0
        birth_t = a.birth_year + (a.birth_doy - 1) / 365.0
        pool = np.flatnonzero(
            a.is_candidate
            & (a.subpop == DOMESTIC)
            & (a.death_year > year)
            & (birth_t <= year - min_age)
        )
        for k in range(self.K):
            if self.avail[k] > year or pool.size == 0:
                continue
            g = pool[~self.tested[pool, k]]
            rates = np.array([self.dna_rate(k, b, year) for b in range(len(self.setup.breeds))])
            g = g[rng.random(g.size) < rates[a.breed[g]]]
            self._test(g, k, year + rng.random(g.size) * 0.99, rng)
        # HD screening at 12 to 24 months (one decision per animal)
        lo_m, hi_m = self.cfg.hd_screening_age_months.value
        start = np.array([b.health.hd_screening_start_year.value for b in self.setup.breeds])
        cohort = np.flatnonzero(
            (a.birth_year == year - 1) & (a.death_year > year) & ~self.screen_decided[: state.n]
        )
        cohort = cohort[start[a.breed[cohort]] <= year]
        if cohort.size:
            self.screen_decided[cohort] = True
            r_c = np.array([b.health.hd_screening_rate_candidates.value for b in self.setup.breeds])
            r_o = np.array([b.health.hd_screening_rate_others.value for b in self.setup.breeds])
            br = a.breed[cohort]
            rate = np.where(a.is_candidate[cohort], r_c[br], r_o[br])
            s = cohort[rng.random(cohort.size) < rate]
            bt = birth_t[s]
            lo = np.maximum(year, bt + lo_m / 12.0)
            hi = np.minimum(year + 0.999, bt + hi_m / 12.0)
            t = lo + rng.random(s.size) * np.maximum(hi - lo, 0.0)
            liab = self.tbv[s] + rng.normal(0.0, np.sqrt(1.0 - self.h2), s.size)
            self.liability[s] = liab
            self.screen_t[s] = t
            th = self.thresholds[a.breed[s]]
            self.grade[s] = (liab[:, None] > th).sum(axis=1).astype(np.int8)
        self.compact(state, year)

    # ------------------------------------------------------------------ persistence
    def state_arrays(self) -> dict[str, np.ndarray]:
        n = self.n
        return {
            "g_tbv": self.tbv[:n],
            "g_u_excl": self.u_excl[:n],
            "g_liability": self.liability[:n],
            "g_grade": self.grade[:n],
            "g_screen_t": self.screen_t[:n],
            "g_screen_decided": self.screen_decided[:n],
            "g_geno": self.geno[:n],
            "g_tested": self.tested[:n],
            "g_test_t": self.test_t[:n],
            "g_test_lab": self.test_lab[:n],
            "g_row_of": self.row_of[:n],
            "g_neutral": self.neutral[: self.n_rows],
        }

    def load_arrays(self, arrays: dict[str, np.ndarray]) -> None:
        self.tbv = arrays["g_tbv"].copy()
        self.n = self.tbv.shape[0]
        self.u_excl = arrays["g_u_excl"].copy()
        self.liability = arrays["g_liability"].copy()
        self.grade = arrays["g_grade"].copy()
        self.screen_t = arrays["g_screen_t"].copy()
        self.screen_decided = arrays["g_screen_decided"].copy()
        self.geno = arrays["g_geno"].copy()
        self.tested = arrays["g_tested"].copy()
        self.test_t = arrays["g_test_t"].copy()
        self.test_lab = arrays["g_test_lab"].copy()
        self.row_of = arrays["g_row_of"].copy()
        self.neutral = arrays["g_neutral"].copy()
        self.n_rows = self.neutral.shape[0]

    # ------------------------------------------------------------------ tables
    def contribute_tables(
        self, state: SimState, setup: SimSetup, tables: dict[str, pd.DataFrame], idx_of: np.ndarray
    ) -> None:
        """Health and DNA test rows for registered animals, truth columns and genotypes."""
        n = state.n
        self._ensure(n)
        end = setup.sim.end_year + 1
        a = state.animals
        reg = idx_of >= 0
        stub = a.foreign_stub
        birth_t = a.birth_year + (a.birth_doy - 1) / 365.0
        hs = np.flatnonzero(reg & ~stub & (self.grade[:n] >= 0) & (self.screen_t[:n] < end))
        hs = hs[np.argsort(idx_of[hs], kind="stable")]
        tables[HEALTH_TESTS.name] = pd.DataFrame(
            {
                "test_id": np.arange(hs.size, dtype=np.int64),
                "idx": idx_of[hs],
                "test_type": "HD",
                "scheme": "FCI",
                "result": np.array(GRADES, dtype=object)[self.grade[hs]],
                "test_date": _frac_dates(self.screen_t[hs]),
                "age_months": np.floor((self.screen_t[hs] - birth_t[hs]) * 12).astype(np.int16),
                "official": True,
            }
        )
        rows = []
        for k, locus in enumerate(self.loci.loci):
            if not locus.testable:
                continue  # NOVEL_X never appears in observed tables
            g = np.flatnonzero(reg & self.tested[:n, k] & (self.test_t[:n, k] < end))
            rows.append(
                pd.DataFrame(
                    {
                        "idx": idx_of[g],
                        "locus_id": locus.id,
                        "genotype": np.array(GENOTYPE_NAMES, dtype=object)[self.geno[g, k]],
                        "test_date": _frac_dates(self.test_t[g, k]),
                        "lab": np.array(self.cfg.labs, dtype=object)[self.test_lab[g, k]],
                    }
                )
            )
        dna = (
            pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=DNA_TESTS.columns)
        )
        tables[DNA_TESTS.name] = dna.sort_values(["idx", "locus_id"], kind="stable").reset_index(
            drop=True
        )
        truth = tables[ANIMALS_TRUTH.name]
        truth["tbv_hd"] = self.tbv[:n]
        truth["hd_liability"] = np.where(self.screen_t[:n] < end, self.liability[:n], np.nan)
        tables[GENOTYPES_TRUTH.name] = pd.DataFrame(
            {
                "gid": np.repeat(np.arange(n, dtype=np.int64), self.K),
                "locus_id": np.tile(np.array(self.loci.ids, dtype=object), n),
                "n_risk_alleles": self.geno[:n].ravel().astype(np.int8),
            }
        )

    def post_write(self, run_root: Any) -> None:
        """Pedigree BLUP on the registry tables just written (P4 task 4.6)."""
        from breeding_smarter.evaluation.blup import evaluate_run

        evaluate_run(run_root, self.h2, self.cfg)
