from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

import numpy as np

from . import config as C
from .grid import block_mean_power, load_grid, read

LISTEN = C.OUT / "listen"


def encode_db(db: np.ndarray) -> np.ndarray:
    v = np.full(db.shape, 255, np.uint8)
    ok = np.isfinite(db)
    v[ok] = np.clip(np.round((db[ok] + 40.0) * 4.0), 0, 254).astype(np.uint8)
    return v


def decode(v: np.ndarray) -> np.ndarray:
    out = v.astype(np.float32) / 4.0 - 40.0
    out[v == 255] = np.nan
    return out


def cell_db(db: np.ndarray, valid: np.ndarray, k: int = C.LISTEN_CELL_PX) -> np.ndarray:
    p = np.where(valid & np.isfinite(db), 10.0 ** (db / 10.0), np.nan).astype(np.float32)
    m, n = block_mean_power(p, k)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (10.0 * np.log10(m)).astype(np.float32)
    out[n < (k * k) / 2.0] = np.nan
    return out


def build_listen(event: str = C.EVENT) -> dict:
    t0 = time.time()
    g = load_grid(event)
    k, ch = C.LISTEN_CELL_PX, C.LISTEN_CHUNK
    W, H = g.width // k, g.height // k
    cube = np.full((len(C.SERIES), 2, H, W), 255, np.uint8)
    for i, d in enumerate(C.SERIES):
        valid = read(C.raster(f"{event}_{d}_vmask.tif")) == 1
        for j, pol in enumerate(("hh", "hv")):
            cube[i, j] = encode_db(cell_db(read(C.raster(f"{event}_{d}_{pol}_db.tif")), valid))
    if LISTEN.exists():
        shutil.rmtree(LISTEN)
    LISTEN.mkdir(parents=True)
    chunks = []
    total = 0
    for cr in range(0, -(-H // ch)):
        for cc in range(0, -(-W // ch)):
            block = np.full((len(C.SERIES), 2, ch, ch), 255, np.uint8)
            sub = cube[:, :, cr * ch:(cr + 1) * ch, cc * ch:(cc + 1) * ch]
            block[:, :, :sub.shape[2], :sub.shape[3]] = sub
            if (block == 255).all():
                continue
            (LISTEN / f"{cc}_{cr}.bin").write_bytes(block.tobytes(order="C"))
            chunks.append(f"{cc}_{cr}")
            total += block.nbytes
    index = {"crs": g.crs, "utm_zone": 44, "x0": g.x0, "y0": g.y0, "cell": g.res * k, "width": W, "height": H,
             "chunk": ch, "dates": [f"{d[:4]}-{d[4:6]}-{d[6:]}" for d in C.SERIES], "flood_date": "2026-09-28",
             "channels": ["hh", "hv"], "layout": "date,channel,row,col", "nodata": 255,
             "decode": "dB = value / 4 - 40", "chunks": chunks}
    (LISTEN / "index.json").write_text(json.dumps(index))
    silent = float((cube == 255).mean())
    return {"cells": [W, H], "chunks": len(chunks), "mb": round(total / 1e6, 1), "silent_share": round(silent, 3),
            "seconds": round(time.time() - t0, 1)}


def read_cell(listen_dir: Path, col: int, row: int) -> np.ndarray:
    """Decode one cell (dates x 2 channels) from the chunk files, as the browser does."""
    idx = json.loads((listen_dir / "index.json").read_text())
    ch = idx["chunk"]
    name = f"{col // ch}_{row // ch}"
    nd = len(idx["dates"])
    if name not in idx["chunks"]:
        return np.full((nd, 2), np.nan, np.float32)
    b = np.frombuffer((listen_dir / f"{name}.bin").read_bytes(), np.uint8).reshape(nd, 2, ch, ch)
    return decode(b[:, :, row % ch, col % ch])


def install(app_dir: Path = C.REPO / "app") -> int:
    dst = app_dir / "data" / "listen"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(LISTEN, dst)
    return len(list(dst.glob("*.bin")))
