from __future__ import annotations

import json
import time

import numpy as np
from scipy import ndimage

from . import config as C
from .calib import calibrate_channel, offset_map, stable_ground
from .grid import load_grid, read, write_cog
from .thresholds import tile_thresholds

TWO_PART_DATES = {"20260904", "20260928"}   # 40 MHz acquisitions in two observations (prelim T2, follow-up B)


# ------------------------------------------------------------------ pure functions (tested)
def nanmedian3(a: np.ndarray, valid: np.ndarray, strip: int = 512) -> np.ndarray:
    """3 x 3 median over valid neighbours only; NaN where the centre is not valid."""
    x = np.where(valid, a, np.nan).astype(np.float32)
    H, W = x.shape
    p = np.pad(x, 1, constant_values=np.nan)
    out = np.full((H, W), np.nan, np.float32)
    for r0 in range(0, H, strip):
        r1 = min(r0 + strip, H)
        stack = np.stack([p[r0 + dr:r1 + dr, dc:dc + W] for dr in range(3) for dc in range(3)])
        with np.errstate(all="ignore"):
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                out[r0:r1] = np.nanmedian(stack, axis=0)
    out[~valid] = np.nan
    return out


def open_water(lr_co, post_co, t_co):
    """t_co: per-pixel threshold, NaN where the dark-water condition is dropped."""
    dark = np.where(np.isfinite(t_co), post_co < t_co, True)
    return (lr_co <= C.LR_OPEN_DB) & dark


def twosided_open(lr_co, post_co, post_cross, t_co, t_cross):
    dark_x = np.where(np.isfinite(t_cross), post_cross < t_cross, True)
    return open_water(lr_co, post_co, t_co) & dark_x


def flooded_veg(lr_hh, lr_hv):
    return (lr_hh >= C.LR_VEG_DB) & ((lr_hh - lr_hv) >= C.LR_VEG_DIFF_DB)


def classify(pair_valid, perm_ok, ow, veg=None):
    cls = np.full(pair_valid.shape, C.CLASS_NODATA, np.uint8)
    cls[perm_ok] = C.PERMANENT
    cls[pair_valid] = C.DRY
    if veg is not None:
        cls[pair_valid & veg] = C.FLOODED_VEG
    cls[pair_valid & ow] = C.OPEN_WATER
    return cls


def parts_for(date: str, swath: np.ndarray) -> np.ndarray | None:
    """1 = upper single-subswath part, 2 = lower part, 0 = outside. None for one-observation dates."""
    if date not in TWO_PART_DATES:
        return None
    s1 = swath == 1
    lab, n = ndimage.label(s1)
    if n == 0:
        return None
    sizes = ndimage.sum_labels(s1, lab, index=np.arange(1, n + 1))
    upper = ndimage.binary_fill_holes(lab == (int(np.argmax(sizes)) + 1))
    part = np.zeros(swath.shape, np.uint8)
    inside = swath != C.CLASS_NODATA
    part[inside] = 2
    part[upper & inside] = 1
    return part


def threshold_map(th: dict, part: np.ndarray | None, shape) -> np.ndarray:
    t = np.full(shape, np.nan, np.float32)
    if part is None:
        if th["frame"]["db"] is not None:
            t[:] = th["frame"]["db"]
    else:
        for name, code in (("upper", 1), ("lower", 2)):
            if name in th and th[name]["db"] is not None:
                t[part == code] = th[name]["db"]
    return t


# ------------------------------------------------------------------ I/O
def _common(event: str):
    slope = read(C.raster(f"{event}_slope.tif"))
    perm = read(C.raster(f"{event}_permanent.tif")) == 1
    return slope, perm


def _water_any(event: str) -> np.ndarray:
    w = None
    for key, (date, sensor) in C.OPTICAL.items():
        s = read(C.raster(f"{event}_{date}_hls_{sensor.lower()}.tif"))
        w = (s == 1) if w is None else (w | (s == 1))
    for d in C.S1_DATES:
        s = read(C.raster(f"{event}_{d}_ref_c.tif"))
        w |= (s == 1) | (s == 2)
    return w


def run_pair(pre: str, post: str, sensor: str = "nisar", event: str = C.EVENT, water_any=None) -> dict:
    t0 = time.time()
    g = load_grid(event)
    co, cross = ("hh", "hv") if sensor == "nisar" else ("vv", "vh")
    tag = f"{event}_{pre}-{post}"
    slope, perm = _common(event)
    if sensor == "nisar":
        v_pre = read(C.raster(f"{event}_{pre}_vmask.tif")) == 1
        v_post = read(C.raster(f"{event}_{post}_vmask.tif")) == 1
        part = parts_for(post, read(C.raster(f"{event}_{post}_swath.tif")))
        if part is not None:
            write_cog(C.raster(f"{event}_{post}_part.tif"), part, g)
    pre_co = read(C.raster(f"{event}_{pre}_{co}_db.tif"))
    post_co = read(C.raster(f"{event}_{post}_{co}_db.tif"))
    pre_x = read(C.raster(f"{event}_{pre}_{cross}_db.tif"))
    post_x = read(C.raster(f"{event}_{post}_{cross}_db.tif"))
    if sensor != "nisar":
        v_pre = np.isfinite(pre_co) & np.isfinite(pre_x)
        v_post = np.isfinite(post_co) & np.isfinite(post_x)
        part = None
    dates_ok = v_pre & v_post & (slope <= C.SLOPE_MAX_DEG)
    pair_valid = dates_ok & ~perm
    perm_ok = dates_ok & perm
    vout = pair_valid.astype(np.uint8)
    write_cog(C.raster(f"{tag}_valid.tif"), vout, g)
    del vout, v_pre, v_post

    if water_any is None:
        water_any = _water_any(event)
    hand = read(C.raster(f"{event}_hand.tif"))
    builtup = read(C.raster(f"{event}_builtup.tif"))
    jrc = read(C.raster(f"{event}_jrc.tif"))
    stable = stable_ground(pair_valid.astype(np.uint8), slope, jrc, hand, builtup, water_any)
    del hand, builtup, jrc

    calib = {"pair": f"{pre}-{post}", "sensor": sensor, "n_stable": int(stable.sum())}
    lrs = {}
    for ch, a, b in ((co, pre_co, post_co), (cross, pre_x, post_x)):
        raw = (b - a).astype(np.float32)
        rec = calibrate_channel(raw, stable, part)
        calib[ch] = rec
        raw -= offset_map(rec, part, raw.shape)
        lr = nanmedian3(raw, pair_valid)
        del raw
        write_cog(C.raster(f"{tag}_lr_{ch}.tif"), lr, g)
        lrs[ch] = lr
    del pre_co, pre_x, stable
    (C.raster(f"{tag}_calib.json")).write_text(json.dumps(calib, indent=1))

    th = {"pair": f"{pre}-{post}", "date": post}
    th[f"{co}"] = tile_thresholds(post_co, pair_valid.astype(np.uint8), part)
    th[f"{cross}"] = tile_thresholds(post_x, pair_valid.astype(np.uint8), part)
    (C.raster(f"{tag}_thresholds.json")).write_text(json.dumps(th, indent=1))
    t_co = threshold_map(th[co], part, post_co.shape)
    t_x = threshold_map(th[cross], part, post_co.shape)

    ow_lr = open_water(lrs[co], post_co, t_co)
    ow_2s = twosided_open(lrs[co], post_co, post_x, t_co, t_x)
    if sensor == "nisar":
        veg = flooded_veg(lrs["hh"], lrs["hv"])
        write_cog(C.raster(f"{tag}_flood_lr.tif"), classify(pair_valid, perm_ok, ow_lr), g)
        write_cog(C.raster(f"{tag}_flood_twosided.tif"), classify(pair_valid, perm_ok, ow_2s, veg), g)
        n_veg = int((pair_valid & veg).sum())
    else:
        write_cog(C.raster(f"{tag}_flood_s1lr.tif"), classify(pair_valid, perm_ok, ow_lr), g)
        write_cog(C.raster(f"{tag}_flood_s1twosided.tif"), classify(pair_valid, perm_ok, ow_2s), g)
        n_veg = None
    summary = {k: {p: {kk: vv for kk, vv in v.items() if kk != "tiles"} for p, v in th[k].items()}
               for k in (co, cross)}
    return {"pair": f"{pre}-{post}", "sensor": sensor, "valid_px": int(pair_valid.sum()),
            "calib": {ch: {k: v for k, v in calib[ch].items()} for ch in (co, cross)},
            "n_stable": calib["n_stable"], "thresholds": summary,
            "open_lr_px": int((pair_valid & ow_lr).sum()), "open_2s_px": int((pair_valid & ow_2s).sum()),
            "veg_px": n_veg, "seconds": round(time.time() - t0, 1)}


def run_pairs(event: str = C.EVENT, which=None) -> dict:
    water_any = _water_any(event)
    out = {}
    pairs = which or [("lead", *C.LEAD, "nisar"), ("control", *C.CONTROL, "nisar"),
                      ("s1", *C.S1_DATES, "s1"), ("check_0904", *C.CHECK_0904, "nisar")]
    for name, pre, post, sensor in pairs:
        out[name] = run_pair(pre, post, sensor, event, water_any)
        print(json.dumps({name: out[name]}, default=str), flush=True)
    return out
