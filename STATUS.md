# Status

Updated Wed 4 Nov 2026, 07:50 America/Los_Angeles (`EVENT_TZ=America/Los_Angeles`).

**Phase:** pre-event mode, Phase 0 of `prompts/build.md`, partly done. Kickoff is Sat 14 Nov 09:00.

## Done, with evidence

- **Clock.** Windows time zone `Pacific Standard Time`, so `EVENT_TZ=America/Los_Angeles`. Before kickoff, so Phase 0 only.
- **Setup** (`prompts/setup.md`) S1 to S4 done; notes in `prelim/SETUP.md` (committed by the preliminary tests on branch `prelim`).
- **Environment.** `dwts` conda env at `~/miniforge3/envs/dwts`: Python 3.11.18, GDAL 3.10.3, pytest 9.2.0, ffmpeg 9.0.2, gh 2.103.3, Playwright 1.64.1 (pip). Headless Chromium 156.0.8078.4 starts in 1.5 s. DSWX-SAR is not installed yet; the preliminary tests' T10 installs it.
- **Disk.** Linux ext4 disk: 948 GB free of 1,007 GB (`df -h ~`, 3 Nov 2026). C: has 1.1 TB free.
- **Earthdata.** `~/.netrc` works: HTTP 206 on the first 1 KB of one DSWx-HLS file and one NISAR GCOV file (4 Nov 2026, 07:46).
- **Repo files.** `LICENSE` (Apache-2.0, from apache.org), `app/index.html` placeholder, `.github/workflows/pages.yml`, `DECISIONS.md`, `docs/AI_USE.md`, this file. Committed on `main`; not pushed yet.
- **Push check** on `main`: 6.4 MB tracked, no file over 50 MB; the `machine urs`, `password` and `token=` hits are all instructions in `prompts/` and `prep/download.py`, not credentials.

## Waiting on a person

- **GitHub login** (hard stop 1): run `bash ~/dwts-setup/gh_login.sh` in an Ubuntu window. Then: create `dancing-with-the-sars` (public), add remote `github`, push `main`, enable Pages from Actions, load the placeholder at a phone viewport and save the screenshot to `$DWTS_OUT/screens/`.

## Running

- **Preliminary tests** (`prompts/prelim-tests.md`) in their own Ubuntu window, writing `prelim/REPORT.md`. Several hours, about 13 GB of downloads.

## Deferred to a rerun of build.md after the preliminary tests

- Step 4, downloads (the full manifest; past 15 GB in one session needs a yes under `CLAUDE.md`).
- Step 5, ancillary layers for both frames, with URLs into `CITATIONS.md`.
- Step 7, every FAIL, PARTIAL and flag from `prelim/REPORT.md` with its fallback.
- Step 2's DSWX-SAR check (`dswx_s1.py --help`), once T10 has installed it.

Why each was deferred: `DECISIONS.md`.

## Next

1. GitHub repo, push and placeholder deploy, once logged in.
2. After the preliminary tests and the team's review (by Sun 8 Nov): rerun `prompts/build.md` for steps 2, 4, 5 and 7, then stop until 09:00 Sat 14 Nov.

## Blockers

None beyond the GitHub login.

## Machine note

On 4 Nov at 02:47 Windows had 4.2 GB free of 31.6 GB, and Claude Code stopped two idle background checks for low memory. The `docker-desktop` WSL distro was running alongside Ubuntu.
