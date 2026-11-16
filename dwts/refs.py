from __future__ import annotations

import glob
import re
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject, transform_bounds
from rasterio.windows import from_bounds

from . import config as C
from .grid import Grid, load_grid, power_to_db, read, write_cog

GANDAK = C.DOWNLOADS / C.MANIFEST_EVENT["gandak"]
UNK = C.CLASS_NODATA


def _latest_tiles(files: list[str]) -> list[str]:
    """One file per MGRS tile and acquisition time: the latest production version."""
    best = {}
    for f in files:
        name = Path(f).name
        m = re.search(r"_(T\w{5})_(\d{8}T\d{6})Z_(\d{8}T\d{6})Z_", name)
        if not m:
            continue
        key = (m.group(1), m.group(2))
        if key not in best or m.group(3) > best[key][0]:
            best[key] = (m.group(3), f)
    return sorted(v[1] for v in best.values())


def hls_tiles(date: str, sensor: str) -> list[str]:
    files = glob.glob(str(GANDAK / "OPERA_L3_DSWX-HLS_V1*" / f"OPERA_L3_DSWx-HLS_*_{date}T*_{sensor}_30_*_B01_WTR.tif"))
    return _latest_tiles(files)


def dswx_s1_tiles(date: str) -> list[str]:
    files = glob.glob(str(GANDAK / "OPERA_L3_DSWX-S1_V1" / f"OPERA_L3_DSWx-S1_*_{date}T00*_B01_WTR.tif"))
    return _latest_tiles(files)


def _warp_mode(files: list[str], g: Grid, dst: Path) -> np.ndarray:
    xmin, ymin, xmax, ymax = g.bounds
    subprocess.run(["gdalwarp", "-q", "-overwrite", "-wm", "512", "-t_srs", g.crs,
                    "-te", str(xmin), str(ymin), str(xmax), str(ymax), "-ts", str(g.width), str(g.height),
                    "-r", "mode", "-srcnodata", "255", "-dstnodata", "255", "-ot", "Byte",
                    "-co", "TILED=YES", "-co", "COMPRESS=DEFLATE", *files, str(dst)], check=True)
    return read(dst)


def hls_state(raw: np.ndarray) -> np.ndarray:
    s = np.full(raw.shape, UNK, np.uint8)
    s[raw == 0] = C.DRY
    s[raw == 1] = C.OPEN_WATER
    return s


def dswx_s1_state(raw: np.ndarray) -> np.ndarray:
    s = np.full(raw.shape, UNK, np.uint8)
    s[raw == 0] = C.DRY
    s[raw == 1] = C.OPEN_WATER
    s[raw == 3] = C.FLOODED_VEG
    return s


def build_optical(event: str = C.EVENT) -> dict:
    """One state map per optical pass, the permanent-water layer and both referees."""
    g = load_grid(event)
    info = {}
    states = {}
    with tempfile.TemporaryDirectory(dir=C.OUT) as td:
        for key, (date, sensor) in C.OPTICAL.items():
            files = hls_tiles(date, sensor)
            if not files:
                raise FileNotFoundError(f"no DSWx-HLS tiles for {date} {sensor}")
            s = hls_state(_warp_mode(files, g, Path(td) / f"{key}.tif"))
            write_cog(C.raster(f"{event}_{date}_hls_{sensor.lower()}.tif"), s, g)
            states[key] = s
            info[key] = {"tiles": len(files), "clear_px": int((s != UNK).sum()), "water_px": int((s == 1).sum())}
    jrc = read(C.raster(f"{event}_jrc.tif"))
    pre_a, pre_b = states["pre_s2b_0916"], states["pre_l8_0917"]
    permanent = (jrc >= C.JRC_PERMANENT) | ((pre_a == 1) & (pre_b == 1))
    write_cog(C.raster(f"{event}_permanent.tif"), permanent.astype(np.uint8), g)

    # Head-to-head referee (change-log row 1): water in both L9 27 Sep and S2C 1 Oct, both clear,
    # JRC occurrence below 25%; stable dry = not water in both, both clear.
    a, b = states["post_l9_0927"], states["post_s2c_1001"]
    ref = np.full(a.shape, UNK, np.uint8)
    ref[(a == 0) & (b == 0)] = C.DRY
    ref[(a == 1) & (b == 1) & (jrc < C.CLAIM1_REFEREE_JRC_MAX)] = C.OPEN_WATER
    ref[permanent] = C.PERMANENT
    write_cog(C.raster(f"{event}_ref_optical.tif"), ref, g)

    # Claim 1a referee (change-log rows 2 and 8): the 29 Sep Sentinel-2B map alone, with the
    # build spec's new-water definition (not water in any clear pre-event map, at least one clear).
    p = states["post_s2b_0929"]
    pre_clear = (pre_a != UNK) | (pre_b != UNK)
    pre_water = (pre_a == 1) | (pre_b == 1)
    r1a = np.full(p.shape, UNK, np.uint8)
    r1a[p == 0] = C.DRY
    r1a[(p == 1) & pre_clear & ~pre_water] = C.OPEN_WATER
    r1a[permanent] = C.PERMANENT
    write_cog(C.raster(f"{event}_ref_optical_1a.tif"), r1a, g)
    info["permanent_px"] = int(permanent.sum())
    info["ref_new_water_px"] = int((ref == 1).sum())
    info["ref_stable_dry_px"] = int((ref == 0).sum())
    info["ref1a_new_water_px"] = int((r1a == 1).sum())
    info["ref1a_stable_dry_px"] = int((r1a == 0).sum())
    return info


def build_dswx_s1(event: str = C.EVENT) -> dict:
    g = load_grid(event)
    info = {}
    with tempfile.TemporaryDirectory(dir=C.OUT) as td:
        for date in C.S1_DATES:
            files = dswx_s1_tiles(date)
            s = dswx_s1_state(_warp_mode(files, g, Path(td) / f"dswx_{date}.tif"))
            write_cog(C.raster(f"{event}_{date}_ref_c.tif"), s, g)
            info[date] = {"tiles": len(files), "known_px": int((s != UNK).sum()),
                          "water_px": int((s == 1).sum()), "inund_veg_px": int((s == 2).sum())}
    return info


def rtc_bursts(date: str) -> list[Path]:
    hs = sorted(glob.glob(str(GANDAK / "OPERA_L2_RTC-S1_V1" / f"OPERA_L2_RTC-S1_*_{date}T*_v1.0.h5")))
    return [Path(h[:-3]) for h in hs]   # stem without .h5


def build_rtc(date: str, event: str = C.EVENT) -> dict:
    """Mosaic every RTC-S1 burst of a pass onto the grid, averaging linear power."""
    t0 = time.time()
    g = load_grid(event)
    stems = rtc_bursts(date)
    if not stems:
        raise FileNotFoundError(f"no RTC-S1 bursts for {date}")
    out = {}
    first_time = None
    for pol in ("VV", "VH"):
        s = np.zeros((g.height, g.width), np.float32)
        n = np.zeros((g.height, g.width), np.uint16)
        for stem in stems:
            with rasterio.open(f"{stem}_mask.tif") as msrc:
                mask = msrc.read(1)
            with rasterio.open(f"{stem}_{pol}.tif") as src:
                a = src.read(1).astype(np.float32)
                if src.nodata is not None and not np.isnan(src.nodata):
                    a[a == src.nodata] = np.nan
                a[(mask != 0) | ~(a > 0)] = np.nan
                l, b_, r, t = transform_bounds(src.crs, g.crs, *src.bounds, densify_pts=21)
                xmin, ymin, xmax, ymax = g.bounds
                l, b_, r, t = max(l, xmin), max(b_, ymin), min(r, xmax), min(t, ymax)
                if l >= r or b_ >= t:
                    continue
                w = from_bounds(l, b_, r, t, g.transform).round_offsets().round_lengths()
                c0, r0 = max(int(w.col_off), 0), max(int(w.row_off), 0)
                c1 = min(int(w.col_off + w.width) + 1, g.width)
                r1 = min(int(w.row_off + w.height) + 1, g.height)
                dst = np.full((r1 - r0, c1 - c0), np.nan, np.float32)
                dtr = g.transform * g.transform.translation(c0, r0)
                reproject(a, dst, src_transform=src.transform, src_crs=src.crs, src_nodata=np.nan,
                          dst_transform=dtr, dst_crs=g.crs, dst_nodata=np.nan, resampling=Resampling.average)
            ok = np.isfinite(dst)
            s[r0:r1, c0:c1][ok] += dst[ok]
            n[r0:r1, c0:c1][ok] += 1
            del a, dst, ok, mask
        with np.errstate(invalid="ignore", divide="ignore"):
            m = np.where(n > 0, s / np.maximum(n, 1), np.nan).astype(np.float32)
        write_cog(C.raster(f"{event}_{date}_{pol.lower()}_db.tif"), power_to_db(m), g)
        out[f"{pol.lower()}_px"] = int((n > 0).sum())
        del s, n, m
    for stem in stems:
        mt = re.search(r"_(\d{8}T\d{6})Z_", stem.name)
        if mt and (first_time is None or mt.group(1) < first_time):
            first_time = mt.group(1)
    out.update({"date": date, "bursts": len(stems), "first_burst_utc": first_time,
                "seconds": round(time.time() - t0, 1)})
    return out
