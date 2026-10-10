"""Status-quo breeding market (P3 task 3.5): popular sires, distance, partial avoidance."""

from __future__ import annotations

import numpy as np

from breeding_smarter.pedigree.relationships import pairwise_close_flags
from breeding_smarter.sim.interfaces import YearContext
from breeding_smarter.sim.kennels import haversine_km
from breeding_smarter.sim.state import DOMESTIC

MAX_MATRIX = 4_000_000  # process dams in blocks so the weight matrix stays small


def sample_rows(W: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """One column index per row with probability proportional to the row weights.

    Rows with zero total weight get -1.
    """
    if W.shape[1] == 0:
        return np.full(W.shape[0], -1, np.int64)
    cdf = np.cumsum(W, axis=1)
    tot = cdf[:, -1]
    u = rng.random(W.shape[0]) * tot
    j = (cdf <= u[:, None]).sum(axis=1)
    j = np.minimum(j, W.shape[1] - 1)
    return np.where(tot > 0, j, -1).astype(np.int64)


class MarketStrategy:
    """How breeders choose sires today (rich-get-richer popular sires).

    Weight of male j for a dam: `exp(beta a_j) (1 + offspring_5y_j)^alpha exp(-dist/300 km)
    age_factor_j`, with males of the dam's own kennel excluded with probability 0.5 and
    foreign AI sires used with probability `foreign_ai_sire_share` (no distance term).
    Close relatives (parent-offspring, full/half siblings, grandparent) are resampled with
    probability `close_mating_avoidance`, as are pairs the genetics model flags.
    """

    name = "market"

    def sire_weights(self, dams: np.ndarray, sires: np.ndarray, ctx: YearContext) -> np.ndarray:
        st, cfg, mk = ctx.state, ctx.breed_cfg, ctx.setup.sim.market
        a, k = st.animals, st.kennels
        beta = cfg.market.attractiveness_beta.value
        alpha = cfg.market.popular_sire_alpha.at(ctx.year)
        age = ctx.year - (a.birth_year[sires] + (a.birth_doy[sires] - 1) / 365.0)
        lo, hi = mk.prime_age_years.value
        age_f = np.where((age >= lo) & (age <= hi), 1.0, mk.off_prime_age_factor.value)
        base = np.exp(beta * a.attractiveness[sires]) * (1.0 + ctx.offspring_5y[sires]) ** alpha
        base *= age_f
        dk, sk = a.kennel[dams], a.kennel[sires]
        dist = haversine_km(
            k.lat[dk][:, None], k.lon[dk][:, None], k.lat[sk][None, :], k.lon[sk][None, :]
        )
        return base[None, :] * np.exp(-dist / mk.distance_scale_km.value)

    def _choose_domestic(
        self, dams: np.ndarray, sires: np.ndarray, ctx: YearContext, rng: np.random.Generator
    ) -> np.ndarray:
        out = np.full(dams.shape[0], -1, np.int64)
        if sires.size == 0:
            return out
        a = ctx.state.animals
        excl_p = ctx.setup.sim.market.same_kennel_exclusion_prob.value
        block = max(1, MAX_MATRIX // max(1, sires.size))
        for b0 in range(0, dams.shape[0], block):
            d = dams[b0 : b0 + block]
            W = self.sire_weights(d, sires, ctx)
            excl = np.asarray(rng.random(d.shape[0]) < excl_p, dtype=bool)
            same = a.kennel[d][:, None] == a.kennel[sires][None, :]
            W[excl[:, None] & same] = 0.0
            j = sample_rows(W, rng)
            out[b0 : b0 + block] = np.where(j >= 0, sires[np.maximum(j, 0)], -1)
        return out

    def _choose_foreign(self, n: int, ctx: YearContext, rng: np.random.Generator) -> np.ndarray:
        fs = ctx.foreign_sires
        if fs.size == 0 or n == 0:
            return np.full(n, -1, np.int64)
        a = ctx.state.animals
        cfg = ctx.breed_cfg
        w = np.exp(cfg.market.attractiveness_beta.value * a.attractiveness[fs])
        w *= (1.0 + ctx.offspring_5y[fs]) ** cfg.market.popular_sire_alpha.at(ctx.year)
        return fs[rng.choice(fs.size, size=n, p=w / w.sum())]

    def plan_matings(
        self, dams: np.ndarray, sires: np.ndarray, ctx: YearContext, rng: np.random.Generator
    ) -> np.ndarray:
        dams = np.asarray(dams, np.int64)
        out = np.full(dams.shape[0], -1, np.int64)
        if dams.size == 0:
            return out
        use_ai = np.zeros(dams.shape[0], dtype=bool)
        if ctx.subpop == DOMESTIC and ctx.is_registry_era and ctx.foreign_sires.size:
            share = ctx.breed_cfg.market.foreign_ai_sire_share.value
            use_ai = np.asarray(rng.random(dams.shape[0]) < share, dtype=bool)
        out[use_ai] = self._choose_foreign(int(use_ai.sum()), ctx, rng)
        dom = ~use_ai
        out[dom] = self._choose_domestic(dams[dom], sires, ctx, rng)
        return self._avoid(dams, out, sires, use_ai, ctx, rng)

    def _avoid(
        self,
        dams: np.ndarray,
        out: np.ndarray,
        sires: np.ndarray,
        use_ai: np.ndarray,
        ctx: YearContext,
        rng: np.random.Generator,
    ) -> np.ndarray:
        a = ctx.state.animals
        avoid_p = ctx.breed_cfg.market.close_mating_avoidance.value
        for attempt in range(ctx.setup.sim.market.max_resample_retries.value + 1):
            has = out >= 0
            close = np.zeros(dams.shape[0], dtype=bool)
            close[has] = pairwise_close_flags(a.sire, a.dam, dams[has], out[has])
            if attempt == 0:
                self._count(ctx, "close_initial", int(close.sum()), int(has.sum()))
            if attempt == ctx.setup.sim.market.max_resample_retries.value:
                break
            redo = close & (rng.random(dams.shape[0]) < avoid_p)
            redo[has] |= ctx.genetics.pair_avoid(ctx.state, dams[has], out[has], rng)
            if not redo.any():
                break
            ai = redo & use_ai
            dom = redo & ~use_ai
            out[ai] = self._choose_foreign(int(ai.sum()), ctx, rng)
            out[dom] = self._choose_domestic(dams[dom], sires, ctx, rng)
        has = out >= 0
        final = pairwise_close_flags(a.sire, a.dam, dams[has], out[has])
        self._count(ctx, "close_final", int(final.sum()), 0)
        return out

    @staticmethod
    def _count(ctx: YearContext, key: str, n_close: int, n_pairs: int) -> None:
        """Close-relative mating counters (registry era, per breed) for the avoidance test."""
        if not ctx.is_registry_era or ctx.subpop != DOMESTIC:
            return
        m = ctx.state.meta.setdefault(f"close_{ctx.breed_cfg.breed_id}", {})
        m[key] = m.get(key, 0) + n_close
        if n_pairs:
            m["pairs"] = m.get("pairs", 0) + n_pairs
