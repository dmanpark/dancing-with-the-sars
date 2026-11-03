# Review of the "Dancing with the SARS" research line

Checked on 3 Nov 2026 against the Space Apps site, ASF's NISAR documentation and a live query of the ASF catalog (`prep/find_scenes.py`). Space Apps starts on 14 Nov, eleven days from now.

**Update, later on 3 Nov:** the plan that came out of this review is in [concept.md](concept.md), and the schedule is in [playbook.md](playbook.md). Two findings since the first pass: Sentinel-2 water maps bracket the Gandak NISAR pass at −8 h and +16 h, and the north Bihar floods replace Bangladesh as the held-out event.

## Verdict

**Go on SAR flood mapping, but change the research question.**

The data question is settled. PROVISIONAL L-band GCOV pre/post pairs exist for every 2026 flood I checked, and one of them is close to ideal: NISAR imaged the Gandak River floodplain in Bihar on 28 Sep 2026 at 13:07 UTC, one day after the river hit a record level at the Devghat gauge, and Sentinel-1D passed over the same area about 11 hours later. That gives you an L-band and a C-band look at the same flood on nearly the same day. The early-September floods in north Bihar have an even tighter pairing (Sentinel-1 38 minutes before NISAR, on both the pre and post dates), which makes them the held-out event.

The research question as written does not survive a literature check. Directions 1 to 4 in the doc (physics-aware masking, reliability under shift, abstention, decision-aware ranking) each already exist for Sentinel-1, some of them as operational products. What I could not find anywhere is the same work done with L-band. So the question I would take into the event is:

> Where C-band flood maps have to give up (vegetated floodplains, the areas inside GFM's exclusion mask), does NISAR's L-band recover the flooding? And can a reliability map built from radar physics predict where the detector is wrong on a flood it was never tuned on?

The ranked inspection list stays as the demo layer on top of that. It is the part judges will see, and it is a fair test of whether the reliability map is worth anything.

## The biggest problem: the novelty claim

Every direction in the doc has prior art. All of it is C-band or optical.

| Direction in the doc | Already done by | What is left |
|---|---|---|
| Physics-aware masking, "when to distrust" | Copernicus GFM ships an exclusion mask for shadow, layover, urban and dense vegetation, built on [Zhao et al. 2020](https://isprs-annals.copernicus.org/articles/V-1-2020/395/2020/). OPERA's DSWx masks with HAND, slope and land cover. | Nothing for L-band, where dense vegetation stops being a blind spot. |
| Uncertainty that tracks errors | GFM's ensemble likelihood ([Krullikowski et al. 2023](https://arxiv.org/abs/2304.12488)); Bayesian CNN vs MC dropout with a reliability evaluation ([Hertel et al. 2023, RSE 285](https://doi.org/10.1016/j.rse.2022.113388)); conformal prediction on Sentinel-2 floods (Konidakis et al., IGARSS 2025) | Whether uncertainty still tracks errors on a new event and a new wavelength. |
| Cross-event generalization | Kuro Siwo (NeurIPS 2024 Datasets track) and Sen1Floods11's held-out event | Nothing on NISAR, because NISAR flood labels do not exist yet. |
| Ranking where to inspect | ALTIS ([arXiv 2603.13803](https://arxiv.org/abs/2603.13803), Mar 2026): confidence-scored triage from Sentinel-1, Hurricane Harvey | Its results are preliminary design targets. A budgeted recall@K comparison against trivial rankings is still open. |

Three facts make the L-band angle real rather than a relabeling:

- OPERA lists DSWx-NI (the NISAR water product) as "Under Development." There is no operational NISAR flood or water map to compete with.
- The DSWx-NI code is public in [opera-adt/DSWX-SAR](https://github.com/opera-adt/DSWX-SAR) (`src/dswx_sar/dswx_ni.py`), and a comment in it says full-polarization mode is still to be added. Many NISAR land tracks are quad-pol.
- [Hübinger et al. (EGU26-9354)](https://meetingorganizer.copernicus.org/EGU26/EGU26-9354.html) expect NISAR's inundation products to lean on backscatter thresholding, and report that thresholding underestimates flooding in densely vegetated floodplains at L-band.

The challenge text also asks, word for word, "Which polarizations highlight these changes on land and ice?" A project about HH double-bounce under canopy answers that directly, which is the Relevance criterion.

My search was about fifteen targeted queries, not the 8 to 12 paper review the doc asks for. NISAR first-results papers are appearing now, so someone should search arXiv and the IGARSS 2026 program for "NISAR flood" again the week of the event.

## The ground-truth problem lands exactly where L-band helps

This is the part I am least sure how to solve.

Optical imagery cannot see water under a forest canopy. The independent references you can get for the 2026 events are Sentinel-1 products (OPERA DSWx-S1, GFM) and optical water maps (OPERA DSWx-HLS from Sentinel-2 and Landsat, coarse MODIS). C-band and optical are both blind under canopy. So the claim "L-band finds flooding that C-band misses" cannot be scored against any reference map available to you during the hackathon. The reference will call those pixels dry.

What you can do in 39 hours:

1. Score accuracy only where the reference is trustworthy: open water outside GFM's exclusion mask.
2. In vegetated areas, show the mechanism (HH brightens from trunk-water double bounce, more than HV does, which is the opposite sign from open water darkening) and indirect plausibility: low HAND, hydraulic connection to the river, consistency with the gauge level.
3. Say plainly in the submission that the vegetated-flood claim is evidence, not a validated accuracy number. That is exactly what the Validity criterion asks about.

A real fix needs field reports, or ALOS-2 / ALOS-4 L-band scenes acquired within hours of NISAR. I did not check whether JAXA has any over the Gandak or what access would take.

## Other corrections

**The build window is about 39 hours, not 48.** Submissions open Saturday 14 Nov at 9:00 AM local time and close Sunday 15 Nov at 11:59 PM local time ([spaceappschallenge.org/2026](https://www.spaceappschallenge.org/2026/)).

**The judging criteria are Influence, Creativity, Validity, Relevance and Presentation** ([Judging & Awards Guide](https://spaceappschallenge.org/resources/judging-awards-guide)). "NASA data usage" is not one of them; Best Use of Data is one of the ten global awards. The guide says Presentation counts as much as the others. The page I read still carries 2024 dates, so check whether a 2026 version replaces it.

**Don't plan on training a deep segmentation model.** There are no NISAR flood labels. The public flood datasets are Sentinel-1 VV/VH at C-band, while NISAR over land is mostly HH/HV at L-band, so a pretrained model would face a shift in both polarization and wavelength. With two or three events, a per-pixel logistic regression or gradient-boosted model on physical features, validated with one event held out, is the right size. Labels are the constraint, not the 3090.

**The strongest baseline is OPERA's own algorithm, not a log-ratio threshold.** Run DSWx-NI from the public code on the same GCOV frames. If your method only beats a hand-tuned log-ratio, the first question from anyone who knows the field will be why you skipped the algorithm NASA is building for exactly this data.

**NISAR has data traps the doc does not mention.** Details are in [data.md](data.md); the ones that change the plan:

- Tracks alternate radar modes between cycles, so many 12-day pairs mix quad-pol and dual-pol. Compare on the shared HH and HV channels.
- The Gandak browse images show dark along-track stripes whose positions differ between the 16 Sep and 28 Sep dates. ASF describes three to six SweepSAR gaps across the swath in quad-pol areas. A naive difference image will show fake change at every stripe edge. This is also a great on-screen example of an observation the system should refuse to trust.
- Quad-pol phase between channels is not fully calibrated. ASF gives a 59° correction that has to be applied before any decomposition that uses the HH-VV phase.
- GCOV has no layover/shadow layer (ASF lists one only for GSLC). Derive it from the DEM and geometry.
- A pre/post pair is 10 to 17 GB. Use Harmony's GCOV variable subsetting (released June 2026) to pull only HHHH, HVHV and the mask.

## Go / no-go

**Go**, if three checks pass by Sunday 8 Nov:

1. Someone with an Earthdata login downloads the Gandak pair (track 149, frame 75, 16 Sep and 28 Sep) and the HH log-ratio shows flooding along the Gandak where NASA's MODIS image of 29 Sep does.
2. ~~GFM or DSWx-S1 output exists for the Sentinel-1D pass of 29 Sep 00:19 UTC over that frame.~~ Passed: OPERA DSWx-S1 has 15 tiles for that pass, and DSWx-HLS has optical water maps (Sentinel-2 and Landsat 8) at −8 h and +16 h.
3. The GCOV mask layer explains the stripes, so you know whether they are no-data or low-signal.

What would downgrade the idea: if the L-band map and the GFM map agree everywhere, including in vegetated floodplain, then H1 in [concept.md](concept.md) is dead. Fall back to H0 and H2 (open-water head-to-head, and reliability across two events), which is still a defensible result and still uses NISAR-specific physics.

I did not investigate CLPS. With the SAR data confirmed, I would not spend prep days on it.
