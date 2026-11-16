from __future__ import annotations

import glob
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np

from . import config as C
from .grid import Grid, load_grid, read, write_cog

WARP = ["gdalwarp", "-q", "-overwrite", "-wm", "512", "-multi", "-wo", "NUM_THREADS=4"]


def _target(g: Grid) -> list[str]:
    xmin, ymin, xmax, ymax = g.bounds
    return ["-t_srs", g.crs, "-te", str(xmin), str(ymin), str(xmax), str(ymax),
            "-ts", str(g.width), str(g.height)]


def _vrt(files: list[str], out: Path) -> Path:
    subprocess.run(["gdalbuildvrt", "-q", str(out), *files], check=True)
    return out


def _warp(src: Path, dst: Path, g: Grid, method: str, extra: list[str] = ()) -> Path:
    subprocess.run([*WARP, *_target(g), "-r", method, *extra, "-of", "GTiff",
                    "-co", "TILED=YES", "-co", "COMPRESS=DEFLATE", str(src), str(dst)], check=True)
    return dst


def build_all(event: str = C.EVENT) -> dict:
    g = load_grid(event)
    out = {}
    with tempfile.TemporaryDirectory(dir=C.OUT) as td:
        td = Path(td)
        # HAND, bilinear
        t = time.time()
        v = _vrt(sorted(glob.glob(str(C.ANCILLARY / "hand" / "*_HAND.tif"))), td / "hand.vrt")
        tmp = _warp(v, td / "hand.tif", g, "bilinear", ["-dstnodata", "-9999"])
        write_cog(C.raster(f"{event}_hand.tif"), read(tmp), g)
        out["hand_s"] = round(time.time() - t, 1)
        # slope: DEM to UTM at 30 m, gdaldem slope in metres, average to 40 m
        t = time.time()
        v = _vrt(sorted(glob.glob(str(C.ANCILLARY / "dem" / "*_DEM.tif"))), td / "dem.vrt")
        xmin, ymin, xmax, ymax = g.bounds
        pad = 600
        subprocess.run([*WARP, "-t_srs", g.crs, "-te", str(xmin - pad), str(ymin - pad), str(xmax + pad),
                        str(ymax + pad), "-tr", "30", "30", "-r", "bilinear", "-dstnodata", "-9999",
                        "-co", "TILED=YES", "-co", "BIGTIFF=YES", str(v), str(td / "dem30.tif")], check=True)
        subprocess.run(["gdaldem", "slope", "-q", str(td / "dem30.tif"), str(td / "slope30.tif"),
                        "-compute_edges", "-co", "TILED=YES", "-co", "BIGTIFF=YES"], check=True)
        tmp = _warp(td / "slope30.tif", td / "slope.tif", g, "average", ["-dstnodata", "-9999"])
        write_cog(C.raster(f"{event}_slope.tif"), read(tmp), g)
        out["slope_s"] = round(time.time() - t, 1)
        # WorldCover, nearest
        t = time.time()
        v = _vrt(sorted(glob.glob(str(C.ANCILLARY / "worldcover" / "*_Map.tif"))), td / "wc.vrt")
        tmp = _warp(v, td / "wc.tif", g, "near", ["-dstnodata", "0"])
        lc = read(tmp).astype(np.uint8)
        lc[lc == 0] = C.CLASS_NODATA
        write_cog(C.raster(f"{event}_landcover.tif"), lc, g)
        out["landcover_s"] = round(time.time() - t, 1)
        # GHSL built-up surface (m2 per 100 m cell) as a fraction, averaged
        t = time.time()
        files = sorted(glob.glob(str(C.ANCILLARY / "ghsl" / "GHS_BUILT_S_*.tif")))
        v = _vrt(files, td / "ghsl.vrt")
        tmp = _warp(v, td / "ghsl.tif", g, "average", ["-ot", "Float32", "-dstnodata", "-9999"])
        b = read(tmp) / 10000.0
        b = np.clip(np.nan_to_num(b, nan=0.0), 0, 1).astype(np.float32)
        write_cog(C.raster(f"{event}_builtup.tif"), b, g)
        out["builtup_s"] = round(time.time() - t, 1)
        # JRC occurrence (percent, 255 = no data) as a fraction, averaged
        t = time.time()
        files = sorted(glob.glob(str(C.ANCILLARY / "jrc" / "occurrence_*.tif")))
        v = _vrt(files, td / "jrc.vrt")
        tmp = _warp(v, td / "jrc.tif", g, "average", ["-srcnodata", "255", "-ot", "Float32", "-dstnodata", "-9999"])
        j = read(tmp) / 100.0
        j = np.clip(np.nan_to_num(j, nan=0.0), 0, 1).astype(np.float32)
        write_cog(C.raster(f"{event}_jrc.tif"), j, g)
        out["jrc_s"] = round(time.time() - t, 1)
    return out
