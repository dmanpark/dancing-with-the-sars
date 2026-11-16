from __future__ import annotations

import time

import h5py
import numpy as np

from . import config as C
from .grid import Grid, block_mean_power, grid_from_coords, power_to_db, save_grid, write_cog

GROUP = "/science/LSAR/GCOV/grids/frequencyA"
STRIP_ROWS = 1024


def file_info(path) -> dict:
    with h5py.File(path, "r") as h:
        g = h[GROUP]
        x = g["xCoordinates"][()]
        y = g["yCoordinates"][()]
        posting = float(g["xCoordinateSpacing"][()])
        return {"x": x, "y": y, "posting": posting, "epsg": int(g["projection"][()]),
                "n_swaths": int(g["numberOfSubSwaths"][()]), "shape": g["HHHH"].shape}


def factor_for(posting: float) -> int:
    k = C.PIXEL_M / posting
    if abs(k - round(k)) > 1e-6:
        raise ValueError(f"posting {posting} m does not divide {C.PIXEL_M} m")
    return int(round(k))


def make_grid(date: str = C.LEAD[1]) -> Grid:
    """grid_gandak.json from the lead post-event file (28 Sep), averaged 2 x 2 to 40 m."""
    info = file_info(C.nisar_file(date))
    k = factor_for(info["posting"])
    g = grid_from_coords(info["x"], info["y"], info["posting"], info["epsg"], k)
    save_grid(g)
    return g


def read_date(date: str, g: Grid) -> dict:
    """HH and HV dB, the per-date valid mask and the subswath id, all on the 40 m grid."""
    path = C.nisar_file(date)
    info = file_info(path)
    k = factor_for(info["posting"])
    # alignment with the analysis grid
    x0 = float(info["x"][0]) - info["posting"] / 2
    y0 = float(info["y"][0]) + info["posting"] / 2
    if abs(x0 - g.x0) > 1e-6 or abs(y0 - g.y0) > 1e-6:
        raise ValueError(f"{date}: grid origin {x0},{y0} differs from {g.x0},{g.y0}")
    nsw = info["n_swaths"]
    H, W = g.height, g.width
    hh = np.full((H, W), np.nan, np.float32)
    hv = np.full((H, W), np.nan, np.float32)
    valid = np.zeros((H, W), np.uint8)
    inside = np.zeros((H, W), bool)
    swath = np.zeros((H, W), np.uint8)
    step = (STRIP_ROWS // k) * k
    with h5py.File(path, "r") as h:
        grp = h[GROUP]
        dsh, dsv, dsm = grp["HHHH"], grp["HVHV"], grp["mask"]
        nrows = min(dsh.shape[0], H * k)
        ncols = W * k
        for r0 in range(0, nrows, step):
            r1 = min(r0 + step, nrows)
            o0, o1 = r0 // k, r1 // k
            m = dsm[r0:r1, :ncols]
            for ds, out in ((dsh, hh), (dsv, hv)):
                a = ds[r0:r1, :ncols].astype(np.float32)
                a[a <= 0] = np.nan
                mean, _ = block_mean_power(a, k)
                out[o0:o1] = power_to_db(mean)
                del a, mean
            mb = m.reshape(o1 - o0, k, W, k)
            ok = (mb >= 1) & (mb <= nsw)
            valid[o0:o1] = ok.all(axis=(1, 3))
            inside[o0:o1] = (mb != 255).any(axis=(1, 3))
            first = mb[:, 0, :, 0]
            same = (mb == first[:, None, :, None]).all(axis=(1, 3))
            swath[o0:o1] = np.where(same & (first >= 1) & (first <= nsw), first, 0)
            del m, mb, ok
    valid &= np.isfinite(hh) & np.isfinite(hv)
    valid = valid.astype(np.uint8)
    valid[~inside] = C.CLASS_NODATA
    swath[~inside] = C.CLASS_NODATA
    return {"hh": hh, "hv": hv, "valid": valid, "swath": swath, "n_swaths": nsw, "factor": k}


def write_date(date: str, g: Grid, event: str = C.EVENT) -> dict:
    t = time.time()
    d = read_date(date, g)
    write_cog(C.raster(f"{event}_{date}_hh_db.tif"), d["hh"], g)
    write_cog(C.raster(f"{event}_{date}_hv_db.tif"), d["hv"], g)
    write_cog(C.raster(f"{event}_{date}_vmask.tif"), d["valid"], g)
    write_cog(C.raster(f"{event}_{date}_swath.tif"), d["swath"], g)
    v = d["valid"]
    return {"date": date, "factor": d["factor"], "n_swaths": d["n_swaths"],
            "valid_px": int((v == 1).sum()), "inside_px": int((v != C.CLASS_NODATA).sum()),
            "seconds": round(time.time() - t, 1)}
