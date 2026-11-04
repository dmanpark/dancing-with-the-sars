# Audit of the plan (3 Nov 2026)

Two passes: an independent reviewer that read only the overview and the build spec, then a check of its findings against the scene and reference data. Every fix below has been applied to [overview.md](overview.md) and [build-spec.md](build-spec.md) (version 2). The Claude doc and the two Drive copies are still version 1.

## Scores

| Dimension | v1 (as reviewed) | v2 (after fixes), my estimate | What moved it |
| --- | --- | --- | --- |
| Core idea | 8 | 8 | Unchanged: L-band, C-band and optical on one record flood within 16 hours is rare and sits squarely on the challenge |
| Scientific validity | 6 | 8 | Claim 2 now has a same-pixel control; trust is tested against the optical referee; paired comparisons |
| Feasibility in 39 h | 6 | 7 | North Bihar run starts at 9:05; load moved off Truth; fallback pair now downloadable |
| Influence | 7 | 7 | Reframed from "send boats" to "verify first"; still no user voice |
| Creativity | 8 | 8 | Quad-pol phase test added as the Tier 3 physics check |
| Validity (as a judge sees it) | 7 | 8 | A SAR judge's first three objections now have answers |
| Relevance | 8 | 8 | Polarization answer goes beyond HH against HV if Tier 3 lands |
| Presentation | 6 | 7 | Video rebuilt around two plain numbers |
| Clarity as a team document | 8 | 8 | Contradictions fixed |
| **Overall** | **7** | **8** | |

The reviewer's odds for v1: a likely global nominee, winner possible (about 1 in 10). I would not put a number on it. Ten global awards across every challenge means no plan makes winning likely; v2 removes the reasons a SAR judge would mark it down, and the rest is execution and the video.

## What the review found, and what changed

Ranked by what each would have cost.

1. **Claim 2 could pass with no real L-band signal.** On this flat plain, HAND above 15 m with gentle slope is mostly Siwalik and Nepal hill forest, where the rain fell; low ground is groves and sugarcane on wet soil. Soil moisture and crop growth alone would flag low ground more often. **Fix:** the primary test is now a same-pixel control. Flag rates on 16 to 28 Sep minus flag rates on the previous 12-day interval, 23 Aug to 4 Sep, which has the same quad-pol to dual-pol order. The headline is the excess km². The control interval may itself hold some early-September flooding, so the excess is conservative. The HAND contrast stays as a secondary test within each land-cover class, dropped if high-HAND vegetated pixels on gentle slopes are under 5% of the vegetated area.
2. **Claims 3 and 4 graded NISAR against C-band**, the sensor the project calls blind. Real hidden water on cropland would have counted as a NISAR error. **Fix:** the trust model is fit on north Bihar (C-band 38 minutes from NISAR, open-water decisions only) and tested on Gandak against the optical referee. Claim 4's headline moves to Gandak, where the breach villages and the video are.
3. **Claim 4's fail test was too easy**, and recall at 50 is capped at 50 divided by the number of flooded cells. **Fix:** the headline is the hit rate among the first 50 cells, and it fails unless it beats log-ratio flood share × built-up area on a paired bootstrap.
4. **The video asked viewers to read an AUROC in six seconds**, and shot 5 paired a Gandak village with a north Bihar number. **Fix:** two plain numbers (excess km², hit rate in 50 checks), both from Gandak. The reviewer's worry that embankments broke between the NISAR and Sentinel-1 passes does not apply: the reports put the breaches on the night of 29 to 30 Sep (India time), after NISAR (28 Sep 18:37 IST), Sentinel-1 (29 Sep 05:48 IST) and Sentinel-2 (29 Sep 10:50 IST).
5. **One midnight job held up claims 3 and 4.** **Fix:** Truth starts `dswx_s1.py` on north Bihar in the background at 9:05 Saturday. The fallback ascending pair (19 Sep and 1 Oct) is now in the download list.
6. **Claim 1 compared algorithms, not sensors.** **Fix:** the same log-ratio method also runs on Sentinel-1 RTC (17 and 29 Sep, now in the download list). The primary NISAR method is named in advance (two-sided detector, open-water class), with a non-inferiority margin of 0.05 in F1 and a paired bootstrap of the difference.
7. **Thresholds might not transfer.** A scene-wide Kittler-Illingworth threshold fails when water is a few percent of the frame. Quad-pol and dual-pol calibration may differ. The HH-spread feature spanned 24 days on one event and 60 on the other. **Fix:** Kittler-Illingworth runs on 10 km tiles that pass a bimodality test (Ashman D > 2), as DSWx does. A fixed rule subtracts any median log-ratio offset over 0.5 dB on stable ground. HH spread uses every 20 MHz pre-event date since 17 Jun on each track: Gandak 6 Jul, 23 Aug, 4 Sep and 16 Sep (6 Jul added to the downloads); north Bihar 29 Jun, 11 Jul and 28 Aug.
8. **Tiles would break GitHub's limits.** PNG tiles with transparency at zoom 12 can pass 100 MB per file, and branch deploys are capped at about 10 builds an hour. **Fix:** WEBP tiles, deploys through GitHub Actions with `.nojekyll`, tile pushes at most twice.
9. **Overclaims.** "The first public radar that can look there" is wrong: ALOS-2 ScanSAR and the PALSAR archive are open. **Fix:** "the first free L-band radar that images all land every 12 days". "Cannot see water under crops" became "largely misses".
10. **Inconsistencies.** **Fixes:**
    - The Tier 3 gate requires Tier 1 and claim 2 everywhere.
    - Flooded-vegetation flags count as not open water in claim 1.
    - "Sentinel-1 called dry" now excludes DSWx-S1's inundated-vegetation class.
    - The shared machine is spelled out: the 3090 box runs Radar and Truth, with data on WSL2's ext4 disk.
11. **Challenge gap.** The polarization question was answered only with HH against HV. **Fix:** Tier 3 adds an HH-VV phase test on the two quad-pol dates (16 Sep and the partial 10 Oct frame, after ASF's 59° correction). It sits ahead of S-band, which depends on a Bhoonidhi registration.

## What the review said to keep

- The optical referee: two passes that bracket both radars.
- Thresholds fixed before kickoff, and the held-out rule.
- The block bootstrap, the limits box and the naive-difference toggle.
- Tier 1 as a complete submission, the 12:00 gate, and the file contracts.

## Still open

- **Influence has no user voice.** A one-line quote from a Bihar flood-response official or an NGO, gathered before the event, would carry more than any number. Optional.
- **Breach times inside West Champaran** are reported only as "within about 10 hours" of the 1 Oct articles. Story confirms them before the video says anything about timing.
- **Typical L-band flood and double-bounce thresholds in dB.** Neither pass found a citable source. The ±3 dB and +2 dB cuts are fixed in advance on physical reasoning, and the methods should say exactly that.

## What the reviewer checked

The OPERA DSWx ATBD (tile bimodality selection, HAND as a fuzzy input, inundated vegetation limited to herbaceous wetland), OPERA's DSWx-NI workshop slides (still under development; dual-pol GCOV support not confirmed), GDAL's MBTiles driver and the GitHub Pages limits, ASF's provisional known issues, and Earthdata's ALOS-2 ScanSAR release.
