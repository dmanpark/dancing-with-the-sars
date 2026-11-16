# Literature matrix (first pass)

About fifteen targeted searches on 3 Nov 2026. This is a map of what to read, not a finished review. Rows marked "abstract only" were checked at the abstract or landing page; read the full paper before citing a number from it.

## Uncertainty, reliability and "when to distrust SAR"

| Work | Data | What it contributes | Baselines / evaluation | What it leaves open for us |
|---|---|---|---|---|
| Krullikowski et al., [arXiv 2304.12488](https://arxiv.org/abs/2304.12488) (2023). GFM ensemble likelihoods. Abstract only. | Sentinel-1 | Three independent flood algorithms, likelihoods harmonized to 0 to 100 and averaged. This is the uncertainty layer in Copernicus GFM. | Two sites: Myanmar flood, Somalia (hard case). Ensemble reduced false detections in Somalia. | The abstract does not show the likelihoods are calibrated against errors. C-band only. |
| Zhao, Chini, Pelich, Matgen, Hostache, Cao, Wagner, [ISPRS Annals V-1-2020](https://isprs-annals.copernicus.org/articles/V-1-2020/395/2020/). Exclusion maps. | Sentinel-1 IW, 20 m, River Severn and Lake Maggiore | Defines exclusion maps: where SAR change detection cannot see water (shadow, layover, urban, dense vegetation). The idea behind GFM's exclusion mask. | About 63% agreement with references | Static per-location mask. At L-band, "dense vegetation" should shrink, and nobody has measured by how much. |
| Hertel, Chow, Wani, Wieland, Martinis, [RSE 285, 113388](https://doi.org/10.1016/j.rse.2022.113388) (2023) | Sentinel-1 GRD | Variational Bayesian CNN vs MC dropout for water segmentation, with uncertainty judged at data, model, tile and scene level | MC dropout tends to be overconfident; the Bayesian CNN is recommended | Single sensor. Whether the uncertainty survives a move to a new event and a new wavelength. |
| Konidakis, Panayidou, Tsagkatakis, Tsakalides, IGARSS 2025, [doi:10.1109/IGARSS55030.2025.11242848](https://doi.org/10.1109/IGARSS55030.2025.11242848). Abstract only. | Sentinel-2 | Conformal prediction on a bitemporal U-Net for floods | Inductive CP is weak with scarce data; CV+ balances better | Optical. Standard conformal guarantees assume calibration and test data are exchangeable, which a new flood event breaks. |
| OPERA DSWx-S1/NI ATBD, JPL D-108763 Rev A (2024), [PDF](https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/web-misc/opera/atbd/D-108763_Rev_A_OPERA_DSWx_S1_NI_ATBD_20240530_SIGNED.pdf) | Sentinel-1 RTC; NISAR GCOV | Kittler-Illingworth thresholds on bimodal tiles, fuzzy logic over intensity, slope, HAND and JRC occurrence, region growing, a CONF layer. Inundated vegetation from the co-pol / cross-pol ratio with land-cover-specific thresholds for NISAR. | OPERA cal/val | Single-date water map, not change detection. The NISAR version is unreleased, and the public code ([opera-adt/DSWX-SAR](https://github.com/opera-adt/DSWX-SAR)) notes full-pol mode is still to be added. **This is your strongest baseline.** |

## Flood datasets and cross-event evaluation

| Work | Data | Contribution | Open for us |
|---|---|---|---|
| Bountos et al., Kuro Siwo, [NeurIPS 2024 Datasets & Benchmarks](https://proceedings.neurips.cc/paper_files/paper/2024/hash/43612b0662cb6a4986edf859fd6ebafe-Abstract.html) | Sentinel-1, multi-temporal, global | Large annotated SAR flood benchmark across many events | C-band. Useful as a pattern for event-held-out splits. |
| Bonafilia et al., Sen1Floods11, CVPR Workshops 2020. Not re-checked in this pass. | Sentinel-1 and Sentinel-2 | Hand-labeled chips from 11 events with a held-out event for testing | Same |

## L-band and flooded vegetation

| Work | Data | Contribution | Open for us |
|---|---|---|---|
| Hübinger, Fluet-Chouinard, Escobar, Jaramillo, [EGU26-9354](https://meetingorganizer.copernicus.org/EGU26/EGU26-9354.html). Abstract only. | ALOS PALSAR-1/2 L-band InSAR, Atrato (Colombia), Pastaza (Amazon) | InSAR maps more inundation in dense vegetation than intensity thresholding; about 70% agreement with existing L-band inundation products. Expects NISAR inundation products to rely mainly on backscatter thresholding. | Not NISAR data. Uses InSAR coherence, which NISAR GUNW / GSLC could also provide. |
| Chapman et al., Mapping regional inundation with spaceborne L-band SAR, [Remote Sensing 7(5), 5440](https://www.mdpi.com/2072-4292/7/5/5440) (2015). Title only. | ALOS PALSAR | Regional L-band wetland inundation mapping | Read for the physics and the classification features they used |

## Decisions under a verification budget

| Work | Contribution | Open for us |
|---|---|---|
| Vinaykumar and Kamasani, ALTIS, [arXiv 2603.13803](https://arxiv.org/abs/2603.13803) (Mar 2026). Abstract only. | Sentinel-1 change detection, DEM depth, parcel statistics and NFIP claims combined into a confidence-scored triage ranking for Hurricane Harvey. Reports an "Inspection Reduction Rate." | The abstract frames results as preliminary design targets. No fixed-budget recall@K against trivial rankings. |
| Lu, Kluger, Bates, Wang, [arXiv 2602.10045](https://arxiv.org/abs/2602.10045) (Feb 2026) | Conformal prediction sets for instance segmentation (agricultural fields, cells, vehicles) | A method to borrow, not a competitor |
| Xu, Guo, Wei, [arXiv 2512.12844](https://arxiv.org/abs/2512.12844) (Dec 2025) | Selective conformal risk control: abstain first, then calibrate on what is kept | Directly the "abstain, then guarantee" structure the doc's direction 3 wants |

## What I did not find

- Any published flood mapping evaluation using NISAR L-band data against an independent reference.
- A reliability or abstention map for SAR flood mapping evaluated on whether it predicts errors on an event it was not tuned on.
- A fixed-budget inspection comparison (recall@K) against change-magnitude and exposure-only rankings.

"Did not find" after fifteen searches is weak evidence. The first one is also the one most likely to stop being true in the next few weeks.

## Still to read before the event

- The GFM product definition (layers, exclusion mask rules). The EODC wiki page did not render for me: [extwiki.eodc.eu/GFM](https://extwiki.eodc.eu/GFM/PDD/GFM_Product_Output_Layers).
- Hess et al. on L-band (SIR-C, JERS-1) flooded forest in the Amazon, for the double-bounce physics.
- NISAR first-results talks from the 2026 science team meeting, IGARSS 2026 and AGU 2026 abstracts.
