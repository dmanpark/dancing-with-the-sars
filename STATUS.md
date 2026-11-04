# Status

Updated Wed 4 Nov 2026, 13:40 America/Los_Angeles (`EVENT_TZ=America/Los_Angeles`).

**Phase:** pre-event mode, Phase 0 of `prompts/build.md`, partly done. Kickoff is Sat 14 Nov 09:00.

## Done, with evidence

- **Clock.** Windows time zone `Pacific Standard Time`, so `EVENT_TZ=America/Los_Angeles`. Before kickoff, so Phase 0 only.
- **Setup** (`prompts/setup.md`) done; notes in `prelim/SETUP.md` (committed by the preliminary tests on branch `prelim`).
- **Environment.** `dwts` conda env at `~/miniforge3/envs/dwts`: Python 3.11.18, GDAL 3.10.3, pytest 9.2.0, ffmpeg 9.0.2, gh 2.103.3, Playwright 1.64.1 (pip). Headless Chromium 156.0.8078.4 starts in 1.5 s. DSWX-SAR is not installed yet; the preliminary tests' T10 installs it.
- **Disk.** Linux ext4 disk: 928 GB free of 1,007 GB (`df -h ~`, 4 Nov 2026, 12:11). C: has about 1.1 TB free.
- **Earthdata.** `~/.netrc` works: HTTP 206 on the first 1 KB of one DSWx-HLS file and one NISAR GCOV file (4 Nov 2026, 07:46).
- **GitHub.** Logged in as `dmanpark` (scopes gist, read:org, repo, workflow). Public repo https://github.com/dmanpark/dancing-with-the-sars, remote `github`, `main` pushed. `LICENSE` is Apache-2.0 from apache.org.
- **Placeholder site.** Pages builds from GitHub Actions (`.github/workflows/pages.yml`). First run 41863159350: queued 27 min waiting for a runner, then succeeded at 16:26 UTC. https://dmanpark.github.io/dancing-with-the-sars/ returns HTTP 200 with "Dancing with the SARS: coming 15 Nov 2026".
- **Phone check.** Playwright, iPhone 13 emulation (390 × 664 viewport): HTTP 200, load 0.33 s, 0 console errors. Screenshot `$DWTS_OUT/screens/placeholder_phone.png` (30 KB).
- **Push check** on `main`: 6.4 MB tracked, no file over 50 MB, no data file types; the `machine urs`, `password` and `token=` hits are all instructions or notes, not credentials. `pytest -q` collects no tests (exit 5) because there is no code before kickoff.

## Running

- **Preliminary tests** (`prompts/prelim-tests.md`) in the "DWTS prelim tests" Ubuntu window, writing `prelim/REPORT.md`. Resumed 12:19 in auto mode after the memory incident below, and again at 13:38 (`~/dwts-setup/resume_prelim_auto2.sh`) after a VM pause of about 40 minutes from 12:50 dropped its connection. By then T0 to T5, T7 to T9 and T11 had run; T6, T10 and T12 were next. T1's own downloads are complete: the lead pair (7,927 MB and 1,925 MB, both matching their CMR MD5 checksums), the crop's RTC bursts and the Gandak water-map tiles.
- **Phase 0 step 4 downloads** in the "DWTS downloads" Ubuntu window (`~/dwts-setup/phase0_downloads.sh`, log `$DWTS_OUT/logs/phase0_downloads.log`). Done by 12:41 with `prep/download.py`: Gandak series (4 files, 19.4 GB), history (2.0 GB), tier3-phase (3.7 GB), water-map tiles. Restarted 13:36 with curl (resume, retry, stall abort) after a VM pause froze the transfer: fallback (14.1 GB), north Bihar heldout roles (15.0 GB), every Gandak and north Bihar RTC burst (VV, VH, mask, `.h5`; about 12 GB), north Bihar DSWx-S1 water tiles. Skips `stretch` and `imagery`. At the end `~/dwts-setup/verify_downloads.py` checks every file against `size_mb` and writes `$DWTS_OUT/logs/downloads_verify.txt`. Closing the window stops it; rerunning resumes `.part` files.
- **ASF agreement.** `earthaccess` refuses the RTC files with `EulaNotAccepted`, while `curl --netrc` gets them (HTTP 206, HDF5 header, 13:33). Accepting the ASF data-use agreement in the Earthdata profile should make `prep/download.py` work for RTC too; not yet confirmed.

## Deferred to a rerun of build.md after the preliminary tests

- Step 4's check of the finished downloads (`downloads_verify.txt`).
- Step 5, ancillary layers for both frames, with URLs into `CITATIONS.md`.
- Step 7, every FAIL, PARTIAL and flag from `prelim/REPORT.md` with its fallback.
- Step 2's DSWX-SAR check (`dswx_s1.py --help`), once T10 has installed it.

Why each was deferred: `DECISIONS.md`.

## Next

1. Let the preliminary tests finish; the team reviews `prelim/REPORT.md` by Sun 8 Nov and logs agreed changes at the end of `docs/build-spec.md`.
2. Then rerun `prompts/build.md` for steps 2, 4, 5 and 7, and stop until 09:00 Sat 14 Nov.

## Blockers

None.

## Memory incident, 4 Nov 2026

Around 11:40 Windows ran out of memory (0.3 GB free of 31.6 GB) and WSL stopped responding (`Wsl/Service/0x8007274c`). The WSL VM was at its default cap (15.8 GB) with 4 GB swap, while the preliminary tests worked on the 7.9 GB quad-pol file. With the user's go-ahead, `C:\Users\daria\.wslconfig` now sets `memory=20GB` and `swap=16GB`; the user ran `wsl --shutdown` and Ubuntu came back with 19 GB RAM and 16 GB swap visible. The tests were told to read GCOV layers in blocks and keep peak memory under about 12 GB. Other large Windows users at the time: 15 Claude processes (6.2 GB), a `vmmem` VM (4.0 GB), Chrome (3 to 4 GB). Before the event, close what the build does not need.
