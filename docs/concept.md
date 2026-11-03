# The project: what to build on 14 Nov

Second iteration, 3 Nov 2026. Supersedes the plan in the first review. Every date and sensor pass below was checked against ASF or NASA CMR today; the queries are reproducible with `prep/`.

## In one paragraph

Working name: **Wallflower**, for the floods that sit out the dance because the usual radar never sees them. (If the team hates it: *Under the Canopy*.)

> Most of the world's operational flood maps are built from Sentinel-1's C-band radar, which cannot see water under crops and trees, so those areas come out dry or blank. NISAR's L-band can see there. On 28 Sep 2026, one day after the Gandak River hit a record level, NISAR imaged the Bihar floodplain at 13:07 UTC. Sentinel-2 photographed the same area 8 hours earlier and 16 hours later, and Sentinel-1 imaged it 11 hours later. Wallflower uses that coincidence to show where L-band finds water that C-band missed, how far to trust every NISAR pixel, and which villages a response team should check first.

That paragraph is the 30-second video, the project summary and the elevator pitch. Learn it.

## Why this version is stronger than the original idea

The original doc wanted "uncertainty-aware change detection with decision prioritization." Good instincts, but every piece of it already exists for Sentinel-1 (see [review.md](review.md)). Three things changed after digging into the data:

**1. The reference data around the Gandak pass is unusually good.** The same pattern repeats before and after the flood:

| | Pre-event | Post-event |
|---|---|---|
| NISAR L-band | 16 Sep 13:07 (quad-pol) | 28 Sep 13:07 (dual-pol) |
| Optical (OPERA DSWx-HLS water maps) | Sentinel-2B 16 Sep 05:10 (−8 h); Landsat 8 17 Sep 05:00 (+16 h) | Sentinel-2C and Landsat 8 28 Sep 04:41 to 05:00 (−8 h); Sentinel-2B 29 Sep 05:20 (+16 h) |
| Sentinel-1 C-band (OPERA DSWx-S1 water maps) | 17 Sep 00:18 (+11 h) | 29 Sep 00:18 (+11 h) |

On 29 Sep, four Sentinel-2 tiles over the frame have 5 to 12% cloud. Optical imagery is a referee neither radar depends on. Score both radars only on pixels where the two optical passes (−8 h and +16 h) agree, and the timing differences stop favoring either sensor. That's a fair L-band vs C-band comparison on open water, and I found nothing published like it.

**2. The held-out event is much better than Bangladesh.** The early-September north Bihar floods (officials reported about 44 lakh people affected statewide on 10 Sep, with the Bagmati and Kosi above danger level, per [Telangana Today](https://telanganatoday.com/bihar-floods-44-lakh-affected-across-14-districts)) have a NISAR pair on track 48 (28 Aug → 9 Sep, 20 MHz like Gandak). Sentinel-1 imaged the area 38 minutes before NISAR on both dates. OPERA did not make water maps for those two passes, but its RTC-S1 backscatter exists, so you run OPERA's own DSWx-S1 code on it and get a C-band twin of the NISAR pair.

**3. S-band may be there too.** ASF marks every Bihar NISAR scene as a joint observation. My reading is that ISRO's S-band radar imaged at the same moment, but confirm it. ISRO has released S-band GCOV as daily products for acquisitions from Cycle 25 (8 Jul 2026) onward ([ISRO, 24 Jul 2026](https://www.isro.gov.in/ISRO%5FEN/NISARS_Band_SAR_Data_Products_Release.html)), downloadable from [Bhoonidhi](https://bhoonidhi.nrsc.gov.in/NISAR/NisarProducts.html) after registration. If those scenes exist, the project has three wavelengths on one flood: C-band at 5.5 cm, S-band at 9.4 cm and L-band at 24 cm. Physics predicts that the water found under vegetation grows with wavelength. One chart of that would be the most memorable figure in the competition. If S-band access fails, nothing else depends on it.

## What the app shows

A static web map, hosted on GitHub Pages, no login, still working when global judging runs in December and January.

1. **The dance.** Six same-track NISAR dates animated (23 Aug, 4 Sep, 16 Sep, 28 Sep and 10 Oct at 20 MHz; 22 Oct at 40 MHz). The Gandak floodplain darkens, spreads and recedes. The browse images already show it: [quicklook](../quicklooks/gandak_T149_F075_DH_20260904_20260928_20261010.png).
2. **Two radars, one flood.** Swipe between the NISAR flood map and Sentinel-1's DSWx-S1 from 11 hours later.
3. **Hidden water.** Pixels where L-band shows flooded-vegetation evidence (HH brightening from double bounce, HH/HV ratio up) and C-band says dry. Drawn in its own color and labeled "evidence, not verified."
4. **Trust layer.** Per-pixel reliability, with NISAR's swath-gap stripes hatched as "don't trust." Toggle "naive difference" and the stripes light up as fake change. That shows why the layer exists in about three seconds.
5. **Check first.** A ranked list of 500 m cells (flood probability × built-up area × trust). Click one to see its HH and HV change, its height above the river (HAND), its land cover and why it's trusted or not.

## Hypotheses

Ranked by order of build, not by importance.

**H0, open-water head-to-head.** Against stable optical water (DSWx-HLS, both passes agree, cloud-free), NISAR new-water F1 is at least Sentinel-1's. This is the cleanest result and the foundation for everything else. Report it with 5 km block-bootstrap intervals, whichever radar wins.

**H1, hidden water.** In vegetated pixels, the L-band flag rate is clearly higher on low ground connected to the river (HAND < 2 m) than on high ground (HAND > 15 m), and much of the low-ground signal falls where DSWx-S1 says dry. High ground cannot flood, so its flag rate is the false-alarm floor from crop growth and soil moisture. Optical cannot see under canopy either, so this is a signal test, not an accuracy test. Say that on screen.

**H2, trust that transfers.** A reliability model trained on Gandak predicts where NISAR disagrees with the reference on north Bihar better than the raw |log-ratio| margin does. Measure it with error-prediction AUROC and a risk-coverage curve. Features: incidence angle, slope, layover/shadow, HAND, land cover, distance to a swath-gap stripe, pre-event HH variability over the summer stack, and pre-event backscatter level (dark sand bars mimic water).

**H3, check-first list.** With 50 inspections, the ranking finds more flooded built-up cells than ranking by change magnitude or by built-up area alone (recall@25/50/100, block bootstrap). If it does not beat both, say so. That is still a result.

**Stretch, wavelength ladder.** Hidden-water area at C < S < L on the same pixels.

## The physical drivers (the challenge asks for these)

- **The flood itself:** rain over Nepal's Gandak basin from 24 to 27 Sep drove the river to a record at Devghat on 27 Sep ([NASA Earth Observatory](https://science.nasa.gov/earth/earth-observatory/rains-swamp-the-gandak-river/)). A secondary source reports a record 91.25 m at Bagaha in Bihar on 3 Oct ([Vajiram & Ravi](https://vajiramandravi.com/current-affairs/bihar-floods-2026/)), which matches the browse image of 10 Oct looking wetter than 28 Sep. Check this against gauge data before saying it on stage.
- **What the radar sees:** open water reflects the pulse away, so it goes dark in HH and HV. Water under stalks and trunks bounces the pulse back twice, so HH goes bright. Longer wavelengths get through more canopy before scattering, which is the whole L-band argument. A second hypothesis to test: wind-roughened water should fool C-band more than L-band, because 24 cm waves need rougher water to scatter.
- **Why the pre-event date matters:** late-season paddies can already hold standing water in September. Only change against 16 Sep separates the flood from farming.

## Results slots

Fill these in on Sunday. Write them first on the project page, in this order:

1. "Sentinel-1 called **___ km²** of low-lying vegetated floodplain dry; NISAR L-band shows flood evidence there."
2. "On open water, NISAR scored **F1 ___** vs Sentinel-1's **___**, both judged against Sentinel-2 and Landsat."
3. "On a flood it never saw (north Bihar, 9 Sep), the trust map predicted NISAR's errors with **AUROC ___** vs **___** for the raw signal."
4. "Fifty inspections from the check-first list reach **___%** of flooded settlements vs **___%** ranked by change alone."

## The 30-second video

The 2025 guide limits the demo to a 30-second video or a 7-slide deck, with English subtitles on video ([Project Submission Guide](https://www.spaceappschallenge.org/resources/project-submission-guide/)). Use the video and screen-record the real app, with no AI-generated imagery. The guide requires a visible watermark on AI-made images or video, and it would undercut the Validity pitch anyway.

| Seconds | Picture | Caption |
|---|---|---|
| 0 to 5 | Sentinel-2 true color, 29 Sep, brown water across the plain | "Bihar, 28 Sep 2026. The Gandak hits a record." |
| 5 to 11 | DSWx-S1 flood map, vegetated floodplain dry | "The world's flood maps use C-band radar. It can't see under crops and trees." |
| 11 to 18 | Swipe to NISAR; hidden water appears | "NASA-ISRO's NISAR uses L-band. It can." + result 1 |
| 18 to 24 | Toggle naive difference, then the trust layer | "Not every radar pixel deserves trust. Wallflower knows which." + result 3 |
| 24 to 30 | Check-first list, click a village | "Where to send the boats first." + result 4, name, URL |

## How the judges' criteria map onto it

| Criterion | What answers it | Where the judge sees it |
|---|---|---|
| Influence | A blind spot in operational flood maps, quantified for a 2026 flood that affected millions | Result 1 and the check-first list |
| Creativity | First L-band vs C-band flood comparison on NISAR data, maybe three wavelengths | Hidden-water layer, wavelength chart |
| Validity | Optical referee, held-out event, negative-control test, baselines that include OPERA's own algorithm, stated limits | Results 2 and 3 and a "what this can't tell you" box |
| Relevance | NISAR GCOV throughout; the challenge's own question about which polarizations show change, answered with HH vs HV physics; a time series | The dance animation and the physics panel |
| Presentation | One sentence, one swipe, one number per claim | The video |

## What you are deliberately not doing

- Training a deep segmentation model. No NISAR labels exist.
- Saying "damaged" or "impassable." Flooded and built-up is not damaged.
- Claiming NISAR replaces Sentinel-1. Each NISAR pass direction repeats every 12 days and products land 36 to 72 hours later. It fills Sentinel-1's blind spots; it does not replace Sentinel-1's revisit.
- Claiming global generalization. Both events are in Bihar. Bangladesh is the far-shift stretch goal, and without it the honest claim is "transfers across two Bihar floods."
