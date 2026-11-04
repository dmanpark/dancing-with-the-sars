# CLAUDE.md

Context for Claude Code sessions in this repo.

## What this is

Team repo for NASA Space Apps 2026 (14 to 15 Nov), challenge "Dancing with the SARS". The project, **Dancing with the SARS: The Hidden Steps**, uses NISAR L-band radar to find flood water under vegetation that C-band (Sentinel-1) flood maps largely miss. The lead event is Bihar's record Gandak flood of 28 Sep 2026; the trust model is fit on the north Bihar floods of early September. The output is a static web map with a trust layer and a ranked list of places to verify first.

Status: **pre-event**. The submission is built during the 39 hours of the event. Before kickoff the repo holds planning docs, data lists, the `prep/` search and download tools, and throwaway preliminary tests in `prelim/`.

## Read first

1. `docs/overview.md`: what we build and why, the four claims, the demo, the schedule.
2. `docs/build-spec.md`: fixed decisions, file contracts, each role's steps, done-criteria.
3. `docs/data.md`: verified scenes and references, and the NISAR data traps.
4. `docs/audit.md`: what the audit changed in version 2, and what is still open.

`docs/review.md` and `docs/literature.md` are background. `docs/archive/` holds superseded drafts; do not work from them.

## Hard rules

- **Never commit data or credentials.** No `.h5`, `.tif`, `.pmtiles` or `.mbtiles` files, no `.netrc`, no Earthdata tokens. Data lives in `$DWTS_DATA` (default `~/dwts-data`) and outputs in `$DWTS_OUT` (default `~/dwts-out`), both on the WSL2 ext4 disk, never on `/mnt/c`.
- **The fixed decisions in `docs/build-spec.md` are frozen.** Do not change cuts, thresholds, pixel sets, tests or margins. If one looks wrong, write a proposal with the evidence; the team decides and logs the change at the end of the build spec.
- **Before kickoff, compute no claim number.** No F1, excess km², AUROC or hit count against any reference, on either event. Feasibility checks (file structure, masks, calibration offsets on stable ground, bimodal tile counts, legends, sizes, run times) are fine.
- **No pre-event submission code.** The Space Apps FAQ asks teams to start the actual work at kickoff. Code written before 14 Nov 09:00 local goes in `prelim/` only and is rewritten during the event. The `prep/` tools are pre-event tools and get cited on the project page if used.
- **Ask before** any download that takes the running total past 15 GB in one session, `sudo`, `apt`, Docker or any other system-level install, `git push`, any deploy or anything else that publishes, and deleting anything outside `prelim/out/` and `$DWTS_DATA`.
- **Do not edit `docs/` or `prep/` unasked.** Report problems in them instead.

## Conventions

- Rasters: Cloud-Optimized GeoTIFF, one band, on the event's analysis grid (the lead post-event NISAR file's projection, averaged 2 × 2 to 40 m). Names `{event}_{yyyymmdd}_{layer}.tif`, `{event}_{pre}-{post}_{layer}.tif`, `{event}_{layer}.tif`; events `gandak`, `nbihar`.
- Classes: 0 dry, 1 open water, 2 flooded vegetation, 3 permanent water, 255 unknown or no data.
- Backscatter: average in linear power, then 10·log10. dB layers are float32 with nodata −9999.
- NISAR: frequency A only; HH and HV; PROVISIONAL products only (never mix with BETA).
- Statistics: 5 km blocks, 1,000 bootstrap draws, 95% percentile intervals, seed 2026.
- Paths and granule IDs come from `data/manifest.csv`; `prep/download.py` fetches by event, role, product and filename match.

## Environment

The 3090 machine under WSL2 runs the heavy jobs. Python 3.11 in a conda env (`dwts`) with numpy, scipy, h5py, rasterio, GDAL, xarray, rioxarray, pyproj, shapely, geopandas, scikit-learn, matplotlib, earthaccess, asf_search. OPERA's DSWX-SAR gets its own env, built from its repo's instructions. The `pmtiles` CLI is a single binary in `~/bin`.

## Writing in this repo

Plain sentences. No em-dashes. Every number carries its unit and, for anything that can change, the date it was checked. Link sources. Say what a result cannot tell you.

## Team roles

Radar (NISAR processing), Truth (references and every reported number), Map (ancillary layers and the app), Story (video, project page, citations).
