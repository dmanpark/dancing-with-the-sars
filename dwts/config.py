from __future__ import annotations

import csv
import os
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("DWTS_DATA", Path.home() / "dwts-data"))
OUT = Path(os.environ.get("DWTS_OUT", Path.home() / "dwts-out"))
DOWNLOADS = DATA / "downloads"
ANCILLARY = DATA / "ancillary"
RASTERS = OUT / "rasters"
FIGURES = OUT / "figures"
LOGS = OUT / "logs"
TILES = OUT / "tiles"
MANIFEST = REPO / "data" / "manifest.csv"

EVENT = "gandak"
MANIFEST_EVENT = {"gandak": "gandak-2026-09", "nbihar": "nbihar-2026-09"}

# ---------------------------------------------------------------- grid and signal
EPSG = 32644
AVG_FACTOR_20M = 2            # 20 m posting -> 40 m (T2, T3)
PIXEL_M = 40.0
NODATA_DB = -9999.0
CLASS_NODATA = 255
DRY, OPEN_WATER, FLOODED_VEG, PERMANENT = 0, 1, 2, 3

SLOPE_MAX_DEG = 10.0
JRC_PERMANENT = 0.80          # occurrence fraction
CALIB_ABS_DB = 0.5
CALIB_SPREAD_DB = 0.5
CALIB_TILE_PX = 250           # 10 km tiles
CALIB_MIN_STABLE_PER_TILE = 1000
STABLE_HAND_HIGH_M = 15.0
STABLE_HAND_TOWN_M = 5.0
STABLE_BUILTUP_MIN = 0.5

# ---------------------------------------------------------------- detection
TILE_PX = 250
TILE_MIN_VALID = 0.5
ASHMAN_D_MIN = 2.0
GMM_MIN_WEIGHT = 0.05
GMM_MAX_SAMPLES = 50_000
KI_BIN_DB = 0.1
MIN_BIMODAL_TILES = 5
LR_OPEN_DB = -3.0
LR_VEG_DB = 3.0
LR_VEG_DIFF_DB = 2.0
MEDIAN_SIZE = 3

# ---------------------------------------------------------------- scoring
CLAIM1_MARGIN = -0.05
CLAIM1_REFEREE_JRC_MAX = 0.25  # change-log row 1
PIXEL_KM2 = 0.0016
VEG_CLASSES = (10, 20, 90)
CROP_CLASS = 40
CLAIM2_HAND_MAX_M = 2.0
SECONDARY_HAND_HIGH_M = 15.0
SECONDARY_MIN_SHARE = 0.05
BLOCK_PX = 125
N_BOOT = 1000
SEED = 2026
CI = (2.5, 97.5)

# ---------------------------------------------------------------- app
LISTEN_CELL_PX = 6
LISTEN_CHUNK = 128
HH_STRETCH_DB = (-25.0, 0.0)

# ---------------------------------------------------------------- dates (Gandak, track 149 frame 75)
SERIES = ["20260706", "20260823", "20260904", "20260916", "20260928", "20261010", "20261022"]
LEAD = ("20260916", "20260928")
CONTROL = ("20260823", "20260904")
CHECK_0904 = ("20260904", "20260928")   # "if the offset varies" check pair
S1_DATES = ("20260917", "20260929")
PASSES = {
    "nisar_pre": "2026-09-16T13:07:04Z", "nisar_post": "2026-09-28T13:07:05Z",
    "s1_pre": "2026-09-17T00:18:59Z", "s1_post": "2026-09-29T00:18:59Z",
    "control_pre": "2026-08-23T13:07:05Z", "control_post": "2026-09-04T13:07:05Z",
}

# Optical passes (DSWx-HLS), by role. Sensor tag and date select the tiles.
OPTICAL = {
    "pre_s2b_0916": ("20260916", "S2B"),     # pre -8 h
    "pre_l8_0917": ("20260917", "L8"),       # pre +16 h
    "post_l9_0927": ("20260927", "L9"),      # head-to-head referee, -32 h (change-log row 1)
    "post_s2b_0929": ("20260929", "S2B"),    # claim 1a referee, +16 h (change-log row 2)
    "post_s2c_1001": ("20261001", "S2C"),    # head-to-head referee, +64 h (change-log row 1)
}


@lru_cache(maxsize=1)
def manifest_rows() -> list[dict]:
    with open(MANIFEST, newline="") as f:
        return list(csv.DictReader(f))


def nisar_file(date: str, event: str = EVENT) -> Path:
    """The track-149 frame-75 GCOV file for a date (full frame, never the partial 10 Oct quad-pol file)."""
    ev = MANIFEST_EVENT[event]
    hits = []
    for r in manifest_rows():
        g = r["granule"]
        if r["event"] == ev and r["product"].startswith("NISAR") and f"_{date}T" in g:
            if event == "gandak" and "_149_D_075_" not in g:
                continue
            if r["role"] == "tier3-phase":
                continue
            hits.append(g)
    if len(hits) != 1:
        raise RuntimeError(f"expected one NISAR granule for {event} {date}, got {hits}")
    p = DOWNLOADS / ev / "NISAR_L2_GCOV_PROVISIONAL_V1" / f"{hits[0]}.h5"
    if not p.exists():
        raise FileNotFoundError(p)
    return p


def raster(name: str) -> Path:
    RASTERS.mkdir(parents=True, exist_ok=True)
    return RASTERS / name


def grid_json(event: str = EVENT) -> Path:
    return raster(f"grid_{event}.json")
