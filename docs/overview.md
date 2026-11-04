# Dancing with the SARS: The Hidden Steps

Version 3, 3 Nov 2026. Reshaped around the interactive app: the app comes first, claims 1 and 2 are the proof underneath it, and the trust map and check-first list move to Tier 3. Every audit fix from version 2 still applies ([audit.md](audit.md)). Methods, file formats and done-criteria per role: [build-spec.md](build-spec.md). Preliminary tests to run before kickoff: [../prompts/setup.md](../prompts/setup.md).

A web app that shows anyone the flood water that today's radar flood maps miss. Bihar's Gandak River hit a record on 27 Sep 2026. NISAR's L-band radar imaged it on 28 Sep and Sentinel-1's C-band radar eleven hours later. One slider moves between the two maps, and the water hiding under trees and crops appears. We check it against optical satellites and show the pixels we can't trust. Built in the 39 hours of NASA Space Apps, 14 to 15 Nov 2026.

## Why the app comes first

The challenge asks for "an interactive application" with "intuitive tools and innovative visualizations… that make NISAR data accessible to a broad audience." Projects pass three rounds of judges: local judges at our event, then NASA and partner-agency experts, then an executive committee ([Judging & Awards Guide](https://www.spaceappschallenge.org/resources/judging-awards-guide)). Only the middle round is likely to know radar. The 2025 global winners were all things a non-expert gets in seconds: an interactive dashboard won Best Use of Science, and farming mini-games won Art & Technology ([NASA](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-announces-2025-international-space-apps-challenge-global-winners/)). Version 2 was shaped like a research paper. Version 3 keeps its two strongest tests and puts them behind something a judge can play with.

The realistic target is the top 10% of our local event, which makes us a Global Nominee (the guide says the Universal Event picks about one nominee per ten projects). In 2025 there were more than 11,500 submissions, 45 global finalists and 10 winners, so nothing past that round can be planned for.

## Why it matters

**The flood.** Rain over Nepal's Gandak basin from 24 to 27 Sep pushed the river to a record at the Devghat gauge on 27 Sep ([NASA Earth Observatory](https://science.nasa.gov/earth/earth-observatory/rains-swamp-the-gandak-river/)). Downstream at Bagaha in Bihar it reached 91.25 m, above the 2024 record of 90.90 m, with 5.4 lakh cusecs through the Valmikinagar barrage ([Daijiworld](https://daijiworld.com/news/newsDisplay?newsID=1328211), 1 Oct).

- Embankments broke at four places in West Champaran within about 10 hours (Khairatwa, Phuliyakhad, Bathuwaria, Golaghat), plus Areraj in East Champaran and Sheetalpur in Gopalganj ([Daijiworld](https://daijiworld.com/news/newsDisplay?newsID=1328211)). The reports put the breaches on the night of 29 to 30 Sep (India time), after all three of our lead observations.
- About 2.03 lakh people in six districts were affected by 1 Oct ([Telangana Today](https://telanganatoday.com/flood-crisis-deepens-in-bihar-as-embankments-breached-by-gandak-river-across-multiple-districts)). Three weeks earlier, floods on the Kosi and Bagmati had affected about 44 lakh people statewide ([Telangana Today](https://telanganatoday.com/bihar-floods-44-lakh-affected-across-14-districts), 10 Sep).

**The blind spot.** Copernicus GFM and NASA's OPERA DSWx-S1, two global radar flood products, both run on Sentinel-1's 5.5 cm C-band. That wavelength scatters off leaves, so GFM ships an exclusion mask marking dense vegetation as unmappable ([Zhao et al. 2020](https://isprs-annals.copernicus.org/articles/V-1-2020/395/2020/)).

**Why now.** NISAR's 24 cm L-band gets through far more canopy and bounces off the water beneath. Calibrated L-band data went public on 20 Jul 2026 ([ASF](https://nisar-docs.asf.alaska.edu/availability-overview/)), and OPERA still lists its NISAR water product as under development ([JPL OPERA](https://www.jpl.nasa.gov/go/opera/products/dswx-product-suite/)). We found no published NISAR flood evaluation. NISAR is the first free L-band radar that images all land every 12 days.

**Who it's for.** Anyone curious what a radar sees, teachers explaining it, and two groups who would act on it: district teams verifying damage in the days after a flood (NISAR products arrive 36 to 72 hours after each pass, so this is for verification, not first response), and the people who build global flood maps and need to know where NISAR fills C-band's gap.

## The app

One page. The map fills the screen. A step card sits at the bottom on a phone and at the side on a laptop, with Next and Back; "Explore" leaves the tour at any step. Static files on GitHub Pages: no login, no server, still loading when global judging runs in December and January.

| Step | What you see | What it tells you | Behind it |
| --- | --- | --- | --- |
| **1. The dance** | NISAR's view of the Gandak every 12 days, 6 Jul to 22 Oct, animated, with the date in the corner | The river rises, breaks out and spreads across the plain | Seven track-149 dates, one fixed gray stretch |
| **2. Two radars** | A slider between Sentinel-1's flood map (29 Sep) and NISAR's (28 Sep) | Where the two radars agree, and where only one sees water | The same detection rules run on both |
| **3. The hidden steps** | Flooded ground under vegetation that Sentinel-1 called dry, in its own color, labeled "evidence, not verified," with the km² figure. Two small diagrams: open water as a mirror; water under trees bouncing the signal off trunks and back | Why L-band finds water C-band misses, and which polarization shows it (HH brightens, HV much less) | Claim 2 |
| **4. Listen** | Tap any spot: a small chart of HH and HV across the seven dates, and the same series played as sound. Two voices; open water drops low and quiet, flooded forest jumps up | The flood as something you hear, at any pixel you pick | A coarse time-series grid shipped with the app |
| **5. How we know** | The optical satellite referee, the two headline numbers with intervals, a toggle that hatches NISAR's swath gaps and shows the fake change a naive difference makes, and the limits box | What to believe, and what not to | Claim 1, the valid mask |
| **Explore** | Every layer with a legend; the reported breach villages as pins | Free browsing | All of the above |

Tier 3 adds a sixth step, **Check first**: the trust map and a ranked list of 480 m cells to verify, each with the reason it was ranked.

## What we will show

Two claims carry the project. Each headline is a difference with its own interval, and each has a test that could come out against us.

| Claim | Test | Headline we report | It fails if |
| --- | --- | --- | --- |
| **1. Open water, head to head.** NISAR maps new open water at least as well as Sentinel-1. | The same open-water rule on NISAR (HH, HV) and on Sentinel-1 (VV, VH, 17 and 29 Sep RTC), plus OPERA's DSWx-S1, scored only on pixels where both optical maps agree and are cloud-free | F1 difference, NISAR minus Sentinel-1, with a paired 95% interval | The interval's lower end falls below −0.05 (our non-inferiority margin). Reported either way. |
| **2. The hidden steps.** L-band finds flooding under vegetation that C-band calls dry. | On the same vegetated low-ground pixels (HAND < 2 m), the flooded-vegetation flag rate for 16 to 28 Sep minus the rate for the previous 12 days (23 Aug to 4 Sep) | Excess km² flagged where Sentinel-1 saw neither open water nor inundated vegetation | The excess interval includes zero. |

Tier 3, only if Tier 1 is done at the Saturday 18:00 gate:

| Claim | Test | It fails if |
| --- | --- | --- |
| **3. Trust that transfers.** A trust map built from radar physics predicts NISAR's errors on a flood it never saw. | Fit on north Bihar against C-band (38 minutes apart); test once on Gandak against the optical referee. AUROC minus the raw signal's | The difference's interval includes zero |
| **4. Check first.** Ranking cells by trust-weighted flooded built-up area finds more flooded settlements. | Gandak, first 50 cells, scored by the optical referee, against log-ratio flood share × built-up area | The paired difference's interval includes zero |
| **The phase test.** Double bounce has a signature in the quad-pol phase. | HH-VV phase on 16 Sep and the partial 10 Oct quad-pol frame, after ASF's 59° correction | No shift toward 180° |
| **Three wavelengths.** Hidden water grows from C-band (5.5 cm) to S-band (9.4 cm) to L-band (24 cm). | Claim 2's test on ISRO's S-band scene, if NISAR recorded one | The scene is missing, or the order does not hold |

The project page opens with these lines, filled in on Sunday:

1. "On low ground under trees and wetland, NISAR flagged ___ km² more flooding than in the 12 days before, where Sentinel-1 saw dry land."
2. "On open water, NISAR's F1 was ___ against Sentinel-1's ___ on the same pixels (difference ___, 95% interval ___ to ___)."

## The data

Every scene below was found in the ASF and NASA CMR catalogs on 3 Nov. Tiers 1 and 2 need about 30 GB of NISAR files plus the reference tiles. North Bihar (Tier 3), the fallback pair and the quad-pol phase scene add about 32 GB.

**Lead event: Gandak, NISAR track 149, frame 75** (descending, 20 MHz; about 25.4 to 28.1°N, 81.9 to 85.1°E, covering Bagaha and the West Champaran breach sites).

| Sensor | Before: 16 Sep | Rising river: 28 Sep |
| --- | --- | --- |
| NISAR L-band (GCOV) | 13:07 UTC, quad-pol, 7.9 GB | 13:07 UTC, dual-pol HH + HV, 1.9 GB |
| Optical water maps (OPERA DSWx-HLS) | Sentinel-2B at −8 h; Landsat 8 at +16 h | Sentinel-2C and Landsat 8 at −8 h; Sentinel-2B at +16 h, four tiles at 5 to 12% cloud |
| C-band (OPERA DSWx-S1 maps and RTC-S1 backscatter) | Sentinel-1D at +11 h (15 tiles, 54 bursts) and −1 h (1 tile) | Sentinel-1D at +11 h (15 tiles, 54 bursts) and −1 h (1 tile) |

**Control interval.** 23 Aug (quad-pol) to 4 Sep (dual-pol) on the same track: the same 12-day gap and the same mode order as the lead pair.

**The dance.** Track 149 repeats at 13:07 UTC every 12 days: 6 Jul, 23 Aug, 4 Sep, 16 Sep, 28 Sep, 10 Oct (20 MHz) and 22 Oct (40 MHz). The browse images already show the flood zone widening by 28 Sep and spreading further by 10 Oct, after the breaches.

**After the breaches.** 10 Oct on track 149 (in the dance, plus a partial quad-pol frame for the phase test), and 1 Oct at 23:47 UTC on ascending track 26 (40 MHz, with its 19 Sep pre-event scene), the fallback pair.

**Tier 3: north Bihar, track 48, frame 75** (20 MHz, Kosi and Bagmati plains). NISAR imaged it on 28 Aug and 9 Sep at 12:58 UTC, and Sentinel-1 at 12:20 on both days. OPERA made no water maps for those passes, so we run OPERA's own DSWx-S1 code on the 56 Sentinel-1 bursts per date. Earlier 20 MHz dates (29 Jun, 11 Jul) feed the trust model. It is downloaded before the event so Tier 3 is possible, and used only if Tier 1 is done at 18:00.

**Stretch.** ASF flags every Bihar scene as a joint L- and S-band observation; ISRO's S-band files are on [Bhoonidhi](https://bhoonidhi.nrsc.gov.in/NISAR/NisarProducts.html) behind a registration.

**Traps we plan around**

- Only PROVISIONAL products (17 Jun 2026 onward). ASF warns against mixing them with the older BETA release, and no data exists from 27 Jul to 10 Aug.
- Tracks alternate between quad-pol and dual-pol from cycle to cycle. Pairs compare on the shared HH and HV channels, and a fixed rule removes any calibration offset over 0.5 dB measured on stable ground.
- NISAR swaths carry along-track gaps whose positions move between dates. A naive difference lights them up as fake change; the app shows this on purpose in step 5.
- Water is a few percent of the frame, so dark-water thresholds come from 10 km tiles that pass a bimodality test, as OPERA's DSWx does.
- Quad-pol phase needs ASF's 59° correction before any decomposition ([known issues](https://nisar-docs.asf.alaska.edu/provisional-known-issues/)). GCOV has no layover or shadow layer, so we mask slopes above 10° from the Copernicus DEM; the plain itself is flat.

## The 30-second video

The 2025 submission guide caps the demo at 30 seconds with English subtitles ([guide](https://www.spaceappschallenge.org/resources/project-submission-guide/)). We screen-record the real app with its real sound, and use no AI-generated imagery. Two numbers carry it, both from the Gandak.

| Seconds | Picture | Caption |
| --- | --- | --- |
| 0 to 5 | Step 1: the river spreading across Bihar | "Every monsoon the Gandak dances across Bihar. In 2026 it broke its record." |
| 5 to 11 | Sentinel-1's flood map, vegetated plain left dry | "The world's flood maps use C-band radar. Under trees and crops, it largely misses the water." |
| 11 to 19 | The slider drags across; the hidden water appears | "NISAR's L-band SAR (synthetic aperture radar) sees through: ___ km² of flooding Sentinel-1 called dry." |
| 19 to 25 | A finger taps a field; the chart draws and the sound plays | "Tap any field and hear its radar change as the water arrives." |
| 25 to 30 | Step 5: the referee and the swath-gap toggle; title and link | "On open water it keeps up with Sentinel-1 (F1 ___ vs ___). Checked against optical satellites." |

## Why the results will hold up

- **A fair sensor comparison.** The same detection rules run on NISAR and on Sentinel-1, so claim 1 compares radars rather than algorithms. OPERA's DSWx-S1 and DSWx-NI ([opera-adt/DSWX-SAR](https://github.com/opera-adt/DSWX-SAR)) sit beside them for context.
- **A referee neither radar depends on.** Optical water maps 8 hours before and 16 hours after the NISAR pass. We score only pixels where both agree and the sky is clear.
- **New water only.** Permanent rivers and ponds come out first, using JRC surface-water occurrence and the pre-event optical maps.
- **A same-pixel control.** Claim 2 subtracts what the detector flags on the same pixels in the 12 days before the flood, which absorbs crop growth and wet soil.
- **Paired intervals.** Every headline is a difference resampled over 5 km blocks; no random pixel splits.
- **Thresholds fixed before kickoff.** Written in the build spec, with a calibration rule for the quad-pol to dual-pol switch.
- **Errors shown, not hidden.** The swath-gap toggle and the "evidence, not verified" label are in the app, where judges see them.

**What this can't tell you** (this box goes in the app and on the project page as written)

- How accurate the map is under canopy. No reference sees there, so claim 2 is evidence of a signal, not an accuracy figure.
- Damage. Flooded and built-up is not the same as damaged.
- Global performance. This is one flood in Bihar.
- Real-time use. Each NISAR pass direction repeats every 12 days and products arrive 36 to 72 hours later, so NISAR fills Sentinel-1's blind spots rather than replacing its revisit.
- Final calibration. These are PROVISIONAL products; the validated reprocessing is due by the end of 2026.

## How it scores

Judges score five criteria, and the guide weights Presentation as heavily as the rest (the 2026 guide comes out on 13 Nov, so recheck then).

| Criterion and the judges' question | What answers it | Where the judge sees it |
| --- | --- | --- |
| **Influence:** how much influence can it have? | A blind spot in the radar flood maps used for floods like this one, shown so anyone can see it; Tier 3 turns it into a list a district team could use | Steps 2 and 3 |
| **Creativity:** has it been attempted before? | The first NISAR flood comparison we could find, two radars on one flood 11 hours apart, and radar you can listen to | Steps 3 and 4 |
| **Validity:** is it scientifically valid? | Optical referee, a same-pixel control, paired intervals, thresholds fixed in advance, errors and limits shown in the app | Step 5 |
| **Relevance:** does it answer the challenge? | An interactive application that makes NISAR accessible to a broad audience, with the time-series animation, the polarization answer (HH against HV) and the physical drivers the challenge asks for | Steps 1, 3 and 4 |
| **Presentation:** how well is it communicated? | One slider moment, two plain numbers, a 30-second video cut from the live app, and it works on a phone | The video; the first view |

Best Use of Data and Best Storytelling fit best. Art & Technology fits if the listening step is good, which we only learn on Saturday night.

## Scope

Tier 1 alone is a complete submission, and it is done by Saturday evening. Everything after that raises the ceiling without risking the floor. It fits in 39 hours because the data is downloaded before kickoff, there are no trained models below Tier 3, and the app is static files. Processing runs in Python (h5py, rasterio, xarray, scikit-learn) on the 3090 machine; the app is MapLibre GL reading PMTiles on GitHub Pages, with sound from the browser's Web Audio API.

| Tier | What | Done by | Owner |
| --- | --- | --- | --- |
| 1 | Gandak pair read, on one grid, masks combined, calibration offset checked | Sat 12:00 | Radar |
| 1 | Optical referee, DSWx-S1 and the Sentinel-1 rules on the grid | Sat 12:00 | Truth |
| 1 | Log-ratio and two-sided flood maps, lead pair and control pair | Sat 18:00 | Radar |
| 1 | Claims 1 and 2 with their paired intervals | Sat 18:00 | Truth |
| 1 | App live with steps 1 and 2 on real tiles (the dance and the slider) | Sat 18:00 | App |
| 1 | Video, project page and the limits box | Sun 19:00 | Story |
| 2 | Steps 3 and 5: hidden-steps layer, diagrams, referee panel, swath-gap toggle | Sun 13:00 | App, Story, Truth |
| 2 | Step 4: the listening grid and the sound | Sun 13:00 | Radar, App |
| 2 | OPERA DSWx-NI baseline, timeboxed to 2 hours | Sat 24:00 | Radar |
| 3 | North Bihar pipeline, claims 3 and 4, the Check first step | Sun 13:00 | Radar, Truth, App |
| 3 | HH-VV phase test; S-band; the ascending post-breach scene | Sun 13:00 | Radar |

**Out of scope:** training a deep segmentation model, claims about damage or which roads are passable, a real-time pipeline, and any code written before kickoff ending up in the submission.

## The 39 hours

Core maps and both numbers land by Sat 18:00. Saturday night goes to the parts of the app judges remember; Sunday morning goes to polish and the video.

| Role | Sat 9:30 to 12 | Sat 12 to 18 | Sat 18 to 24 | Night, 0 to 8 | Sun 8 to 13 | Sun 13 to 21 |
| --- | --- | --- | --- | --- | --- | --- |
| Radar | Read, grid, calibration check, log-ratio | Two-sided maps, control pair; series batch in the background | Listening grid; DSWx-NI | Sleep in shifts | North Bihar if Tier 3; otherwise a gallery of where NISAR fails | Methods and limits |
| Truth | Start north Bihar DSWx-S1 at 9:05 in the background; optical and C-band references | Claims 1 and 2 | Numbers and failure examples for step 5 | Sleep in shifts | Claims 3 and 4 if Tier 3; otherwise recheck every number | Final numbers on the page |
| App | Ancillary layers on the grid, then the app shell deployed | Real tiles, the dance, the slider | Step 4 sound and chart; step 3 layer | Sleep in shifts | Step 5, the tour, phone polish | Link tests on a phone |
| Story | Breach sites; page skeleton; storyboard | Summary draft; the two diagrams | Tune the sound with App; storyboard frames | Sleep in shifts | Record the app, first cut | 30 s video, subtitles, page fields |

Gates: **12:00** flood visible? · **18:00** Tier 1 done (both numbers, steps 1 and 2 live) · **Sun 13:00** feature freeze, words only from here · **submit by 21:00** (deadline 23:59 local event time).

If the flood does not show at the 12:00 gate, everyone helps Radar until it does. The 3090 machine runs Radar's and Truth's jobs, with data on WSL2's ext4 disk; App and Story work on laptops from outputs shared over the local network. With three people, Story folds into App after Saturday; with five or six, a second App person takes step 4 and the tour.

## Risks and fallbacks

| Risk | When we know | Fallback |
| --- | --- | --- |
| Downloads too slow before the event | Wed 11 Nov | Harmony variable subsetting: pull only HHHH, HVHV and the mask; north Bihar dropped first |
| DSWX-SAR will not install | Sun 8 Nov (prelim tests) | Our Sentinel-1 rules stand in for DSWx-S1 where we need it; DSWx-NI is dropped and the methods say so |
| Quad-pol and dual-pol differ by more than 0.5 dB on stable ground | Sun 8 Nov (prelim tests) | The fixed offset rule; if the offset varies across the frame, per-tile offsets, plus claim 1 rerun on 4 Sep → 28 Sep (both dual-pol) as a check |
| Fewer than 5 tiles pass the bimodality test | Sun 8 Nov (prelim tests) | The log-ratio cut alone, stated |
| The HH log-ratio shows no flood | Sat 12:00 | Check dB conversion, mask and HH-to-HH matching; then switch to the ascending pair (19 Sep to 1 Oct, already downloaded) |
| Claim 2's excess interval includes zero | Sat 18:00 | Step 3 becomes "where L-band helps and where it doesn't," with the same layer and an honest number; the video leads with the dance and claim 1 |
| The sound is confusing or grating | Sat 24:00 | Off by default behind a Listen button; the chart always shows; cut step 4 from the video if it doesn't help |
| The tour is too much on a phone | Sun 13:00 | Steps collapse to the map, the slider and one card of text |
| Map tiles too big | Sat 18:00 | WEBP and PNG8 tiles, display at 60 m; analysis resolution unchanged |
| Video runs past 30 seconds | Sun 17:00 | Cut the 19 to 25 shot to 3 seconds |

## Before 14 Nov

The Space Apps FAQ asks teams to "start the actual work when the hackathon begins" ([FAQ](https://legacy.spaceappschallenge.org/resources/faq/)), so this list is accounts, data, setup and feasibility checks. Nothing written before kickoff becomes submission code.

**By Thu 5 Nov**

- [ ] Everyone registered at the same local event, listed on the Members tab, not waitlisted (teams are 1 to 6 people).
- [ ] Everyone has a NASA Earthdata login ([sign up](https://urs.earthdata.nasa.gov/users/new)).
- [ ] Ask the local lead in writing whether cited pre-event tools and throwaway feasibility tests are fine, and whether the event has its own AI-tool rules.
- [ ] Story starts looking for a human voice: someone in Bihar, a flood-response official or an NGO, who can say in one line what current flood maps miss. This matters more for the first round of judging than any number.
- [ ] Optional: one person registers on Bhoonidhi and checks for S-band scenes over the Gandak (28 Sep, about 13:07 UTC).

**By Sun 8 Nov: go or no-go**

- [ ] Run [../prompts/setup.md](../prompts/setup.md) on the 3090 machine; it sets everything up and runs the preliminary tests. Review `prelim/REPORT.md` as a team.
- [x] Optical and Sentinel-1 water maps exist around both Gandak dates (checked 3 Nov).

**By Fri 13 Nov**

- [ ] Download the rest of the list and the ancillary layers: Copernicus GLO-30 DEM and HAND, ESA WorldCover, JRC surface water, GHSL built-up area.
- [ ] Deploy an empty GitHub Pages site through GitHub Actions and load it on a phone.
- [ ] Assign the four roles: Radar, Truth, App, Story.
- [ ] Friday night, read the 2026 submission and judging guides when they come out; adjust the storyboard if the rules changed.

## After Space Apps

The hackathon version proves the comparison on one flood. A paper needs the same test on many floods.

1. Rerun everything on NISAR's validated reprocessing when it lands, expected by the end of 2026.
2. Add north Bihar and the other 2026 floods that already have NISAR pairs: Assam, central Indiana, southeast Bangladesh and the Rasuwa debris flow in Nepal.
3. Release the coincident NISAR, Sentinel-1 and optical stack as a small benchmark. We found none like it.
4. Target a remote-sensing venue such as IGARSS or IEEE TGRS.

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
- [NASA announces 2025 Space Apps global winners](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-announces-2025-international-space-apps-challenge-global-winners/), NASA, and [2025 Global Finalists](https://www.spaceappschallenge.org/2025/awards/global-finalists/)
- [Space Apps 2026](https://www.spaceappschallenge.org/2026/), [Judging & Awards Guide](https://www.spaceappschallenge.org/resources/judging-awards-guide), [Project Submission Guide](https://www.spaceappschallenge.org/resources/project-submission-guide/) and [participant FAQ](https://legacy.spaceappschallenge.org/resources/faq/)
- [GDAL MBTiles driver](https://gdal.org/en/stable/drivers/raster/mbtiles.html) and [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
