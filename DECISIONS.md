# Decisions

One line per technical decision taken during the build. Times are `America/Los_Angeles`.

## Pre-event (3 to 5 Nov 2026)

*   **Environment Setup:** Created the `dwts` conda environment from `prelim/environment.yml`, including pytest, ffmpeg, gh, and playwright.
*   **Playwright Setup:** Installed the Python `playwright` package via pip to ensure the latest version. Handled missing system libraries (libnspr4, libnss3, etc.) manually.
*   **Early Downloads:** Deferred Phase 0 downloads to avoid skewing the T1 throughput measurements; followed the 15 GB session cap.
*   **Placeholder Deployment:** Deployed the placeholder page early to ensure the GitHub Pages workflow (pinned to current release tags: checkout v7.0.1, etc.) was functioning.
*   **Repo Setup:** Set the repository to public under `dmanpark` with the live site as the homepage.
*   **Download Strategy:** Switched from `earthaccess` to `curl` for ASF RTC files due to earthaccess hanging on 0 MB/s and refusing ASF RTC files without the EULA accepted.
*   **T10 Rerun:** Executed the T10 like-for-like rerun under the 8 GB memory rule (per process).
*   **Ancillary Data:** Fetched only the missing DEM, HAND, and WorldCover tiles for the north Bihar frame.
*   **Thresholds & Rules:** Established that thresholds are applied per part of the frame, with "valid" pixels read literally. The claim 2 secondary test was dropped. 
*   **Data Fallbacks:** Dropped DSWx-NI due to memory constraints. Applied the Sentinel-1 two-sided rule as a fallback for DSWx-S1 on north Bihar.

## Sat 14 Nov 2026 (event)

*   **Cut Ladder:** Applied rung 1 of the cut ladder, removing Tier 3 (north Bihar pipeline, breach-site check, etc.) to keep the schedule on track.
*   **Calibration:** Established that when a channel's tile spread exceeds 0.5 dB, each part's median is subtracted regardless of size. Sentinel-1 calibration uses one frame median as it lacks parts.
*   **Referee Logic:** Defined the head-to-head referee exactly as change-log row 1 (water in both L9 and S2C, JRC below 25%). Claim 2 "passes" if the interval's lower end is above zero.
*   **Hidden-Steps Layer:** Configured the layer to use claim 2's vegetation pixel set (tree cover, shrubland, herbaceous wetland), excluding cropland.
*   **App Settings:** Pinned library versions (maplibre-gl 6.18.0, pmtiles 4.5.0, etc.) and used OpenFreeMap positron for the basemap due to no API key requirement.
*   **Breach Sites:** Only Areraj (East Champaran) could be accurately placed; left out Khairatwa, Phuliyakhad, Bathuwaria, Golaghat, and Sheetalpur.
*   **Reported Caution:** Reported that hidden-steps pixels sit near buildings 52% of the time (against 24% for the claim 2 set). Kept the method and number unchanged.
*   **Video Timeline:** Adjusted video timeline (step 5 at 24s, naive toggle at 26.6s) because the step 5 change maps take ~2.4s to draw.

## Sun 15 Nov 2026 (event)

*   **Video Recording:** Recorded the final video from the local server serving byte-identical files (commit 030398d) because the live URL network latency caused missing tiles at specific storyboard moments.
*   **Captions & Wording:** Updated Caption 5 to state "Sentinel-1 did better (F1 0.17 vs 0.05)" and Caption 2 to say "under trees" (not crops) to match the cropland result (-105 km2).
*   **Final Edits:** Completed final words-only edits to SUBMISSION.md, adding the low-recall sentence to claim 1 and the "(evidence, not verified)" tag to claim 2.