from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import rasterio
from rasterio.shutil import copy as rio_copy
from rasterio.transform import Affine

from . import config as C


@dataclass(frozen=True)
class Grid:
    epsg: int
    x0: float          # west edge, m
    y0: float          # north edge, m
    res: float
    width: int
    height: int

    @property
    def transform(self) -> Affine:
        return Affine(self.res, 0.0, self.x0, 0.0, -self.res, self.y0)

    @property
    def crs(self) -> str:
        return f"EPSG:{self.epsg}"

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return (self.x0, self.y0 - self.height * self.res, self.x0 + self.width * self.res, self.y0)

    def to_json(self) -> dict:
        return {"crs": self.crs, "epsg": self.epsg, "transform": list(self.transform)[:6],
                "width": self.width, "height": self.height, "res": self.res}


def grid_from_coords(x: np.ndarray, y: np.ndarray, posting: float, epsg: int, factor: int) -> Grid:
    """Grid of `factor x factor` blocks of a GCOV coordinate grid (pixel centres)."""
    x0 = float(x[0]) - posting / 2
    y0 = float(y[0]) + posting / 2
    return Grid(epsg, x0, y0, posting * factor, len(x) // factor, len(y) // factor)


def save_grid(g: Grid, event: str = C.EVENT) -> Path:
    p = C.grid_json(event)
    p.write_text(json.dumps(g.to_json(), indent=1))
    return p


def load_grid(event: str = C.EVENT) -> Grid:
    d = json.loads(C.grid_json(event).read_text())
    t = d["transform"]
    return Grid(d["epsg"], t[2], t[5], t[0], d["width"], d["height"])


def block_mean_power(a: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Mean of k x k blocks of linear power, ignoring NaN. Returns (mean, count of finite samples)."""
    h, w = (a.shape[0] // k) * k, (a.shape[1] // k) * k
    v = a[:h, :w].reshape(h // k, k, w // k, k)
    fin = np.isfinite(v)
    s = np.where(fin, v, 0.0).sum(axis=(1, 3), dtype=np.float64)
    n = fin.sum(axis=(1, 3))
    with np.errstate(invalid="ignore", divide="ignore"):
        m = (s / n).astype(np.float32)
    m[n == 0] = np.nan
    return m, n


def power_to_db(p: np.ndarray) -> np.ndarray:
    with np.errstate(invalid="ignore", divide="ignore"):
        d = 10.0 * np.log10(p)
    d = d.astype(np.float32)
    d[~np.isfinite(d)] = np.nan
    return d


def write_cog(path: Path, arr: np.ndarray, g: Grid, nodata=None) -> Path:
    """Write one band as a Cloud-Optimized GeoTIFF. float arrays: NaN becomes nodata."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    a = arr
    if np.issubdtype(a.dtype, np.floating):
        nodata = C.NODATA_DB if nodata is None else nodata
        a = np.where(np.isfinite(a), a, nodata).astype(np.float32)
        pred = 3
    else:
        nodata = C.CLASS_NODATA if nodata is None else nodata
        pred = 2
    prof = dict(driver="GTiff", width=g.width, height=g.height, count=1, dtype=a.dtype, crs=g.crs,
                transform=g.transform, nodata=nodata, tiled=True, blockxsize=512, blockysize=512,
                compress="deflate", BIGTIFF="IF_SAFER")
    fd, tmp = tempfile.mkstemp(suffix=".tif", dir=path.parent)
    os.close(fd)
    try:
        with rasterio.open(tmp, "w", **prof) as dst:
            dst.write(a, 1)
        rio_copy(tmp, path, driver="COG", compress="DEFLATE", predictor=pred, blocksize=512,
                 overviews="NONE", BIGTIFF="IF_SAFER")
    finally:
        os.remove(tmp)
    return path


def read(path: Path, dtype=None) -> np.ndarray:
    """Read band 1; float nodata becomes NaN."""
    with rasterio.open(path) as src:
        a = src.read(1)
        nd = src.nodata
    if np.issubdtype(a.dtype, np.floating):
        a = a.astype(np.float32)
        if nd is not None:
            a[a == nd] = np.nan
    if dtype is not None:
        a = a.astype(dtype)
    return a
