from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REQUIRED = {
    "generated_utc": str, "commit": str, "event": str, "passes": dict, "time_offsets_h": dict,
    "calibration": dict, "thresholds": dict, "claim1": dict, "claim1a": dict, "claim2": dict,
}
CLAIM1 = ["metric", "margin", "nisar_twosided", "s1_twosided", "others", "diff", "ci95", "noninferior",
          "n_pixels", "n_new_water", "by_landcover"]
SCORES = ["f1", "precision", "recall", "iou", "ci95"]
CLAIM2_ROW = ["excess_km2", "ci95", "flood_km2", "control_km2", "n_pixels", "passes"]


def walk_nan(x, path="$"):
    bad = []
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        bad.append(path)
    elif isinstance(x, dict):
        for k, v in x.items():
            bad += walk_nan(v, f"{path}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            bad += walk_nan(v, f"{path}[{i}]")
    return bad


def check_interval(errs, where, point, ci):
    if not (isinstance(ci, list) and len(ci) == 2 and all(isinstance(v, (int, float)) for v in ci)):
        errs.append(f"{where}: ci95 missing or not two numbers: {ci}")
        return
    if point is None:
        errs.append(f"{where}: point estimate missing")
        return
    lo, hi = ci
    if not (lo <= point + 1e-9 and point <= hi + 1e-9):
        errs.append(f"{where}: interval {ci} does not contain {point}")


def check(res: dict) -> list[str]:
    errs = []
    for k, t in REQUIRED.items():
        if k not in res:
            errs.append(f"missing {k}")
        elif not isinstance(res[k], t):
            errs.append(f"{k} is not {t.__name__}")
    if "tier3" not in res:
        errs.append("missing tier3 (null when Tier 3 is cut)")
    errs += [f"NaN or inf at {p}" for p in walk_nan(res)]
    c1 = res.get("claim1", {})
    for k in CLAIM1:
        if k not in c1:
            errs.append(f"claim1 missing {k}")
    for m in ("nisar_twosided", "s1_twosided"):
        for k in SCORES:
            if k not in c1.get(m, {}):
                errs.append(f"claim1.{m} missing {k}")
        if m in c1:
            check_interval(errs, f"claim1.{m}.f1", c1[m].get("f1"), c1[m].get("ci95"))
    for m, v in c1.get("others", {}).items():
        if v is not None:
            check_interval(errs, f"claim1.others.{m}.f1", v.get("f1"), v.get("ci95"))
    check_interval(errs, "claim1.diff", c1.get("diff"), c1.get("ci95"))
    if c1.get("n_pixels", 0) <= 0 or c1.get("n_new_water", 0) <= 0:
        errs.append("claim1 has no pixels or no new water")
    c1a = res.get("claim1a", {})
    for m in ("nisar_twosided", "nisar_lr"):
        if m in c1a:
            check_interval(errs, f"claim1a.{m}.f1", c1a[m].get("f1"), c1a[m].get("ci95"))
        else:
            errs.append(f"claim1a missing {m}")
    check_interval(errs, "claim1a.diff", c1a.get("diff"), c1a.get("ci95"))
    c2 = res.get("claim2", {})
    for row in ("vegetation", "cropland"):
        r = c2.get(row)
        if not r:
            errs.append(f"claim2 missing {row}")
            continue
        for k in CLAIM2_ROW:
            if k not in r:
                errs.append(f"claim2.{row} missing {k}")
        check_interval(errs, f"claim2.{row}.excess_km2", r.get("excess_km2"), r.get("ci95"))
        if r.get("n_pixels", 0) <= 0:
            errs.append(f"claim2.{row} has no pixels")
    if "secondary" not in c2:
        errs.append("claim2 missing secondary (the contrast or its drop note)")
    return errs


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    path = Path(argv[0]) if argv else Path(__file__).resolve().parents[1] / "app" / "data" / "results.json"
    res = json.loads(path.read_text())
    errs = check(res)
    for e in errs:
        print("FAIL", e)
    print(f"{path}: {'OK' if not errs else f'{len(errs)} problem(s)'}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
