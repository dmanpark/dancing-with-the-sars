from __future__ import annotations

import numpy as np

from . import config as C


def stable_ground(valid: np.ndarray, slope: np.ndarray, jrc: np.ndarray, hand: np.ndarray,
                  builtup: np.ndarray, water_any: np.ndarray) -> np.ndarray:
    high = hand > C.STABLE_HAND_HIGH_M
    town = (builtup >= C.STABLE_BUILTUP_MIN) & (hand > C.STABLE_HAND_TOWN_M)
    return (valid == 1) & (slope <= C.SLOPE_MAX_DEG) & (jrc == 0) & ~water_any & (high | town)


def tile_medians(lr: np.ndarray, stable: np.ndarray) -> list[float]:
    n = C.CALIB_TILE_PX
    H, W = lr.shape
    meds = []
    for r in range(0, H, n):
        for c in range(0, W, n):
            s = stable[r:r + n, c:c + n]
            if s.sum() < C.CALIB_MIN_STABLE_PER_TILE:
                continue
            v = lr[r:r + n, c:c + n][s]
            v = v[np.isfinite(v)]
            if v.size >= C.CALIB_MIN_STABLE_PER_TILE:
                meds.append(float(np.median(v)))
    return meds


def calibrate_channel(lr: np.ndarray, stable: np.ndarray, part: np.ndarray | None) -> dict:
    """Decide the branch for one channel and return the offset per part (to subtract)."""
    s = stable & np.isfinite(lr)
    n = int(s.sum())
    med = float(np.median(lr[s])) if n else 0.0
    meds = tile_medians(lr, s)
    spread = float(np.percentile(meds, 90) - np.percentile(meds, 10)) if len(meds) >= 2 else 0.0
    rec = {"median_db": round(med, 4), "n_stable": n, "n_tiles": len(meds), "tile_spread_db": round(spread, 4)}
    if spread > C.CALIB_SPREAD_DB:
        rec["branch"] = "per_part"
        offs = {}
        if part is None:
            offs["frame"] = {"offset_db": round(med, 4), "n_stable": n}
        else:
            for name, code in (("upper", 1), ("lower", 2)):
                sp = s & (part == code)
                k = int(sp.sum())
                if k:
                    offs[name] = {"offset_db": round(float(np.median(lr[sp])), 4), "n_stable": k}
                else:
                    offs[name] = {"offset_db": round(med, 4), "n_stable": 0, "note": "no stable ground in this part; frame median used"}
        rec["offsets"] = offs
    elif abs(med) > C.CALIB_ABS_DB:
        rec["branch"] = "scene"
        rec["offsets"] = {"frame": {"offset_db": round(med, 4), "n_stable": n}}
    else:
        rec["branch"] = "none"
        rec["offsets"] = {"frame": {"offset_db": 0.0, "n_stable": n}}
    return rec


def offset_map(rec: dict, part: np.ndarray | None, shape) -> np.ndarray:
    """Per-pixel offset to subtract, from a calibrate_channel record."""
    out = np.zeros(shape, np.float32)
    offs = rec["offsets"]
    if "frame" in offs:
        out[:] = offs["frame"]["offset_db"]
    else:
        out[part == 1] = offs["upper"]["offset_db"]
        out[part == 2] = offs["lower"]["offset_db"]
    return out
