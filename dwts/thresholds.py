from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from . import config as C


def ashman_d(mu1: float, mu2: float, s1: float, s2: float) -> float:
    return float(np.sqrt(2.0) * abs(mu1 - mu2) / np.sqrt(s1 ** 2 + s2 ** 2))


def kittler_illingworth(values: np.ndarray, lo: float, hi: float, bin_db: float = C.KI_BIN_DB) -> float | None:
    """Minimum-error threshold on a histogram with `bin_db` bins, searched in [lo, hi]."""
    v = values[np.isfinite(values)]
    if v.size < 10:
        return None
    edges = np.arange(np.floor(v.min() / bin_db) * bin_db, v.max() + 2 * bin_db, bin_db)
    h, edges = np.histogram(v, bins=edges)
    c = 0.5 * (edges[:-1] + edges[1:])
    p = h / h.sum()
    P = np.cumsum(p)
    M = np.cumsum(p * c)
    S = np.cumsum(p * c * c)
    Pt, Mt, St = P[-1], M[-1], S[-1]
    best, best_t = np.inf, None
    for i in range(len(c) - 1):
        t = edges[i + 1]
        if t < lo or t > hi:
            continue
        p1, p2 = P[i], Pt - P[i]
        if p1 <= 1e-9 or p2 <= 1e-9:
            continue
        m1, m2 = M[i] / p1, (Mt - M[i]) / p2
        v1 = S[i] / p1 - m1 * m1
        v2 = (St - S[i]) / p2 - m2 * m2
        if v1 <= 1e-9 or v2 <= 1e-9:
            continue
        j = 1 + 2 * (p1 * np.log(np.sqrt(v1)) + p2 * np.log(np.sqrt(v2))) - 2 * (p1 * np.log(p1) + p2 * np.log(p2))
        if j < best:
            best, best_t = j, float(t)
    return best_t


def fit_tile(values: np.ndarray, seed: int = C.SEED) -> dict:
    """GMM + Ashman D + KI for one tile's valid dB values."""
    from sklearn.mixture import GaussianMixture
    v = values[np.isfinite(values)].astype(np.float64)
    rng = np.random.default_rng(seed)
    sample = v if v.size <= C.GMM_MAX_SAMPLES else rng.choice(v, C.GMM_MAX_SAMPLES, replace=False)
    gm = GaussianMixture(n_components=2, random_state=seed).fit(sample.reshape(-1, 1))
    mu = gm.means_.ravel()
    sd = np.sqrt(gm.covariances_.ravel())
    w = gm.weights_.ravel()
    o = np.argsort(mu)
    mu, sd, w = mu[o], sd[o], w[o]
    d = ashman_d(mu[0], mu[1], sd[0], sd[1])
    passes = bool(d > C.ASHMAN_D_MIN and w.min() >= C.GMM_MIN_WEIGHT)
    t = kittler_illingworth(v, mu[0], mu[1]) if passes else None
    if t is None:
        passes = False
    return {"mu": [round(float(x), 3) for x in mu], "sd": [round(float(x), 3) for x in sd],
            "w": [round(float(x), 4) for x in w], "ashman_d": round(d, 3), "passes": passes,
            "threshold_db": None if t is None else round(t, 2)}


def _fit(args):
    key, vals = args
    return key, fit_tile(vals)


def tile_thresholds(db: np.ndarray, valid: np.ndarray, part: np.ndarray | None, workers: int = 4) -> dict:
    """Per part: tiles tested, tiles passing, each tile's threshold, the scene threshold."""
    H, W = db.shape
    n = C.TILE_PX
    jobs = []
    tile_part = {}
    for r in range(0, H - n + 1, n):
        for c in range(0, W - n + 1, n):
            v = valid[r:r + n, c:c + n] == 1
            if v.sum() < C.TILE_MIN_VALID * n * n:
                continue
            vals = db[r:r + n, c:c + n][v]
            vals = vals[np.isfinite(vals)]
            if vals.size < C.TILE_MIN_VALID * n * n:
                continue
            if part is None:
                pid = "frame"
            else:
                pv = part[r:r + n, c:c + n][v]
                counts = {k: int((pv == code).sum()) for k, code in (("upper", 1), ("lower", 2))}
                pid = max(counts, key=counts.get)
            key = f"r{r // n}_c{c // n}"
            tile_part[key] = pid
            jobs.append((key, vals))
    env = {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}
    for k in env:
        os.environ[k] = "1"
    try:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            fits = dict(ex.map(_fit, jobs, chunksize=4))
    finally:
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    out = {}
    for pid in sorted(set(tile_part.values()) | ({"frame"} if part is None else {"upper", "lower"})):
        keys = [k for k, p in tile_part.items() if p == pid]
        passing = [fits[k]["threshold_db"] for k in keys if fits[k]["passes"]]
        scene = float(np.median(passing)) if len(passing) >= C.MIN_BIMODAL_TILES else None
        out[pid] = {"tiles_tested": len(keys), "tiles_passing": len(passing),
                    "db": None if scene is None else round(scene, 2),
                    "fallback": "log-ratio cut alone" if scene is None else None,
                    "tiles": {k: fits[k] for k in keys}}
    return out
