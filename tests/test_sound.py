import json

import numpy as np
import pytest

from dwts import config as C
from dwts import sound
from dwts.listen import LISTEN

pytestmark = pytest.mark.skipif(not sound.SOUND_JSON.exists(), reason="sound.json not written yet")


def test_mapping_monotonic_both_channels():
    cfg = sound.load()
    for voice in ("hh", "hv"):
        prev = None
        for b in range(0, 255):
            n = sound.note(cfg, voice, b)
            if prev is not None:
                assert n["freq"] >= prev["freq"] and n["peak"] >= prev["peak"]
            prev = n
        assert sound.note(cfg, voice, 255) is None


def test_hv_voice_lower_than_hh():
    cfg = sound.load()
    assert cfg["voices"]["hv"]["base_midi"] == cfg["voices"]["hh"]["base_midi"] - 12


def _cells(n_random=10):
    """Ten random cells with data on every date, from the real listening grid if it exists."""
    rng = np.random.default_rng(C.SEED)
    if (LISTEN / "index.json").exists():
        idx = json.loads((LISTEN / "index.json").read_text())
        out = []
        while len(out) < n_random:
            name = idx["chunks"][int(rng.integers(len(idx["chunks"])))]
            b = np.frombuffer((LISTEN / f"{name}.bin").read_bytes(), np.uint8).reshape(len(idx["dates"]), 2, 128, 128)
            r, c = int(rng.integers(128)), int(rng.integers(128))
            cell = b[:, :, r, c]
            if (cell != 255).all():
                out.append(cell.copy())
        return out
    return [rng.integers(40, 160, size=(7, 2)).astype(np.uint8) for _ in range(n_random)]


def test_random_cells_pitch_order_peak_and_length():
    cfg = sound.load()
    beat, lead = cfg["beat_s"], cfg["lead_in_s"]
    for cell in _cells():
        x = sound.render(cell, cfg)
        assert sound.dbfs(x) < -1.0
        dur = len(x) / sound.SR
        assert 6.5 * beat <= dur <= 8.5 * beat, dur
        for j, voice in enumerate(("hh", "hv")):
            notes = [sound.note(cfg, voice, int(v)) for v in cell[:, j]]
            order_db = np.argsort([n["db"] for n in notes], kind="stable")
            freqs = np.array([n["freq"] for n in notes])
            assert np.all(np.diff(freqs[order_db]) >= 0)
        # the rendered audio carries the notes: the loudest frequency in the first beat is one of its two notes
        f = sound.dominant_freq(x, lead + 0.01, lead + beat - 0.01)
        cands = [sound.note(cfg, v, int(cell[0, j]))["freq"] for j, v in enumerate(("hh", "hv"))]
        assert min(abs(f - c) for c in cands) < 3.0, (f, cands)
