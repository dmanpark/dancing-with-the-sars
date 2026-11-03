"""List NISAR L2 GCOV granules over candidate events and pair pre/post scenes.

NISAR tracks often alternate radar modes from one 12-day cycle to the next
(e.g. 20+5 MHz quad-pol, then 20+5 MHz dual-pol). A strict "identical mode"
pair is then 24 days apart. This script instead pairs on:

  * same flight direction, track and frame (same geometry), and
  * same frequency-A range bandwidth (same resolution / noise class), and
  * at least two shared frequency-A polarizations (normally HH and HV).

Only PROVISIONAL (PR) granules are used, since mixing BETA and PROVISIONAL is
discouraged by ASF. Writes one CSV of granules per event plus pairs.csv.

Usage:
    python scripts/find_scenes.py data/events.json --out data/scenes
"""
import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import asf_search as asf

# NISAR L2 file name fields:
# NISAR_L2_PR_GCOV_{cycle}_{track}_{dir}_{frame}_{mode}_{pols}_{obs}_{start}_{end}_{crid}_{acc}_{cov}_{src}_{ctr}
FIELDS = ["mission", "level", "config", "product", "cycle", "track", "direction", "frame",
          "mode", "pols", "obs", "start", "end", "crid", "accuracy", "coverage", "source", "counter"]

# Two-letter polarization codes for frequency A (first two characters of the pols field)
POLS = {"DH": {"HH", "HV"}, "DV": {"VV", "VH"}, "QP": {"HH", "HV", "VH", "VV"},
        "SH": {"HH"}, "SV": {"VV"}, "NA": set()}

# Permanent NISAR data gap listed by ASF (no acquisitions will ever exist here)
DATA_GAP = ("2026-07-27T22:03:25Z", "2026-08-10T00:55:27Z")


def parse_name(name):
    parts = name.split("_")
    return dict(zip(FIELDS, parts)) if len(parts) == len(FIELDS) else {}


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def search_event(ev):
    lon, lat = ev["point"]
    results = asf.geo_search(
        dataset=asf.DATASET.NISAR,
        processingLevel="GCOV",
        intersectsWith=f"POINT({lon} {lat})",
        start=ev["pre_start"],
        end=ev["post_end"],
        maxResults=2000,
    )
    rows = []
    for g in results:
        p = g.properties
        f = parse_name(p["sceneName"])
        if not f or f["config"] != "PR":
            continue
        h5 = next((v["bytes"] for k, v in (p.get("bytes") or {}).items() if k.endswith(".h5")), None)
        rows.append({
            "event": ev["id"],
            "start": p["startTime"],
            "direction": p["flightDirection"],
            "track": int(f["track"]),
            "frame": int(f["frame"]),
            "cycle": int(f["cycle"]),
            "bw_a_mhz": int(f["mode"][:2]),
            "bw_b_mhz": int(f["mode"][2:]),
            "pols_a": f["pols"][:2],
            "pols_b": f["pols"][2:],
            "frame_coverage": p.get("frameCoverage"),
            "h5_mb": round(h5 / 1e6) if h5 else None,
            "scene": p["sceneName"],
            "url": p.get("url"),
        })
    return sorted(rows, key=lambda r: r["start"])


def pair_scenes(ev, rows):
    onset = datetime.fromisoformat(ev["onset"]).replace(tzinfo=timezone.utc)
    stacks = defaultdict(list)
    for r in rows:
        stacks[(r["direction"], r["track"], r["frame"])].append(r)
    pairs = []
    for (direction, track, frame), stack in stacks.items():
        post = [r for r in stack if ts(r["start"]) >= onset and POLS[r["pols_a"]]]
        if not post:
            continue
        b = post[0]
        pre = [r for r in stack if ts(r["start"]) < onset
               and r["bw_a_mhz"] == b["bw_a_mhz"]
               and len(POLS[r["pols_a"]] & POLS[b["pols_a"]]) >= 2]
        if not pre:
            continue
        a = pre[-1]
        pairs.append({
            "event": ev["id"],
            "direction": direction, "track": track, "frame": frame,
            "bw_a_mhz": b["bw_a_mhz"],
            "pre_date": a["start"][:10], "post_date": b["start"][:10],
            "post_time_utc": b["start"][11:16],
            "days_after_onset": (ts(b["start"]) - onset).days,
            "baseline_days": round((ts(b["start"]) - ts(a["start"])).total_seconds() / 86400),
            "pre_pols": a["pols_a"], "post_pols": b["pols_a"],
            "shared_pols": "+".join(sorted(POLS[a["pols_a"]] & POLS[b["pols_a"]])),
            "post_coverage": b["frame_coverage"],
            "download_gb": round(((a["h5_mb"] or 0) + (b["h5_mb"] or 0)) / 1e3, 1),
            "pre_scene": a["scene"], "post_scene": b["scene"],
        })
    return sorted(pairs, key=lambda p: (p["days_after_onset"], p["baseline_days"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("events")
    ap.add_argument("--out", default="data/scenes")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    all_pairs = []
    for ev in json.loads(Path(args.events).read_text()):
        rows = search_event(ev)
        pairs = pair_scenes(ev, rows)
        all_pairs += pairs
        if rows:
            with open(out / f"{ev['id']}_granules.csv", "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
        print(f"{ev['id']}: {len(rows)} PROVISIONAL GCOV granules, {len(pairs)} pre/post pairs")
        for p in pairs:
            print(f"   {p['direction'][:4]} T{p['track']:03d} F{p['frame']:03d} {p['bw_a_mhz']} MHz "
                  f"{p['pre_pols']}->{p['post_pols']}: {p['pre_date']} -> {p['post_date']} "
                  f"(+{p['days_after_onset']} d after onset, {p['baseline_days']} d baseline, "
                  f"{p['download_gb']} GB)")
    if all_pairs:
        with open(out / "pairs.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(all_pairs[0]))
            w.writeheader()
            w.writerows(all_pairs)


if __name__ == "__main__":
    main()
