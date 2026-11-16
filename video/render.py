from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dwts import config as C  # noqa: E402
from dwts import sound  # noqa: E402
from dwts.listen import LISTEN, read_cell  # noqa: E402
from dwts.words import captions  # noqa: E402

URL = "https://dmanpark.github.io/dancing-with-the-sars/"
TARGET_PEAK_DBFS = -3.0
OUT = C.OUT / "video"


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(res: dict, timeline: dict, path: Path) -> list[str]:
    caps = captions(res)
    times = timeline["captions"]
    lines, texts = [], []
    for i, ((s0, e0, text), t) in enumerate(zip(caps, times), 1):
        s, e = t["start_s"], min(t["end_s"], timeline["duration_s"]) - 0.05
        lines += [str(i), f"{srt_time(s)} --> {srt_time(e)}", text, ""]
        texts.append(text)
    path.write_text("\n".join(lines), encoding="utf-8")
    return texts


def tap_cell(timeline: dict) -> np.ndarray:
    from pyproj import Transformer
    idx = json.loads((LISTEN / "index.json").read_text())
    x, y = Transformer.from_crs("EPSG:4326", idx["crs"], always_xy=True).transform(timeline["tap"]["lon"], timeline["tap"]["lat"])
    col = int((x - idx["x0"]) // idx["cell"])
    row = int((idx["y0"] - y) // idx["cell"])
    db = read_cell(LISTEN, col, row)
    b = np.where(np.isfinite(db), np.round((db + 40) * 4), 255).astype(np.uint8)
    return b


def record(url: str, timeline: dict, workdir: Path) -> tuple[Path, float]:
    from playwright.sync_api import sync_playwright
    w, h = timeline["viewport"]
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1,
                                  record_video_dir=str(workdir), record_video_size={"width": w, "height": h})
        sep = "&" if "?" in url else "?"
        # In video mode the app visits every storyboard view before it starts the clock (warm-up),
        # so each shot draws from its first frame; the cut below starts at videoStartMs.
        t_rec = time.time() * 1000.0
        page = ctx.new_page()
        page.goto(f"{url}{sep}video=1", wait_until="load")
        page.wait_for_function("window.__dwts && typeof window.__dwts.videoStartMs === 'number'", timeout=180_000)
        start = page.evaluate("performance.timeOrigin + window.__dwts.videoStartMs")
        page.wait_for_function("window.__dwts && window.__dwts.videoDone === true",
                               timeout=int((timeline["duration_s"] + 30) * 1000))
        page.wait_for_timeout(1500)   # the recorder drops the last few hundred ms otherwise
        vid = page.video.path()
        ctx.close()
        browser.close()
    return Path(vid), max(0.0, (start - t_rec) / 1000.0)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    url = argv[0] if argv else URL
    OUT.mkdir(parents=True, exist_ok=True)
    res = json.loads((ROOT / "app" / "data" / "results.json").read_text())
    timeline = json.loads((ROOT / "video" / "timeline.json").read_text())
    dur = float(timeline["duration_s"])
    srt = ROOT / "video" / "captions.srt"
    texts = write_srt(res, timeline, srt)
    work = OUT / "work"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    webm, offset = record(url, timeline, work)
    # sound: the tapped cell, played from the tap time, in a 30 s track
    cell = tap_cell(timeline)
    clip = sound.render(cell)
    track = np.zeros(int(math.ceil(dur * sound.SR)), np.float32)
    i0 = int(timeline["tap"]["t_s"] * sound.SR)
    n = min(len(clip), len(track) - i0)
    track[i0:i0 + n] = clip[:n]
    # level: the tap's sound peaks at -3 dBFS in the video (gain only; the mapping is unchanged)
    peak = float(np.max(np.abs(track)))
    if peak > 0:
        track *= 10 ** (TARGET_PEAK_DBFS / 20) / peak
    wav = work / "sound.wav"
    sound.write_wav(wav, track)
    out = OUT / "dwts_30s.mp4"
    style = "FontName=DejaVu Sans,FontSize=13,PrimaryColour=&H00FFFFFF,OutlineColour=&H00202020,BackColour=&H00202020,BorderStyle=3,Outline=1,Shadow=0,MarginV=28"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{offset:.3f}", "-i", str(webm), "-i", str(wav),
                    "-t", f"{dur:.3f}", "-vf", f"subtitles={srt}:force_style='{style}',fps=30,format=yuv420p",
                    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)], check=True)
    probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,codec_name,duration",
                                       "-of", "json", str(out)], capture_output=True, text=True, check=True).stdout)
    d = float(probe["format"]["duration"])
    v = [s for s in probe["streams"] if s.get("width")][0]
    report = {"video": str(out), "duration_s": d, "width": v["width"], "height": v["height"], "codec": v["codec_name"],
              "record_offset_s": round(offset, 3), "tap_cell_bytes": cell.tolist(), "captions": texts,
              "peak_dbfs": round(sound.dbfs(track), 2), "stream_durations_s": [float(st.get("duration", "nan")) for st in probe["streams"]],
              "ok": d <= 30.0 and v["height"] == 1080 and all(float(st.get("duration", 0)) <= 30.0 for st in probe["streams"])}
    (OUT / "render_report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
