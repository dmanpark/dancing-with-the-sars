# Dancing with the SARS: The Hidden Steps

Version 2, 3 Nov 2026 (after the audit in [audit.md](audit.md)). Methods, file formats and done-criteria per role: [build-spec.md](build-spec.md). Preliminary tests to run before kickoff: [../prompts/prelim-tests.md](../prompts/prelim-tests.md).

We use NISAR's newly calibrated L-band radar data to find the flood water that today's C-band flood maps largely miss. We test it on Bihar's record Gandak flood of 28 Sep 2026 against optical satellites, and turn it into a trust-rated list of places to verify first, built in the 39 hours of NASA Space Apps on 14 to 15 Nov 2026.

## Why it matters

The flood maps responders lean on are built from C-band radar, which largely misses water under trees, tall crops and wetland grass. Bihar's 2026 floods are the test case, and NISAR is the first free L-band radar that images all land every 12 days.

**The flood.** Rain over Nepal's Gandak basin from 24 to 27 Sep pushed the river to a record at the Devghat gauge on 27 Sep ([NASA Earth Observatory](https://science.nasa.gov/earth/earth-observatory/rains-swamp-the-gandak-river/)). Downstream at Bagaha in Bihar it reached 91.25 m, above the 2024 record of 90.90 m, with 5.4 lakh cusecs through the Valmikinagar barrage ([Daijiworld](https://daijiworld.com/news/newsDisplay?newsID=1328211), 1 Oct).

- Embankments broke at four places in West Champaran within about 10 hours (Khairatwa, Phuliyakhad, Bathuwaria, Golaghat), plus Areraj in East Champaran and Sheetalpur in Gopalganj ([Daijiworld](https://daijiworld.com/news/newsDisplay?newsID=1328211)). The reports put the breaches on the night of 29 to 30 Sep (India time), after all three of our lead observations.
- About 2.03 lakh people in six districts were affected by 1 Oct ([Telangana Today](https://telanganatoday.com/flood-crisis-deepens-in-bihar-as-embankments-breached-by-gandak-river-across-multiple-districts)). Three weeks earlier, floods on the Kosi and Bagmati had affected about 44 lakh people statewide ([Telangana Today](https://telanganatoday.com/bihar-floods-44-lakh-affected-across-14-districts), 10 Sep).

**The blind spot.** Copernicus GFM and NASA's OPERA DSWx-S1, two global radar flood products, both run on Sentinel-1's 5.5 cm C-band. That wavelength scatters off leaves, so GFM ships an exclusion mask marking dense vegetation as unmappable ([Zhao et al. 2020](https://isprs-annals.copernicus.org/articles/V-1-2020/395/2020/)).

**Why now.** NISAR's 24 cm L-band gets through far more canopy and bounces off the water beneath. Calibrated L-band data went public on 20 Jul 2026 ([ASF](https://nisar-docs.asf.alaska.edu/availability-overview/)), and OPERA still lists its NISAR water product as under development ([JPL OPERA](https://www.jpl.nasa.gov/go/opera/products/dswx-product-suite/)). We found no published NISAR flood evaluation.

**Who uses it.** District teams checking damage and relief needs in the days after a flood (NISAR products arrive 36 to 72 hours after each pass, so this is for verification, not first response), and the people who build global flood maps and need to know where NISAR fills C-band's gap.

## At a glance

NISAR finds the water; two other satellites test how far to trust it.

| Step | Takes in | Does | In the app |
| --- | --- | --- | --- |
| Flood detector | NISAR L-band: HH and HV, lead pass 28 Sep 13:07 UTC, plus five other dates | Open water: HH and HV darken. Under plants: HH brightens. Baselines: log-ratio, DSWx-NI | The dance; two radars; hidden steps |
| Referee | Optical water maps 8 h before and 16 h after; Sentinel-1 as the rival | Scores NISAR against Sentinel-1 (same log-ratio method, and DSWx-S1) on pixels where both optical maps agree and the sky is clear | The results panel |
| Trust map | Copernicus DEM and HAND, ESA WorldCover, NISAR's own masks | Predicts where NISAR is wrong. Fit on north Bihar against C-band; tested on Gandak against the optical referee | Out of step: trust layer, gaps hatched |
| Check-first list | GHSL built-up area, reported breach villages | Ranks 480 m cells by expected flooded built-up area, weighted by trust | Where to look: click a cell to see why |

## What we will show

Four claims. Each headline is a difference with its own interval, and each has a test that could come out against us.

| Claim | Test | Headline we report | It fails if |
| --- | --- | --- | --- |
| **1. Open water, head to head.** NISAR maps new open water at least as well as Sentinel-1. | The same open-water rule on NISAR (HH, HV) and on Sentinel-1 (VV, VH, 17 and 29 Sep RTC), plus OPERA's DSWx-S1, scored only on pixels where both optical maps agree and are cloud-free | F1 difference, NISAR minus Sentinel-1, with a paired 95% interval | The interval's lower end falls below −0.05 (our non-inferiority margin). Reported either way. |
| **2. The hidden steps.** L-band finds flooding under vegetation that C-band calls dry. | On the same vegetated low-ground pixels (HAND < 2 m), the flooded-vegetation flag rate for 16 to 28 Sep minus the rate for the previous 12 days (23 Aug to 4 Sep) | Excess km² flagged where Sentinel-1 saw neither open water nor inundated vegetation | The excess interval includes zero. |
| **3. Trust that transfers.** A trust map built from radar physics predicts NISAR's errors on a flood it never saw. | Fit on north Bihar against C-band (38 minutes apart); test once on Gandak against the optical referee | AUROC for spotting NISAR's errors, minus the AUROC of the raw signal, with a paired interval | The difference's interval includes zero. |
| **4. Check first.** Ranking cells by trust-weighted flooded built-up area finds more flooded settlements. | On Gandak, the first 50 cells of each ranking, scored by the optical referee | How many of the first 50 cells are flooded settlements, against log-ratio flood share × built-up area | The paired difference's interval includes zero. |
| **Tier 3. The phase test.** Double bounce has a signature in the quad-pol phase. | HH-VV phase on the two quad-pol dates (16 Sep, and the partial 10 Oct frame), after ASF's 59° correction | Phase shift toward 180° on flagged pixels against unflagged vegetation | No shift. |
| **Tier 3. Three wavelengths.** Hidden water grows from C-band (5.5 cm) to S-band (9.4 cm) to L-band (24 cm). | Claim 2's test on ISRO's S-band scene, if NISAR recorded one | Excess km² per wavelength | The scene is missing, or the order does not hold. |

The project page opens with these four lines, filled in on Sunday:

1. "On low ground under trees and wetland, NISAR flagged ___ km² more flooding than in the 12 days before, where Sentinel-1 saw dry land."
2. "Of the first 50 places on our list, ___ were flooded settlements; ranking by flood extent alone found ___."
3. "On open water, NISAR's F1 was ___ against Sentinel-1's ___ on the same pixels (difference ___, 95% interval ___ to ___)."
4. "Trained on a different flood, the trust map spotted NISAR's errors with AUROC ___, against ___ for the raw signal."

## The data

Every scene below was found in the ASF and NASA CMR catalogs on 3 Nov. The core download is about 46 GB of NISAR files plus the reference tiles. The fallback and Tier 3 scenes add about 18 GB.

**Lead event: Gandak, NISAR track 149, frame 75** (descending, 20 MHz; about 25.4 to 28.1°N, 81.9 to 85.1°E, covering Bagaha and the West Champaran breach sites).

| Sensor | Before: 16 Sep | Rising river: 28 Sep |
| --- | --- | --- |
| NISAR L-band (GCOV) | 13:07 UTC, quad-pol, 7.9 GB | 13:07 UTC, dual-pol HH + HV, 1.9 GB |
| Optical water maps (OPERA DSWx-HLS) | Sentinel-2B at −8 h; Landsat 8 at +16 h | Sentinel-2C and Landsat 8 at −8 h; Sentinel-2B at +16 h, four tiles at 5 to 12% cloud |
| C-band (OPERA DSWx-S1 maps and RTC-S1 backscatter) | Sentinel-1D at +11 h (15 tiles, 54 bursts) and −1 h (1 tile) | Sentinel-1D at +11 h (15 tiles, 54 bursts) and −1 h (1 tile) |

**Control interval.** 23 Aug (quad-pol) to 4 Sep (dual-pol) on the same track: the same 12-day gap and the same mode order as the lead pair.

**After the breaches.** 10 Oct on track 149 (20 MHz, both dual-pol and a partial quad-pol frame), and 1 Oct at 23:47 UTC on ascending track 26 (40 MHz, with its 19 Sep pre-event scene).

**The dance.** Track 149 repeats at 13:07 UTC every 12 days: 6 Jul, 23 Aug, 4 Sep, 16 Sep, 28 Sep, 10 Oct (20 MHz) and 22 Oct (40 MHz). The browse images already show the flood zone widening by 28 Sep and spreading further by 10 Oct.

**Held-out event: north Bihar, track 48, frame 75** (20 MHz, Kosi and Bagmati plains). NISAR imaged it on 28 Aug and 9 Sep at 12:58 UTC, and Sentinel-1 at 12:20 on both days. OPERA made no water maps for those two passes, so we run OPERA's own DSWx-S1 code on the 56 Sentinel-1 bursts per date. Earlier 20 MHz dates (29 Jun, 11 Jul) feed the trust model.

**Stretch.** ASF flags every Bihar scene as a joint L- and S-band observation; ISRO's S-band files are on [Bhoonidhi](https://bhoonidhi.nrsc.gov.in/NISAR/NisarProducts.html) behind a registration. Southeast Bangladesh (12 Jul, Sentinel-1 13 hours later) is the far-away test.

**Traps we plan around**

- Only PROVISIONAL products (17 Jun 2026 onward). ASF warns against mixing them with the older BETA release, and no data exists from 27 Jul to 10 Aug.
- Tracks alternate between quad-pol and dual-pol from cycle to cycle. Pairs compare on the shared HH and HV channels, and a fixed rule removes any calibration offset over 0.5 dB measured on stable ground.
- NISAR swaths carry along-track gaps whose positions move between dates. A naive difference lights them up as fake change.
- Water is a few percent of the frame, so dark-water thresholds come from 10 km tiles that pass a bimodality test, as OPERA's DSWx does.
- Quad-pol phase needs ASF's 59° correction before any decomposition ([known issues](https://nisar-docs.asf.alaska.edu/provisional-known-issues/)). GCOV has no layover or shadow layer, so we mask slopes above 10° from the Copernicus DEM; the plain itself is flat.

## The demo

A static web map on GitHub Pages: no login, no server, and still loading when global judging runs in December and January. Five layers, each answering one question a judge will ask.

1. **The dance.** The track-149 dates animated, 6 Jul to 22 Oct. The Gandak rises, breaks out and spreads across the plain.
2. **Two radars, one flood.** A swipe between NISAR on 28 Sep and Sentinel-1 eleven hours later.
3. **The hidden steps.** Vegetated pixels where L-band shows flood evidence and Sentinel-1 says dry, in their own color, labeled "evidence, not verified."
4. **Out of step.** The trust layer. NISAR's swath gaps are hatched as "don't trust"; a "naive difference" toggle shows them lighting up as fake change.
5. **Check first.** A ranked list of 480 m cells. Clicking one shows its HH and HV change, its height above the river, its land cover and why it is trusted or not. The reported breach villages sit on the map as pins to compare against.

**The 30-second video.** The 2025 submission guide caps the demo at 30 seconds with English subtitles ([guide](https://www.spaceappschallenge.org/resources/project-submission-guide/)). We screen-record the real app and use no AI-generated imagery. Two numbers carry it, both from the Gandak.

| Seconds | Picture | Caption |
| --- | --- | --- |
| 0 to 5 | The animation: the river spreading across Bihar | "Every monsoon the Gandak dances across Bihar. In 2026 it broke its record." |
| 5 to 11 | Sentinel-1's flood map, vegetated plain left dry | "The world's flood maps use C-band radar. Under trees and wetland, it largely misses the water." |
| 11 to 18 | Swipe to NISAR; the hidden water appears | "NISAR's L-band SAR (synthetic aperture radar) sees the hidden steps: ___ km² Sentinel-1 called dry." |
| 18 to 24 | The naive difference, then the trust layer | "Some pixels fall out of step. We flag which ones to distrust." |
| 24 to 30 | The check-first list; click a village by a breach | "___ of our first 50 checks were flooded villages." + title, link |

## Why the results will hold up

Every claim has a baseline to beat, a referee neither radar depends on and a control that would catch a fake signal.

- **A fair sensor comparison.** The same detection rules run on NISAR and on Sentinel-1, so claim 1 compares radars rather than algorithms. OPERA's DSWx-S1 and DSWx-NI ([opera-adt/DSWX-SAR](https://github.com/opera-adt/DSWX-SAR)) sit beside them for context.
- **A referee neither radar depends on.** Optical water maps 8 hours before and 16 hours after the NISAR pass. We score only pixels where both agree and the sky is clear.
- **New water only.** Permanent rivers and ponds come out first, using JRC surface-water occurrence and the pre-event optical maps.
- **A same-pixel control.** Claim 2 subtracts what the detector flags on the same pixels in the 12 days before the flood, which absorbs crop growth and wet soil.
- **A flood the model never saw.** The trust model is fit on north Bihar and tested once on Gandak, where its targets come from optical satellites rather than C-band.
- **Paired intervals.** Every headline is a difference resampled over 5 km blocks; no random pixel splits.
- **Thresholds fixed before kickoff.** Written in the build spec, with a calibration rule for the quad-pol to dual-pol switch.
- **An outside sanity check.** On the post-breach scene, cells holding the named breach villages should rank near the top. A check, not a score.
- **Right-sized models.** No deep segmentation network: there are no NISAR flood labels. Logistic regression or gradient boosting on physical features.

**What this can't tell you** (this box goes on the project page as written)

- How accurate the map is under canopy. No reference sees there, so claim 2 is evidence of a signal, not an accuracy figure.
- Damage. Flooded and built-up is not the same as damaged.
- Global performance. Both events are in Bihar; the honest claim is "transfers across two Bihar floods."
- Real-time use. Each NISAR pass direction repeats every 12 days and products arrive 36 to 72 hours later, so NISAR fills Sentinel-1's blind spots rather than replacing its revisit.
- Final calibration. These are PROVISIONAL products; the validated reprocessing is due by the end of 2026.

## How it scores

Judges score five criteria, and the guide weights Presentation as heavily as the rest ([Judging & Awards Guide](https://spaceappschallenge.org/resources/judging-awards-guide); the 2026 version comes out on 13 Nov, so recheck then).

| Criterion and the judges' question | What answers it | Where the judge sees it |
| --- | --- | --- |
| **Influence:** how much influence can it have? | A measured blind spot in the world's radar flood maps on a flood that affected lakhs of people, plus a list a district team could use to verify damage | Claims 2 and 4; the check-first layer |
| **Creativity:** has it been attempted before? | The first NISAR flood evaluation we could find: L-band against C-band on one flood, 11 hours apart, with a quad-pol phase check | The hidden-steps layer; the physics panel |
| **Validity:** is it scientifically valid? | Optical referee, a same-pixel control, a cross-event trust test, paired intervals, thresholds fixed in advance, stated limits | The results panel; the limits box |
| **Relevance:** does it answer the challenge? | NISAR throughout. It answers "Which polarizations highlight these changes?" with HH against HV and, in Tier 3, HH-VV phase, and delivers the time-series animation and physical drivers the challenge asks for | The dance; the physics panel |
| **Presentation:** how well is it communicated? | Two plain numbers in a 30-second video cut from the live app | The video; the project page's first lines |

The two global awards it fits best are Best Use of Science and Best Use of Data.

## Scope

Tier 1 alone is a complete submission, and it is done by Saturday evening. Everything after that raises the ceiling without risking the floor. It fits in 39 hours because the data is downloaded before kickoff, the only models are small, and the app is static files. Processing runs in Python (h5py, rasterio, xarray, scikit-learn) on the 3090 machine; the app is MapLibre GL reading PMTiles on GitHub Pages.

| Tier | What | Done by | Owner |
| --- | --- | --- | --- |
| 1 | Gandak pair read, on one grid, swath-gap masks combined, calibration offset checked | Sat 12:00 | Radar |
| 1 | Optical referee, DSWx-S1 and Sentinel-1 log-ratio on the grid | Sat 12:00 | Truth |
| 1 | Log-ratio and two-sided flood maps | Sat 18:00 | Radar |
| 1 | Claim 1 with its paired interval | Sat 18:00 | Truth |
| 1 | Live app with the swipe and the animation on real tiles | Sat 18:00 | Map |
| 1 | Video, project page and the limits box | Sun 19:00 | Story |
| 2 | Claim 2 with the control interval | Sat 18:00 | Radar, Truth |
| 2 | OPERA DSWx-NI baseline, timeboxed to 2 hours | Sat 18:00 | Radar |
| 2 | North Bihar maps and its C-band reference (DSWx-S1 started at 9:05 in the background) | Sat 21:00 | Radar, Truth |
| 2 | Claim 3 (fit on north Bihar, tested on Gandak) and claim 4, in the app | Sun 13:00 | Truth, Map |
| 3 | HH-VV phase test on the quad-pol dates | Sun 13:00 | Radar |
| 3 | S-band, the 1 Oct ascending scene, Bangladesh | Sun 13:00 | Radar, Map |

Tier 3 starts only if Tier 1 and claim 2 are done at the Saturday 18:00 gate.

**Out of scope:** training a deep segmentation model, claims about damage or which roads are passable, a real-time pipeline, and any code written before kickoff ending up in the submission.

## The 39 hours

Core maps and scores land by Sat 18:00, leaving Sunday for trust and the video.

| Role | Sat 9:30 to 12 | Sat 12 to 18 | Sat 18 to 24 | Night, 0 to 8 | Sun 8 to 13 | Sun 13 to 21 |
| --- | --- | --- | --- | --- | --- | --- |
| Radar | Read, grid, calibration check, log-ratio | Two-sided, control pair, DSWx-NI | North Bihar pipeline; post-breach pair | Sleep in shifts | Failure gallery; phase test if Tier 3 | Methods and limits |
| Truth | Start north Bihar DSWx-S1 at 9:05; optical and C-band references | Claim 1; claim 2 | Trust fit on north Bihar | Sleep in shifts | Claims 3 and 4 on Gandak | Final numbers |
| Map | Ancillary layers on the grid, then the map shell | Real tiles live | The animation | Sleep in shifts | Trust layer, list, click panel | Link tests on a phone |
| Story | Breach sites, page skeleton | Summary draft | Storyboard frames | Sleep in shifts | Record the app, first cut | 30 s video, subtitles, fields |

Gates: **12:00** flood visible? · **18:00** Tier 1 and claim 2 done · **Sun 13:00** feature freeze, words only from here · **submit by 21:00** (deadline 23:59 local event time).

If the flood does not show at the 12:00 gate, everyone helps Radar until it does. The 3090 machine runs Radar's and Truth's jobs, with data on WSL2's ext4 disk rather than a Windows drive; Map and Story work on laptops from outputs shared over the local network. With three people, Story folds into Map after Saturday; with five or six, a second Radar takes north Bihar from the start.

## Risks and fallbacks

| Risk | When we know | Fallback |
| --- | --- | --- |
| Downloads too slow before the event | Wed 11 Nov | Harmony variable subsetting: pull only HHHH, HVHV and the mask |
| DSWX-SAR will not install | Fri 13 Nov | The Sentinel-1 two-sided rule on RTC stands in for DSWx-S1 on north Bihar; DSWx-NI is dropped and the methods say so |
| Quad-pol and dual-pol differ by more than 0.5 dB on stable ground | Sun 8 Nov (prelim tests) | The fixed offset rule; if the offset varies across the frame, per-tile offsets, plus claim 1 rerun on 4 Sep → 28 Sep (both dual-pol) as a check |
| Fewer than 5 tiles pass the bimodality test | Sun 8 Nov (prelim tests) | The log-ratio cut alone, stated |
| The HH log-ratio shows no flood | Sat 12:00 | Check dB conversion, mask and HH-to-HH matching; then switch to the ascending pair (19 Sep to 1 Oct, already downloaded) |
| Claim 2's excess interval includes zero | Sat 18:00 | Lead with claims 4 and 1; the physics panel explains why L-band added little here, which is still a finding |
| DSWx-S1 on north Bihar fails | Sat 14:00 | OPERA's DSWx-S1 from 12 Sep (59 hours later), stated, or the Sentinel-1 two-sided rule |
| S-band scenes missing or locked | Sun 8 Nov | Tier 3 runs the phase test only |
| Map tiles too big | Sat 18:00 | WEBP tiles, display at 60 m; analysis resolution unchanged |
| Video runs past 30 seconds | Sun 17:00 | Cut shot 1 |

## Before 14 Nov

The Space Apps FAQ asks teams to "start the actual work when the hackathon begins" ([FAQ](https://legacy.spaceappschallenge.org/resources/faq/)), so this list is accounts, data, setup and feasibility checks. Nothing written before kickoff becomes submission code.

**By Thu 5 Nov**

- [ ] Everyone registered at the same local event, listed on the Members tab, not waitlisted (teams are 1 to 6 people).
- [ ] Everyone has a NASA Earthdata login.
- [ ] One person registers on Bhoonidhi and checks for S-band scenes over the Gandak (28 Sep, about 13:07 UTC) and north Bihar (9 Sep, about 12:58 UTC).
- [ ] Ask the local lead in writing whether cited pre-event tools and throwaway feasibility tests are fine, and whether the event has its own AI-tool rules.
- [ ] Optional: a one-line quote from a Bihar flood-response official or NGO on what they cannot see in current flood maps.

**By Sun 8 Nov: go or no-go**

- [ ] Run the preliminary tests in [../prompts/prelim-tests.md](../prompts/prelim-tests.md) and review `prelim/REPORT.md` as a team.
- [x] Optical and Sentinel-1 water maps exist around both Gandak dates (checked 3 Nov).

**By Fri 13 Nov**

- [ ] Download the rest of the list and the ancillary layers: Copernicus GLO-30 DEM and HAND, ESA WorldCover, JRC surface water, GHSL built-up area.
- [ ] Set up the 3090 machine with WSL2 and conda; DSWX-SAR from source. Confirm it starts.
- [ ] Deploy an empty GitHub Pages site through GitHub Actions and load it on a phone.
- [ ] Assign the four roles: Radar, Truth, Map, Story.
- [ ] Friday night, read the 2026 submission and judging guides when they come out; adjust the storyboard if the rules changed.

## After Space Apps

The hackathon version proves the comparison on one flood and tests transfer on a second. A paper needs the same test on many floods.

1. Rerun everything on NISAR's validated reprocessing when it lands, expected by the end of 2026.
2. Add the other 2026 floods that already have NISAR pairs: Assam, central Indiana, southeast Bangladesh and the Rasuwa debris flow in Nepal.
3. Release the coincident NISAR, Sentinel-1 and optical stack as a small benchmark. We found none like it.
4. Target a remote-sensing venue such as IGARSS or IEEE TGRS, and an ML venue only if the trust method holds beyond floods.

## Sources

Scene and reference lists come from live queries of the ASF search API and NASA CMR on 3 Nov 2026.

- [Rains swamp the Gandak River](https://science.nasa.gov/earth/earth-observatory/rains-swamp-the-gandak-river/), NASA Earth Observatory
- [Bihar flood crisis deepens as Gandak hits record level](https://daijiworld.com/news/newsDisplay?newsID=1328211), Daijiworld, 1 Oct 2026
- [Flood crisis deepens as embankments breached by Gandak](https://telanganatoday.com/flood-crisis-deepens-in-bihar-as-embankments-breached-by-gandak-river-across-multiple-districts), Telangana Today (IANS), 1 Oct 2026
- [Bihar floods: 44 lakh affected across 14 districts](https://telanganatoday.com/bihar-floods-44-lakh-affected-across-14-districts), Telangana Today, 10 Sep 2026
- [NISAR data availability](https://nisar-docs.asf.alaska.edu/availability-overview/) and [provisional known issues](https://nisar-docs.asf.alaska.edu/provisional-known-issues/), ASF
- [NISAR L-band data released](https://www.earthdata.nasa.gov/news/nisar-l-band-data-released-expanding-record-surface-changes), NASA Earthdata, 21 Jul 2026
- [NISAR S-band data products release](https://www.isro.gov.in/ISRO%5FEN/NISARS_Band_SAR_Data_Products_Release.html), ISRO, and [Bhoonidhi NISAR products](https://bhoonidhi.nrsc.gov.in/NISAR/NisarProducts.html)
- [OPERA DSWx product suite](https://www.jpl.nasa.gov/go/opera/products/dswx-product-suite/), NASA JPL; [OPERA DSWx ATBD](https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/web-misc/opera/atbd/D-108763_Rev_A_OPERA_DSWx_S1_NI_ATBD_20240530_SIGNED.pdf); [opera-adt/DSWX-SAR](https://github.com/opera-adt/DSWX-SAR)
- [Deriving exclusion maps from C-band SAR time series](https://isprs-annals.copernicus.org/articles/V-1-2020/395/2020/), Zhao et al., ISPRS Annals 2020
- [ALOS-2 ScanSAR data now available](https://www.earthdata.nasa.gov/news/alos-2-scansar-data-now-available-earthdata), NASA Earthdata
- [GDAL MBTiles driver](https://gdal.org/en/stable/drivers/raster/mbtiles.html) and [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
- [Space Apps 2026](https://www.spaceappschallenge.org/2026/), [Judging & Awards Guide](https://spaceappschallenge.org/resources/judging-awards-guide), [Project Submission Guide](https://www.spaceappschallenge.org/resources/project-submission-guide/) and [participant FAQ](https://legacy.spaceappschallenge.org/resources/faq/)
