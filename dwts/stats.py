from __future__ import annotations

import numpy as np

from . import config as C


def block_index(shape, block: int = C.BLOCK_PX) -> np.ndarray:
    H, W = shape
    nbx = -(-W // block)
    r = np.arange(H) // block
    c = np.arange(W) // block
    return (r[:, None] * nbx + c[None, :]).astype(np.int32)


class Bootstrap:
    """Draw weights once over the blocks that hold scoreable pixels; reuse them for every method."""

    def __init__(self, blocks: np.ndarray, n_boot: int = C.N_BOOT, seed: int = C.SEED):
        self.ids = np.unique(blocks)
        self.pos = {int(b): i for i, b in enumerate(self.ids)}
        rng = np.random.default_rng(seed)
        nb = len(self.ids)
        draws = rng.integers(0, nb, size=(n_boot, nb))
        self.w = np.zeros((n_boot, nb), np.float64)
        for i in range(n_boot):
            self.w[i] = np.bincount(draws[i], minlength=nb)

    def per_block(self, blocks: np.ndarray, values: np.ndarray) -> np.ndarray:
        """Sum of `values` per block, ordered as self.ids."""
        idx = np.searchsorted(self.ids, blocks)
        return np.bincount(idx, weights=values.astype(np.float64), minlength=len(self.ids))

    def draws(self, per_block: np.ndarray) -> np.ndarray:
        return self.w @ per_block


def ci(x: np.ndarray) -> list[float]:
    x = x[np.isfinite(x)]
    if x.size == 0:
        return [float("nan"), float("nan")]
    lo, hi = np.percentile(x, C.CI)
    return [float(lo), float(hi)]


def scores(tp, fp, fn):
    tp, fp, fn = (np.asarray(v, np.float64) for v in (tp, fp, fn))
    with np.errstate(invalid="ignore", divide="ignore"):
        prec = tp / (tp + fp)
        rec = tp / (tp + fn)
        f1 = 2 * tp / (2 * tp + fp + fn)
        iou = tp / (tp + fp + fn)
    return {"f1": f1, "precision": prec, "recall": rec, "iou": iou}


def score_methods(truth: np.ndarray, preds: dict, blocks: np.ndarray, boot: Bootstrap | None = None) -> tuple[dict, dict, Bootstrap]:
    """Point scores and bootstrap draws of F1 for each method on the same pixels (1-D arrays)."""
    boot = boot or Bootstrap(blocks)
    point, f1_draws = {}, {}
    for name, p in preds.items():
        tp = boot.per_block(blocks, p & truth)
        fp = boot.per_block(blocks, p & ~truth)
        fn = boot.per_block(blocks, ~p & truth)
        s = scores(tp.sum(), fp.sum(), fn.sum())
        d = scores(boot.draws(tp), boot.draws(fp), boot.draws(fn))
        point[name] = {k: round(float(v), 4) for k, v in s.items()}
        point[name]["ci95"] = [round(v, 4) for v in ci(d["f1"])]
        point[name]["tp"], point[name]["fp"], point[name]["fn"] = int(tp.sum()), int(fp.sum()), int(fn.sum())
        f1_draws[name] = d["f1"]
    return point, f1_draws, boot
