from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
from scipy import ndimage

from . import config as C
from .grid import load_grid, read

Z12_RES = 156543.03392804097 / 2 ** 12
PMTILES = os.path.expanduser("~/bin/pmtiles")
EV = C.EVENT
LEAD = f"{EV}_{C.LEAD[0]}-{C.LEAD[1]}"
S1 = f"{EV}_{C.S1_DATES[0]}-{C.S1_DATES[1]}"
LR_RAW_ZMAX = 11   # the naive difference is speckle-heavy: 84.7 MB at zoom 12, over the 50 MB per-file rule
BLUE, ORANGE, GREEN, PINK, LIGHT = "#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9"


def _rgb(h: str):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _to_3857(arr: np.ndarray, g, resampling, nodata, zmax: int = 12):
    src_crs = g.crs
    res = Z12_RES * 2 ** (12 - zmax)
    tr, w, h = calculate_default_transform(src_crs, "EPSG:3857", g.width, g.height, *g.bounds, resolution=res)
    dst = np.full((h, w), nodata, arr.dtype)
    reproject(arr, dst, src_transform=g.transform, src_crs=src_crs, src_nodata=nodata,
              dst_transform=tr, dst_crs="EPSG:3857", dst_nodata=nodata, resampling=resampling)
    return dst, tr


def _write_rgba(path: Path, rgba: np.ndarray, tr) -> None:
    with rasterio.open(path, "w", driver="GTiff", width=rgba.shape[2], height=rgba.shape[1], count=4,
                       dtype="uint8", crs="EPSG:3857", transform=tr, tiled=True, compress="deflate",
                       photometric="RGB", alpha="YES") as dst:
        dst.write(rgba)


def _pmtiles(rgba_tif: Path, out: Path, fmt: str, resampling: str) -> float:
    mb = rgba_tif.with_suffix(".mbtiles")
    if mb.exists():
        mb.unlink()
    opts = ["-co", f"TILE_FORMAT={fmt}", "-co", "ZOOM_LEVEL_STRATEGY=UPPER", "-co", "RESAMPLING=NEAREST"]
    if fmt == "WEBP":
        opts += ["-co", "QUALITY=75"]
    subprocess.run(["gdal_translate", "-q", "-of", "MBTILES", *opts, str(rgba_tif), str(mb)], check=True)
    subprocess.run(["gdaladdo", "-q", "-r", resampling, str(mb), "2", "4", "8", "16", "32", "64"], check=True)
    if out.exists():
        out.unlink()
    subprocess.run([PMTILES, "convert", str(mb), str(out)], check=True, capture_output=True)
    mb.unlink()
    return round(out.stat().st_size / 1e6, 2)


def continuous(arr: np.ndarray, vmin: float, vmax: float, cmap: str | None = None) -> np.ndarray:
    """float (NaN = transparent) -> RGBA uint8, gray or a diverging map."""
    ok = np.isfinite(arr)
    t = np.clip((np.where(ok, arr, vmin) - vmin) / (vmax - vmin), 0, 1)
    if cmap is None:
        v = (t * 255).astype(np.uint8)
        rgba = np.stack([v, v, v, np.where(ok, 255, 0).astype(np.uint8)])
    else:
        import matplotlib
        lut = (matplotlib.colormaps[cmap](np.linspace(0, 1, 256))[:, :3] * 255).astype(np.uint8)
        idx = (t * 255).astype(np.uint8)
        rgba = np.concatenate([lut[idx].transpose(2, 0, 1), np.where(ok, 255, 0).astype(np.uint8)[None]])
    return rgba


def classes(arr: np.ndarray, colors: dict) -> np.ndarray:
    """uint8 classes -> RGBA; colors = {code: (hex, alpha)}; other codes transparent."""
    rgba = np.zeros((4, *arr.shape), np.uint8)
    for code, (hexc, alpha) in colors.items():
        m = arr == code
        r, g_, b = _rgb(hexc)
        rgba[0][m], rgba[1][m], rgba[2][m], rgba[3][m] = r, g_, b, alpha
    return rgba


def outline_classes(mask: np.ndarray, width: int = 2) -> np.ndarray:
    """1 = ring around the mask (outline), 2 = inside the mask."""
    ring = ndimage.binary_dilation(mask, iterations=width) & ~mask
    out = np.zeros(mask.shape, np.uint8)
    out[mask] = 2
    out[ring] = 1
    return out


def _layer(name: str, arr: np.ndarray, kind: str, g, td: Path, color_fn, zmax: int = 12) -> float:
    if kind == "continuous":
        a3857, tr = _to_3857(arr.astype(np.float32), g, Resampling.average if zmax < 12 else Resampling.bilinear, np.nan, zmax)
        rgba = color_fn(a3857)
        fmt, rs = "WEBP", "average"
    else:
        a3857, tr = _to_3857(arr.astype(np.uint8), g, Resampling.nearest, 255)
        rgba = color_fn(a3857)
        fmt, rs = "PNG8", "nearest"
    tif = td / f"{name}.tif"
    _write_rgba(tif, rgba, tr)
    del a3857, rgba
    C.TILES.mkdir(parents=True, exist_ok=True)
    size = _pmtiles(tif, C.TILES / f"{name}.pmtiles", fmt, rs)
    tif.unlink()
    return size


def gaps_geojson(g) -> dict:
    """Swath gaps of the lead pair (inside the footprint, invalid on either date), at 240 m, as polygons."""
    v16 = read(C.raster(f"{EV}_{C.LEAD[0]}_vmask.tif"))
    v28 = read(C.raster(f"{EV}_{C.LEAD[1]}_vmask.tif"))
    inside = (v28 != 255)
    gap = inside & ((v16 != 1) | (v28 != 1))
    k = 6
    H, W = (g.height // k) * k, (g.width // k) * k
    coarse = gap[:H, :W].reshape(H // k, k, W // k, k).mean(axis=(1, 3)) >= 0.5
    coarse = ndimage.binary_opening(coarse, iterations=1)
    out = C.TILES / "gaps.geojson"
    with tempfile.TemporaryDirectory(dir=C.OUT) as td:
        tif = Path(td) / "gap.tif"
        tr = rasterio.Affine(g.res * k, 0, g.x0, 0, -g.res * k, g.y0)
        with rasterio.open(tif, "w", driver="GTiff", width=coarse.shape[1], height=coarse.shape[0], count=1,
                           dtype="uint8", crs=g.crs, transform=tr, nodata=0) as dst:
            dst.write(coarse.astype(np.uint8), 1)
        shp = Path(td) / "gap_utm.geojson"
        subprocess.run(["gdal_polygonize.py", "-q", str(tif), "-f", "GeoJSON", str(shp)], check=True)
        if out.exists():
            out.unlink()
        subprocess.run(["ogr2ogr", "-q", "-f", "GeoJSON", "-t_srs", "EPSG:4326", "-simplify", "120",
                        "-lco", "COORDINATE_PRECISION=5", str(out), str(shp)], check=True)
    return {"gaps_geojson_kb": round(out.stat().st_size / 1e3, 1)}


def build_tiles(only=None, event: str = EV) -> dict:
    g = load_grid(event)
    t0 = time.time()
    sizes = {}
    layers = []
    want = lambda n: (not only) or (n in only)  # noqa: E731
    gray = lambda a: continuous(a, *C.HH_STRETCH_DB)  # noqa: E731
    with tempfile.TemporaryDirectory(dir=C.OUT) as td:
        td = Path(td)
        for d in C.SERIES:
            name = f"hh_{d}"
            iso = f"{d[:4]}-{d[4:6]}-{d[6:]}"
            layers.append({"id": name, "kind": "continuous", "date": iso,
                           "title": f"NISAR HH, {int(d[6:])} {['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][int(d[4:6]) - 1]} 2026",
                           "description": "L-band radar brightness (HH, gamma0), gray from -25 dB (black) to 0 dB (white); swath gaps left out.",
                           "legend": [{"color": "#000000", "label": "-25 dB, smooth water"}, {"color": "#ffffff", "label": "0 dB, rough or built-up"}]})
            if want(name):
                hh = read(C.raster(f"{event}_{d}_hh_db.tif"))
                hh[read(C.raster(f"{event}_{d}_vmask.tif")) != 1] = np.nan
                sizes[name] = _layer(name, hh, "continuous", g, td, gray)
                del hh
        specs = [
            ("s1_twosided", f"{S1}_flood_s1twosided.tif", {1: (BLUE, 230), 3: (LIGHT, 150)},
             "Sentinel-1 flood map, 17 to 29 Sep 00:18 UTC", "C-band two-sided rule: new open water in blue; permanent water light blue.",
             [{"color": BLUE, "label": "New open water"}, {"color": LIGHT, "label": "Permanent water"}]),
            ("nisar_twosided", f"{LEAD}_flood_twosided.tif", {1: (BLUE, 230), 2: (ORANGE, 230), 3: (LIGHT, 150)},
             "NISAR flood map, 16 to 28 Sep 13:07 UTC", "L-band two-sided detector: new open water in blue, flooded vegetation in orange.",
             [{"color": BLUE, "label": "New open water"}, {"color": ORANGE, "label": "Flooded vegetation"}, {"color": LIGHT, "label": "Permanent water"}]),
            ("hidden", f"{event}_hidden.tif", {1: (ORANGE, 240)},
             "Hidden steps (evidence, not verified)", "Low ground under trees where NISAR flagged flooded vegetation on 28 Sep and Sentinel-1 saw dry land.",
             [{"color": ORANGE, "label": "Flagged under vegetation, evidence, not verified"}]),
        ]
        for name, src, cols, title, desc, legend in specs:
            layers.append({"id": name, "kind": "class", "date": None, "title": title, "description": desc, "legend": legend})
            if want(name):
                a = read(C.raster(src))
                sizes[name] = _layer(name, a, "class", g, td, lambda x, cols=cols: classes(x, cols))
                del a
        ref = read(C.raster(f"{event}_ref_optical.tif"))
        ref1a = read(C.raster(f"{event}_ref_optical_1a.tif"))
        c17 = read(C.raster(f"{event}_{C.S1_DATES[0]}_ref_c.tif"))
        c29 = read(C.raster(f"{event}_{C.S1_DATES[1]}_ref_c.tif"))
        outl = [
            ("referee", ref == C.OPEN_WATER, GREEN, "Optical referee: new water (L9 27 Sep and S2C 1 Oct)",
             "Water in both optical maps, both clear, JRC occurrence below 25%: what claim 1 scores against."),
            ("referee_1a", ref1a == C.OPEN_WATER, GREEN, "Optical referee 1a: new water on 29 Sep (Sentinel-2B)",
             "Water in the 29 Sep Sentinel-2B map, not water in a clear pre-flood map; western frame only."),
            ("dswx_s1_outline", (c29 == 1) & ((c17 == 0) | (c17 == 2)), PINK, "Sentinel-1's own map (OPERA DSWx-S1), new water",
             "Open water on 29 Sep and not on 17 Sep in OPERA's DSWx-S1 product."),
        ]
        del ref, ref1a, c17, c29
        for name, mask, col, title, desc in outl:
            layers.append({"id": name, "kind": "class", "date": None, "title": title, "description": desc,
                           "legend": [{"color": col, "label": "New water outline"}]})
            if want(name):
                sizes[name] = _layer(name, outline_classes(mask), "class", g, td,
                                     lambda x, col=col: classes(x, {1: (col, 255), 2: (col, 90)}))
        # naive difference and what we trust
        layers.append({"id": "lr_raw", "kind": "continuous", "date": None, "title": "Naive difference, HH 28 Sep minus 16 Sep",
                       "description": "Raw HH change with no mask: the swath-gap edges light up as fake change.",
                       "legend": [{"color": "#b2182b", "label": "-8 dB, darker (water arrived)"}, {"color": "#2166ac", "label": "+8 dB, brighter"}]})
        layers.append({"id": "lr_valid", "kind": "continuous", "date": None, "title": "What we trust, HH change with the valid mask",
                       "description": "Calibrated HH log-ratio, 3 x 3 median, only where both dates are fully focused and slope is at most 10 degrees.",
                       "legend": [{"color": "#b2182b", "label": "-8 dB, darker (water arrived)"}, {"color": "#2166ac", "label": "+8 dB, brighter"}]})
        div = lambda a: continuous(a, -8, 8, "RdBu")  # noqa: E731
        if want("lr_raw"):
            raw = read(C.raster(f"{event}_{C.LEAD[1]}_hh_db.tif")) - read(C.raster(f"{event}_{C.LEAD[0]}_hh_db.tif"))
            sizes["lr_raw"] = _layer("lr_raw", raw, "continuous", g, td, div, zmax=LR_RAW_ZMAX)
            del raw
        if want("lr_valid"):
            sizes["lr_valid"] = _layer("lr_valid", read(C.raster(f"{LEAD}_lr_hh.tif")), "continuous", g, td, div)
    if want("gaps"):
        sizes.update(gaps_geojson(g))
    from pyproj import Transformer
    tr = Transformer.from_crs(g.crs, "EPSG:4326", always_xy=True)
    xs, ys = tr.transform([g.bounds[0], g.bounds[2], g.bounds[0], g.bounds[2]], [g.bounds[1], g.bounds[1], g.bounds[3], g.bounds[3]])
    for l_ in layers:
        l_.update({"file": f"tiles/{l_['id']}.pmtiles", "minzoom": 6, "maxzoom": LR_RAW_ZMAX if l_["id"] == "lr_raw" else 12})
    manifest = {"layers": layers, "bounds": [round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)],
                "center": [84.1, 27.0], "gaps": "data/gaps.geojson"}
    (C.TILES / "layers.json").write_text(json.dumps(manifest, indent=1))
    sizes["seconds"] = round(time.time() - t0, 1)
    return sizes


def install(app_dir: Path = C.REPO / "app") -> dict:
    """Copy tiles into app/tiles (gitignored) and the manifest and gaps into app/data for local tests."""
    (app_dir / "tiles").mkdir(parents=True, exist_ok=True)
    n = 0
    for p in C.TILES.glob("*.pmtiles"):
        shutil.copy2(p, app_dir / "tiles" / p.name)
        n += 1
    shutil.copy2(C.TILES / "layers.json", app_dir / "data" / "layers.json")
    if (C.TILES / "gaps.geojson").exists():
        shutil.copy2(C.TILES / "gaps.geojson", app_dir / "data" / "gaps.geojson")
    return {"copied": n}
