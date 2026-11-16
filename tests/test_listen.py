import json

import numpy as np
import pytest

from dwts import config as C
from dwts.listen import LISTEN, decode, encode_db, read_cell


def test_encode_decode_round_trip():
    db = np.array([-40.0, -12.3, 0.0, 10.0, np.nan, -50.0], np.float32)
    v = encode_db(db)
    assert v.tolist() == [0, 111, 160, 200, 255, 0]
    back = decode(v)
    assert abs(back[1] - (-12.25)) < 1e-6 and np.isnan(back[4])
    assert np.all(np.abs(back[:4] - db[:4]) <= 0.125 + 1e-6)


@pytest.mark.skipif(not (LISTEN / "index.json").exists(), reason="listening grid not built")
def test_three_cells_match_rasters():
    from dwts.grid import read
    idx = json.loads((LISTEN / "index.json").read_text())
    k = C.LISTEN_CELL_PX
    date_i, d = 4, C.SERIES[4]   # 28 Sep
    hh = read(C.raster(f"{C.EVENT}_{d}_hh_db.tif"))
    hv = read(C.raster(f"{C.EVENT}_{d}_hv_db.tif"))
    valid = read(C.raster(f"{C.EVENT}_{d}_vmask.tif")) == 1
    rng = np.random.default_rng(2026)
    checked = 0
    while checked < 3:
        col, row = int(rng.integers(0, idx["width"])), int(rng.integers(0, idx["height"]))
        sl = (slice(row * k, (row + 1) * k), slice(col * k, (col + 1) * k))
        v = valid[sl]
        if v.sum() < k * k / 2:
            continue
        cell = read_cell(LISTEN, col, row)
        for j, arr in enumerate((hh, hv)):
            expect = 10 * np.log10(np.mean(10 ** (arr[sl][v] / 10)))
            assert abs(cell[date_i, j] - expect) <= 0.125 + 1e-4, (col, row, j, cell[date_i, j], expect)
        checked += 1
