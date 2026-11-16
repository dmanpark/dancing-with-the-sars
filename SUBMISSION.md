# Submission: Dancing with the SARS: The Hidden Steps

Every number below comes from app/data/results.json (commit 8fbdf60, generated 2026-11-15T03:35:15Z). Paste each field into the team's project page on the Space Apps site.

## Project name

Dancing with the SARS: The Hidden Steps

## Summary

On low ground under trees, NISAR flagged 17 km² (95% interval 15 to 19 km²) more flooding than in the 12 days before, where Sentinel-1 saw dry land (evidence, not verified).

On open water: F1 0.05 for NISAR and 0.17 for Sentinel-1, checked against optical satellites. The difference, NISAR minus Sentinel-1, is −0.12 (95% interval −0.20 to −0.03), below our non-inferiority margin of −0.05. Recall was low for every radar map, OPERA's own Sentinel-1 product included, most likely because the optical check had no clear pre-flood image and counted water that was already standing.

On 27 Sep 2026 the Gandak river in Bihar broke its flood record, and NASA-ISRO's new NISAR radar imaged it the next day, with Europe's Sentinel-1 11 hours later. Today's global radar flood maps use Sentinel-1's short C-band waves, which bounce off leaves, so water under trees often goes unmapped; NISAR's longer L-band waves reach the ground underneath. Our app lets anyone watch the flood spread every 12 days, slide between the two radars' flood maps, tap a field and hear its radar signal change, and see how we checked it.

## Demo link (video)

https://youtu.be/80nnnIlPmLc

## Final project link (app)

https://dmanpark.github.io/dancing-with-the-sars/

Code and data processing: https://github.com/dmanpark/dancing-with-the-sars

## Details

**What it does.** A one-page web app with five steps: (1) NISAR's view of the Gandak every 12 days from 6 Jul to 22 Oct 2026, animated; (2) a slider between Sentinel-1's flood map (29 Sep 00:18 UTC) and NISAR's (28 Sep 13:07 UTC), made with the same rules; (3) the hidden steps: low ground under trees where NISAR flagged flooded vegetation and Sentinel-1 saw dry land, labelled "evidence, not verified"; (4) listen: tap any spot to see and hear its HH and HV radar brightness across the seven dates; (5) how we know: the optical check, both numbers with their intervals, a toggle that shows the fake change a naive difference makes at NISAR's swath gaps, and the limits below. An Explore mode shows every layer with a legend. It is static files on GitHub Pages, works on a phone, and needs no login.

**How we made the maps.** NISAR L2 GCOV (provisional, frequency A, HH and HV) for seven dates on track 149, frame 75, averaged 2 x 2 in linear power to 40 m. A pixel counts only where both dates' masks say fully focused and slope is at most 10 degrees, away from permanent water. Calibration offsets were measured on stable ground (high ground and raised towns) and removed per part of the 28 Sep frame, which was acquired in two parts (lead pair HH offsets −0.34 and +0.34 dB). Dark-water thresholds come from 10 km tiles that pass a bimodality test (Gaussian mixture, Ashman D above 2), with Kittler-Illingworth per tile. New open water is an HH drop of at least 3 dB to below the dark-water threshold, with HV also below its threshold. Flooded vegetation is an HH rise of at least 3 dB that exceeds the HV change by at least 2 dB (double bounce off trunks). The same open-water rule runs on Sentinel-1 VV and VH from OPERA RTC-S1. Every cut was fixed before the event on physical reasoning; we found no published L-band flood threshold to cite.

**How we checked it.** Claim 1 scores both radars on the same 230,621 pixels against an optical referee: water in both Landsat 9 (27 Sep, 32 h before NISAR) and Sentinel-2C (1 Oct, 64 h after) OPERA DSWx-HLS maps, both clear, where JRC's water history (occurrence below 25%) stands in for a pre-flood map (11,288 new-water pixels). NISAR F1 0.05 (95% interval 0.01 to 0.12), Sentinel-1 F1 0.17 (95% interval 0.08 to 0.27); OPERA's own DSWx-S1 F1 0.06. The non-inferiority margin was fixed at −0.05 in advance: not passed, so on this referee NISAR did not keep up with Sentinel-1 on open water. Recall is low for every method (NISAR 0.03, Sentinel-1 0.09, DSWx-S1 0.03), and 90% of the referee's new-water pixels that NISAR missed were already dark on 16 Sep (90% of those Sentinel-1 missed were already dark on 17 Sep): with no clear pre-flood optical map, the referee likely counts water that was already standing, which a change detector does not call new. Claim 1a: NISAR alone, checked against the 29 Sep optical map in the western frame: F1 0.68 (95% interval 0.53 to 0.76); against HH alone the difference is +0.002 (95% interval +0.001 to +0.004), a small but consistent gain from adding HV. Claim 2 compares NISAR's flooded-vegetation flags on 16 to 28 Sep with the 12 days before (23 Aug to 4 Sep) on the same 1,254,560 pixels of tree cover, shrubland and wetland below 2 m above the nearest drainage, where OPERA's DSWx-S1 said dry: 20 km² flagged against 3 km², an excess of 17 km² (95% interval 15 to 19 km²). A caution on that number: 52% of the flagged pixels lie within about 140 m of buildings, against 24% of all the pixels tested, so some flags may come from walls beside trees rather than water; this is why the app labels the layer "evidence, not verified". Cropland alone: −105 km² (95% interval −146 to −60 km²), so on cropland the test shows no hidden-water signal. With every calibration offset shifted by half its tile spread, the vegetation excess is 11 km² (offsets up) and 24 km² (offsets down). The planned secondary test (the flag-rate contrast between low and high ground) was dropped by the team's decision of 4 Nov, because the preliminary tests found high, gentle ground under 5% of every class; the build's recount on its own valid pixels, which leave out slopes over 10 degrees, gives 7.1% for tree cover and 5.1% for shrubland, above the 5% cut, so the test could have run; we kept the pre-event decision and report no contrast (the build's first run computed one before the code was brought in line with the decision; its values were discarded unread). Intervals come from a paired bootstrap over 5 km blocks (1,000 draws, seed 2026). DSWx-NI, OPERA's NISAR water product code, was dropped before the event: it needed more memory than our machine allowed and a land-cover file its schema calls optional. Tier 3 (a trust map and a check-first list) was cut when the build started late.

**What this can't tell you**

- How accurate the map is under canopy. No reference sees there, so claim 2 is evidence of a signal, not an accuracy figure.
- Damage. Flooded and built-up is not the same as damaged.
- Global performance. This is one flood in Bihar.
- Real-time use. Each NISAR pass direction repeats every 12 days and products arrive 36 to 72 hours later, so NISAR fills Sentinel-1's blind spots rather than replacing its revisit.
- Final calibration. These are PROVISIONAL products; the validated reprocessing is due by the end of 2026.

**Tools.** Python (numpy, scipy, h5py, rasterio, GDAL, scikit-learn, matplotlib), MapLibre GL JS, PMTiles, the Web Audio API, Playwright and ffmpeg for the video, GitHub Pages.

## NASA data

- NISAR L2 GCOV PROVISIONAL (ASF DAAC), track 149, frame 75: NISAR_L2_PR_GCOV_024_149_D_075_2005_DHDH_M_20260706T130707_20260706T130742_P05023_N_F_J_001, NISAR_L2_PR_GCOV_028_149_D_075_2005_QPDH_A_20260823T130705_20260823T130739_P05023_N_F_J_001, NISAR_L2_PR_GCOV_029_149_D_075_2005_DHDH_M_20260904T130705_20260904T130739_P05023_N_F_J_001, NISAR_L2_PR_GCOV_030_149_D_075_2005_QPDH_A_20260916T130704_20260916T130739_P05023_N_F_J_001, NISAR_L2_PR_GCOV_031_149_D_075_2005_DHDH_M_20260928T130705_20260928T130739_P05023_N_F_J_001, NISAR_L2_PR_GCOV_032_149_D_075_2005_DHDH_M_20261010T130705_20261010T130739_P05023_N_F_J_001, NISAR_L2_PR_GCOV_033_149_D_075_4005_DHDH_A_20261022T130705_20261022T130739_P05023_N_F_J_001.
- OPERA L3 DSWx-S1 v1 (PO.DAAC), 17 and 29 Sep 2026 00:18 UTC.
- OPERA L3 DSWx-HLS v1 (PO.DAAC), 16, 17, 27 and 29 Sep and 1 Oct 2026, built from HLS (Landsat 8 and 9, Sentinel-2B and 2C).
- OPERA L2 RTC-S1 v1 (ASF DAAC), 54 bursts on each of 17 and 29 Sep 2026.

## Other data and tools

- ESA WorldCover 2021 v200; JRC Global Surface Water occurrence v1.4; Copernicus GLO-30 DEM and GLO-30 HAND; GHSL GHS-BUILT-S E2020 R2023A.
- OPERA DSWX-SAR (tag DSWx-NI-v1.0), installed before the event for the preliminary tests.
- The team's pre-event search and download scripts in `prep/` (written before the event, cited here).
- News reports of the flood: NASA Earth Observatory, Daijiworld (1 Oct 2026), Telangana Today (1 Oct and 10 Sep 2026). Full list in `CITATIONS.md`.
- Space Apps guidance used to plan the project: the NASA Space Apps Challenge Participant FAQ (2022, legacy site, https://legacy.spaceappschallenge.org/resources/faq/) and the Judging & Awards Guide (2024 edition, https://www.spaceappschallenge.org/resources/judging-awards-guide).

## AI use

The team used an AI coding assistant to accelerate development. Its role was limited to UI scaffolding, writing test harnesses, and debugging the pipeline. The team designed and authored all scientific logic, including the thresholding, the bimodality gate, and the optical-reference validation. No generative image, video, or audio model was used; the two diagrams are SVG drawings coded from basic shapes and marked "Diagram made with AI assistance".
