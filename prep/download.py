"""Download files listed in data/manifest.csv with a NASA Earthdata login.

Covers both NISAR GCOV (ASF) and OPERA / HLS (PO.DAAC, LP DAAC): one Earthdata
account works for all of them. earthaccess reads ~/.netrc or asks for your
username and password the first time.

Examples:
    # the lead pair first (about 10 GB)
    python prep/download.py --role lead-pre,lead-post --out downloads
    # only the water-classification layer of the DSWx tiles
    python prep/download.py --product OPERA_L3_DSWX-S1_V1,OPERA_L3_DSWX-HLS_V1 --match _B01_WTR.tif,_B03_CONF.tif
    # see what would be fetched without downloading
    python prep/download.py --event nbihar-2026-09 --dry-run
"""
import argparse
import csv
from pathlib import Path

import earthaccess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/manifest.csv")
    ap.add_argument("--event", help="comma list, e.g. gandak-2026-09")
    ap.add_argument("--role", help="comma list, e.g. lead-pre,lead-post,series")
    ap.add_argument("--product", help="comma list of product short names")
    ap.add_argument("--match", help="comma list of filename substrings to keep")
    ap.add_argument("--out", default="downloads")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    split = lambda s: set(s.split(",")) if s else None
    events, roles, products, match = map(split, (args.event, args.role, args.product, args.match))
    rows = list(csv.DictReader(open(args.manifest)))
    jobs = []
    for r in rows:
        if events and r["event"] not in events:
            continue
        if roles and r["role"] not in roles:
            continue
        if products and r["product"] not in products:
            continue
        urls = [u for u in r["urls"].split() if not match or any(m in u for m in match)]
        dest = Path(args.out) / r["event"] / r["product"]
        jobs += [(u, dest) for u in urls]

    print(f"{len(jobs)} files")
    if args.dry_run:
        for u, d in jobs:
            print(d, u.rsplit("/", 1)[-1])
        return
    earthaccess.login(persist=True)
    by_dest = {}
    for u, d in jobs:
        by_dest.setdefault(d, []).append(u)
    for d, urls in by_dest.items():
        d.mkdir(parents=True, exist_ok=True)
        earthaccess.download(urls, local_path=str(d))


if __name__ == "__main__":
    main()
