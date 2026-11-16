from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dwts import config as C  # noqa: E402
from dwts import sound  # noqa: E402
from dwts.listen import LISTEN, read_cell  # noqa: E402


def to_bytes(db: np.ndarray) -> np.ndarray:
    return np.where(np.isfinite(db), np.round((db + 40) * 4), 255).astype(np.uint8)


def main():
    out = C.OUT / "sound"
    out.mkdir(parents=True, exist_ok=True)
    cfg = sound.load()
    places = json.loads((C.OUT / "places.json").read_text())
    cells = {k: to_bytes(read_cell(LISTEN, v["col"], v["row"])) for k, v in places.items()}
    idx = json.loads((LISTEN / "index.json").read_text())
    rng = np.random.default_rng(C.SEED)
    while len(cells) < 13:
        c, r = int(rng.integers(idx["width"])), int(rng.integers(idx["height"]))
        b = to_bytes(read_cell(LISTEN, c, r))
        if (b != 255).all():
            cells[f"random_{c}_{r}"] = b
    summary = {}
    for name, b in cells.items():
        x = sound.render(b, cfg)
        sound.write_wav(out / f"{name}.wav", x)
        ok = True
        for j, v in enumerate(("hh", "hv")):
            notes = [sound.note(cfg, v, int(t)) for t in b[:, j]]
            o = np.argsort([n["db"] for n in notes], kind="stable")
            ok &= bool(np.all(np.diff(np.array([n["freq"] for n in notes])[o]) >= 0))
        summary[name] = {"peak_dbfs": round(sound.dbfs(x), 2), "seconds": round(len(x) / sound.SR, 3),
                         "pitch_follows_db": ok, "hh_db": (b[:, 0] / 4 - 40).tolist(), "hv_db": (b[:, 1] / 4 - 40).tolist()}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    bad = [k for k, v in summary.items() if not (v["pitch_follows_db"] and v["peak_dbfs"] < -1)]
    print(json.dumps({"clips": len(summary), "max_peak_dbfs": max(v["peak_dbfs"] for v in summary.values()),
                      "seconds": sorted({v["seconds"] for v in summary.values()}), "problems": bad, "dir": str(out)}))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
