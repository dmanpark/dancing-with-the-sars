from __future__ import annotations

import json
import math
import wave
from pathlib import Path

import numpy as np

from . import config as C

SR = 44100
SOUND_JSON = C.REPO / "app" / "data" / "sound.json"


def load(path: Path = SOUND_JSON) -> dict:
    return json.loads(Path(path).read_text())


def note(cfg: dict, voice: str, b: int) -> dict | None:
    """Pitch and peak for one byte value, exactly as the 'mapping' text in sound.json says."""
    if b == cfg["nodata"]:
        return None
    v = cfg["voices"][voice]
    db = b / 4.0 - 40.0
    x = min(max((db - v["db_min"]) / (v["db_max"] - v["db_min"]), 0.0), 1.0)
    steps = cfg["scale"]["steps"]
    iv = cfg["scale"]["intervals"]
    s = min(steps - 1, math.floor(x * steps))
    midi = v["base_midi"] + 12 * (s // len(iv)) + iv[s % len(iv)]
    return {"db": db, "x": x, "step": s, "midi": midi, "freq": 440.0 * 2 ** ((midi - 69) / 12.0),
            "peak": v["gain_min"] + (v["gain_max"] - v["gain_min"]) * x}


def _osc(shape: str, f: float, t: np.ndarray) -> np.ndarray:
    if shape == "sine":
        return np.sin(2 * np.pi * f * t)
    if shape == "triangle":
        return (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * f * t))
    if shape == "square":
        return np.sign(np.sin(2 * np.pi * f * t))
    if shape == "sawtooth":
        return 2 * ((f * t) % 1.0) - 1
    raise ValueError(shape)


def render(cell: np.ndarray, cfg: dict | None = None) -> np.ndarray:
    """cell: uint8 bytes, shape (dates, 2) for (hh, hv). Returns mono float32 at 44.1 kHz."""
    cfg = cfg or load()
    nd = cell.shape[0]
    total = cfg["lead_in_s"] + (nd - 1) * cfg["beat_s"] + max(v["attack_s"] + v["decay_s"] for v in cfg["voices"].values())
    out = np.zeros(int(math.ceil(total * SR)) + 1, np.float64)
    for k in range(nd):
        for j, voice in enumerate(("hh", "hv")):
            n = note(cfg, voice, int(cell[k, j]))
            if n is None:
                continue
            v = cfg["voices"][voice]
            t0 = cfg["lead_in_s"] + k * cfg["beat_s"]
            dur = v["attack_s"] + v["decay_s"]
            i0 = int(round(t0 * SR))
            t = np.arange(int(dur * SR)) / SR
            env = np.where(t < v["attack_s"], n["peak"] * t / v["attack_s"],
                           n["peak"] * np.exp(-(t - v["attack_s"]) / (v["decay_s"] / 5.0)))
            sig = env * _osc(v["waveform"], n["freq"], t)
            out[i0:i0 + len(sig)] += sig[: len(out) - i0]
    return (out * cfg["master_gain"]).astype(np.float32)


def write_wav(path: Path, x: np.ndarray) -> None:
    pcm = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((pcm * 32767).astype("<i2").tobytes())


def dbfs(x: np.ndarray) -> float:
    p = float(np.max(np.abs(x)))
    return -np.inf if p == 0 else 20 * np.log10(p)


def dominant_freq(x: np.ndarray, t0: float, t1: float) -> float:
    seg = x[int(t0 * SR):int(t1 * SR)]
    if seg.size < 256 or not np.any(seg):
        return float("nan")
    spec = np.abs(np.fft.rfft(seg * np.hanning(seg.size), n=1 << 16))
    return float(np.fft.rfftfreq(1 << 16, 1 / SR)[np.argmax(spec)])
