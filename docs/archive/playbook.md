> **Superseded on 3 Nov 2026** by [../overview.md](../overview.md) and [../build-spec.md](../build-spec.md). Kept for the record; the project is no longer called Wallflower, and several methods here changed after the audit ([../audit.md](../audit.md)).

# Playbook: the next eleven days and the 39 hours

Times are your local event's time zone. The submission deadline is 11:59 PM **local event time** on Sunday 15 Nov, so confirm which event the team owner is registered at.

## Before the event

The FAQ asks teams to start the actual work when the hackathon begins. So this list covers accounts, data, setup and reading. Code that becomes part of the submission waits until 9:00 AM Saturday. The scripts in `prep/` are reconnaissance tools; list them under external resources if you use them during the event.

### By Thursday 5 Nov

- [ ] Everyone registered, assigned to the same local event, on the team's Members tab, and not waitlisted. Teams are 1 to 6 people.
- [ ] Everyone has a NASA Earthdata login ([urs.earthdata.nasa.gov](https://urs.earthdata.nasa.gov)). One account covers ASF, PO.DAAC and LP DAAC.
- [ ] One person registers on ISRO's [Bhoonidhi](https://bhoonidhi.nrsc.gov.in) and searches for S-band GCOV over the Gandak on 28 Sep around 13:07 UTC and over north Bihar on 9 Sep around 12:58 UTC. Write down what exists.
- [ ] Ask your local lead two questions in writing: is cited pre-event reconnaissance tooling acceptable, and does the local event have its own rules on AI tools? (The submission form asks you to disclose AI use either way.)

### By Sunday 8 Nov: the go/no-go checks

- [ ] `python prep/download.py --role lead-pre,lead-post --out downloads` (about 10 GB). Open both files in QGIS or a throwaway notebook. Does HH darken along the Gandak on 28 Sep where the Sentinel-2 image of 29 Sep shows water?
- [ ] Look at the `mask` layer across the dark stripes. No-data or low signal?
- [x] OPERA water maps exist for the Sentinel-1 and optical (Sentinel-2, Landsat 8) passes around both Gandak dates (checked 3 Nov, listed in `data/manifest.csv`).
- [ ] Delete the throwaway notebook. The point was to look, not to build.

If the first check fails, call it early. The fallback is the Gandak ascending track (26, 40 MHz) or Assam, and `docs/data.md` lists both.

### Monday 9 to Friday 13 Nov

- [ ] Download the rest: `python prep/download.py` with no filters pulls every row in the manifest (about 40 GB of NISAR plus the reference tiles; add `--match _B01_WTR.tif,_B03_CONF.tif` for DSWx to skip the other layers). Skip the `stretch` rows unless someone owns Bangladesh.
- [ ] Ancillary layers for both frames (roughly 81.9 to 87.2°E, 25.4 to 28.2°N): Copernicus GLO-30 DEM, a HAND layer derived from it (ASF publishes one), ESA WorldCover, JRC Global Surface Water occurrence, GHSL built-up surface.
- [ ] Environment on the machine with the 3090: conda or mamba with `gdal rasterio rioxarray xarray h5py geopandas scikit-learn matplotlib`. Install [DSWX-SAR](https://github.com/opera-adt/DSWX-SAR) from source per its README (it warns that pip installs break on GDAL; on Windows use WSL2). Confirm `dswx_ni.py --help` and `dswx_s1.py --help` run. Don't process anything yet.
- [ ] Hosting test: an empty GitHub Pages site deploys and loads on a phone. Pages caps a site at about 1 GB, which decides your display resolution (40 to 60 m tiles will fit).
- [ ] Read: GCOV product spec (layers, `mask` values), DSWx ATBD sections on thresholds and inundated vegetation, ASF's provisional known issues.
- [ ] Pick the name. Assign roles.
- [ ] **Friday night:** the 2026 submission and judging guides come out on 13 Nov. Read both. If the demo format or criteria changed, adjust the storyboard before you sleep.

## Roles

| Role | Owns | Saturday deliverable |
|---|---|---|
| **Radar** | GCOV reading, common grid, masks, detectors, DSWx-NI baseline | Gandak flood maps by 18:00 |
| **Truth** | Reference mosaics, stable-optical-water mask, all scoring, trust model, statistics | H0 table by 18:00 |
| **Map** | Tiles, web app, hosting | Live URL with real layers by 18:00 |
| **Story** | Project page, physical-driver text, citations, video, subtitles | Page skeleton and storyboard by 12:00 |

With three people, Story merges into Map after Saturday. With five or six, add a second Radar on north Bihar from the start, and a Bangladesh owner if anyone is left.

## The 39 hours

| When | Radar | Truth | Map | Story |
|---|---|---|---|---|
| **Sat 9:00 to 9:30** | Kickoff together. Create the Space Apps project page. Re-read the result slots in [concept.md](concept.md). | | | |
| 9:30 to 12:00 | Read HH, HV and mask for 16 and 28 Sep; same grid, dB, union of both masks; log-ratio map | Mosaic DSWx-S1 and DSWx-HLS tiles onto the NISAR grid; stable-water mask from the two optical passes; permanent water from pre dates | Map skeleton: swipe, layer toggles, first deploy | Page sections; physical-driver paragraph; citation list started |
| **12:00 checkpoint** | Does the log-ratio map show the flood? If not, everyone helps Radar until it does. | | | |
| 12:00 to 18:00 | Two-sided detector (darkening plus HH brightening); DSWx-NI baseline, timeboxed to 2 h | H0 scores with block bootstrap; H1 HAND test | Tile pipeline; real Gandak layers live | Draft summary; capture screenshots |
| **18:00 checkpoint** | H0 and H1 numbers exist. Decide the headline: hidden water if H1 holds, otherwise open-water head-to-head plus trust. | | | |
| 18:00 to 24:00 | North Bihar pair through the same pipeline | Run DSWx-S1 on north Bihar RTC bursts, both dates, timeboxed to 3 h; trust features on Gandak | Time-series animation | Storyboard frames from the live app |
| Night | Sleep in shifts. Nobody works past 3:00 without sleeping first. | | | |
| Sun 8:00 to 13:00 | Failure gallery: stripes, urban, sand bars | Trust model Gandak → north Bihar; AUROC, risk-coverage, recall@K | Trust layer, check-first list, click panel | Record the app; first video cut |
| **13:00 feature freeze** | From here on: bug fixes, numbers and words only. | | | |
| 13:00 to 19:00 | Methods text, limits box | Final numbers into the page | Private-window and phone test of every link | Video to 30 s with English subtitles; NASA data field; references; AI-use field |
| 19:00 to 21:00 | Buffer. **Submit by 21:00.** | | | |

## If something breaks

| If, by | Then |
|---|---|
| DSWX-SAR won't install by Fri 13 Nov | Baseline becomes a Kittler-Illingworth threshold written during the event (about an hour). Say so in the methods. |
| The log-ratio shows no flood by Sat 12:00 | Check dB conversion, the mask, and that you're comparing HH to HH. If it's real, switch to the Gandak ascending pair (1 Oct). |
| The H1 rates are indistinguishable at Sat 18:00 | Drop hidden water from the headline. Lead with H0 and trust. Keep a physics panel explaining why L-band didn't add much here; that is still a finding. |
| North Bihar DSWx-S1 run fails by Sat 24:00 | Use OPERA's DSWx-S1 from 12 Sep (+59 h, recession) and say so, or hold out the eastern half of the Gandak frame instead. |
| S-band isn't accessible | It never enters the headline. One line in "future work." |
| Tiles exceed hosting limits | Drop display resolution to 60 m. The analysis resolution doesn't change. |
| The video runs over 30 s | Cut shot 1. The app shows the flood anyway. |

## Submission checklist

From the 2025 guide; re-check against the 2026 version on 13 Nov.

- [ ] Project name and high-level summary (what you built, how it answers the challenge, why it matters). Lead with the result slots.
- [ ] Demo link: a video of 30 seconds or less with English subtitles, public, no login.
- [ ] Final project link: the live app, public, no login, tested in a private window.
- [ ] Detailed description: tools, languages, methods, limits.
- [ ] NASA data: NISAR L2 GCOV PROVISIONAL (scene IDs), OPERA DSWx-S1, DSWx-HLS, RTC-S1, HLS.
- [ ] Other data and resources: ESA WorldCover, JRC surface water, Copernicus DEM, GHSL, DSWX-SAR code, the `prep/` scripts. Cite everything.
- [ ] AI tools: disclose which ones and how they were used. No AI-generated images or video in the submission.
- [ ] No recognizable names, voices or faces of anyone under 18.
- [ ] Every team member listed on the Members tab.
- [ ] The app stays online through January 2027, when global winners are announced.
