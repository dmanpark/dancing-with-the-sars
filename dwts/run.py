from __future__ import annotations

import argparse
import json
import resource
import sys
import time

from . import config as C


def log(stage: str, info: dict) -> None:
    C.LOGS.mkdir(parents=True, exist_ok=True)
    rec = {"stage": stage, "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "peak_gb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6, 2), **info}
    with open(C.LOGS / "run.jsonl", "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")
    print(json.dumps(rec, default=str), flush=True)


def stage_grid(args):
    from .gcov import make_grid
    g = make_grid()
    log("grid", g.to_json())


def stage_db(args):
    from .gcov import write_date
    from .grid import load_grid
    g = load_grid()
    for d in args.dates or [*C.LEAD]:
        log("db", write_date(d, g))


def stage_series(args):
    from .gcov import write_date
    from .grid import load_grid
    g = load_grid()
    for d in C.SERIES:
        if d in C.LEAD and C.raster(f"{C.EVENT}_{d}_hh_db.tif").exists() and not args.force:
            continue
        log("series", write_date(d, g))


def stage_ancillary(args):
    from .ancillary import build_all
    log("ancillary", build_all())


def stage_refs(args):
    from .refs import build_optical, build_dswx_s1
    log("refs_optical", build_optical())
    log("refs_dswx_s1", build_dswx_s1())


def stage_s1(args):
    from .refs import build_rtc
    for d in C.S1_DATES:
        log("s1", build_rtc(d))


def stage_pairs(args):
    from .detect import run_pairs
    log("pairs", run_pairs())


def stage_claims(args):
    from .claims import run_claims
    log("claims", run_claims())


def stage_listen(args):
    from .listen import build_listen
    log("listen", build_listen())


def stage_tiles(args):
    from .tiles import build_tiles
    log("tiles", build_tiles(args.only))


STAGES = {"grid": stage_grid, "db": stage_db, "series": stage_series, "ancillary": stage_ancillary,
          "refs": stage_refs, "s1": stage_s1, "pairs": stage_pairs, "claims": stage_claims,
          "listen": stage_listen, "tiles": stage_tiles}


def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m dwts.run")
    p.add_argument("stage", choices=[*STAGES, "all"])
    p.add_argument("--event", default="gandak", choices=["gandak"])
    p.add_argument("--dates", nargs="*")
    p.add_argument("--only", nargs="*")
    p.add_argument("--force", action="store_true")
    a = p.parse_args(argv)
    if a.stage == "all":
        for name in ["grid", "db", "series", "ancillary", "refs", "s1", "pairs", "claims", "listen", "tiles"]:
            STAGES[name](a)
    else:
        STAGES[a.stage](a)


if __name__ == "__main__":
    sys.exit(main())
