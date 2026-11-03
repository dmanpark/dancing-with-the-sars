# Hypotheses, experiment and schedule

## Three hypotheses, ranked

| | Hypothesis | Novelty | Feasible in 39 h | Impact |
|---|---|---|---|---|
| **H1** | L-band recovers flooding inside the areas C-band maps exclude | High (no NISAR flood evaluation found) | Partly: evidence, not an accuracy number | High |
| **H2** | A physics-based reliability map predicts detector errors on a held-out event better than the detector's own score | Medium | Yes | Medium |
| **H3** | Ranking cells by flood probability × exposure × reliability recovers more flooded, exposed cells under a fixed budget than trivial rankings | Medium (ALTIS is close) | Yes, once H2 exists | High for the demo |

Build H2 first because H3 depends on it, and pitch H1 because it is the NISAR-specific idea.

### H1: L-band sees under the canopy

**Claim.** On the 28 Sep Gandak pass, a two-sided L-band detector flags flooding in low-lying vegetated floodplain that GFM marks as excluded or dry.

**Detector.** Open water: HH and HV both darken against the 16 Sep scene. Flooded vegetation: HH brightens (trunk-water double bounce) and the HH/HV ratio rises. The 16 Sep quad-pol scene supplies the pre-flood double-bounce fraction from a Freeman-Durden decomposition, after ASF's 59° phase correction.

**Test that needs no flooded-vegetation labels.** Split vegetated pixels (WorldCover tree and shrub classes) by HAND: below 2 m and connected to the river versus above 15 m. Higher ground cannot flood, so its flag rate is the false-alarm rate from crop growth, soil moisture and wind. H1 survives only if the low-HAND flag rate is clearly above the high-HAND rate, with a block-bootstrap confidence interval that excludes zero difference.

**What kills it.** The two rates are indistinguishable, or the L-band flags line up with GFM's flood pixels and add nothing inside its exclusion mask.

This test cannot say how accurate the vegetated-flood map is, only whether the signal is there. Say that in the submission.

### H2: reliability that transfers

**Claim.** A reliability model trained on Gandak predicts where the NISAR detector disagrees with the Sentinel-1 reference on Bangladesh better than the detector's own confidence does.

**Features**, all physical and per pixel:

- incidence angle; local slope and a DEM-derived layover/shadow flag
- HAND
- WorldCover class
- distance to a swath-gap stripe in either date's `mask`
- pre-event temporal variability: standard deviation of HH across the PROVISIONAL cycles from 17 Jun to the pre date, which separates "always noisy" ground from real change
- number of looks
- pre-event backscatter level, because dark land (sand, tarmac, dry fields) mimics water

**Model.** Logistic regression first, gradient boosting second. Target: detector disagrees with the reference, scored only outside GFM's exclusion mask and with permanent water removed.

**Baselines for the error predictor.** The detector's own |log-ratio| margin from its threshold; the DSWx-NI CONF layer; GFM's likelihood where it applies.

**Metrics.** Error-prediction AUROC; risk-coverage curve and AURC when the lowest-reliability pixels are abstained from.

**What kills it.** AUROC on Bangladesh no better than the |log-ratio| margin.

### H3: a better inspection list

Grid both events to 500 m cells. A cell is "truly affected" if the reference shows new inundation and the GHSL built-up layer shows settlement in that cell.

Rank cells five ways and report recall@K for K = 25, 50 and 100:

1. raw change magnitude
2. exposure only (built-up area)
3. log-ratio flood fraction × exposure
4. DSWx-NI flood fraction × exposure
5. ours: P(flood) × exposure, with low-reliability, high-exposure cells pushed up as "verify first"

Bootstrap over 5 km spatial blocks for confidence intervals. Pixel-level random splits would leak spatial autocorrelation into the score, as the original doc warned.

This inherits every error in the reference, and "flooded and built-up" is not "damaged." Keep both caveats on the slide.

## Minimum viable experiment

Gandak only, end to end:

1. Subset and download HHHH, HVHV and `mask` for the 16 Sep and 28 Sep frames. Multilook both to a common grid.
2. Baselines: HH log-ratio threshold; DSWx-NI run from [opera-adt/DSWX-SAR](https://github.com/opera-adt/DSWX-SAR) on each date, with flood defined as water on 28 Sep that is not water on 16 Sep.
3. The two-sided detector from H1.
4. Score against GFM and DSWx-S1 for the 29 Sep Sentinel-1D pass, open water only, offset 11 hours.
5. H1 HAND-stratified test.
6. Reliability map and inspection ranking. Score them within Gandak using spatial blocks.

Bangladesh as a true held-out event is the stretch goal. If it is not done by Saturday midnight, drop it and say Gandak results are single-event.

## Schedule

| When | What |
|---|---|
| Tue 3 to Sun 8 Nov | The three go/no-go checks in [review.md](review.md). Earthdata logins for everyone. Install DSWX-SAR (conda; the README says pip is not recommended because of GDAL). Read the DSWx-NI code and the GFM layer definitions. |
| Mon 9 to Fri 13 Nov | Pull GFM and DSWx-S1 tiles for Gandak and Bangladesh. Download the GCOV subsets. Assign roles: one person on data and baselines, one on reliability and evaluation, one on the app, one on story and video. |
| Sat 14, 9:00 to 21:00 | Grid alignment, both baselines, two-sided detector, first scores against GFM |
| Sat 14 night | H1 test; reliability features; tile the layers for the app |
| Sun 15, 9:00 to 16:00 | H2 and H3 numbers; app wired to real tiles |
| Sun 15, 16:00 to 23:00 | Video, project page, references list. Submit with an hour to spare. |

## The app

Static, no backend. MapLibre GL with pre-tiled Cloud-Optimized GeoTIFFs or PMTiles, so a judge on bad Wi-Fi still sees it load. Layers:

- swipe between 16 Sep and 28 Sep HH
- new open water; flooded-vegetation candidates in a separate color
- reliability, with the swath-gap stripes drawn as hatched "do not trust" zones
- the GFM map from 11 hours later, for side-by-side comparison
- the ranked cell list; clicking a cell shows its HH and HV change, HAND, land cover and why its reliability is high or low

The stripes are worth a moment in the video. A naive difference image lights them up as change, and your system refuses to.

## Rules to check

I could only find the [2025 Participant Terms](https://spaceappschallenge.org/legal). They say nothing explicit about work started before the event. They do require you to cite every source you use, they define original content as content created for Space Apps, and NASA distributes original content under Apache 2.0. The submission form makes you confirm the work is original and that every external resource is listed. So:

- Keep pre-event work to data access, reading, environment setup and throwaway exploration.
- Anything reusable written before 14 Nov (including `scripts/` in this repo) should be listed as an external resource, or rewritten during the event. Ask your local event lead which they prefer.
- If anyone on the team is under 18, the terms bar recognizable names, voices and likenesses of minors from the submission. Plan the video narration around that.
