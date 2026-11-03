"""Find reference products near a NISAR acquisition time, via NASA CMR (no login).

Searches OPERA DSWx-S1 (water maps), OPERA RTC-S1 (Sentinel-1 backscatter, to run
DSWx-S1 yourself where OPERA did not), and HLS (optical) inside a bounding box,
within +/- a time window of a target time. Prints a summary and writes a CSV with
the time offset from the NISAR scene and the download URL.

Usage:
    python prep/find_references.py --bbox 81.93,25.44,85.09,28.13 \
        --time 2026-09-28T13:07:05Z --hours 36 --out data/refs/gandak_post.csv
"""
import argparse
import csv
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

CMR = "https://cmr.earthdata.nasa.gov/search/granules.json"
PRODUCTS = ["OPERA_L3_DSWX-S1_V1", "OPERA_L2_RTC-S1_V1", "HLSS30", "HLSL30"]


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def search(short_name, bbox, t0, t1):
    out, page = [], 1
    while True:
        q = urllib.parse.urlencode({
            "short_name": short_name, "bounding_box": bbox,
            "temporal": f"{t0:%Y-%m-%dT%H:%M:%SZ},{t1:%Y-%m-%dT%H:%M:%SZ}",
            "page_size": 2000, "page_num": page})
        with urllib.request.urlopen(f"{CMR}?{q}", timeout=60) as r:
            entries = json.load(r)["feed"]["entry"]
        out += entries
        if len(entries) < 2000:
            return out
        page += 1


def data_urls(entry):
    return [l["href"] for l in entry.get("links", [])
            if l.get("rel", "").endswith("/data#") and l["href"].startswith("https")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bbox", required=True, help="W,S,E,N")
    ap.add_argument("--time", required=True, help="NISAR acquisition time, ISO UTC")
    ap.add_argument("--hours", type=float, default=36)
    ap.add_argument("--products", default=",".join(PRODUCTS))
    ap.add_argument("--out")
    args = ap.parse_args()
    t = ts(args.time)
    t0, t1 = t - timedelta(hours=args.hours), t + timedelta(hours=args.hours)
    rows = []
    for sn in args.products.split(","):
        for e in search(sn, args.bbox, t0, t1):
            urls = data_urls(e)
            rows.append({
                "product": sn,
                "granule": e["title"],
                "time": e["time_start"][:19] + "Z",
                "offset_h": round((ts(e["time_start"]) - t).total_seconds() / 3600, 1),
                "cloud_cover": e.get("cloud_cover", ""),
                "n_files": len(urls),
                "urls": " ".join(urls),
            })
    rows.sort(key=lambda r: (r["product"], abs(r["offset_h"])))
    groups = {}
    for r in rows:
        groups.setdefault((r["product"], r["time"][:15]), []).append(r)
    for (p, tm), rs in sorted(groups.items(), key=lambda kv: (kv[0][0], abs(kv[1][0]["offset_h"]))):
        cc = sorted({int(float(r["cloud_cover"])) for r in rs if r["cloud_cover"] != ""})
        print(f"{p:22s} {rs[0]['time'][:16]}  {rs[0]['offset_h']:+6.1f} h  {len(rs):3d} granules"
              + (f"  cloud% {cc}" if cc else ""))
    if args.out and rows:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    main()
