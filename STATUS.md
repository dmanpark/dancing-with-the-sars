# Status

Updated Thu 5 Nov 2026, 04:05 America/Los_Angeles (`EVENT_TZ=America/Los_Angeles`).

**Phase:** pre-event mode, Phase 0 of `prompts/build.md`. Done except the RTC-S1 downloads, which wait on the ASF data-use agreement, and the T10 rerun that needs them. Kickoff is Sat 14 Nov 09:00.

## Done, with evidence

- **Clock.** Windows time zone `Pacific Standard Time`, so `EVENT_TZ=America/Los_Angeles`.
- **Setup** (`prompts/setup.md`) done; notes in `prelim/SETUP.md` on branch `prelim`.
- **Step 2, environment.** `dwts` conda env: Python 3.11.18, GDAL 3.10.3, pytest 9.2.0, ffmpeg 9.0.2, gh 2.103.3, Playwright 1.64.1 (pip), headless Chromium 156. The `dswx-sar` env (DSWX-SAR tag DSWx-NI-v1.0) was built by the tests' T10 and runs `dswx_s1.py`.
- **Step 3, disk.** Linux ext4 disk about 900 GB free of 1,007 GB; C: about 1.1 TB free.
- **Step 4, downloads.** All 14 NISAR files outside `stretch` (Gandak lead pair, series, history, tier3-phase, fallback; north Bihar heldout roles) match `size_mb` within 1 MB. Gandak DSWx-HLS and DSWx-S1 water tiles and north Bihar DSWx-S1 water tiles on disk. 80 Gandak crop RTC files from the tests on disk. About 66 GB of downloads in all.
- **Step 5, ancillary layers** for both frames on disk in `~/dwts-data/ancillary/`: GLO-30 DEM and HAND N25 to N28 by E081 to E087 (28 tiles each), WorldCover 2021 (6 tiles), JRC occurrence 80E_30N, GHSL R6_C26 and R6_C27. North Bihar's 18 extra tiles fetched 5 Nov (1.1 GB, all open in GDAL). Sources in `CITATIONS.md`.
- **Step 6, GitHub.** Public repo https://github.com/dmanpark/dancing-with-the-sars, remote `github`. Placeholder https://dmanpark.github.io/dancing-with-the-sars/ live (HTTP 200; iPhone 13 viewport, 0.33 s, 0 console errors; `$DWTS_OUT/screens/placeholder_phone.png`).
- **Step 7, preliminary findings.** Every FAIL, PARTIAL and flag is in `DECISIONS.md` with the fallback or team decision it triggers.
- **Preliminary tests** and follow-ups A to F plus the decision 1 check: `prelim/REPORT.md` on branch `prelim` (latest e7aa06a), pushed to `origin`.
- **Team decisions** of 4 Nov logged in the change log at the end of `docs/build-spec.md` (9262bd4), plus two rows of 5 Nov (fa8ffd0): claim 1a runs as a secondary row in the western frame whatever the head-to-head shows, and "keeps up with Sentinel-1" appears only if the non-inferiority test passes; page line 1 in `docs/overview.md` now says "under trees". Decision 1's check passed: 12,772 new-water and 232,716 stable-dry pixels in the NISAR and Sentinel-1 overlap, so the head-to-head stays with the Landsat 9 27 Sep and Sentinel-2C 1 Oct referee. 71.8% of that new water sits in 10 of 82 5 km blocks, so expect a wide interval.

## Waiting on a person

- **ASF data-use agreement** (hard stop 1). ASF answers HTTP 401 "Could Not Login. Be sure to agree to the EULA." for every RTC-S1 file (fresh login, 18:36 on 4 Nov). Accept it once at https://urs.earthdata.nasa.gov (profile, EULAs).

## Not yet downloaded

- Every Gandak and north Bihar RTC-S1 burst except the tests' 80 crop files (VV, VH, mask, `.h5`; about 12 GB).

## Next

1. After the ASF agreement: run `~/dwts-setup/phase0_downloads.sh` in a "DWTS downloads" window (curl, resumes, skips finished files), then `~/dwts-setup/verify_downloads.py`.
2. Then the tests' T10 like-for-like rerun (`python prelim/t10_setup.py --opera-collection`, `dswx_s1.py`, `prelim/t10_compare.py`) in the tests session. If it reaches IoU 0.8, Saturday's DSWx-S1 runs get the full MGRS collection; if not, the spec's fallback in `DECISIONS.md` stands.
3. Stop until 09:00 Sat 14 Nov. Before the build: `~/PROJECT_DWTS` is on branch `prelim`; run `git checkout main && git pull` there first. `~/dwts-main` is a second worktree on `main` used by the setup session.

## Notes

- **Memory rules** (b919e48, in `prompts/build.md` and `prompts/prelim-tests.md`): 8 GB per process in the build, 6 GB in prelim, at most two heavy jobs at once, no event downloads while preliminary tests run.
- **Correction.** A curl test at 13:33 on 4 Nov fetched an RTC file only because a NISAR session cookie skipped ASF's agreement check. Nothing more was fetched that way.
- **VM pause**, 4 Nov about 12:50 to 13:30: downloads stalled and the tests lost their API connection. Downloads now use curl with resume; a Claude session that loses its connection waits for a new prompt.
- **Memory incident**, 4 Nov about 11:40: Windows ran out of memory and WSL stopped answering. `C:\Users\daria\.wslconfig` sets `memory=20GB` and `swap=16GB`. Before the event, close what the build does not need.
