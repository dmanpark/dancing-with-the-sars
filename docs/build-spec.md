# Dancing with the SARS: Build spec and plan

Version 3, 3 Nov 2026. Companion to [overview.md](overview.md). Version 3 puts the interactive app first: the Map role becomes App, the app gets a listening step, and claims 3 and 4 move to Tier 3. The audit fixes from version 2 ([audit.md](audit.md)) all stand. Setup and preliminary tests that check this spec against real files: [../prompts/setup.md](../prompts/setup.md).

What each role builds, in what format, with which fixed numbers, and when it hands off. It is decided before kickoff so Saturday goes to building, not debating. There is no code in it.

## Decisions fixed before kickoff

We write these into the methods now and do not change them after seeing any claim number. If one must change, the project page says which and why. Changes that come out of the preliminary tests go in the log at the end of this file, before kickoff.

**Grid and signal**

| Decision | Value | Why |
| --- | --- | --- |
| Analysis grid | One per event: the lead post-event file's own projection and grid (Gandak 28 Sep, north Bihar 9 Sep), averaged 2 × 2 from 20 m to 40 m | Cuts speckle; every pair on the same track and frame shares the grid without resampling |
| Radar channels | NISAR HH and HV from frequency A (20 MHz); frequency B unused. Sentinel-1 VV and VH from OPERA RTC-S1 | ASF reports larger calibration errors on frequency B |
| Averaging | Average in linear power, then convert to dB. Sentinel-1 RTC bursts are mosaicked onto the grid the same way | Averaging dB values biases dark water |
| Valid pixel | Valid in every date's mask that the comparison uses, slope ≤ 10°, not permanent water | The plain is flat; steep pixels sit in the Siwalik foothills where layover lives |
| Permanent water | JRC occurrence ≥ 80%, or water in both pre-event optical maps | Scores only water the flood added |
| Calibration rule | On stable ground, take the median HH log-ratio and the median HV log-ratio of the pair. If either is more than 0.5 dB from zero, subtract it from that channel's log-ratio. Applies to every pair, Sentinel-1 included | Quad-pol and dual-pol dates may not share a calibration |
| Stable ground | Valid, slope ≤ 10°, JRC occurrence 0, not water in any reference map of that event, and either HAND > 15 m or GHSL built-up ≥ 0.5 with HAND > 5 m | Ground the flood could not reach; towns on low ground brighten when flooded, so they are left out |
| If the offset varies | When the 10th to 90th percentile range of per-tile medians (10 km tiles with at least 1,000 stable pixels) exceeds 0.5 dB, subtract per-tile offsets interpolated between tile centers instead, and also run claim 1 on 4 Sep → 28 Sep (both dual-pol) as a check | One number cannot fix a gradient across the swath |

**Detection**

| Decision | Value | Why |
| --- | --- | --- |
| Dark-water threshold | Kittler-Illingworth on 10 km tiles (250 × 250 pixels) that are at least half valid and pass a bimodality test: a two-component Gaussian mixture on the tile's dB values with Ashman D > 2 and the smaller component at least 5% of the tile. The scene threshold is the median of the passing tiles' thresholds, computed per channel and per date | Water is a few percent of a frame, so a scene-wide histogram has no second mode; DSWx selects bimodal tiles the same way |
| Too few bimodal tiles | Fewer than 5 passing tiles: drop the dark-water condition and use the log-ratio cut alone, stated in the methods | The threshold would rest on too little |
| Open-water rule | Co-pol log-ratio ≤ −3 dB and post-event co-pol below its dark-water threshold. NISAR uses HH, Sentinel-1 uses VV | A standard change cut plus a scene-adaptive dark threshold |
| Two-sided detector, open water | The open-water rule plus post-event cross-pol below its own threshold (HV for NISAR, VH for Sentinel-1). **This is the primary method for claim 1, on both sensors** | Named before any score, so we cannot pick the best-looking variant afterwards |
| Two-sided detector, flooded vegetation | NISAR only: HH log-ratio ≥ +3 dB and HH log-ratio minus HV log-ratio ≥ 2 dB | Double bounce raises HH far more than HV |
| Never a detector input | HAND and land cover | Claim 2 tests the detector on low ground, so using HAND inside would rig the test |

**Scoring**

| Decision | Value | Why |
| --- | --- | --- |
| New water (optical referee) | Water in both post-event optical maps, both clear, not permanent, and not water in any clear pre-event map; the pixel needs at least one clear pre-event map | Neither radar gains from timing |
| Stable dry (optical referee) | Not water in both post-event optical maps, both clear | The negatives for claim 1 |
| Flooded-vegetation flags in claim 1 | Count as not open water | Claim 1 is about open water; the referee cannot see under canopy |
| Claim 1 margin | NISAR's two-sided open-water F1 minus Sentinel-1's on the same rule. Non-inferior if the lower end of the paired 95% interval is at or above −0.05 | A margin fixed now, so a near-tie is not spun either way |
| Claim 2 pixels | Valid on all four dates (23 Aug, 4 Sep, 16 Sep, 28 Sep), WorldCover tree cover (10), shrubland (20) or herbaceous wetland (90), HAND < 2 m, and DSWx-S1 of 29 Sep 00:18 not masked and showing neither open water nor inundated vegetation. Cropland (40) gets the same numbers in its own row | The same pixels in both intervals, and only where C-band said dry |
| Claim 2 primary test | Flooded-vegetation flags on 16 → 28 Sep minus flags on 23 Aug → 4 Sep, on those pixels, in km² (0.0016 km² per pixel). Fails if the interval includes zero | Crop growth and wet soil show up in both intervals and cancel; early-September flooding in the control makes the excess conservative |
| Claim 2 secondary test | Within each land-cover class: flag rate at HAND < 2 m minus at HAND > 15 m, for the flood pair and the control pair, and the difference between the two. Dropped for any class where high-HAND, gentle-slope pixels are under 5% of the class's valid pixels | On this plain, high gentle ground is scarce and mostly hill forest |
| Claim 3 fit (Tier 3) | North Bihar. Target: the NISAR two-sided open-water decision disagrees with the C-band reference's new-water decision (our DSWx-S1 run, 38 minutes before NISAR). Classes grassland (30), cropland (40), bare (60), water (80); pixels NISAR flags as flooded vegetation are left out | C-band is trustworthy on open water away from canopy |
| Claim 3 test (Tier 3) | Gandak, once. Same target, scored against the optical referee on its new-water and stable-dry pixels, same classes. Headline: AUROC of (1 − trust) minus AUROC of the raw signal (the HH log-ratio's distance from −3 dB, closer meaning more likely wrong). Fails if the paired interval includes zero | Grading against C-band on the test event would count real hidden water as NISAR errors |
| Claim 4 cells (Tier 3) | 12 × 12 pixels (480 m) with at least half their pixels scoreable by the optical referee. A flooded settlement has at least 10% of its scoreable pixels new water and GHSL built-up ≥ 5% | Small enough to send one team to |
| Claim 4 test (Tier 3) | Gandak. Hits among the first 50 cells for mean P(water) × built-up, minus hits for NISAR log-ratio flood share × built-up. Fails if the paired interval includes zero | Recall at 50 is capped by the number of flooded cells; hits in 50 is what a district team would feel |
| Statistics | 5 km blocks (125 × 125 pixels), 1,000 bootstrap draws resampling blocks with replacement, 95% percentile intervals, seed 2026. Every comparison is paired: both methods are scored on the same resampled blocks in each draw | Neighboring pixels are not independent |
| Held-out rule (Tier 3) | The trust model is fit and chosen on north Bihar only. Gandak's optical referee enters claim 3 once, in one final run, and its numbers are reported as they come | A test you can rerun is not a test |

**The app**

| Decision | Value | Why |
| --- | --- | --- |
| Listening grid | HH and HV dB for the seven track-149 dates on a 240 m grid (6 × 6 analysis pixels, averaged in linear power). A cell less than half valid on a date is silent on that date | Fine enough to tap a field, small enough to ship (about 20 MB for the frame) |
| Listening encoding | uint8, value = round((dB + 40) × 4), so 0.25 dB steps from −40 dB; 255 means no data. Chunks of 128 × 128 cells, one file each, plus an index with the grid transform, dates and chunk size | The browser fetches only the chunk under the tap |
| Sound | One beat per date, seven beats, about 0.45 s each. HH is a plucked voice, HV a softer voice an octave lower. Pitch rises with dB on a pentatonic scale (HH −30 to 0 dB, HV −35 to −5 dB); loudness rises with it too | Open water drops low and quiet; flooded vegetation jumps up in HH only, which you can hear |
| Sound rules | Starts only when the user taps Listen; a mute control is always visible; never autoplays. The chart of the same values always shows | Sound supports the chart, never replaces it |
| What may be tuned | Tempo, timbre and the exact scale may be tuned by ear on Saturday. The mapping must stay monotonic (more backscatter, higher pitch) in both channels | Tuning for sound is presentation; it can't make the data say something else |
| Hidden-steps layer | Claim 2's pixels that the two-sided detector flags as flooded vegetation on 16 → 28 Sep, shown as their own class. Labeled "evidence, not verified" wherever it appears | The layer shows exactly what claim 2 counts |
| Tour state | Each step sets the view, layers and card text, and is kept in the URL (`#step=3`) | Judges and the video can link to a step directly |

## File contracts

Roles hand each other files, never notebooks. Every raster is a Cloud-Optimized GeoTIFF on its event's analysis grid, one band. Names:

- one date: `{event}_{yyyymmdd}_{layer}.tif`
- a pair: `{event}_{pre}-{post}_{layer}.tif`, dates as yyyymmdd
- event-wide: `{event}_{layer}.tif`

Events are `gandak` and `nbihar`. Classes use one code set everywhere: 0 dry, 1 open water, 2 flooded vegetation, 3 permanent water, 255 unknown or no data.

| File | Made by | Used by | Contents | Ready by |
| --- | --- | --- | --- | --- |
| `grid_{event}.json` | Radar | everyone | CRS, transform, width and height of the analysis grid | Gandak Sat 10:00; north Bihar (Tier 3) Sat 14:00 |
| `*_hh_db.tif`, `*_hv_db.tif` | Radar | Truth, App | γ⁰ in dB, float32, nodata −9999, one per date | Gandak pair Sat 12:00; series Sat 22:00; north Bihar (Tier 3) Sun 10:00 |
| `*_vv_db.tif`, `*_vh_db.tif` | Truth | Truth, App | Sentinel-1 RTC γ⁰ in dB, Gandak 17 and 29 Sep | Sat 12:00 |
| `*_valid.tif` | Radar | everyone | 1 valid, 0 not, per pair (all masks it uses, slope rule) | Sat 12:00 |
| `*_lr_hh.tif`, `*_lr_hv.tif` | Radar | Truth, App | Post minus pre in dB after the calibration rule, 3 × 3 median | Sat 12:00 |
| `*_calib.json` | Radar | Truth | Per pair: HH and HV medians on stable ground, stable pixel count, whether subtracted, per-tile spread | Sat 12:00 |
| `*_thresholds.json` | Radar, Truth | Truth | Per date and channel: tiles tested, tiles passing, each tile's threshold, the scene threshold | Sat 12:00 |
| `*_flood_{lr, twosided, dswxni}.tif` | Radar | Truth, App | NISAR class maps, uint8, codes above. Gandak: the lead pair and the control pair (23 Aug → 4 Sep) | Sat 18:00 |
| `*_flood_{s1lr, s1twosided}.tif` | Truth | Truth, App | Sentinel-1 class maps on the same rules, Gandak 17 → 29 Sep | Sat 15:00 |
| `{event}_{hand, slope, landcover, builtup, jrc}.tif` | App | everyone | Ancillary layers on the grid; built-up and JRC as fractions 0 to 1 | Gandak Sat 11:00; north Bihar (Tier 3) Sat 15:00 |
| `*_ref_optical.tif` | Truth | Truth, App | Optical referee, class codes (Gandak only) | Sat 12:00 |
| `*_ref_c.tif` | Truth | Truth, App | C-band reference, class codes (Gandak: OPERA DSWx-S1; north Bihar: our DSWx-S1 run) | Gandak Sat 12:00; north Bihar Sat 14:00 |
| `breach_sites.csv` | Story | Truth, App | Name, district, lat, lon, source link | Sat 12:00 |
| `gandak_hidden.tif` | Truth | App | The hidden-steps layer: 1 where claim 2 counts a flagged pixel, 0 elsewhere in claim 2's pixel set, 255 outside it | Sat 19:00 |
| `app/data/listen/` | Radar | App | The listening grid: `index.json` and `{col}_{row}.bin` chunks | Sun 01:00 |
| `*_trust.tif` (Tier 3) | Truth | App | 1 − P(error), float32 0 to 1 | Sun 11:00 |
| `cells_{event}.geojson` (Tier 3) | Truth | App | Top 2,000 cells with rank, score, flood and built-up fractions, trust, HH and HV change, HAND, land cover, a one-line reason | Sun 12:00 |
| `results.json` | Truth | App, Story | Every reported number with its interval, pixel count, time offset in hours and the calibration offsets used | Sun 13:00 |
| `app/tiles/*.pmtiles` | App | the app | Color-mapped raster tiles, zoom 6 to 12 | First set Sat 18:00 |

## Machines

The 3090 machine runs Radar's and Truth's jobs, with data on WSL2's ext4 disk (`~/dwts-data`), never on a Windows drive mounted under `/mnt/c`, which is many times slower for HDF5 reads. Outputs go to `~/dwts-out`, shared read-only over the local network. App and Story work on laptops from that share. The machine has 32 GB of RAM shared with Windows and Ubuntu gets about half, so the pipeline reads GCOV in row strips and keeps each process under 8 GB; close other heavy apps on Windows during the event.

## Radar

Radar turns NISAR files into dB layers, a valid mask and flood maps per pair. Steps 1 to 6 are Tier 1 and land by Saturday 18:00.

1. **Read.** From each GCOV file take HHHH and HVHV (γ⁰, linear power), the mask and the coordinate grid, all from frequency A. Expected paths are under `/science/LSAR/GCOV/grids/frequencyA/`; the exact paths and mask values come from preliminary test T2. Write `grid_gandak.json` from the 28 Sep file by 10:00.
2. **Average and convert.** Average 2 × 2 in linear power to 40 m, then take 10·log10. Write `*_hh_db.tif` and `*_hv_db.tif`. As soon as steps 1 to 3 work (by 13:00), start the series batch in the background: steps 1 and 2 for 6 Jul, 23 Aug, 4 Sep, 10 Oct and 22 Oct. The 22 Oct scene is 40 MHz, so average it to the same 40 m.
3. **Valid mask.** A pixel is valid when every date's mask in the pair says valid and slope is at most 10°. Write `*_valid.tif`. The swath-gap stripes fall out here.
4. **Log-ratios and calibration.** Post minus pre for HH and HV. Apply the calibration rule and write `*_calib.json`. Then a 3 × 3 median on the log-ratio only.
5. **Thresholds.** The dark-water threshold for post-event HH and HV, tile by tile as fixed above. Write `*_thresholds.json`.
6. **Flood maps.** The log-ratio baseline (open-water rule on HH) and the two-sided detector (open water and flooded vegetation). Neither HAND nor land cover enters. Run both on the lead pair (16 → 28 Sep) and the control pair (23 Aug → 4 Sep).
7. **Baseline: DSWx-NI** (Tier 2, 2-hour timebox). Run `dswx_ni.py` from DSWX-SAR with its default NISAR settings on 16 Sep and 28 Sep. New water is water on 28 Sep and not on 16 Sep. If it fails, record why and move on.
8. **North Bihar** (Tier 3). Steps 1 to 6 on 28 Aug → 9 Sep with the cuts unchanged; thresholds are recomputed per scene, as the method defines. Steps 1 and 2 for 29 Jun and 11 Jul (trust features).
9. **After the breaches** (Tier 3). Steps 3 to 6 for 16 Sep → 10 Oct on track 149, for the breach-site check.
10. **Listening grid** (Tier 2, Sat 18:00 to Sun 01:00). From the seven series dates, write `app/data/listen/` as fixed in the app decisions above. Check one chunk by decoding it and comparing three cells with the dB rasters.
11. **Failure gallery.** For 20 flagged flooded-vegetation pixels per land-cover class, and 10 places where NISAR and the optical referee disagree on open water, export HH and HV across the seven dates as a small CSV, for step 5 and the methods.
12. **Phase test** (Tier 3). Only if preliminary test T2 found the HHVV covariance term in the quad-pol files. On 16 Sep and on the partial 10 Oct quad-pol frame, compute the HH-VV phase after applying ASF's documented 59° correction exactly as the known-issues page specifies. Compare the circular-mean phase change on pixels flagged as flooded vegetation in step 9 against unflagged vegetated pixels at HAND < 2 m.

## Truth

Truth owns every number that goes on the project page. Each one lands in `results.json` with its interval, pixel count and time offset in hours.

1. **North Bihar C-band reference, first** (Sat 9:05, for Tier 3). It costs nothing to start, so start it whatever happens later. Start `dswx_s1.py` in the background on the 56 Sentinel-1 bursts of 28 Aug and of 9 Sep, with the run configuration tested in T10. New water is open water on 9 Sep and not on 28 Aug. Check on it at 11:00 and 13:00. If it has failed by 14:00, use OPERA's DSWx-S1 of 12 Sep (59 hours after NISAR) or the Sentinel-1 two-sided rule, and say which.
2. **Optical referee** (Gandak). Mosaic each DSWx-HLS pass onto the grid by majority, keeping three states: water, not water, unknown (cloud, shadow, snow, fill, or partial surface water). The four maps are: pre −8 h (Sentinel-2B, 16 Sep), pre +16 h (Landsat 8, 17 Sep), post −8 h (Sentinel-2C, filled with Landsat 8 where Sentinel-2C is unknown), post +16 h (Sentinel-2B, 29 Sep). New water and stable dry follow the fixed definitions above.
3. **Gandak C-band.** OPERA DSWx-S1 of 17 Sep 00:18 and 29 Sep 00:18 in the same three states, plus its inundated-vegetation class kept as its own code for claim 2. Mosaic the RTC-S1 bursts of the same passes to `*_vv_db.tif` and `*_vh_db.tif`, then run Radar's step 4 to 6 code on them for `*_flood_s1lr.tif` and `*_flood_s1twosided.tif`.
4. **Claim 1, open water.** On pixels valid for both NISAR and Sentinel-1, not permanent, and new water or stable dry in the optical referee: precision, recall, F1 and IoU of new water for the NISAR log-ratio, the NISAR two-sided detector, the Sentinel-1 log-ratio, the Sentinel-1 two-sided rule, DSWx-S1 and DSWx-NI, all on the same pixels. The headline is the paired F1 difference, NISAR two-sided minus Sentinel-1 two-sided, against the −0.05 margin. Add one row per land-cover class.
5. **Claim 2, hidden steps.** The primary excess in km² with its interval, per class row (10, 20 and 90 together, then cropland alone). Then the secondary HAND contrast per class, or the note that the 5% rule dropped it. Write `gandak_hidden.tif` for the app.
6. **Step 5 content** (Sat 18:00 to 24:00). The two headline numbers in plain words with their intervals, the pixel counts behind them, and three examples from Radar's failure gallery with one sentence each on why NISAR got them wrong.
7. **Claim 3, trust** (Tier 3). Features per pixel: slope, HAND, land-cover class, distance to the nearest invalid pixel (swath gaps), HH spread (standard deviation of HH dB across every 20 MHz pre-event date since 17 Jun on that track, each date offset-corrected to the post-event date by the calibration rule: Gandak 6 Jul, 23 Aug, 4 Sep, 16 Sep; north Bihar 29 Jun, 11 Jul, 28 Aug), pre-event HH, the HH log-ratio's distance from −3 dB, the HV log-ratio, and incidence angle if the files carry it. Fit a logistic regression and scikit-learn's HistGradientBoostingClassifier on 200,000 north Bihar pixels drawn evenly across 5 km blocks; keep whichever scores better in 5-fold cross-validation grouped by block. Trust = 1 − P(error). Then score Gandak once: the AUROC difference with its paired interval, a risk-coverage curve, and the error rate at 50%, 80% and 100% coverage.
8. **Claim 4, check first** (Tier 3). P(water) per pixel is the trust where NISAR says open water and 1 − trust where it says dry; flooded-vegetation pixels are left out of the cell mean. On Gandak, rank cells six ways: mean P(water) × built-up (ours), NISAR log-ratio flood share × built-up (the baseline to beat), mean HH change, built-up share alone, DSWx-S1 new-water share × built-up, and DSWx-NI share × built-up if it ran. Report hits at 25, 50 and 100 cells for each, scored by the optical referee; the headline is the paired difference at 50. In each bootstrap draw, rank the cells of the resampled blocks and count the hits. North Bihar's version, scored by its C-band reference, is reported as secondary and labeled as the event the trust model was fit on.
9. **Breach-site check** (Tier 3). On 16 Sep → 10 Oct, the rank percentile of each cell holding a site in `breach_sites.csv`. Reported as a check, not a score.
10. **Write** `results.json` (Tier 1 numbers by Sat 18:00, updated as more land), and in Tier 3 `*_trust.tif` and `cells_{event}.geojson`.

## App

The app is a folder of static files that GitHub Pages serves as is: no server, nothing that can go down before judging ends in January. It is the thing judges remember, so it gets Saturday evening and all of Sunday morning.

- **Ancillary layers first** (Sat 9:30 to 11:00). Onto `grid_gandak.json`: HAND from the Copernicus GLO-30 HAND dataset and slope from GLO-30 itself (computed in a metric projection), ESA WorldCover 2021 by nearest class, GHSL built-up surface and JRC occurrence as averaged fractions. All source files are downloaded before kickoff. Then deploy the empty app shell by 12:00.
- **Stack.** `app/index.html`, `app/app.js` and `app/style.css`, loading MapLibre GL JS, the pmtiles library and the MapLibre compare plugin for the slider from a CDN at pinned versions. Sound and the small charts use the browser's own Web Audio API and SVG, no extra libraries. The basemap is a light vector style whose license allows this use, with its attribution on screen.
- **Layout.** The map fills the screen. The step card sits at the bottom on a phone (under 40% of the height, swipe up for more) and at the left on a laptop. Next, Back, the step number and "Explore" are always visible. Text on each card is three sentences at most.
- **Step 1, the dance.** HH for the seven track-149 dates as raster layers, cross-faded at about one date per second, with the date large in the corner. Plays once on arrival, then waits for a tap. Respects the reduced-motion setting by showing a date slider instead.
- **Step 2, two radars.** The compare slider with Sentinel-1's two-sided flood map (29 Sep 00:18) on the left and NISAR's (28 Sep 13:07) on the right, both over the 28 Sep HH image so the ground is recognizable. Open water in one hue; NISAR's flooded vegetation in a second hue that stays distinct for color-blind viewers. The card names both times.
- **Step 3, the hidden steps.** `gandak_hidden.tif` alone, in the second hue, labeled "evidence, not verified," with the km² figure from `results.json`. Story's two diagrams sit in the card: open water as a mirror (dark in HH and HV); water under trunks bouncing the signal back (bright in HH, much less in HV).
- **Step 4, listen.** Tapping the map fetches the listening chunk under the finger and draws HH and HV across the seven dates as a small chart, with the flood date marked. The Listen button plays the series with the mapping fixed in the decisions above. The card suggests three places to try, picked on Saturday night from Radar's failure gallery and the hidden-steps layer: one open-water field, one flooded grove, one dry town.
- **Step 5, how we know.** The optical referee's new water as an outline, both headline numbers with their intervals in plain words, and a toggle between "naive difference" (raw HH log-ratio, swath-gap edges lighting up) and "what we trust" (the valid mask applied, gaps hatched). Then the "What this can't tell you" box, word for word.
- **Explore.** Every layer with a legend and a one-line description; the breach villages from `breach_sites.csv` as labeled pins.
- **Raster tiles.** Each COG is color-mapped to 8-bit RGBA and written as MBTiles with GDAL (zoom 6 to 12, about 35 m per pixel at the top zoom), then converted with the `pmtiles` command-line tool. Continuous layers (HH dB) use WEBP tiles; class layers use PNG8, which stays small and keeps class colors exact. T12 measures both. Every file stays under GitHub's 100 MB limit; above that, display the layer at 60 m.
- **Colors.** HH in grayscale on one fixed stretch for every date (−25 to 0 dB), so the animation shows change and not contrast. Swath gaps as hatched polygons drawn from the invalid mask.
- **Budget.** The whole site under 600 MB (GitHub Pages caps sites at 1 GB). The first view opens on the Gandak at zoom 9 with one layer and should draw in under 3 seconds on a phone.
- **Release.** Deploy through a GitHub Actions Pages workflow, with `.nojekyll` in the site root. Code lives on `main`; tiles and the listening grid live on an orphan `tiles` branch that is force-pushed, so the repo history does not grow with every tile set, and the workflow checks out both. Tiles are pushed at most twice (Sat 18:00 and Sun 13:00). The first deploy happens Saturday morning, so every later push is a real deploy, never a first one at 20:00 Sunday.
- **Tier 3, check first.** A sixth step reading `gandak_trust.tif` tiles and `cells_gandak.geojson`: the ranked list, and a click panel with each cell's rank, HH and HV change, HAND, land cover, trust and one-line reason.

## Story

Story owns what a judge reads, watches and hears, and keeps the citation list honest from the first hour.

- **A human voice** (before the event). One line from someone in Bihar, a flood-response official or an NGO, on what current flood maps miss, with their permission to quote them by name and role. It goes on the project page and, if it fits, in the video's captions. Nobody under 18.
- **Breach sites** (Sat 12:00). Look up each village named in the 1 Oct reports (Khairatwa, Phuliyakhad, Bathuwaria, Golaghat, Areraj, Sheetalpur) on OpenStreetMap and write `breach_sites.csv` with the source link per row. A site that cannot be placed within about 1 km is left out and listed as such. Confirm the breach times before the video says anything about timing.
- **The two diagrams** (Sat 18:00). Drawn by hand as SVG, no AI images: open water as a mirror, and the double bounce off trunks. One sentence under each. The ±3 dB and +2 dB cuts are described as fixed in advance on physical reasoning, because we found no citable L-band flood threshold.
- **Step card text** (Sat 24:00). Three sentences at most per step, written for someone who has never heard of radar. Truth checks every number in them.
- **The sound** (Sat evening, with App). Listen to the three suggested places and to ten random taps. If any of them sounds wrong for what the chart shows, or grating, App changes tempo or timbre within the rules, or the sound stays off by default.
- **Project page**, field by field from the 2025 guide (recheck on 13 Nov):
  - Name: Dancing with the SARS: The Hidden Steps.
  - Summary: the two result lines first, then two sentences on the flood and the blind spot, then the human voice.
  - Demo link: the video. Final project link: the app.
  - Details: tools, methods, the fixed decisions above, the limits box.
  - NASA data: NISAR L2 GCOV PROVISIONAL with every scene ID, OPERA DSWx-S1, DSWx-HLS and RTC-S1, HLS.
  - Other data: ESA WorldCover, JRC Global Surface Water, Copernicus GLO-30 and its HAND, GHSL, DSWX-SAR, the `prep/` scripts, the news reports.
  - AI use: which tools were used before and during the event, and for what.
- **Video.** 30 seconds or less, 1080p, English subtitles burned in, screen-recorded from the live app with its real sound, public with no login. No AI-generated images or video, and no recognizable names, voices or faces of anyone under 18. Say "SAR, synthetic aperture radar" once. Both numbers come from Gandak. If a breach village appears, the caption must not suggest the breach shows on 28 Sep, since the breaches came the next night.
- **Citations.** One file, `CITATIONS.md`, appended the moment anyone uses a source. Story checks every link on Sunday afternoon.

## Done means

A tier is done when every box is ticked, not when the code runs. Tick them during the event.

**Tier 1, by Sat 18:00 (video and page by Sun 19:00)**

- [ ] HH and HV in dB for 16 and 28 Sep on the grid, with the valid mask; the Gandak channel is the darkest feature on both dates.
- [ ] Calibration offsets and threshold tiles recorded for the lead pair and the control pair.
- [ ] Log-ratio and two-sided flood maps exist for both pairs, and the lead pair's flooded area along the Gandak lines up with Sentinel-2 on 29 Sep side by side.
- [ ] Claim 1 table: F1 with interval, precision, recall and pixel count for each method on the same pixels, and the paired difference against the margin.
- [ ] Claim 2: the excess km² with its interval for vegetation and for cropland, and the secondary contrast or its drop note.
- [ ] The app loads on a phone with steps 1 and 2 working on real tiles.
- [ ] The video is 30 seconds or less with subtitles; both links open in a private window.

**Tier 2, by Sun 13:00**

- [ ] Step 3 live: the hidden-steps layer, the km² figure and both diagrams.
- [ ] Step 4 live: tap, chart and sound work on a phone, with the mute control; three suggested places in the card.
- [ ] Step 5 live: both numbers with intervals, the naive-difference toggle and the limits box.
- [ ] The tour works end to end on a phone, and every step can be linked to.
- [ ] DSWx-NI is in the claim 1 table, or its failure is written in the methods.

**Tier 3, only if Tier 1 was done at Sat 18:00**

- [ ] North Bihar flood maps and its C-band reference exist.
- [ ] Claim 3: the AUROC difference with its interval, and the risk-coverage plot.
- [ ] Claim 4: hits at 25, 50 and 100 for all rankings, the paired difference at 50, and the breach-site percentiles.
- [ ] The Check first step is live in the app.
- [ ] The HH-VV phase test result, or the note that the files lack the term.
- [ ] S-band hidden-water km² next to C-band and L-band.

## Unknowns to settle by Sun 8 Nov

This spec assumes a few things that only a downloaded file can confirm. Each maps to a preliminary test in [../prompts/prelim-tests.md](../prompts/prelim-tests.md) (started by [../prompts/setup.md](../prompts/setup.md)), and each has a fallback that keeps the plan intact.

| Assumption | Test | If it is wrong |
| --- | --- | --- |
| 20 MHz GCOV is posted at 20 m, and the 16 and 28 Sep grids align | T2, T3 | Change the averaging factor so the grid stays 40 m; resample the pre-event date if the grids are offset |
| Dataset paths for HHHH, HVHV and the mask | T2 | Nothing changes but the paths |
| What each mask value means, and whether the stripes are no-data | T4 | Adjust the valid rule in Radar step 3 |
| Quad-pol files carry the HHVV term | T2 | Tier 3 phase test dropped |
| The files carry incidence angle | T2 | Drop that one trust feature on both events |
| The quad-pol to dual-pol offset on stable ground is small or uniform | T5 | The calibration rule handles it; T5 reports which branch applies |
| At least 5 bimodal tiles per date and channel | T6 | The log-ratio cut alone, stated |
| The flood shows in the HH log-ratio along the Gandak | T7 | Check dB conversion, masks and channel matching; then the ascending pair |
| DSWx-S1 and DSWx-HLS class legends, including the inundated-vegetation code | T8 | Adjust the reference mapping in Truth steps 2 and 3 |
| RTC-S1 bursts mosaic onto the grid within a pixel of NISAR | T9 | Shift by the measured offset, stated |
| DSWX-SAR installs, and our `dswx_s1.py` run matches OPERA's own product | T10 | DSWx-NI dropped; the Sentinel-1 two-sided rule stands in for DSWx-S1 on north Bihar (Tier 3) |
| High-HAND gentle vegetated ground is at least 5% of each vegetated class | T11 | The secondary claim 2 test is dropped for that class |
| Tiles and the listening grid fit the size budget | T12 | Display at 60 m; listening grid at 480 m |
| ISRO has S-band scenes for 28 Sep and 9 Sep | Manual, on Bhoonidhi | Stretch goal dropped |

Settled on 3 Nov: north Bihar has two earlier 20 MHz scenes (29 Jun, 11 Jul) besides 28 Aug, and Gandak has 6 Jul, so the HH-spread feature works on both events. All are in the download list.

## Changes after the preliminary tests

Fill this in at the team review, before 14 Nov. Every change needs a reason tied to a test result, not to a claim number.

| Date | Decision changed | From | To | Test and reason |
| --- | --- | --- | --- | --- |
| 4 Nov 2026 | Claim 1 referee and pixel set (Truth steps 2 and 4; claim 1 rows of "Decisions fixed before kickoff") | New water and stable dry from the post −8 h and post +16 h optical maps; the head-to-head on pixels valid for NISAR and Sentinel-1 | First a check that uses no NISAR values: referee new water is water in both Landsat 9 (27 Sep) and Sentinel-2C (1 Oct), both clear, with JRC occurrence below 25%. If that gives at least 10,000 new-water pixels in the NISAR and Sentinel-1 overlap, the head-to-head stays, with that referee, stated as such. Otherwise claim 1 splits in two. **1a:** NISAR two-sided open water against the 29 Sep Sentinel-2B map alone (+16 h), western frame: F1 with its interval, plus the paired F1 difference against the HH-only log-ratio on the same pixels, which fails if the interval's lower end is below 0. **1b:** agreement between NISAR two-sided open water and DSWx-S1 new water in the eastern overlap, labelled "agreement, not accuracy". The video caption at 25 to 30 s and page line 2 report 1a. **Check result, 5 Nov:** 12,772 new-water and 232,716 stable-dry pixels in the NISAR and Sentinel-1 overlap, valid on both NISAR lead dates, so the head-to-head stays with the 27 Sep and 1 Oct referee, and 1a and 1b are not used | T8: the post −8 h pass is 100% fill inside the NISAR footprint, so the referee as specified has 0 pixels, and no pixel has NISAR, Sentinel-1 and a clear post-event optical map together. Follow-up A: the 27 Sep and 1 Oct pair with the pre-event maps gives 135 new-water pixels in the overlap. Decision 1 check (T8): 12,772 is 28% over the bar, 71.8% of that new water sits in 10 of 82 5 km blocks, so the block-bootstrap interval will be wide, and with no pre-event map the referee can count water that was there before the flood |
| 4 Nov 2026 | Optical referee for 1a (Truth step 2) | Two post-event maps, both clear | The 29 Sep Sentinel-2B map alone (+16 h), for 1a only (proposal 1). Not used, because the decision 1 check passed | T8: the post −8 h pass is all fill in the footprint; with the +16 h map alone the referee has 23,857 new-water and 3,089,384 stable-dry pixels valid on both NISAR dates, all in the western frame |
| 4 Nov 2026 | App step 5 (App section) | The optical referee's new water as an outline | The optical comparison in the western frame; at Bagaha, DSWx-S1's outline labelled "Sentinel-1's own map" | Follow-up A: no optical pass is clear at Bagaha (best 13.9% of the crop) |
| 4 Nov 2026 | Calibration rule ("If the offset varies") | Per-tile offsets interpolated between tile centres | One median offset per channel for each part of the post-event frame (upper single-subswath, lower four-subswath), computed separately for each pair from its own stable ground; no per-tile offsets. Claim 2 is also reported with the offsets shifted up and down by half the tile spread | T5: stable ground lies only in the northern third of the frame. Follow-up C: the HH offset changes sign between the two parts in both pairs (lead −0.33 and +0.34 dB, control −0.45 and +0.17 dB). Follow-up B: 4 Sep has the same two-part layout as 28 Sep |
| 4 Nov 2026 | Dark-water threshold (Radar step 5) | One threshold per scene from bimodal tiles; "valid" not defined for tiles | Computed per part of the frame; "valid" read literally, so permanent water is excluded | T6 and follow-up D: the passing tiles' second mode is water, flooded fields or a town, not the step between the parts, but the median thresholds of the two parts differ by 3.1 dB (HH) and 3.85 dB (HV) |
| 4 Nov 2026 | DSWx-NI baseline (Radar step 7) | Tier 2, 2-hour timebox | Dropped | T10 and follow-up F: it peaked at 13.3 GB, over the build's 8 GB per-process limit, and failed for want of a GLAD land-cover file its schema calls optional |
| 4 Nov 2026 | Claim 2 secondary test and wording | A secondary test per land-cover class; "under trees and wetland" on the page and in the video | The secondary test is dropped by the spec's own 5% rule; the page and the video say "under trees" | T11: high-HAND gentle ground is under 5% in every class (tree cover 4.74%, shrubland 3.67%, wetland 0%, cropland 0.16%), and shrubland and wetland cover only 32.5 and 68.3 km² of the frame, so claim 2's vegetation pixels are almost all tree cover |
