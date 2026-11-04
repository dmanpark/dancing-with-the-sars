# Preliminary tests: Claude Code prompt

## How to use this

Run it on the 3090 machine, inside WSL2, from the repo root, with an Earthdata login in `~/.netrc` (never in the repo):

```bash
cd ~/PROJECT_DWTS          # the repo, cloned onto the WSL2 ext4 disk
claude
```

Then tell Claude Code: **"Read prompts/prelim-tests.md and carry out everything below the line."**

It needs about 13 GB of downloads and several hours, most of it waiting on downloads and the DSWX-SAR install. It writes `prelim/REPORT.md` as it goes, so a run that stops early is still useful. Review the report together by Sun 8 Nov, decide on any proposed changes, and log them at the end of `docs/build-spec.md`.

These tests check the plan against real files. They do not build the submission and they compute no claim numbers. The code they leave behind is throwaway.

---

## Your job

You are checking whether the plan in `docs/build-spec.md` works on the real NISAR, OPERA and ancillary files before the team commits to it at NASA Space Apps on 14 Nov. Run tests T0 to T12 below. For each one, record what you found, how long it took and what it means for the spec. Write everything to `prelim/REPORT.md`, with figures in `prelim/figures/`.

Your deliverable is the report, not code. A test that fails clearly, with the reason written down, is a good result. A test that passes because you quietly changed the method is a bad one.

## Read first

1. `CLAUDE.md` (rules and conventions)
2. `docs/build-spec.md` (the fixed decisions you are testing; do not change them)
3. `docs/overview.md`, sections "The data" and "Risks and fallbacks"
4. `docs/data.md` (data traps)
5. `data/manifest.csv` and `prep/download.py` (what to download and how)

## Ground rules

These override anything else in this prompt.

1. **Work only in `prelim/`.** Code in `prelim/*.py`, a shared helper module `prelim/lib.py`, settings in `prelim/config.yaml`, intermediate files in `prelim/out/` (git-ignored), figures in `prelim/figures/` (PNG, each under 1 MB). Do not edit `docs/`, `prep/`, `data/` or `CLAUDE.md`. If something there is wrong, say so in the report.
2. **Data outside the repo.** Downloads go to `$DWTS_DATA/downloads` (default `~/dwts-data/downloads`) on the ext4 disk. Never commit data, rasters or credentials.
3. **Compute no claim numbers.** No F1, precision, recall, IoU or agreement of NISAR against any reference; no flooded-vegetation flag rates or km²; no AUROC; no hit counts. The one allowed comparison of two products is T10 (our DSWx-S1 run against OPERA's, both C-band). If you notice you are about to compute something that looks like a result, stop and describe the feasibility question instead.
4. **Do not tune.** The cuts (−3 dB, +3 dB, 2 dB), the bimodality rule, the calibration rule and every other fixed decision stay as written. Where the spec leaves a value to be read from the files (dataset paths, mask values, legends, posting), read it and record it.
5. **Ask before** any download that would take this session's running total past 15 GB, `sudo`, `apt`, installing Docker or anything system-wide, `git push` or any deploy, and deleting anything outside `prelim/out/` and `$DWTS_DATA`. Keep a running download total in the report.
6. **Timeboxes are real.** When a test hits its timebox, write down where it stands, mark it PARTIAL or BLOCKED, and move on.
7. **Log every command that matters** (installs, downloads, tool runs) in the report's environment section, with versions and wall times.
8. **Gandak only.** This run needs no north Bihar files; they come later with the rest of the download list.

## Shared settings

Write these into `prelim/config.yaml` and read them from there in every script.

- Event: `gandak`. Lead pair from `data/manifest.csv`: role `lead-pre` (16 Sep 13:07 UTC, quad-pol) and role `lead-post` (28 Sep 13:07 UTC, dual-pol), NISAR track 149, frame 75.
- Crop for heavy steps (the Bagaha area): lon 83.80 to 84.50, lat 26.80 to 27.35 (EPSG:4326). Convert it to the analysis grid's CRS once and store the pixel window.
- Full frame at 40 m for T5, T6 and T11, which need frame-wide statistics.
- Paths: `$DWTS_DATA`, `prelim/out`, `prelim/figures`.
- Seed 2026 everywhere.

## Run order

T0 → T1 (start downloads) → start the T10 install in the background → T2 → T3 → T4 → T11 → T8 → T5 → T9 → T6 → T7 → T10 run → T12. (T6's Sentinel-1 part needs T9's mosaic.) Update `prelim/REPORT.md` after every test.

---

## T0. Environment (timebox 45 min)

- Confirm WSL2, that the repo and `$DWTS_DATA` are on ext4 (`df -T`), free disk (need at least 40 GB) and RAM (`free -g`).
- Create a conda env `dwts` from `prelim/environment.yml` (conda-forge): python 3.11, numpy, scipy, h5py, rasterio, gdal, xarray, rioxarray, pyproj, shapely, geopandas, scikit-learn, matplotlib, pyyaml, earthaccess, asf_search. If conda is missing, ask before installing Miniforge.
- Get the `pmtiles` CLI as a single binary from the protomaps go-pmtiles releases into `~/bin`.
- Check `~/.netrc` has an `urs.earthdata.nasa.gov` entry (do not print it) and that `earthaccess.login()` succeeds.
- **Pass:** env builds, GDAL CLI and Python GDAL versions match, login works.

## T1. Downloads and throughput (timebox: the downloads themselves; check every 20 min)

Download with `prep/download.py --out $DWTS_DATA/downloads`, in this order:

1. NISAR lead pair: `--event gandak-2026-09 --role lead-post` first (1.9 GB), then `--role lead-pre` (7.7 GB).
2. Optical and C-band water maps, water layer only: `--event gandak-2026-09 --role ref-pre,ref-post --match _B01_WTR.tif`. These are small.
3. Sentinel-1 RTC bursts that intersect the crop, for roles `ref-pre-rtc` and `ref-post-rtc`. The manifest has no footprints, so write `prelim/select_bursts.py` to look up each granule's footprint in NASA CMR, keep the bursts that intersect the crop, and pass their granule names to `--match`. Take the VV, VH and mask layers, plus any other per-burst file that T10's DSWx-S1 run needs (check the DSWX-SAR docs first).
4. Ancillary layers covering the full Gandak frame (about 25.4 to 28.1°N, 81.9 to 85.1°E): Copernicus GLO-30 DEM, the GLO-30 HAND dataset, ESA WorldCover 2021, JRC Global Surface Water occurrence, and GHSL built-up surface. Find the current official download location for each from its publisher or the AWS Registry of Open Data; do not guess bucket names. Record every URL.

Measure throughput on the first large NISAR file. Extrapolate how long the full download list takes (`prep/download.py --dry-run` for the whole manifest, and the `size_mb` column: about 46 GB core NISAR plus 18 GB fallback and Tier 3).

Optional, 30 min: try Harmony variable subsetting on the 28 Sep granule (HHHH, HVHV and mask only). Record whether it works, the request, and the size against the full file.

- **Pass:** lead pair and references downloaded; projected time for the full list is under 24 hours.
- **Report:** MB/s, projected hours, running total in GB, any failed URLs.

## T2. File structure (timebox 45 min)

On both GCOV files:

- Dump the HDF5 tree (`h5ls -r` or h5py) to `prelim/out/` and record in the report the exact paths of: HHHH, HVHV, the mask, x and y coordinates, the projection (EPSG), the list of polarizations and of covariance terms for frequency A, the posting, and any metadata cube with incidence angle.
- In the quad-pol 16 Sep file, check whether the HHVV term (complex HH-VV covariance) is present. Read ASF's provisional known-issues page and quote, word for word, what it says about the 59° phase correction: which term it applies to and the sign.
- Record frequency A bandwidth and both files' processing versions.
- **Pass:** every path the build spec's Radar step 1 needs is found; posting confirmed (expected 20 m).
- **Spec impact:** posting other than 20 m changes the averaging factor; no HHVV term drops the Tier 3 phase test; no incidence angle drops one trust feature.

## T3. Grid alignment (timebox 30 min)

- Compare the coordinate vectors of 16 Sep and 28 Sep: same CRS, same posting, and whether they align exactly or are offset by whole pixels or fractions.
- Build the 40 m analysis grid from the 28 Sep file (2 × 2 average) and write `prelim/out/grid_gandak.json` (CRS, transform, width, height). Record the frame size in pixels at 40 m and the memory one float32 layer takes.
- **Pass:** the grids align, or the offset is known exactly.

## T4. Mask semantics and swath gaps (timebox 1 h)

- Histogram the mask values on both dates. Find the GCOV product specification on ASF's NISAR documentation and map each value to its meaning. Record the source.
- Find a swath-gap stripe on the 28 Sep HH image (inside the crop if one crosses it; otherwise a 20 km window elsewhere). Plot HH dB and the mask side by side across it on both dates: `prelim/figures/t04_stripe.png`.
- Decide, from the spec and the pixels, whether the stripes are flagged in the mask, are NaN or zero in the data, or are valid but low-signal.
- Write the valid-pixel rule for Radar step 3 as one exact sentence in terms of mask values.
- **Pass:** the stripes are fully excluded by the mask rule. **Fail:** some stripe pixels pass the mask; give the extra condition needed (and say it is a proposal).

## T11. Ancillary layers and the 5% rule (timebox 1.5 h)

- Put HAND, slope (from GLO-30, computed in a metric projection), WorldCover (nearest class), GHSL built-up (averaged fraction) and JRC occurrence (averaged fraction) onto the 40 m Gandak grid. Write them to `prelim/out/`. Time each one; Map does this on Saturday morning.
- On pixels valid on both lead dates, per WorldCover class 10, 20, 90 and 40: the share with HAND > 15 m and slope ≤ 10°, and the area in km² with HAND < 2 m. These use no NISAR values beyond the mask, so they are allowed.
- **Pass:** every layer on the grid; the 5% table written. **Spec impact:** any class under 5% loses the secondary claim 2 test.

## T8. Reference legends and coverage (timebox 1 h)

- Read the DSWx-HLS and DSWx-S1 product specifications and one tile of each. Record every class value present and its meaning, including DSWx-HLS cloud, shadow, snow, fill and partial surface water, and DSWx-S1's inundated-vegetation and masked classes.
- Write the mapping from each legend to the three referee states (water, not water, unknown), following build spec Truth steps 2 and 3. Partial surface water maps to unknown.
- Mosaic each optical pass onto the grid by majority (pre −8 h Sentinel-2B, pre +16 h Landsat 8, post −8 h Sentinel-2C filled with Landsat 8, post +16 h Sentinel-2B) and the two DSWx-S1 passes (17 and 29 Sep 00:18).
- Report, per pass, the share of the frame that is clear. Then count the pixels the optical referee would score: new water and stable dry, on the full frame and on the crop. These counts involve no NISAR data and are the size of the referee, not a result.
- **Pass:** legends mapped; the referee has at least 10,000 new-water pixels on the frame. **Flag** if it has fewer: claim 1's interval will be wide.

## T5. Calibration offset between quad-pol and dual-pol (timebox 1 h)

- Build stable ground exactly as the build spec defines it, on the full frame at 40 m, using T4's mask rule, T11's layers and T8's reference maps.
- HH and HV log-ratio (28 Sep minus 16 Sep, in dB after linear-power averaging): the median over stable ground, the stable pixel count, and separate medians for the two kinds of stable ground (high HAND; towns with HAND > 5 m).
- Per 10 km tile with at least 1,000 stable pixels: the median, mapped in `prelim/figures/t05_offset_tiles.png`, and the 10th to 90th percentile range of the tile medians.
- State which branch of the calibration rule applies: no correction, one offset, or per-tile offsets.
- **Pass:** offsets recorded and a branch named. **Flag** if the two kinds of stable ground disagree by more than 0.5 dB: rain on the hills may have changed soil moisture, and the team should see that before trusting the offset.

## T6. Bimodal tiles (timebox 1 h)

- On the full frame, 10 km tiles at least half valid: fit a two-component Gaussian mixture (scikit-learn, seed 2026) to the dB values of post-event HH and of post-event HV. A tile passes with Ashman D > 2 and the smaller component at least 5% of the tile.
- For passing tiles, the Kittler-Illingworth threshold (0.1 dB bins). Report tiles tested, tiles passing, each threshold, and the median, for HH and HV. Map passing tiles: `prelim/figures/t06_tiles.png`.
- Do the same for Sentinel-1 VV and VH on the crop bursts, and note that it is crop only.
- Do not build flood maps from these thresholds.
- **Pass:** at least 5 passing tiles per channel. **Fail:** fewer; the spec's fallback (log-ratio cut alone) applies to that channel.

## T7. Is the flood visible? (timebox 45 min)

This is the go or no-go check from `docs/review.md`. It is visual only.

- On the crop: HH dB for 16 and 28 Sep on one fixed stretch (−25 to 0 dB), the HH log-ratio on a diverging scale (−6 to +6 dB), and the same for HV. Hatch invalid pixels. Outline the post +16 h optical water (Sentinel-2B, 29 Sep) on the log-ratio panels. Save `prelim/figures/t07_flood_crop.png` (and one full-frame overview at reduced resolution, `t07_flood_frame.png`).
- Describe in three or four sentences what the figures show: does strong negative HH change follow the optical water along the Gandak; do positive HH changes appear in vegetated low ground; do stripe edges or other artifacts dominate.
- Count nothing against the optical outline.
- **Pass:** the flood is plainly visible along the Gandak. **Fail:** it is not; before reporting a fail, check dB conversion, the mask, and that HH was compared with HH.

## T9. Sentinel-1 RTC onto the grid (timebox 1 h)

- Mosaic the crop's RTC-S1 bursts (VV, VH, linear power, with their masks) onto the 40 m grid by averaging, for 17 and 29 Sep.
- Estimate the geolocation offset between NISAR 28 Sep HH and Sentinel-1 29 Sep VV on the crop by cross-correlation of the dB images (or of edge maps). Report it in pixels and metres.
- Figure: `prelim/figures/t09_s1_vs_nisar.png`, the two images side by side with the river centreline from the same JRC layer on both.
- **Pass:** offset under one 40 m pixel. **Flag** otherwise, with the measured shift.

## T10. DSWX-SAR (timebox 3 h for install and runs together)

- Clone `opera-adt/DSWX-SAR` into `$DWTS_DATA/tools/` (outside the repo) at its latest release tag, and record the tag. Build its environment from the repo's own instructions in a separate conda env. If its instructions need Docker or `sudo`, stop and ask.
- Run `dswx_s1.py --help` and `dswx_ni.py --help` (or the repo's equivalent entry points) and record what each needs: run configuration fields and every ancillary input.
- Run DSWx-S1 on the crop's 29 Sep 00:18 RTC bursts, with ancillary inputs cut to the crop. Compare our output with OPERA's own DSWx-S1 product for the same pass on the crop: open-water IoU and overall agreement, plus a difference map `prelim/figures/t10_dswx_s1_ours_vs_opera.png`. This checks our runner, which Truth needs at 9:05 Saturday for north Bihar.
- Record the run time per burst and extrapolate to 112 bursts (north Bihar's two dates).
- Try DSWx-NI on the 28 Sep GCOV. Record whether it starts, what it needs, and whether it accepts dual-pol GCOV. Do not spend more than 45 minutes of the timebox on it.
- Save the working run configuration (with local paths replaced by placeholders) in `prelim/dswx_s1_runconfig.yaml`.
- **Pass:** our DSWx-S1 matches OPERA's with open-water IoU of at least 0.8. **Report** the projected north Bihar run time; if it is over 4 hours, flag it.

## T12. Tiles and app smoke test (timebox 1 h)

- Take two layers on the crop: HH dB for 28 Sep (continuous) and a class layer. For the class layer, use the T8 optical referee states rather than any NISAR flood map.
- Color-map each to 8-bit RGBA, write MBTiles with GDAL at zoom 6 to 12, once as WEBP and once as PNG8, then convert each with `pmtiles convert`. Record file sizes and times.
- Extrapolate the size per layer to the full frame and to the app's layer list: seven HH dates, the flood maps, Sentinel-1, trust and check-first. Compare with the 600 MB site budget and the 100 MB file limit.
- Write a throwaway `prelim/out/app_test/index.html` with MapLibre GL JS and the pmtiles library from a CDN, showing one PMTiles layer. Serve it with `python -m http.server` and confirm tiles load through HTTP range requests (check the server log or a headless browser). Do not deploy anything.
- **Pass:** every projected file under 100 MB and the site under 600 MB. **Flag** layers that need the 60 m display fallback.

---

## The report

Keep `prelim/REPORT.md` in this shape, updated after every test.

```markdown
# Preliminary tests report

Run: <date>, <machine>, repo commit <hash>, run by Claude Code for <person>.
Downloads this run: <GB>.

## Summary

| Test | Status | Key finding | Spec impact |
| --- | --- | --- | --- |
| T0 Environment | PASS / PASS WITH NOTE / PARTIAL / FAIL / BLOCKED / SKIPPED | one line | none / proposal n |

## Go or no-go

Answers to the three checks in docs/review.md and the "By Sun 8 Nov" list in docs/overview.md:
1. The flood shows in the HH log-ratio along the Gandak (T7): yes / no / unclear.
2. Optical and C-band water maps exist around both dates (T8): yes / no.
3. The mask explains the stripes (T4): yes / no.
Plus: DSWX-SAR runs and matches OPERA (T10), calibration branch (T5), bimodal tiles (T6), tile budget (T12).

## Proposed spec changes

The team decides. Nothing here is applied.

| # | Spec item | Now | Proposed | Evidence |
| --- | --- | --- | --- | --- |

## Saturday timing

| Step | Measured | Extrapolated for Saturday | Fits the schedule? |
| --- | --- | --- | --- |

## Details

One section per test: what was done, numbers, figures, problems, and anything surprising.

## Open questions for the team

## Environment and commands

Versions, every install command, download URLs for ancillary layers, wall times.
```

Status meanings: PASS (works as the spec assumes), PASS WITH NOTE (works, with something the team should know), PARTIAL (timebox hit), FAIL (the spec's assumption is wrong; the fallback applies), BLOCKED (needs a human: a login, an approval, a decision), SKIPPED.

Write plainly: short sentences, no em-dashes, units on every number, and say what each result does not show.

## When you are done

1. Make sure `prelim/out/` and every data file are git-ignored, then commit `prelim/` (code, config, environment file, figures, report) to a local branch named `prelim`. Do not push.
2. Print a summary of ten lines or fewer in the chat: the go or no-go answers, every FAIL or BLOCKED test, and the proposed changes by number.
