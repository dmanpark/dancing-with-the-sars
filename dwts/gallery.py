from __future__ import annotations

import csv
import json

import numpy as np
from pyproj import Transformer

from . import config as C
from .claims import LC_NAMES
from .grid import load_grid, read

EV = C.EVENT
LEAD = f"{EV}_{C.LEAD[0]}-{C.LEAD[1]}"
S1 = f"{EV}_{C.S1_DATES[0]}-{C.S1_DATES[1]}"


def build(event: str = EV) -> dict:
    g = load_grid(event)
    rng = np.random.default_rng(C.SEED)
    cls = read(C.raster(f"{LEAD}_flood_twosided.tif"))
    lc = read(C.raster(f"{event}_landcover.tif"))
    ref = read(C.raster(f"{event}_ref_optical.tif"))
    nv = read(C.raster(f"{LEAD}_valid.tif")) == 1
    sv = read(C.raster(f"{S1}_valid.tif")) == 1
    picks = []
    for code in (10, 20, 30, 40, 90):
        rr, cc = np.nonzero((cls == C.FLOODED_VEG) & (lc == code))
        if rr.size == 0:
            continue
        k = rng.choice(rr.size, size=min(20, rr.size), replace=False)
        picks += [("flooded_veg_flag", LC_NAMES[code], int(rr[i]), int(cc[i])) for i in k]
    m = nv & sv
    fp = np.nonzero(m & (ref == C.DRY) & (cls == C.OPEN_WATER))
    fn = np.nonzero(m & (ref == C.OPEN_WATER) & (cls != C.OPEN_WATER))
    for name, (rr, cc) in (("nisar_only_water", fp), ("referee_only_water", fn)):
        k = rng.choice(rr.size, size=min(5, rr.size), replace=False)
        picks += [(name, LC_NAMES.get(int(lc[rr[i], cc[i]]), str(int(lc[rr[i], cc[i]]))), int(rr[i]), int(cc[i])) for i in k]
    del cls
    series = {}
    for d in C.SERIES:
        series[d] = {p: read(C.raster(f"{event}_{d}_{p}_db.tif")) for p in ("hh", "hv")}
        rows = [r for _, _, r, _ in picks]
        cols = [c for _, _, _, c in picks]
        series[d] = {p: a[rows, cols] for p, a in series[d].items()}
    tr = Transformer.from_crs(g.crs, "EPSG:4326", always_xy=True)
    out = C.OUT / "gallery.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "landcover", "lon", "lat", "row", "col", *[f"hh_{d}" for d in C.SERIES], *[f"hv_{d}" for d in C.SERIES]])
        for i, (kind, lcn, r, c) in enumerate(picks):
            lon, lat = tr.transform(g.x0 + (c + 0.5) * g.res, g.y0 - (r + 0.5) * g.res)
            w.writerow([kind, lcn, round(lon, 5), round(lat, 5), r, c,
                        *[round(float(series[d]["hh"][i]), 2) for d in C.SERIES],
                        *[round(float(series[d]["hv"][i]), 2) for d in C.SERIES]])
    # why the referee-only pixels were missed: already dark before the flood?
    th = json.loads(C.raster(f"{LEAD}_thresholds.json").read_text())
    part = read(C.raster(f"{event}_{C.LEAD[1]}_part.tif"))
    t = np.full(part.shape, np.nan, np.float32)
    for name, code in (("upper", 1), ("lower", 2)):
        if th["hh"][name]["db"] is not None:
            t[part == code] = th["hh"][name]["db"]
    pre = read(C.raster(f"{event}_{C.LEAD[0]}_hh_db.tif"))
    post = read(C.raster(f"{event}_{C.LEAD[1]}_hh_db.tif"))
    rr, cc = fn
    already = int(np.sum(pre[rr, cc] < t[rr, cc]))
    post_dark = int(np.sum(post[rr, cc] < t[rr, cc]))
    lr = read(C.raster(f"{LEAD}_lr_hh.tif"))
    small_drop = int(np.sum(lr[rr, cc] > C.LR_OPEN_DB))
    del pre, post, lr, part, t
    # the same question for Sentinel-1's misses: already below its VV dark-water threshold on 17 Sep?
    s1cls = read(C.raster(f"{S1}_flood_s1twosided.tif"))
    s1th = json.loads(C.raster(f"{S1}_thresholds.json").read_text())["vv"]["frame"]["db"]
    vv17 = read(C.raster(f"{event}_{C.S1_DATES[0]}_vv_db.tif"))
    s1miss = m & (ref == C.OPEN_WATER) & (s1cls != C.OPEN_WATER)
    s1_info = {"s1_referee_only_px": int(s1miss.sum()),
               "s1_referee_only_dark_on_17sep": int((s1miss & (vv17 < s1th)).sum()) if s1th is not None else None}
    del s1cls, vv17, s1miss
    lead = read(C.raster(f"{LEAD}_flood_twosided.tif"))
    c29 = read(C.raster(f"{event}_{C.S1_DATES[1]}_ref_c.tif"))
    vf = lead == C.FLOODED_VEG
    seen = vf & (c29 != C.CLASS_NODATA)          # flags where Sentinel-1's DSWx-S1 has a known state
    info_veg = {"veg_flags": int(vf.sum()), "veg_flags_s1_known": int(seen.sum()),
                "veg_flags_on_s1_water": int((vf & (c29 == C.OPEN_WATER)).sum()), **s1_info}
    del lead, c29, vf, seen
    # are the hidden-steps pixels near buildings more often than claim 2's pixel set as a whole?
    from scipy import ndimage
    hidden = read(C.raster(f"{event}_hidden.tif"))
    built = np.nan_to_num(read(C.raster(f"{event}_builtup.tif")))
    near = ndimage.uniform_filter(built, size=7) >= 0.05      # >= 5% built-up within about 140 m
    in_set, flag = hidden != C.CLASS_NODATA, hidden == 1
    info_veg.update({"hidden_px": int(flag.sum()), "hidden_near_builtup_px": int((flag & near).sum()),
                     "claim2_set_px": int(in_set.sum()), "claim2_set_near_builtup_px": int((in_set & near).sum()),
                     "near_builtup_rule": "mean GHSL built-up share >= 0.05 in the 7 x 7 pixel (280 m) window around the pixel"})
    del hidden, built, near
    info = {**info_veg, "gallery_csv": str(out), "rows": len(picks), "referee_only_px": int(rr.size),
            "referee_only_dark_on_16sep": already, "referee_only_dark_on_28sep": post_dark,
            "referee_only_hh_drop_smaller_than_3db": small_drop,
            "nisar_only_px": int(fp[0].size)}
    (C.OUT / "gallery_summary.json").write_text(json.dumps(info, indent=1))
    return info


if __name__ == "__main__":
    print(json.dumps(build(), indent=1))
