# Status

Updated Wed 4 Nov 2026, 14:35 America/Los_Angeles (`EVENT_TZ=America/Los_Angeles`).

**Phase:** pre-event mode, Phase 0 of `prompts/build.md`, partly done. The preliminary tests are finished. Kickoff is Sat 14 Nov 09:00.

## Done, with evidence

- **Clock.** Windows time zone `Pacific Standard Time`, so `EVENT_TZ=America/Los_Angeles`. Before kickoff, so Phase 0 only.
- **Setup** (`prompts/setup.md`) done; notes in `prelim/SETUP.md` on branch `prelim`.
- **Environment.** `dwts` conda env: Python 3.11.18, GDAL 3.10.3, pytest 9.2.0, ffmpeg 9.0.2, gh 2.103.3, Playwright 1.64.1 (pip), headless Chromium 156. The `dswx-sar` env (DSWX-SAR tag DSWx-NI-v1.0) was built by the tests' T10; `dswx_s1.py --help` runs there.
- **Disk.** Linux ext4 disk: about 900 GB free of 1,007 GB. C: has about 1.1 TB free.
- **Earthdata.** `~/.netrc` works for PO.DAAC (DSWx) and ASF NISAR.
- **GitHub.** Public repo https://github.com/dmanpark/dancing-with-the-sars, remote `github`, `main` pushed. Placeholder https://dmanpark.github.io/dancing-with-the-sars/ is live (HTTP 200; iPhone 13 viewport, 0.33 s load, 0 console errors; screenshot `$DWTS_OUT/screens/placeholder_phone.png`).
- **Preliminary tests** finished 4 Nov. Report `prelim/REPORT.md` on branch `prelim` (commit 84357fe), pushed to `origin`. Headline: the radar side works (flood visible in HH, mask explains the stripes, grids align, tile budget about 151 MB), but claim 1 as specified has no referee pixels: the post −8 h optical pass is all fill inside the NISAR footprint, and no pixel has NISAR, Sentinel-1 and a clear post-event optical map together. Four proposals and eight open questions for the team.
- **NISAR downloads complete.** All 14 NISAR files in `data/manifest.csv` outside `stretch` (Gandak lead pair, series, history, tier3-phase, fallback; north Bihar heldout roles) are on disk and match `size_mb` within 1 MB (`~/dwts-setup/verify_downloads.py`, 14:25). 64.4 GB on disk in total.

## Waiting on a person

- **ASF data-use agreement** (hard stop 1). ASF answers HTTP 401 "Could Not Login. Be sure to agree to the EULA." for every RTC-S1 file, with both curl and `prep/download.py`. The user accepts it once in a browser while signed in to Earthdata. Downloads are stopped until then.
- **The team's review** of `prelim/REPORT.md` by Sun 8 Nov: proposals 1 to 4 and the open questions, especially the claim 1 design. Agreed changes are logged at the end of `docs/build-spec.md`.

## Not yet downloaded

- Every Gandak and north Bihar RTC-S1 burst (VV, VH, mask, `.h5`; about 12 GB; 80 Gandak crop files from the tests are on disk).
- North Bihar DSWx-S1 water tiles (`ref-post`, small).

## Next

1. After the ASF agreement: rerun `~/dwts-setup/phase0_downloads.sh` in the "DWTS downloads" window (it resumes and skips finished files), then the size check.
2. With the RTC bursts on disk: the tests' T10 like-for-like rerun (`python prelim/t10_setup.py --opera-collection`, then `dswx_s1.py`, then `prelim/t10_compare.py`) in the tests session, which updates the report.
3. After the team's review: rerun `prompts/build.md` for step 5 (ancillary layers for both frames) and step 7 (every FAIL, PARTIAL and flag with its fallback), then stop until 09:00 Sat 14 Nov.
4. Before Saturday's build: `~/PROJECT_DWTS` is on branch `prelim`; run `git checkout main` there first.

## Notes

- **12 GB memory guard.** The tests stopped DSWx-NI at 12.5 GB because the setup session told them to keep peak memory under about 12 GB after the freeze below. That limit is not in the spec. WSL now has 20 GB of RAM and 16 GB of swap; whether DSWx-NI gets more is the team's call (report, open question 7).
- **Correction.** At 13:33 a curl test fetched an RTC file from ASF. It got through only because the cookie jar held a session cookie from the NISAR download, which skipped ASF's agreement check for RTC; a fresh login is refused. Nothing more was fetched that way.
- **VM pause**, 4 Nov about 12:50 to 13:30: the downloads stalled and the tests lost their API connection. Downloads now use curl with resume (`~/dwts-setup/fetch_one.sh`); a Claude session that loses its connection waits for a new prompt.
- **Memory incident**, 4 Nov about 11:40: Windows ran out of memory and WSL stopped answering. `C:\Users\daria\.wslconfig` now sets `memory=20GB` and `swap=16GB`. Before the event, close what the build does not need (other Claude windows, ChatGPT, Docker Desktop, Steam).
