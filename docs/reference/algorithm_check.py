"""Verify the algorithms specified in the plan against a dense oracle."""
import heapq
import numpy as np

rng = np.random.default_rng(0)


def random_ped(n, p_unknown=0.2):
    sire = -np.ones(n, int); dam = -np.ones(n, int); sex = rng.integers(0, 2, n)
    for i in range(n):
        males = [j for j in range(i) if sex[j] == 1]
        females = [j for j in range(i) if sex[j] == 0]
        if males and rng.random() > p_unknown:
            sire[i] = males[rng.integers(max(0, len(males) - 15), len(males))]
        if females and rng.random() > p_unknown:
            dam[i] = females[rng.integers(max(0, len(females) - 15), len(females))]
    return sire, dam


def dense_A(sire, dam):
    n = len(sire); A = np.zeros((n, n))
    for i in range(n):
        s, d = sire[i], dam[i]
        for j in range(i):
            A[i, j] = A[j, i] = 0.5 * ((A[j, s] if s >= 0 else 0) + (A[j, d] if d >= 0 else 0))
        A[i, i] = 1 + (0.5 * A[s, d] if s >= 0 and d >= 0 else 0)
    return A


def Fget(F, k):
    return -1.0 if k < 0 else F[k]


def l_row(sire, dam, D, start_parents, start_D):
    """Row of L for a (possibly virtual) animal with given parents; returns dict and sum L^2 D."""
    L = {}
    acc = start_D
    heap = []
    for p in start_parents:
        if p >= 0:
            if p not in L:
                heapq.heappush(heap, -p)
            L[p] = L.get(p, 0) + 0.5
    while heap:
        j = -heapq.heappop(heap)
        acc += L[j] ** 2 * D[j]
        for p in (sire[j], dam[j]):
            if p >= 0:
                if p not in L:
                    heapq.heappush(heap, -p)
                L[p] = L.get(p, 0) + 0.5 * L[j]
    return L, acc


def meuwissen_luo(sire, dam):
    n = len(sire); F = np.zeros(n); D = np.zeros(n)
    for i in range(n):
        s, d = sire[i], dam[i]
        D[i] = 0.5 - 0.25 * (Fget(F, s) + Fget(F, d))
        if s < 0 or d < 0:
            F[i] = 0; continue
        _, acc = l_row(sire, dam, D, (s, d), D[i])
        F[i] = acc - 1
    return F, D


def colleau(sire, dam, D, x):
    n = len(sire); u = x.astype(float).copy()
    for i in range(n - 1, -1, -1):
        if sire[i] >= 0: u[sire[i]] += 0.5 * u[i]
        if dam[i] >= 0: u[dam[i]] += 0.5 * u[i]
    w = D * u; y = np.zeros(n)
    for i in range(n):
        y[i] = w[i] + 0.5 * ((y[sire[i]] if sire[i] >= 0 else 0) + (y[dam[i]] if dam[i] >= 0 else 0))
    return y


def full_row(sire, dam, D, i):
    L, _ = l_row(sire, dam, D, (sire[i], dam[i]), 0)
    L[i] = 1.0
    return L


def eqg(sire, dam):
    e = np.zeros(len(sire))
    for i in range(len(sire)):
        for p in (sire[i], dam[i]):
            if p >= 0: e[i] += 0.5 * (1 + e[p])
    return e


def eqg_brute(sire, dam, i, g=1):
    tot = 0
    for p in (sire[i], dam[i]):
        if p >= 0: tot += 0.5 ** g + eqg_brute(sire, dam, p, g + 1)
    return tot


def henderson_ainv(sire, dam, D):
    n = len(sire); Ai = np.zeros((n, n))
    for i in range(n):
        b = 1 / D[i]; s, d = sire[i], dam[i]
        Ai[i, i] += b
        for p in (s, d):
            if p >= 0:
                Ai[i, p] -= b / 2; Ai[p, i] -= b / 2
        for p in (s, d):
            for q in (s, d):
                if p >= 0 and q >= 0: Ai[p, q] += b / 4
    return Ai


maxerr = {k: 0.0 for k in ["F", "Ax", "pair_virtual", "decomp", "Ainv", "eqg", "contrib_sum"]}
for trial in range(40):
    n = int(rng.integers(5, 120))
    sire, dam = random_ped(n)
    A = dense_A(sire, dam)
    F, D = meuwissen_luo(sire, dam)
    maxerr["F"] = max(maxerr["F"], np.abs(F - (np.diag(A) - 1)).max())
    x = rng.normal(size=n)
    maxerr["Ax"] = max(maxerr["Ax"], np.abs(colleau(sire, dam, D, x) - A @ x).max())
    for _ in range(10):
        a, b = rng.integers(0, n, 2)
        Fa, Fb = F[a], F[b]
        _, acc = l_row(sire, dam, D, (a, b), 0.5 - 0.25 * (Fa + Fb))
        maxerr["pair_virtual"] = max(maxerr["pair_virtual"], abs((acc - 1) - A[a, b] / 2))
        La, Lb = full_row(sire, dam, D, a), full_row(sire, dam, D, b)
        dec = sum(0.5 * La[j] * Lb[j] * D[j] for j in La if j in Lb)
        maxerr["decomp"] = max(maxerr["decomp"], abs(dec - A[a, b] / 2))
    maxerr["Ainv"] = max(maxerr["Ainv"], np.abs(henderson_ainv(sire, dam, D) - np.linalg.inv(A)).max())
    if n <= 40:
        e = eqg(sire, dam)
        maxerr["eqg"] = max(maxerr["eqg"], max(abs(e[i] - eqg_brute(sire, dam, i)) for i in range(n)))
    # founder contributions with phantom parents: build phantom ped
    ns, nd, mapping = [], [], {}
    for i in range(n):
        s, d = sire[i], dam[i]
        if (s >= 0) != (d >= 0):  # exactly one known -> phantom
            ns.append(-1); nd.append(-1); ph = len(ns) - 1
            s = mapping[s] if s >= 0 else ph
            d = mapping[d] if d >= 0 else ph
        else:
            s = mapping[s] if s >= 0 else -1
            d = mapping[d] if d >= 0 else -1
        ns.append(s); nd.append(d); mapping[i] = len(ns) - 1
    ns, nd = np.array(ns), np.array(nd)
    ref = np.zeros(len(ns)); idxs = [mapping[i] for i in range(n - min(10, n), n)]
    ref[idxs] = 1 / len(idxs)
    u = ref.copy()
    for i in range(len(ns) - 1, -1, -1):
        if ns[i] >= 0: u[ns[i]] += 0.5 * u[i]
        if nd[i] >= 0: u[nd[i]] += 0.5 * u[i]
    founders = (ns < 0) & (nd < 0)
    maxerr["contrib_sum"] = max(maxerr["contrib_sum"], abs(u[founders].sum() - 1))

print({k: f"{v:.2e}" for k, v in maxerr.items()})

# Known answers: repeated full-sib mating
sire = np.array([-1, -1, 0, 0, 2, 2, 4, 4, 6]); dam = np.array([-1, -1, 1, 1, 3, 3, 5, 5, 7])
# sexes: 0 M,1 F,2 M,3 F,4 M,5 F,6 M,7 F
F, _ = meuwissen_luo(sire, dam)
print("full-sib series F:", F[[4, 6, 8]])
