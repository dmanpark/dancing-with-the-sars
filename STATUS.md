# Status

Updated Thu 5 Nov 2026, 17:25 America/Los_Angeles (`EVENT_TZ=America/Los_Angeles`).

**Phase:** pre-event prep done (Phase 0 of `prompts/build.md`). Nothing more runs before kickoff, Sat 14 Nov 09:00.

## Done, with evidence

- **Clock.** Windows time zone `Pacific Standard Time`, so `EVENT_TZ=America/Los_Angeles`.
- **Setup** (`prompts/setup.md`) done; notes in `prelim/SETUP.md` on branch `prelim`.
- **Step 2, environment.** `dwts` conda env: Python 3.11.18, GDAL 3.10.3, pytest 9.2.0, ffmpeg 9.0.2, gh 2.103.3, Playwright 1.64.1 (pip), headless Chromium 156. The `dswx-sar` env (DSWX-SAR tag DSWx-NI-v1.0) runs `dswx_s1.py`; the working run configuration is `prelim/dswx_s1_runconfig.yaml` on branch `prelim`.
- **Step 3, disk.** Linux ext4 disk about 900 GB free of 1,007 GB; C: about 1.1 TB free.
- **Step 4, downloads complete.** `~/dwts-setup/verify_downloads.py` on 5 Nov at 16:39: 990 files, 0 wrong size, 0 missing, 67.2 GB on disk. That is every manifest row outside `stretch` and `imagery`: all 14 NISAR files (Gandak lead pair, series, history, tier3-phase, fallback; north Bihar heldout roles), the DSWx-HLS and DSWx-S1 water tiles for both events, and every RTC-S1 burst (VV, VH, mask, `.h5`) for both events. The ASF data-use agreement was accepted by the user on 5 Nov; RTC files were fetched with curl (`~/dwts-setup/phase0_downloads.sh`), since `prep/download.py` still fails on them (see `prelim/REPORT.md` T1).
- **Step 5, ancillary layers** for both frames in `~/dwts-data/ancillary/`: GLO-30 DEM and HAND N25 to N28 by E081 to E087 (28 tiles each), WorldCover 2021 (6 tiles), JRC occurrence 80E_30N, GHSL R6_C26 and R6_C27. Sources in `CITATIONS.md`.
- **Step 6, GitHub.** Public repo https://github.com/dmanpark/dancing-with-the-sars, remote `github`. Placeholder https://dmanpark.github.io/dancing-with-the-sars/ live (HTTP 200; iPhone 13 viewport, 0.33 s, 0 console errors; `$DWTS_OUT/screens/placeholder_phone.png`).
- **Step 7, preliminary findings.** Every FAIL, PARTIAL and flag is in `DECISIONS.md` with the fallback or team decision it triggers.
- **Preliminary tests**, follow-ups A to F, the decision 1 check and the T10 like-for-like rerun: `prelim/REPORT.md` on branch `prelim` (latest 144f814), pushed to `origin`.
- **T10 rerun (5 Nov).** With OPERA's own 39 bursts, our DSWx-S1 run matches OPERA's product at open-water IoU 0.813 on OPERA's 30 m grid and 0.782 at 40 m (0.730 and 0.724 with 10 bursts). PASS WITH NOTE: the burst set was the main cause; the team decides whether the 40 m figure matters. 15 min 20 s, 23.6 s per burst; peak 5.4 GB for the largest process, 5.6 GB summed (2 workers). North Bihar projection: about 22 min per 56-burst date, about 45 min for both run one after the other, at about 7.6 GB per run, under the build's 8 GB rule with little room. For Saturday: give every DSWx-S1 run the full MGRS collection of bursts, and run the two north Bihar dates one after the other, not together.
- **Team decisions** of 4 and 5 Nov: nine rows in the change log at the end of `docs/build-spec.md`; page line 1 in `docs/overview.md` says "under trees". Decision 1's check passed (12,772 new-water and 232,716 stable-dry pixels in the NISAR and Sentinel-1 overlap), so the head-to-head stays with the Landsat 9 27 Sep and Sentinel-2C 1 Oct referee; claim 1a runs as a secondary row either way.

## Waiting on a person

Nothing. `docs/overview.md` and `docs/synopsis.md` were brought in line with the change log on 5 Nov (ba4a190: the referee timing of 32 h before and 64 h after, DSWx-NI out of the schedule, calibration per part of the frame, step 5 with the western-frame view and 1a).

## Next

1. Sat 14 Nov 09:00: in an Ubuntu window, `cd ~/PROJECT_DWTS && git checkout main && git pull && claude --permission-mode auto`, then "Read prompts/build.md and carry out everything below the line." The clone is on branch `prelim` until then; `~/dwts-main` is a second worktree on `main` used by the setup session.
2. Before Saturday, close what the build does not need on Windows (other Claude windows, ChatGPT, Docker Desktop, Steam, spare Chrome tabs).

## Notes

- **Memory rules** (b919e48, in `prompts/build.md` and `prompts/prelim-tests.md`): 8 GB per process in the build, 6 GB in prelim, at most two heavy jobs at once, no event downloads while preliminary tests run. The rule is per process; DSWx-S1 spreads one run over several worker processes, so a guard that sums them stops a run that is within the rule.
- **WSL memory.** `C:\Users\daria\.wslconfig` sets `memory=20GB`, `swap=16GB` and, from 5 Nov, `autoMemoryReclaim=gradual` (takes effect at the next WSL restart). On 5 Nov the VM held 20 GB on Windows while 16 GB of it was idle file cache from the downloads; the user dropped it with `sudo sh -c 'sync; echo 1 > /proc/sys/vm/drop_caches'` (`~/dwts-setup/drop_caches.sh`), and the VM fell to 5.5 GB.
- **Correction.** A curl test at 13:33 on 4 Nov fetched an RTC file only because a NISAR session cookie skipped ASF's agreement check. Nothing more was fetched that way.
- **VM pause**, 4 Nov about 12:50 to 13:30: downloads stalled and the tests lost their API connection. A Claude session that loses its connection waits for a new prompt.
- **Memory incident**, 4 Nov about 11:40: Windows ran out of memory and WSL stopped answering; fixed by `wsl --shutdown` and the `.wslconfig` above.
