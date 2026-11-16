from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import time

import numpy as np

from . import config as C
from .grid import load_grid, read, write_cog
from .refs import hls_tiles
from .stats import Bootstrap, block_index, ci, score_methods

R = lambda name: read(C.raster(name))  # noqa: E731
EV = C.EVENT
LEAD = f"{EV}_{C.LEAD[0]}-{C.LEAD[1]}"
CTRL = f"{EV}_{C.CONTROL[0]}-{C.CONTROL[1]}"
S1 = f"{EV}_{C.S1_DATES[0]}-{C.S1_DATES[1]}"
CHK = f"{EV}_{C.CHECK_0904[0]}-{C.CHECK_0904[1]}"
LC_NAMES = {10: "tree cover", 20: "shrubland", 30: "grassland", 40: "cropland", 50: "built-up",
            60: "bare", 70: "snow and ice", 80: "permanent water", 90: "herbaceous wetland",
            95: "mangroves", 100: "moss and lichen"}


def _r4(x):
    return None if x is None or not np.isfinite(x) else round(float(x), 4)


def _time(s: str) -> dt.datetime:
    return dt.datetime.strptime(s, "%Y%m%dT%H%M%S").replace(tzinfo=dt.timezone.utc)


def _iso(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def pass_time(date: str, sensor: str) -> dt.datetime:
    """Earliest tile acquisition time of an optical pass (from the file names)."""
    ts = [re.search(r"_(\d{8}T\d{6})Z_", f.split("/")[-1]).group(1) for f in hls_tiles(date, sensor)]
    return _time(min(ts))


def diff_block(point: dict, draws: dict, a: str, b: str) -> dict:
    d = draws[a] - draws[b]
    pd_ = point[a]["f1"] - point[b]["f1"]
    lo, hi = ci(d)
    return {"diff": _r4(pd_), "ci95": [_r4(lo), _r4(hi)]}


def claim1(lead2s, leadlr, s12s, s1lr, ref, lc, blocks, nisar_valid, s1_valid, c17, c29) -> dict:
    m = nisar_valid & s1_valid & ((ref == C.DRY) | (ref == C.OPEN_WATER))
    truth = ref[m] == C.OPEN_WATER
    dswx_new = (c29 == C.OPEN_WATER) & ((c17 == C.DRY) | (c17 == C.FLOODED_VEG))
    preds = {"nisar_twosided": lead2s[m] == C.OPEN_WATER, "s1_twosided": s12s[m] == C.OPEN_WATER,
             "nisar_lr": leadlr[m] == C.OPEN_WATER, "s1_lr": s1lr[m] == C.OPEN_WATER,
             "dswx_s1": dswx_new[m]}
    b = blocks[m]
    point, draws, boot = score_methods(truth, preds, b)
    hd = diff_block(point, draws, "nisar_twosided", "s1_twosided")
    by_lc = {}
    lcm = lc[m]
    for code in np.unique(lcm):
        k = lcm == code
        if truth[k].sum() == 0:
            continue
        row = {"name": LC_NAMES.get(int(code), str(int(code))), "n_pixels": int(k.sum()), "n_new_water": int(truth[k].sum())}
        for name, p in preds.items():
            tp = int((p[k] & truth[k]).sum()); fp = int((p[k] & ~truth[k]).sum()); fn = int((~p[k] & truth[k]).sum())
            row[name] = {"f1": _r4(2 * tp / (2 * tp + fp + fn)) if (2 * tp + fp + fn) else None, "tp": tp, "fp": fp, "fn": fn}
        by_lc[str(int(code))] = row
    return {"metric": "F1", "margin": C.CLAIM1_MARGIN,
            "nisar_twosided": point["nisar_twosided"], "s1_twosided": point["s1_twosided"],
            "others": {"nisar_lr": point["nisar_lr"], "s1_lr": point["s1_lr"], "dswx_s1": point["dswx_s1"],
                       "dswx_ni": None},
            "dswx_ni_note": "DSWx-NI dropped before the event (build-spec change log, 4 Nov): it peaked at 13.3 GB, over the 8 GB per-process limit, and failed for want of a GLAD land-cover file its schema calls optional.",
            "diff": hd["diff"], "ci95": hd["ci95"], "noninferior": bool(hd["ci95"][0] is not None and hd["ci95"][0] >= C.CLAIM1_MARGIN),
            "n_pixels": int(m.sum()), "n_new_water": int(truth.sum()), "n_stable_dry": int((~truth).sum()),
            "n_blocks": int(len(boot.ids)), "by_landcover": by_lc}


def claim1a(lead2s, leadlr, ref1a, blocks, nisar_valid) -> dict:
    m = nisar_valid & ((ref1a == C.DRY) | (ref1a == C.OPEN_WATER))
    truth = ref1a[m] == C.OPEN_WATER
    preds = {"nisar_twosided": lead2s[m] == C.OPEN_WATER, "nisar_lr": leadlr[m] == C.OPEN_WATER}
    point, draws, boot = score_methods(truth, preds, blocks[m])
    d = diff_block(point, draws, "nisar_twosided", "nisar_lr")
    return {"metric": "F1", "referee": "Sentinel-2B DSWx-HLS 29 Sep alone (+16 h), western frame",
            "nisar_twosided": point["nisar_twosided"], "nisar_lr": point["nisar_lr"],
            "diff": d["diff"], "ci95": d["ci95"], "passes": bool(d["ci95"][0] is not None and d["ci95"][0] >= 0),
            "n_pixels": int(m.sum()), "n_new_water": int(truth.sum()), "n_blocks": int(len(boot.ids))}


def veg_flags(lr_hh, lr_hv):
    return (lr_hh >= C.LR_VEG_DB) & ((lr_hh - lr_hv) >= C.LR_VEG_DIFF_DB)


def claim2_row(pix, flag_lead, flag_ctrl, blocks) -> dict:
    b = blocks[pix]
    boot = Bootstrap(b)
    fl = boot.per_block(b, flag_lead[pix])
    fc = boot.per_block(b, flag_ctrl[pix])
    ex = (fl - fc) * C.PIXEL_KM2
    draws = boot.draws(ex)
    lo, hi = ci(draws)
    pt = float(ex.sum())
    return {"excess_km2": round(pt, 2), "ci95": [round(lo, 2), round(hi, 2)],
            "flood_km2": round(float(fl.sum()) * C.PIXEL_KM2, 2), "control_km2": round(float(fc.sum()) * C.PIXEL_KM2, 2),
            "n_pixels": int(pix.sum()), "area_km2": round(float(pix.sum()) * C.PIXEL_KM2, 1),
            "n_blocks": int(len(boot.ids)), "passes": bool(lo > 0)}


def run_claims(event: str = EV) -> dict:
    t0 = time.time()
    g = load_grid(event)
    blocks = block_index((g.height, g.width))
    lc = R(f"{event}_landcover.tif")
    nisar_valid = R(f"{LEAD}_valid.tif") == 1
    s1_valid = R(f"{S1}_valid.tif") == 1
    lead2s, leadlr = R(f"{LEAD}_flood_twosided.tif"), R(f"{LEAD}_flood_lr.tif")
    s12s, s1lr = R(f"{S1}_flood_s1twosided.tif"), R(f"{S1}_flood_s1lr.tif")
    c17, c29 = R(f"{event}_{C.S1_DATES[0]}_ref_c.tif"), R(f"{event}_{C.S1_DATES[1]}_ref_c.tif")
    ref, ref1a = R(f"{event}_ref_optical.tif"), R(f"{event}_ref_optical_1a.tif")

    res = {"generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                                    cwd=C.REPO).stdout.strip()
                     + ("-dirty" if subprocess.run(["git", "status", "--porcelain", "dwts"], capture_output=True,
                                                   text=True, cwd=C.REPO).stdout.strip() else ""),
           "event": event}
    s1info = {}
    for line in (C.LOGS / "run.jsonl").read_text().splitlines():
        rec = json.loads(line)
        if rec.get("stage") == "s1":
            s1info[rec["date"]] = rec.get("first_burst_utc")
    passes = dict(C.PASSES)
    for key, d in (("s1_pre", C.S1_DATES[0]), ("s1_post", C.S1_DATES[1])):
        if s1info.get(d):
            passes[key] = _time(s1info[d]).strftime("%Y-%m-%dT%H:%M:%SZ")
    t_n = _iso(passes["nisar_post"])
    l9 = pass_time(*C.OPTICAL["post_l9_0927"])
    s2c = pass_time(*C.OPTICAL["post_s2c_1001"])
    s2b = pass_time(*C.OPTICAL["post_s2b_0929"])
    passes.update({"optical_post_before": l9.strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "optical_post_after": s2c.strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "optical_1a": s2b.strftime("%Y-%m-%dT%H:%M:%SZ")})
    res["passes"] = passes
    h = lambda t: round((t - t_n).total_seconds() / 3600, 1)  # noqa: E731
    res["time_offsets_h"] = {"s1": h(_iso(passes["s1_post"])), "optical_post_before": h(l9),
                             "optical_post_after": h(s2c), "optical_1a": h(s2b)}

    calib, thresholds = {}, {}
    for name, tag, co, cr in (("lead", LEAD, "hh", "hv"), ("control", CTRL, "hh", "hv"),
                              ("s1", S1, "vv", "vh"), ("check_0904", CHK, "hh", "hv")):
        c = json.loads(C.raster(f"{tag}_calib.json").read_text())
        calib[name] = {f"{co}_db": c[co]["median_db"], f"{cr}_db": c[cr]["median_db"],
                       "branch": {co: c[co]["branch"], cr: c[cr]["branch"]}, "n_stable": c["n_stable"],
                       "offsets_subtracted": {co: c[co]["offsets"], cr: c[cr]["offsets"]},
                       "tile_spread_db": {co: c[co]["tile_spread_db"], cr: c[cr]["tile_spread_db"]}}
        t = json.loads(C.raster(f"{tag}_thresholds.json").read_text())
        for ch in (co, cr):
            thresholds[f"{name}_post_{ch}"] = {p: {k: v for k, v in d.items() if k != "tiles"} for p, d in t[ch].items()}
    res["calibration"] = calib
    res["thresholds"] = thresholds

    res["claim1"] = claim1(lead2s, leadlr, s12s, s1lr, ref, lc, blocks, nisar_valid, s1_valid, c17, c29)
    res["claim1a"] = claim1a(lead2s, leadlr, ref1a, blocks, nisar_valid)
    chk_valid = R(f"{CHK}_valid.tif") == 1
    chk2s, chklr = R(f"{CHK}_flood_twosided.tif"), R(f"{CHK}_flood_lr.tif")
    chk = claim1(chk2s, chklr, s12s, s1lr, ref, lc, blocks, chk_valid, s1_valid, c17, c29)
    res["claim1_check_0904"] = {"note": "Claim 1 rerun on 4 Sep -> 28 Sep (both dual-pol), the check the calibration rule asks for when the offset varies",
                                "nisar_twosided": chk["nisar_twosided"], "s1_twosided": chk["s1_twosided"],
                                "diff": chk["diff"], "ci95": chk["ci95"], "noninferior": chk["noninferior"],
                                "n_pixels": chk["n_pixels"], "n_new_water": chk["n_new_water"]}
    del chk2s, chklr, chk_valid, s12s, s1lr

    # ---------------- claim 2
    ctrl_valid = R(f"{CTRL}_valid.tif") == 1
    hand = R(f"{event}_hand.tif")
    base = nisar_valid & ctrl_valid & (hand < C.CLAIM2_HAND_MAX_M) & (c29 == C.DRY)
    veg_pix = base & np.isin(lc, C.VEG_CLASSES)
    crop_pix = base & (lc == C.CROP_CLASS)
    flag_lead = lead2s == C.FLOODED_VEG
    ctrl2s = R(f"{CTRL}_flood_twosided.tif")
    flag_ctrl = ctrl2s == C.FLOODED_VEG
    c2 = {"vegetation": claim2_row(veg_pix, flag_lead, flag_ctrl, blocks),
          "cropland": claim2_row(crop_pix, flag_lead, flag_ctrl, blocks)}
    c2["vegetation"]["classes"] = list(C.VEG_CLASSES)
    c2["cropland"]["classes"] = [C.CROP_CLASS]
    hidden = np.full(lead2s.shape, C.CLASS_NODATA, np.uint8)
    hidden[veg_pix] = 0
    hidden[veg_pix & flag_lead] = 1
    write_cog(C.raster(f"{event}_hidden.tif"), hidden, g)
    del hidden, ctrl2s

    # sensitivity: every offset shifted up, then down, by half its own tile spread
    sens = {}
    lr = {k: R(f"{tag}_lr_{ch}.tif") for k, tag, ch in (("lh", LEAD, "hh"), ("lv", LEAD, "hv"), ("ch", CTRL, "hh"), ("cv", CTRL, "hv"))}
    sp = {k: calib[n]["tile_spread_db"][ch] / 2 for k, n, ch in (("lh", "lead", "hh"), ("lv", "lead", "hv"), ("ch", "control", "hh"), ("cv", "control", "hv"))}
    for sign, label in ((+1, "offsets_up"), (-1, "offsets_down")):
        fl = nisar_valid & veg_flags(lr["lh"] - sign * sp["lh"], lr["lv"] - sign * sp["lv"])
        fc = ctrl_valid & veg_flags(lr["ch"] - sign * sp["ch"], lr["cv"] - sign * sp["cv"])
        sens[label] = {"vegetation": claim2_row(veg_pix, fl, fc, blocks), "cropland": claim2_row(crop_pix, fl, fc, blocks)}
    c2["sensitivity"] = {"note": "Offsets shifted by half the tile spread of their own pair and channel (change-log row 4); every offset up together, then every offset down together.",
                         "half_spread_db": {k: round(v, 3) for k, v in sp.items()}, **sens}
    del lr

    # secondary test: dropped by the team (build-spec change log, row of 4 Nov on the claim 2 secondary
    # test, from prelim T11). The 5% shares are recounted here for the record only; no contrast is computed.
    slope = R(f"{event}_slope.tif")
    sec = {}
    for code in (10, 20, 90, 40):
        cls = nisar_valid & (lc == code)
        n = int(cls.sum())
        hi = int((cls & (hand > C.SECONDARY_HAND_HIGH_M) & (slope <= C.SLOPE_MAX_DEG)).sum())
        sec[str(code)] = {"name": LC_NAMES[code], "valid_px": n, "high_gentle_px": hi,
                          "share_of_valid": round(hi / n if n else 0.0, 4), "dropped": True}
    c2["secondary"] = {"dropped": True,
                       "note": "Dropped by the team's change-log decision of 4 Nov (prelim T11 found high-HAND, gentle ground under 5% of every class's pixels). Recounted here on pixels valid for the lead pair, whose definition already excludes slopes over 10 degrees, the shares are higher than T11's (tree cover and shrubland above 5%); flagged to the team, decision unchanged.",
                       "classes": sec}
    res["claim2"] = c2
    del ctrl_valid, hand, slope, lc, lead2s, leadlr, c17, c29, ref, ref1a
    from .gallery import build as build_gallery
    fg = build_gallery(event)
    res["failure_gallery"] = {k: v for k, v in fg.items() if k != "gallery_csv"}
    res["tier3"] = None
    res["cuts"] = ["Tier 3 (claims 3 and 4, north Bihar, Check first, phase test, S-band): cut at 14:28 Sat 14 Nov after the late start",
                   "DSWx-NI: dropped before the event (change log, 4 Nov)"]
    res["seconds"] = round(time.time() - t0, 1)
    out = C.OUT / "results.json"
    out.write_text(json.dumps(res, indent=1))
    app = C.REPO / "app" / "data" / "results.json"
    app.parent.mkdir(parents=True, exist_ok=True)
    app.write_text(json.dumps(res, indent=1))
    return {"results": str(out), "claim1_diff": res["claim1"]["diff"], "claim2_veg": c2["vegetation"]["excess_km2"],
            "seconds": res["seconds"]}
