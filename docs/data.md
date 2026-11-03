# NISAR data feasibility

Everything in the scene tables came from a live ASF query on 3 Nov 2026. Re-run it any time:

```bash
pip install -r requirements.txt
python prep/find_scenes.py data/events.json --out data/scenes
```

## What is public, and which part to use

| Release | Date | Acquisitions covered | Use it? |
|---|---|---|---|
| Sample (pre-calibration) | 23 Jan 2026 | 25 products | No |
| BETA | 27 Feb 2026 | Subset of 17 Oct 2025 to 20 Jan 2026, up to 8 per track | No. Pre-calibration, intended for building workflows. |
| **PROVISIONAL** | **20 Jul 2026, ongoing** | **Everything from 17 Jun 2026 forward** | **Yes, and only this** |
| Validated | Not yet | Reprocessing expected to finish by end of 2026; it will supersede earlier versions | Re-run your results on it afterwards |

Source: [ASF availability overview](https://nisar-docs.asf.alaska.edu/availability-overview/). ASF warns that BETA was produced with older processing software (CRIDs below 05023), so do not pair a BETA scene with a PROVISIONAL one.

So the usable window is **17 Jun 2026 to now**, minus a **permanent gap from 2026-07-27 22:03 UTC to 2026-08-10 00:55 UTC**. No acquisitions will ever exist inside that gap.

NISAR images each location twice every 12 days (once ascending, once descending), through cloud ([Earthdata, 21 Jul 2026](https://www.earthdata.nasa.gov/news/nisar-l-band-data-released-expanding-record-surface-changes)). Download of the HDF5 files needs an Earthdata login. The browse PNGs do not, which is what `prep/quicklook.py` uses.

## Candidate events with real scene pairs

Pairs share direction, track, frame and frequency-A bandwidth, and at least two frequency-A polarizations. Sizes are the two full HDF5 files.

| Event | Pass | Track / frame | Freq A | Pre → post | Post date vs event | Baseline | Nearest Sentinel-1 | Pair size |
|---|---|---|---|---|---|---|---|---|
| **Gandak, Bihar (lead)** | Desc | 149 / 75 | 20 MHz | 16 Sep (QP) → **28 Sep 13:07 UTC** (DH) | 1 day after the 27 Sep record crest | 12 d | **+11 h** (S1D, 29 Sep 00:19) | 9.9 GB |
| Gandak | Asc | 26 / 15 | 40 MHz | 19 Sep (DH) → 1 Oct (DH) | Recession | 12 d | −71 h | 14.1 GB |
| **North Bihar, Kosi / Bagmati (held-out)** | Desc | 48 / 75 | 20 MHz | 28 Aug (QP) → **9 Sep 12:58 UTC** (DH) | Floods ongoing statewide (44 lakh affected on 10 Sep) | 12 d | **−38 min** (S1D RTC, 9 Sep 12:20; also −38 min on 28 Aug) | 11.0 GB |
| North Bihar | Desc | 120 / 76 | 20 MHz | 21 Aug (QP) → 2 Sep (QP) | Early in the event; quad-pol both dates | 12 d | −61 h | 17.9 GB |
| SE Bangladesh (far-shift stretch) | Asc | 69 / 13 | 40 MHz | 30 Jun (DH) → **12 Jul 23:21 UTC** (DH) | Onset day | 12 d | **+13 h** (S1D, 13 Jul 12:03) | 12.4 GB |
| SE Bangladesh | Desc | 91 / 77 | 20 MHz | 20 Jun (QP) → 14 Jul (DV) | 2 days after onset | 24 d | −25 h | 9.9 GB |
| Assam | Asc | 40 / 15 | 40 MHz | 10 Jul (DH) → 22 Jul (DH) | 3 days after onset, near the peak | 12 d | none within 3 days | 14.2 GB |
| Assam | Desc | 163 / 75 | 40 MHz | 25 Jun (DH) → 19 Jul (DH) | Onset day | 24 d | −37 h | 14.3 GB |
| Central Indiana | Asc | 47 / 22 | 20 MHz | 23 Jul (QP) → 16 Aug (QP) | 3 days after onset | 24 d (data gap) | +61 h | 16.5 GB |
| Central Indiana | Desc | 156 / 68 | 20 MHz | 12 Aug (QP) → 24 Aug (QP) | 11 days after onset | 12 d | none within 3 days | 16.2 GB |
| Rasuwa GLOF, Nepal | Desc | 48 / 74 | 20 MHz | 11 Jul (QP) → 28 Aug (QP) | 6 days after | 48 d | −37 min | 15.8 GB |
| Rasuwa GLOF, Nepal | Asc | 98 / 16 | 40 MHz | 19 Aug (DH) → 31 Aug (DH) | 9 days after | 12 d | none within 3 days | 14.3 GB |

"Nearest Sentinel-1" is the closest IW GRD pass over the event point within ±3 days of the NISAR post scene; positive means Sentinel-1 came after NISAR.

Full scene IDs are in `data/scenes/pairs.csv`; every granule per event is in `data/scenes/<event>_granules.csv`.

Polarization codes: DH = HH + HV, DV = VV + VH, QP = quad-pol (full covariance, including the off-diagonal terms such as HHVV).

### Why Gandak leads

- NISAR's 28 Sep pass came one day after the river reached a record level at Devghat on 27 Sep ([NASA Earth Observatory](https://science.nasa.gov/earth/earth-observatory/rains-swamp-the-gandak-river/)).
- **Sentinel-1D passed at 00:19 UTC on 29 Sep, about 11 hours after NISAR**, and OPERA's DSWx-S1 water map exists for it (15 MGRS tiles). One more DSWx-S1 tile, in the northeast corner, comes from a pass 54 minutes before NISAR.
- **Sentinel-2 imaged the frame 8 hours before and 16 hours after NISAR**, and OPERA's DSWx-HLS water maps exist for both passes. On 29 Sep four tiles are 5 to 12% cloud. The pre-event date has the same structure (Sentinel-2 at −8 h and +16 h, Sentinel-1 at +11 h). See "Reference products found" below.
- NASA Earth Observatory published MODIS false-color images from 20 Sep and 29 Sep, which you can cite for the story and use as a coarse sanity check.
- The frame (roughly 25.4°N to 28.1°N, 81.9°E to 85.1°E) covers most of the Gandak's course in India: flat, agricultural, with riparian vegetation. Good for open-water detection, and the vegetated edges are where the L-band question lives.
- The pre-event date is quad-pol, so the pre-flood polarimetric state of the floodplain is fully measured.

### Where the others fall short

- **North Bihar** is the held-out event. Same 20 MHz mode and same kind of landscape as Gandak, a different river system three weeks earlier, and Sentinel-1 38 minutes before NISAR on both dates. OPERA made no DSWx-S1 maps for those two passes, so you run DSWx-S1 yourself on the RTC-S1 bursts (56 per date). Optical (HLS) is mostly cloudy, 46% at best. The frame covers the Kosi and Bagmati plains of north Bihar; it stops just north of the Ganga mainstem districts. Because it is the same region, the honest claim is "transfers across two Bihar floods," not "generalizes."
- **Bangladesh** becomes the far-shift stretch goal: a Sentinel-1 pass 13 hours after NISAR, but no OPERA water map for it (RTC-S1 exists). Its weaknesses: the NISAR pass is on the onset day (12 Jul), while Chattogram's heaviest rain (412.3 mm) fell on 15 Jul, so the flood was still growing; and the frame mixes coastal plain with the Chittagong Hill Tracts and a large city. It is also 40 MHz where Gandak is 20 MHz, which is a useful test of whether anything tuned on Gandak transfers. I have not looked at its browse images yet.
- **Assam**: good pairs, but the affected population peaked around 24 to 26 Jul ([Wikipedia: 2026 Assam floods](https://en.wikipedia.org/wiki/2026_Assam_floods)) and the permanent data gap starts on 27 Jul. No Sentinel-1 pass falls within 3 days of the 22 Jul NISAR scene. Good for the story, weak for scoring.
- **Indiana**: quad-pol on both dates, US data sources (USGS gauges) for context. But the near-peak pair has a 24-day baseline, so crop growth between 23 Jul and 16 Aug will contaminate change in the farmland. Sentinel-1D passed on 18 Aug, 2 days after NISAR, during recession.
- **Rasuwa**: a debris flow in a steep Himalayan valley, where layover and shadow dominate. Track 48 has Sentinel-1D 37 minutes before NISAR, the closest L-band/C-band timing in this list, but over a 48-day NISAR baseline. A good "where SAR fails" example, a poor flood-extent case.

Event dates for Indiana, Bangladesh and Rasuwa come from [Wikipedia: Weather of 2026](https://en.wikipedia.org/wiki/Weather_of_2026), a secondary source. Copernicus EMS activated EMSR927 for Rasuwa ([CEMS](https://mapping.emergency.copernicus.eu/news/flood-in-nepal-emsr927/)). I did not find CEMS activations for the Indian events. The past Indian flood activations I found went through the International Charter with ISRO as requestor (for example [activation 612](https://disasterscharter.org/activations/flood-large-in-india-activation-612-), July 2019), and Charter products are not always open.

## Reference data you can actually get

| Reference | Sensor | Strength | Weakness |
|---|---|---|---|
| Copernicus GFM | Sentinel-1 C-band, global, automatic | Flood extent, ensemble likelihood and exclusion mask for the 29 Sep Gandak pass | Same physics family as NISAR, so errors correlate in urban areas and under wind roughening. Blind under canopy. |
| [OPERA DSWx-S1](https://podaac.jpl.nasa.gov/dataset/OPERA_L3_DSWX-S1_V1) | Sentinel-1, 30 m, near-global, forward production since Sep 2024 | Independent algorithm from GFM | Same C-band blind spots |
| OPERA DSWx-HLS | Landsat / Sentinel-2 | Truly independent physics, and passes 8 h before and 16 h after both Gandak NISAR dates | Cloud (5 to 58% per tile on 28 and 29 Sep). Blind under canopy like C-band. |
| OPERA RTC-S1 | Sentinel-1 backscatter, 30 m bursts | Lets you run DSWx-S1 yourself where OPERA didn't (north Bihar, Bangladesh) | You own the processing errors |
| MODIS (NASA EO, 29 Sep) | Optical, 250 m to 500 m | Same-day, citable | Far too coarse for pixel scoring |

Use time offsets explicitly. A flood map from a different day is not ground truth for this day. Report the offset in hours for every comparison, and separate permanent water (JRC occurrence, or the pre-event NISAR date) from new inundation before scoring.

## Known issues that affect this project

From ASF's [PROVISIONAL known issues](https://nisar-docs.asf.alaska.edu/provisional-known-issues/) (updated 30 Jul 2026), plus what the browse images show:

- **Swath gaps.** The Gandak browse images show dark along-track stripes: three full-length ones on 16 Sep (quad-pol) and shorter ones in different positions on 28 Sep (dual-pol). ASF describes "three to six gaps across the swath due to the nature of NISAR's SweepSAR acquisition" in quad-pol areas (stated for the soil moisture product). Check the GCOV `mask` layer before trusting any pixel near a stripe, and use the union of both dates' masks.
- **Mode alternation.** On track 149 the 20 MHz mode alternates QP, DH, QP, DH across cycles. A strict same-mode pair is 24 days apart; the 12-day pair is cross-mode on HH and HV. On track 163 over Assam it alternates between 40 MHz DH and 20 MHz QP, so the 12-day pair also changes bandwidth. Do not compare across bandwidths without multilooking both to a common posting.
- **Polarimetric phase.** "The relative phase between polarimetric channels is not fully calibrated." ASF gives a θ = 59° correction for coherent dual-pol or quad-pol analysis. Apply it before any Freeman-Durden or Yamaguchi decomposition.
- **Frequency B (5 MHz)** has larger radiometric calibration residuals than frequency A. Use frequency A.
- **40 MHz joint-mode products** have residual radiometric bands across the swath, still within requirements. Expect along-track banding in the Assam and Gandak-ascending pairs.
- **RFI** filtering sometimes leaves residual interference or removes real features in high-contrast areas. Low-backscatter water is where residual RFI shows most.
- **Browse colors** depend on the polarization mode, so a QP browse and a DH browse are not color-comparable. Never present the two browse PNGs as a before/after.

## GCOV product notes

- Radiometrically terrain-corrected γ⁰ covariance terms, geocoded. Layers include `mask`, number of looks, and the RTC γ⁰-to-σ⁰ factor ([ASF products overview](https://nisar-docs-test.asf.alaska.edu/products-overview)).
- Pixel spacing depends on range bandwidth; ASF lists 10, 20 or 80 m. Read the actual posting from the HDF5 rather than assuming it.
- No layover/shadow layer in GCOV. Compute one from the Copernicus GLO-30 DEM and the incidence-angle geometry, or take it from the matching GSLC.
- Files run about 2 to 9 GB each. Harmony's GCOV dataset (variable) subsetting has been complete since June 2026; spatial subsetting is pending for Q4 2026 ([ASF roadmap](https://nisar-docs.asf.alaska.edu/roadmap)). Pull only `HHHH`, `HVHV` and `mask` for the first pass.

## Reference products found (CMR, 3 Nov)

From `prep/find_references.py`; every granule and URL is in `data/manifest.csv`, and the raw query output is in `data/refs/`.

| Event, date | Product | Time (UTC) | Offset from NISAR | Granules |
|---|---|---|---|---|
| Gandak post, 28 Sep 13:07 | DSWx-HLS (Sentinel-2) | 28 Sep 05:00 | −8 h | 11 |
| | DSWx-S1 | 28 Sep 12:13 | −1 h | 1 (NE corner) |
| | DSWx-S1 | 29 Sep 00:18 | +11 h | 15 |
| | DSWx-HLS (Sentinel-2) | 29 Sep 05:20 | +16 h | 11 (four at 5 to 12% cloud) |
| Gandak pre, 16 Sep 13:07 | DSWx-HLS | 16 Sep 05:10 | −8 h | 17 |
| | DSWx-S1 | 16 Sep 12:13 | −1 h | 1 |
| | DSWx-S1 | 17 Sep 00:18 | +11 h | 15 |
| | DSWx-HLS | 17 Sep 05:00 | +16 h | 10 |
| North Bihar post, 9 Sep 12:58 | RTC-S1 | 9 Sep 12:20 | −0.6 h | 56 bursts |
| | DSWx-S1 | 12 Sep 00:10 | +59 h | 15 |
| North Bihar pre, 28 Aug 12:58 | RTC-S1 | 28 Aug 12:20 | −0.6 h | 56 bursts |

## Time series on the lead track

Track 149, frame 75, descending, all 13:07 UTC: 23 Aug (20 MHz QP), 4 Sep (20 DH), 16 Sep (20 QP), 28 Sep (20 DH), 10 Oct (20 DH), 22 Oct (40 DH). The three 20 MHz DH dates are color-comparable in the browse images ([quicklook](../quicklooks/gandak_T149_F075_DH_20260904_20260928_20261010.png)): the flood zone along the river widens by 28 Sep and spreads further by 10 Oct. The stripe positions change from date to date.

## S-band

ASF's metadata sets `jointObservation = True` on every Bihar scene listed here. I read that as the L- and S-band radars imaging together, which is NISAR's design over India; confirm it on Bhoonidhi. ISRO releases S-band GCOV for acquisitions from 8 Jul 2026 onward ([ISRO](https://www.isro.gov.in/ISRO%5FEN/NISARS_Band_SAR_Data_Products_Release.html)), and the portal needs registration.

