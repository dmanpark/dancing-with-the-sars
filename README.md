# Dancing with the SARS: The Hidden Steps

A web app that shows anyone the flood water that today's radar flood maps miss under trees. Bihar's Gandak River hit a record on 27 Sep 2026; NASA-ISRO's NISAR imaged it with L-band radar on 28 Sep, and Europe's Sentinel-1 with C-band radar 11 hours later. Watch the river spread every 12 days, slide between the two radars' flood maps, tap a field and hear its radar signal change, and see how we checked it. Built during NASA Space Apps 2026 (14 to 15 Nov), challenge "Dancing with the SARS".

- **Live app:** https://dmanpark.github.io/dancing-with-the-sars/ (works on a phone; each step links directly, for example `#step=3`)
- **Video (30 s):** https://youtu.be/80nnnIlPmLc
- **Every number:** [`app/data/results.json`](app/data/results.json), written by the pipeline; the project text is in [`SUBMISSION.md`](SUBMISSION.md)

## What we found

The numbers below are copied from `results.json` at commit time; the app and `SUBMISSION.md` read them from that file.

- **Under trees (claim 2):** on low ground under trees where Sentinel-1's own water map (OPERA DSWx-S1) said dry, NISAR flagged 17 km² more flooded vegetation on 16 to 28 Sep than in the 12 days before (95% interval 15 to 19 km²). Half of the flagged pixels sit near buildings, so this is evidence, not a verified map. On cropland the same test shows no signal.
- **Open water, head to head (claim 1):** against an optical referee (Landsat 9 on 27 Sep and Sentinel-2C on 1 Oct), NISAR's F1 was 0.05 and Sentinel-1's 0.17 on the same pixels; NISAR did not pass our pre-set non-inferiority margin. Recall is low for every radar map, OPERA's own included, likely because most of the referee's water was already standing before the radars' pre-flood passes (90% of NISAR's misses were already dark on 16 Sep).
- **NISAR alone (claim 1a):** against the 29 Sep Sentinel-2B map in the western frame, NISAR's F1 was 0.68 (95% interval 0.53 to 0.76).

**What this can't tell you:** accuracy under canopy (no reference sees there), damage, global performance (one flood), real-time use (12-day repeat, 36 to 72 h latency), or final calibration (PROVISIONAL products). The full box is in the app's step 5.

## How to reproduce

On a Linux machine (we used WSL2 on Windows 11, 20 GB RAM for WSL) with a NASA Earthdata login in `~/.netrc`:

```bash
conda env create -f environment.yml && conda activate dwts && playwright install chromium
python prep/download.py --event gandak-2026-09 --role lead-pre,lead-post,series,history --out ~/dwts-data/downloads
python prep/download.py --event gandak-2026-09 --role ref-pre,ref-post --match _B01_WTR.tif --out ~/dwts-data/downloads
# RTC-S1 bursts (roles ref-pre-rtc, ref-post-rtc) need the ASF data-use agreement accepted in your Earthdata profile
# ancillary layers: the URLs in CITATIONS.md, into ~/dwts-data/ancillary/{dem,hand,worldcover,jrc,ghsl}
python -m dwts.run all                    # grid, dB layers, references, flood maps, claims, listening grid, tiles
python scripts/check_results.py && pytest -q
python scripts/serve.py 8765              # the app, with the tiles copied into app/tiles (dwts.tiles.install())
```

`$DWTS_DATA` (default `~/dwts-data`) holds inputs and `$DWTS_OUT` (default `~/dwts-out`) the outputs. The run takes about 75 min on 8 cores (most of it the four pairs and the tiles), peaking at 4.5 GB in one process. The fixed decisions (cuts, thresholds, pixel sets, statistics) are in [`docs/build-spec.md`](docs/build-spec.md) and its change log; every choice made during the build is in [`DECISIONS.md`](DECISIONS.md).

## Layout

```
dwts/            the pipeline: GCOV reader, grid, ancillary layers, references, calibration, thresholds,
                 detectors, statistics, claims, listening grid, tiles, sound renderer
tests/           pytest on synthetic arrays, the listening grid and the sound mapping
scripts/         check_results.py, check_app.py, serve.py, make_submission.py, render_sounds.py, push_tiles.sh
app/             the static site (index.html, app.js, style.css, steps.json, data/); tiles come from the `tiles` branch
video/           render.py, timeline.json, captions.srt
prep/            pre-event search and download scripts (written before the event)
docs/            the plan, build spec, data notes, audit, AI use
```

## Data and credits

NISAR L2 GCOV PROVISIONAL (NASA-ISRO, via ASF DAAC); OPERA DSWx-S1, DSWx-HLS and RTC-S1 (NASA JPL, via PO.DAAC and ASF); HLS (Landsat 8 and 9, Sentinel-2B and 2C); ESA WorldCover 2021; JRC Global Surface Water; Copernicus GLO-30 DEM and HAND; GHSL built-up surface; basemap by OpenFreeMap with OpenStreetMap data. Full list with links: [`CITATIONS.md`](CITATIONS.md).

## License and AI use

**Development Notes:** The team directed the plan and made the key scientific decisions, including the choice of optical referee, calibration offsets, and validation criteria. An AI coding assistant was used to accelerate development for UI scaffolding, writing test harnesses, and debugging the pipeline. 