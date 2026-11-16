from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402
from pyproj import Transformer  # noqa: E402

from . import config as C  # noqa: E402
from .grid import load_grid, read  # noqa: E402

CROP = {"lon_min": 83.80, "lon_max": 84.50, "lat_min": 26.80, "lat_max": 27.35}   # Bagaha


def window_lonlat(g, lon_min, lon_max, lat_min, lat_max):
    tr = Transformer.from_crs("EPSG:4326", g.crs, always_xy=True)
    xs, ys = tr.transform([lon_min, lon_max, lon_min, lon_max], [lat_min, lat_min, lat_max, lat_max])
    c0 = int((min(xs) - g.x0) // g.res); c1 = int((max(xs) - g.x0) // g.res)
    r0 = int((g.y0 - max(ys)) // g.res); r1 = int((g.y0 - min(ys)) // g.res)
    return max(r0, 0), min(r1, g.height), max(c0, 0), min(c1, g.width)


def gate12(event: str = C.EVENT) -> str:
    g = load_grid(event)
    r0, r1, c0, c1 = window_lonlat(g, **CROP)
    s = (slice(r0, r1), slice(c0, c1))
    pre, post = C.LEAD
    lr = read(C.raster(f"{event}_{post}_hh_db.tif"))[s] - read(C.raster(f"{event}_{pre}_hh_db.tif"))[s]
    valid = (read(C.raster(f"{event}_{pre}_vmask.tif"))[s] == 1) & (read(C.raster(f"{event}_{post}_vmask.tif"))[s] == 1)
    ref = read(C.raster(f"{event}_ref_optical.tif"))[s]
    c17 = read(C.raster(f"{event}_{C.S1_DATES[0]}_ref_c.tif"))[s]
    c29 = read(C.raster(f"{event}_{C.S1_DATES[1]}_ref_c.tif"))[s]
    dswx_new = (c29 == 1) & ((c17 == 0) | (c17 == 2))
    fig, ax = plt.subplots(1, 2, figsize=(16, 7.5), constrained_layout=True)
    for a, show_mask in zip(ax, (False, True)):
        im = a.imshow(np.where(valid | ~show_mask, lr, np.nan), cmap="RdBu", vmin=-8, vmax=8, interpolation="nearest")
        if show_mask:
            a.contourf(~valid, levels=[0.5, 1.5], colors="none", hatches=["////"])
        a.contour(dswx_new.astype(float), levels=[0.5], colors="#CC79A7", linewidths=0.6)
        a.contour((ref == 1).astype(float), levels=[0.5], colors="#009E73", linewidths=1.2)
        a.set_xticks([]); a.set_yticks([])
    ax[0].set_title("HH log-ratio 28 Sep minus 16 Sep, raw (dB)")
    ax[1].set_title("Same, invalid pixels hatched (T4 mask rule)")
    fig.colorbar(im, ax=ax, shrink=0.7, label="dB (red = darker on 28 Sep, blue = brighter)")
    fig.suptitle("Gate 12:00, Bagaha crop (83.80 to 84.50 E, 26.80 to 27.35 N). Green: optical new water "
                 "(L9 27 Sep and S2C 1 Oct). Pink: DSWx-S1 new water 17 to 29 Sep.", fontsize=10)
    C.FIGURES.mkdir(parents=True, exist_ok=True)
    out = C.FIGURES / "gate12_flood.png"
    fig.savefig(out, dpi=110)
    plt.close(fig)
    blue = np.nanmean(lr[valid] <= C.LR_OPEN_DB)
    return f"{out} (share of valid crop pixels with raw HH log-ratio <= -3 dB: {blue:.3f})"


def nisar_vs_s2(event: str = C.EVENT) -> str:
    """NISAR's lead-pair two-sided map beside Sentinel-2B DSWx-HLS of 29 Sep, where S2B is clear."""
    g = load_grid(event)
    s2b = read(C.raster(f"{event}_20260929_hls_s2b.tif"))
    cls = read(C.raster(f"{event}_{C.LEAD[0]}-{C.LEAD[1]}_flood_twosided.tif"))
    n = 1000   # 40 km window with the most clear Sentinel-2B water that NISAR also covers
    best, rc = -1, (0, 0)
    for r in range(0, g.height - n, n // 4):
        for c in range(0, g.width - n, n // 4):
            k = int(((s2b[r:r + n, c:c + n] == 1) & (cls[r:r + n, c:c + n] != 255)).sum())
            if k > best:
                best, rc = k, (r, c)
    r, c = rc
    s = (slice(r, r + n), slice(c, c + n))
    hh = read(C.raster(f"{event}_{C.LEAD[1]}_hh_db.tif"))[s]
    fig, ax = plt.subplots(1, 3, figsize=(18, 6.4), constrained_layout=True)
    ax[0].imshow(hh, cmap="gray", vmin=-25, vmax=0)
    ax[0].set_title("NISAR HH, 28 Sep 13:07 UTC", fontsize=10)
    cm = ListedColormap(["#f2f2f2", "#0072B2", "#E69F00", "#56B4E9"])
    k = cls[s].astype(float); k[k == 255] = np.nan
    ax[1].imshow(k, cmap=cm, vmin=-0.5, vmax=3.5, interpolation="nearest")
    ax[1].set_title("NISAR two-sided, 16 to 28 Sep\nblue new open water, orange flooded vegetation", fontsize=10)
    v = s2b[s].astype(float); v[v == 255] = np.nan
    ax[2].imshow(v, cmap=ListedColormap(["#f2f2f2", "#0072B2"]), vmin=-0.5, vmax=1.5, interpolation="nearest")
    ax[2].set_title("Sentinel-2B DSWx-HLS, 29 Sep (+16 h)\nblue water; white is dry, cloud or no data", fontsize=10)
    for a in ax:
        a.set_xticks([]); a.set_yticks([])
    x0, y0 = g.x0 + c * g.res, g.y0 - r * g.res
    tr = Transformer.from_crs(g.crs, "EPSG:4326", always_xy=True)
    lon, lat = tr.transform(x0 + n * g.res / 2, y0 - n * g.res / 2)
    fig.suptitle(f"40 km window centred on {lon:.2f} E, {lat:.2f} N (the window with the most clear Sentinel-2B water)", fontsize=10)
    out = C.FIGURES / "nisar_vs_s2_20260929.png"
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return f"{out} (centre {lon:.3f} E, {lat:.3f} N)"


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "gate12"
    print(gate12() if which == "gate12" else nisar_vs_s2())
