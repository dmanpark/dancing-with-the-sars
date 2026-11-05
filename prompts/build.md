# Build everything: Claude Code prompt

## How to use this (for the team)

**When.** Run it any time from Fri 13 Nov. Before kickoff (Sat 14 Nov, 09:00 local event time) it does only pre-event prep: the remaining downloads, environment checks, the GitHub login and an empty placeholder site. At or after kickoff it builds the whole project. It checks the clock itself, so running it early is safe.

**Before you run it.** `prompts/setup.md` has run on the 3090 machine, the team has read `prelim/REPORT.md`, and any changes you agreed on are logged at the end of `docs/build-spec.md`.

**Start it** in an Ubuntu window on the 3090 machine:

```bash
cd ~/PROJECT_DWTS && git checkout main && git pull
claude --permission-mode auto
```

Then say: **"Read prompts/build.md and carry out everything below the line."**

Auto mode lets a safety check approve routine actions instead of you. It can still stop for something it thinks is risky; if a permission prompt appears, read it and allow it if it matches what the prompt says Claude is doing. The prompt itself tells Claude never to ask you questions and to take the recommended option every time.

**If it stops or the window closes:**

```bash
cd ~/PROJECT_DWTS && claude --continue --permission-mode auto
```

and say: **"Continue prompts/build.md from STATUS.md."**

**What a person still has to do.** Claude tells you when each one comes up: log in to GitHub once (`gh auth login`), upload the finished video under the team's account, and submit the project form on the Space Apps site. Everything else is Claude's. `STATUS.md` in the repo always says where it is.

---

## Your job

Build and ship **Dancing with the SARS: The Hidden Steps** exactly as `docs/overview.md` and `docs/build-spec.md` describe: the NISAR pipeline, claims 1 and 2, the five-step app, the 30-second video and the submission text, all ready by **Sun 15 Nov 21:00 local event time**. The hard deadline is 23:59.

The team is around but busy. Work without them except at the hard stops below.

## Never ask: take the recommended option

**IMPORTANT.** Do not ask the user questions. Do not call AskUserQuestion, do not end a turn on a question, and do not wait for confirmation. Whenever you would ask, choose the option you would have labeled "(Recommended)", write one line to `DECISIONS.md`, and keep going. When it isn't obvious which option is recommended, decide in this order:

1. A fixed decision or file contract in `docs/build-spec.md`.
2. A change the team logged at the end of `docs/build-spec.md`, or a fallback that the build spec or the overview's risk table already names.
3. Whatever keeps Tier 1 on schedule.
4. The simpler option.
5. The option that is easier to undo.

A `DECISIONS.md` line is `HH:MM | decision | options considered | why`. Recording a decision is not asking; never block on one.

## Hard stops: the only times you wait

Send one short message saying exactly what the person must do, then wait. Keep working on anything that doesn't depend on the answer.

1. **A login or password.** `gh auth login`, Earthdata if `~/.netrc` stops working, the Claude login. Never ask for a password in the chat.
2. **Anything needing `sudo` or Windows administrator rights**, including system libraries Playwright's browser needs.
3. **Publishing under a person's account outside GitHub.** Uploading the video and submitting the Space Apps form. You prepare everything; a team member clicks.
4. **Destroying what you can't recreate.** Deleting anything outside the repo, `$DWTS_DATA` and `$DWTS_OUT`; force-pushing `main`; rewriting history that is already on GitHub.

The team asks you, through this prompt, to create its public GitHub repo, push `main` to it, force-push the orphan `tiles` branch (the build spec's design) and deploy GitHub Pages. Those pushes are the job, so do them without asking. `CLAUDE.md`'s other "ask before" rules still apply.

## Rules that override everything else

1. **Event rules.** Before Sat 14 Nov 09:00 local event time, write no project code: do Phase 0 only. Code in `prelim/` is throwaway; never copy from it. You may read `prelim/REPORT.md`, `prelim/SETUP.md`, `prelim/config.yaml`, `prelim/environment.yml` and `prelim/dswx_s1_runconfig.yaml` (on the `prelim` branch: `git show prelim:<path>`), because they record findings and settings, not code.
2. **Honest numbers.** Every number in the app, the video and the project page comes from `results.json`, written by the pipeline. Never hard-code, round to flatter or invent a value. A failed claim is reported as failed, using the overview's fallback wording. Never change a fixed decision after seeing a claim number. If a real bug forces a change afterwards, fix it, log it in `DECISIONS.md` marked "changed after results", and rerun everything downstream.
3. **No silent placeholders.** Until a number exists, the app shows the word "computing". Before submission there must be zero matches for `___`, `TODO`, `TBD` or `computing` in `app/`, `SUBMISSION.md` and the video captions.
4. **Data and credentials.** Never commit `.h5`, `.tif`, `.nc`, `.mp4`, `.wav` files, `.netrc` or tokens to `main`. Tiles and the listening grid go only on the `tiles` branch. Before every push, run `git ls-files` with a size check (nothing over 50 MB) and a grep for `machine urs`, `password` and `token=`.
5. **AI disclosure.** Keep `docs/AI_USE.md` current: which AI tools and models were used, before and during the event, and for what. Use no generative image or video models. The two diagrams are simple SVG drawings coded from basic shapes; each carries a small visible note "Diagram made with AI assistance", and the team may redraw them.
6. **Writing.** Plain sentences, no em-dashes, units on every number. The "What this can't tell you" box is copied from `docs/overview.md` word for word.
7. **Leave the plan alone.** Do not edit `docs/overview.md`, `docs/build-spec.md`, `prep/` or `data/`. Decisions go in `DECISIONS.md`.

## Read first

1. `CLAUDE.md`
2. `docs/build-spec.md`: the source of truth. Where it and the overview disagree, the build spec wins.
3. `docs/overview.md`: the app's five steps, the video storyboard, the risk table, the limits box.
4. `docs/data.md`
5. `git show prelim:prelim/REPORT.md` and `git show prelim:prelim/SETUP.md`: dataset paths, mask values, legends, calibration branch, bimodal tiles, timings, failures.
6. The change log at the end of `docs/build-spec.md`.
7. Check `git branch --show-current` says `main`; if not, `git checkout main` first (the preliminary tests left this clone on `prelim`).
8. If `STATUS.md` exists, you are resuming: read it, `DECISIONS.md` and `git log -10`, then continue from the first unfinished item.

## The clock

- Set `EVENT_TZ` once and record it in `STATUS.md`: take the Windows time zone (`powershell.exe -NoProfile -Command "(Get-TimeZone).Id"`) and convert it to its IANA name (for example `Pacific Standard Time` is `America/Los_Angeles`). Use `TZ=$EVENT_TZ date` for every time check.
- Kickoff Sat 14 Nov 09:00. Gates: **12:00** flood visible; **18:00** Tier 1 done; **Sun 13:00** feature freeze; **Sun 21:00** ready to submit; **23:59** deadline.
- The overview's night block is for people. You keep working through the night.
- At each gate, write the result to `STATUS.md` with evidence. If a gate slips by more than an hour, cut from the top of this ladder until the schedule holds again:
  1. Tier 3, all of it
  2. DSWx-NI
  3. Tour polish (keep Explore)
  4. Step 4's sound (keep the chart)
  5. Step 5's toggle (keep the numbers and the limits box)
  6. Step 3's diagrams

  Never cut claims 1 and 2, steps 1 and 2, the limits box, the video or the submission text.

## How to work

- **Phases in order**, with the parallel tracks marked below. Use subagents for independent tracks (the app shell, the Sentinel-1 mosaics, the ancillary layers) and for the final independent review. You integrate and you verify; a subagent's report is not verification.
- **Long jobs in the background**, logging to `$DWTS_OUT/logs/`. Check on them; don't sit idle while they run.
- **Memory.** The machine has 32 GB shared with Windows; Ubuntu gets about 16 GB, and the preliminary run froze it once. Keep each process under 8 GB: read GCOV in row strips and average as you read, keep layers float32 at 40 m, fit each tile's mixture on at most 50,000 sampled pixels, and free arrays between dates. Run at most two heavy jobs at once (a background download or DSWx-S1 run counts as one). Check `free -g` before starting a heavy job; if less than 4 GB is available, wait.
- **`STATUS.md`** (repo root, committed) is updated at the end of every phase and gate: local time, phase, what is done with its evidence (file paths, test output, screenshot paths), what's next, blockers. A fresh session must be able to continue from it alone.
- **Commit** after each phase. Push `main` to GitHub (remote `github`, the team's shared copy) at least at 12:00, 18:00, Sun 13:00 and the end. Don't push `main` to `origin`: it is the Windows folder with `main` checked out, and git refuses that push.
- **Tests before every push:** `pytest -q` must pass.
- **Show evidence.** Each phase below has a check. Run it and paste the output, or the screenshot path, into `STATUS.md`.

## Layout to create at kickoff

```
dwts/                     the pipeline (Python package)
  config.py               paths, events, dates and granules from data/manifest.csv; every fixed decision as a named constant
  gcov.py                 read GCOV with the dataset paths and mask rule from prelim T2 and T4
  grid.py                 analysis grid, 2 × 2 linear-power averaging, COG writer
  ancillary.py            HAND, slope, WorldCover, GHSL, JRC onto a grid
  refs.py                 optical referee, DSWx-S1, RTC-S1 mosaics
  calib.py                stable ground and the calibration rule
  thresholds.py           bimodal tiles (Gaussian mixture, Ashman D) and Kittler-Illingworth
  detect.py               log-ratio, open-water rule, two-sided detector
  stats.py                5 km blocks and the paired block bootstrap
  claims.py               claims 1 and 2 (Tier 3: claims 3 and 4)
  listen.py               the listening grid
  tiles.py                color maps, MBTiles, PMTiles
  run.py                  python -m dwts.run <stage> [--event gandak]
tests/                    pytest on small synthetic arrays
scripts/                  check_results.py, check_app.py
app/                      index.html, app.js, style.css, steps.json, data/ (results.json, sound.json, breach_sites.csv)
video/                    render.py, timeline.json, captions.srt
.github/workflows/pages.yml
SUBMISSION.md  CITATIONS.md  STATUS.md  DECISIONS.md  LICENSE (Apache-2.0)  docs/AI_USE.md
```

Add `*.mp4`, `*.wav` and `*.webm` to `.gitignore`.

---

## Phase 0: preflight (both modes, about an hour)

1. **Mode.** Set `EVENT_TZ`. If it is before kickoff, you are in pre-event mode: do steps 2 to 8, then stop.
2. **Environment.** The `dwts` conda env from the preliminary tests exists; if not, create it from `prelim/environment.yml`. Add `pytest`, `ffmpeg`, `gh` and Python `playwright` from conda-forge or pip, then `playwright install chromium`. If Chromium will not start because system libraries are missing, that is hard stop 2: ask the user to run the one install command Playwright prints, in an Ubuntu window. Check the DSWX-SAR env still runs `dswx_s1.py --help`.
3. **Disk.** At least 110 GB free on the ext4 disk (`df -h ~`). If less, download in the priority order below and skip what doesn't fit, logging it.
4. **Downloads.** If the preliminary tests are still running (a Claude session is working on `prompts/prelim-tests.md` and `prelim/REPORT.md` has unfinished tests), wait until they finish: running both at once ran the machine out of memory. Then download in the background with `prep/download.py --out $DWTS_DATA/downloads`, in this order: `lead-pre`, `lead-post`, `series`, `history`; then `ref-pre` and `ref-post` with `--match _B01_WTR.tif`; then `ref-pre-rtc` and `ref-post-rtc` for Gandak (every burst, the layers T10 recorded as needed); then `tier3-phase`, `fallback`, and the north Bihar roles (`heldout-*`, its `ref-*-rtc`). Skip `stretch` and `imagery`. Verify each file's size against `size_mb`.
5. **Ancillary layers** for both frames (GLO-30 DEM and HAND, WorldCover 2021, JRC occurrence, GHSL built-up), from the sources the preliminary report recorded. Record the URLs in `CITATIONS.md`.
6. **GitHub.** `gh auth status`. If not logged in, hard stop 1. Then create the public repo `dancing-with-the-sars` under the logged-in account if it doesn't exist, add it as remote `github`, push `main` (never the `prelim` branch), add `LICENSE` (Apache-2.0, which Space Apps uses for submissions), and deploy a one-line placeholder page ("Dancing with the SARS: coming 15 Nov 2026") through a GitHub Actions Pages workflow. Load it with Playwright at a phone viewport and save the screenshot.
7. **Preliminary findings.** List every FAIL, PARTIAL and flag from `prelim/REPORT.md` with the fallback it triggers. For any proposal the team didn't log, apply the spec's own fallback if one exists; otherwise keep the spec as written. Log each in `DECISIONS.md`.
8. **Pre-event mode ends here.** Write `STATUS.md` ("Pre-event prep done" plus the download totals), commit, push, tell the user in five lines or fewer what is ready, and that the next run should start at 09:00 on Sat 14 Nov. Stop.

## Phase 1: the core pipeline (Sat 09:00 to 12:00)

Start at 09:00 sharp. Tracks A and B run in parallel.

**Track A: NISAR**

1. 09:05: if the north Bihar Sentinel-1 bursts are downloaded, start `dswx_s1.py` on 28 Aug and 9 Sep in the background with the T10 run configuration (build spec Truth step 1). It is insurance for Tier 3 and costs nothing.
2. `config.py`, `gcov.py`, `grid.py`: write `grid_gandak.json` from the 28 Sep file by 10:00; HH and HV dB for 16 and 28 Sep; the valid mask (Radar steps 1 to 3).
3. As soon as step 2 works, start the series batch in the background: 6 Jul, 23 Aug, 4 Sep, 10 Oct and 22 Oct (Radar step 2; average the 40 MHz date to 40 m).
4. `calib.py`, `thresholds.py`, `detect.py`: log-ratios with the calibration rule, `*_calib.json`, `*_thresholds.json`, and the log-ratio baseline map (Radar steps 4 to 6).

**Track B: references (subagents are fine here)**

5. `ancillary.py`: the five layers on the Gandak grid by 11:00.
6. `refs.py`: the four optical maps and the referee states; DSWx-S1 for 17 and 29 Sep with the inundated-vegetation code kept; RTC-S1 VV and VH mosaics for 17 and 29 Sep (Truth steps 2 and 3).

**Tests** (write them as the code lands): Kittler-Illingworth recovers a known threshold on synthetic bimodal data within 0.5 dB; Ashman D matches a hand calculation; the calibration rule picks each of its three branches on synthetic offsets; 2 × 2 averaging happens in linear power; the bootstrap is identical across runs with seed 2026.

**12:00 gate check.** Write `$DWTS_OUT/figures/gate12_flood.png`: the Bagaha crop's HH log-ratio with the optical new-water outline. Say in `STATUS.md` whether the flood is visible along the Gandak. If it isn't, follow the overview's risk row for that case (check dB conversion, the mask and HH-to-HH matching, then the ascending pair) before anything else. Push.

## Phase 2: flood maps and the two claims (12:00 to 18:00)

1. Two-sided detector on the lead pair and the control pair (23 Aug to 4 Sep); the Sentinel-1 log-ratio and two-sided rules on 17 to 29 Sep (Radar step 6, Truth step 3).
2. `stats.py` and `claims.py`: claim 1 (Truth step 4) and claim 2 primary and secondary (Truth step 5), with the fixed pixel sets, margin and bootstrap. Write `gandak_hidden.tif`.
3. Write `$DWTS_OUT/results.json` in this shape, and copy it to `app/data/results.json`:

```json
{
  "generated_utc": "2026-11-14T00:00:00Z",
  "commit": "abc1234",
  "event": "gandak",
  "passes": {
    "nisar_pre": "2026-09-16T13:07:04Z", "nisar_post": "2026-09-28T13:07:05Z",
    "s1_pre": "2026-09-17T00:18:00Z", "s1_post": "2026-09-29T00:18:00Z",
    "control_pre": "2026-08-23T13:07:05Z", "control_post": "2026-09-04T13:07:05Z"
  },
  "time_offsets_h": {"s1": 0.0, "optical_post_before": 0.0, "optical_post_after": 0.0},
  "calibration": {"lead": {"hh_db": 0.0, "hv_db": 0.0, "branch": "none", "n_stable": 0}, "control": {}},
  "thresholds": {"lead_post_hh": {"tiles_tested": 0, "tiles_passing": 0, "db": null}},
  "claim1": {
    "metric": "F1", "margin": -0.05,
    "nisar_twosided": {"f1": 0, "precision": 0, "recall": 0, "iou": 0},
    "s1_twosided": {"f1": 0, "precision": 0, "recall": 0, "iou": 0},
    "others": {"nisar_lr": {}, "s1_lr": {}, "dswx_s1": {}, "dswx_ni": null},
    "diff": 0, "ci95": [0, 0], "noninferior": false,
    "n_pixels": 0, "n_new_water": 0, "by_landcover": {}
  },
  "claim2": {
    "vegetation": {"excess_km2": 0, "ci95": [0, 0], "flood_km2": 0, "control_km2": 0, "n_pixels": 0, "passes": false},
    "cropland": {"excess_km2": 0, "ci95": [0, 0], "flood_km2": 0, "control_km2": 0, "n_pixels": 0, "passes": false},
    "secondary": {}
  },
  "tier3": null
}
```

4. Write `scripts/check_results.py` that validates this shape and fails on missing fields, NaN or intervals that don't contain their point estimate. Add it to the test run.
5. **Check:** the Tier 1 boxes in the build spec's "Done means" that belong to the pipeline, each with evidence, including the side-by-side figure of NISAR's flooded area and Sentinel-2 on 29 Sep.

## Phase 3: the app, Tier 1 (11:00 to 18:00, in parallel with Phase 2)

A subagent can build the shell while the pipeline runs; you wire in real data.

1. `.github/workflows/pages.yml`: checks out `main`, checks out the `tiles` branch into a separate folder and copies its `tiles/` and `listen/` folders into `app/tiles` and `app/data/listen`, adds `.nojekyll`, and deploys `app/`.
2. `tiles.py`: HH for each series date as it lands (one fixed −25 to 0 dB gray stretch, WEBP), and the NISAR and Sentinel-1 two-sided maps (PNG8), zoom 6 to 12, each under 100 MB.
3. The app as the build spec's App section describes: `index.html`, `app.js`, `style.css`, `steps.json`. Steps 1 and 2 and Explore first. Numbers come from `results.json`; until it exists they read "computing". Each step is linkable (`#step=2`). Add a brief ripple where the user taps; it helps on a phone and in the video.
4. Pin exact library versions: look up the current stable versions of `maplibre-gl`, `pmtiles` and the MapLibre compare plugin on the npm registry (`curl -s https://registry.npmjs.org/<name>/latest`), load them from jsDelivr at those exact versions, and log them in `DECISIONS.md`.
5. A `?video=1` mode that plays the storyboard from `video/timeline.json` automatically: fixed step times, a scripted slider drag, and a tap on a fixed cell at a fixed second. The video renderer uses the same file.
6. **Check:** a Playwright script (`scripts/check_app.py`) loads the deployed site at a phone viewport (iPhone 13 emulation) and at 1440 × 900, visits every live step, drags the slider, records console errors (must be zero) and the time to first draw (target under 3 s on the phone viewport), and saves screenshots to `$DWTS_OUT/screens/`. List them in `STATUS.md`.

## 18:00 gate

Tick every Tier 1 box in the build spec's "Done means" with evidence. If all pass, Tier 3 is allowed later. Push the first of the two tile sets to `tiles`. Push `main`.

## Phase 4: Tier 2 (Sat 18:00 to Sun 13:00)

1. **Step 3.** Tiles of `gandak_hidden.tif` in the second hue, the km² figure, the "evidence, not verified" label, and the two SVG diagrams.
2. **Listening grid.** `listen.py` writes the chunks and `index.json` exactly as the build spec's app decisions fix them. Decode one chunk and compare three cells with the dB rasters; add that as a test.
3. **Step 4.** Tap fetches the chunk, draws the SVG chart of HH and HV across the seven dates with the flood date marked, and the Listen button plays it through Web Audio using `app/data/sound.json` (tempo, voices, scale ranges). A mute control is always visible; nothing autoplays. Pick the three suggested places from the data (an open-water field, a flooded grove from the hidden-steps layer, a dry town) and log their coordinates.
4. **Sound checks.** You can't listen, so test it: render the three places and ten random cells to WAV offline in Python with the same `sound.json`; check that pitch order matches dB order in both channels, peaks stay below −1 dBFS and each clip lasts about seven beats. Note in `STATUS.md` that a person should listen once; it is not a hard stop.
5. **Step 5.** The optical new-water outline, both numbers in plain words with their intervals, the toggle between "naive difference" and "what we trust" (gaps hatched), three failure examples with one sentence each (Radar step 11, Truth step 6), and the limits box.
6. **The tour.** `steps.json` drives every step's view, layers and card text (three sentences at most, written for someone who has never heard of radar). Reduced motion shows a date slider instead of the animation. The phone layout keeps the card under 40% of the screen.
7. **DSWx-NI**, timeboxed to 2 hours (Radar step 7). Add it to the claim 1 table, or write why it failed.
8. **Check:** rerun `scripts/check_app.py` across all five steps on both viewports, plus the listening test. Commit and push.

## Phase 5: Tier 3 (only if the 18:00 gate passed and Tier 2 is on track at Sun 02:00)

North Bihar pipeline (Radar step 8), claims 3 and 4 and the breach-site check (Truth steps 7 to 9), the Check first step, and the phase test if T2 found the HHVV term (Radar step 12). S-band only if its files are already on disk. Stop all Tier 3 work at Sun 11:00; anything unfinished stays out of the app and the page, and `results.json` keeps `"tier3": null`.

## Phase 6: freeze, video and words (Sun 13:00 to 19:00)

13:00 is the feature freeze: after it, only fixes and words.

1. **Final tiles.** Push the second and last tile set.
2. **The video.** `video/render.py`:
   - records the deployed site in `?video=1` mode with Playwright at 1920 × 1080;
   - renders the tapped cell's sound offline from `sound.json` and mixes it in at the tap time from `timeline.json`;
   - writes `captions.srt` from the overview's storyboard, with numbers filled from `results.json` (if a claim failed, use the overview's fallback wording);
   - burns the subtitles in with ffmpeg and encodes H.264 at 1080p, then checks with ffprobe that it is 30.0 s or shorter.

   Output `$DWTS_OUT/video/dwts_30s.mp4`, then hard stop 3: ask a team member to upload it to YouTube as Public or Unlisted (no login needed to watch) and paste the link into `SUBMISSION.md`.
3. **`SUBMISSION.md`**, every field the build spec's Story section lists, filled from `results.json`. If the team has added a quote to `docs/quote.md`, use it with the person's name and role; otherwise leave that line out entirely.
4. **`CITATIONS.md`** complete; check every link responds.
5. **The public README:** what it is, the live link, the video link, how to reproduce (`python -m dwts.run all`), data credits, license and AI use.

## Phase 7: final checks and handoff (Sun 19:00 to 21:00)

1. **Independent review.** Start a subagent that has not seen your work. Give it the build spec's "Done means", the deployed URL, `results.json` and `SUBMISSION.md`. It checks every box, and every number in the app, the captions and `SUBMISSION.md` against `results.json`, and reports gaps. Fix gaps that affect correctness or the requirements; ignore style.
2. **Full checks:** `pytest -q`; the placeholder grep; the secret grep; `git ls-files` size check; total site under 600 MB; `scripts/check_app.py` in a fresh browser context on both viewports; the app and video links open in a private window.
3. **Final push** of `main` to GitHub. `STATUS.md` says "Ready to submit" and lists the steps for the person submitting: open the team's project on the Space Apps site, paste each field from `SUBMISSION.md`, add the video and app links, check the team members, submit before 21:00 (deadline 23:59). Hard stop 3: a team member submits.
4. Tell the user in ten lines or fewer: the two numbers, the links, what was cut and why, and what they still need to click.
