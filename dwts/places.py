from __future__ import annotations

import json

import numpy as np
from pyproj import Transformer

from . import config as C
from .grid import load_grid, read
from .listen import LISTEN, read_cell

REGION = (84.0, 84.6, 26.6, 27.4)


def _cells(a: np.ndarray, k: int) -> np.ndarray:
    H, W = (a.shape[0] // k) * k, (a.shape[1] // k) * k
    return a[:H, :W].reshape(H // k, k, W // k, k).mean(axis=(1, 3))


def pick(event: str = C.EVENT) -> dict:
    g = load_grid(event)
    k = C.LISTEN_CELL_PX
    lead = f"{event}_{C.LEAD[0]}-{C.LEAD[1]}"
    cls = read(C.raster(f"{lead}_flood_twosided.tif"))
    lc = read(C.raster(f"{event}_landcover.tif"))
    hidden = read(C.raster(f"{event}_hidden.tif"))
    built = read(C.raster(f"{event}_builtup.tif"))
    ow = _cells((cls == C.OPEN_WATER).astype(np.float32), k)
    crop = _cells((lc == C.CROP_CLASS).astype(np.float32), k)
    hid = _cells((hidden == 1).astype(np.float32), k)
    anyflag = _cells(((cls == C.OPEN_WATER) | (cls == C.FLOODED_VEG)).astype(np.float32), k)
    valid = _cells((cls != C.CLASS_NODATA).astype(np.float32), k)
    bu = _cells(np.nan_to_num(built), k)
    del cls, lc, hidden, built
    Hc, Wc = ow.shape
    xs = g.x0 + (np.arange(Wc) + 0.5) * g.res * k
    ys = g.y0 - (np.arange(Hc) + 0.5) * g.res * k
    X, Y = np.meshgrid(xs, ys)
    lon, lat = Transformer.from_crs(g.crs, "EPSG:4326", always_xy=True).transform(X, Y)
    lon, lat = np.asarray(lon), np.asarray(lat)
    inreg = (lon >= REGION[0]) & (lon <= REGION[1]) & (lat >= REGION[2]) & (lat <= REGION[3]) & (valid > 0.9)
    idx = json.loads((LISTEN / "index.json").read_text())
    ch, nd = idx["chunk"], len(idx["dates"])
    full = np.zeros((idx["height"], idx["width"]), bool)
    for name in idx["chunks"]:
        cc, cr = (int(v) for v in name.split("_"))
        b = np.frombuffer((LISTEN / f"{name}.bin").read_bytes(), np.uint8).reshape(nd, 2, ch, ch)
        sub = (b != 255).all(axis=(0, 1))
        h = min(ch, idx["height"] - cr * ch)
        w = min(ch, idx["width"] - cc * ch)
        full[cr * ch:cr * ch + h, cc * ch:cc * ch + w] = sub[:h, :w]
    ok = inreg & full[:Hc, :Wc]

    def best(score, mask):
        s = np.where(ok & mask, score, -np.inf)
        r, c = np.unravel_index(int(np.argmax(s)), s.shape)
        return {"lon": round(float(lon[r, c]), 5), "lat": round(float(lat[r, c]), 5), "col": int(c), "row": int(r),
                "score": round(float(s[r, c]), 3)}

    places = {
        "open_water_field": {"name": "A flooded field", **best(ow, crop > 0.6), "why": "cropland cell with the largest share of NISAR new open water on 28 Sep"},
        "flooded_grove": {"name": "A flooded grove", **best(hid, hid > 0), "why": "the cell with the largest share of hidden-steps pixels"},
        "dry_town": {"name": "A dry town", **best(bu, anyflag == 0), "why": "the most built-up cell with no flood flag"},
    }
    for p in places.values():
        p["hh_hv_db"] = np.round(read_cell(LISTEN, p["col"], p["row"]), 2).tolist()
    del idx
    out = C.OUT / "places.json"
    out.write_text(json.dumps(places, indent=1))
    return places


if __name__ == "__main__":
    print(json.dumps(pick(), indent=1))
