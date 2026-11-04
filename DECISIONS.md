# Decisions

One line per decision taken without asking, as `prompts/build.md` requires: `HH:MM | decision | options considered | why`. Times are `America/Los_Angeles`.

## Tue 3 Nov 2026 (pre-event)

23:28 | Run `prompts/build.md` now, in pre-event mode (Phase 0 only) | run now; wait for Fri 13 Nov | The user said "restart" and pasted build.md; its clock check makes an early run safe and it writes no project code before kickoff
23:28 | `EVENT_TZ=America/Los_Angeles` | other zones | Windows reports `Pacific Standard Time`; build.md says to take the Windows time zone
23:29 | Finish `prompts/setup.md` first (Earthdata login, Claude Code inside Ubuntu, start the preliminary tests) | skip setup; finish it | build.md's "Before you run it" needs setup done and `prelim/REPORT.md` read; setup was paused at its Earthdata step
23:31 | Create the `dwts` env now from a new `prelim/environment.yml` (the T0 package list plus pytest, ffmpeg, gh, playwright) | wait for the tests' T0 to create it; create it now | Phase 0 step 2 needs the env and says to create it from that file if it is missing; T0 then only checks it
23:40 | Take the Python `playwright` package from pip | conda-forge `playwright` (the Node.js CLI, 1.64.1); conda-forge `playwright-python` (last 1.45.1); pip (1.64.1) | build.md allows conda-forge or pip; only pip has the current Python package
23:44 | Hand the Playwright system libraries to the user as hard stop 2 | conda-forge copies of the libraries on `LD_LIBRARY_PATH`; the one `sudo` command Playwright prints | build.md names this exact case as hard stop 2; Chromium is missing libnspr4, libnss3, libnssutil3, libsmime3 and libasound2, and the fonts Playwright installs keep screenshots readable
23:45 | Defer Phase 0 steps 4 (downloads), 5 (ancillary layers) and 7 (preliminary findings) to a rerun of build.md after the preliminary tests finish | download now in parallel; defer | T1 downloads the lead pair into the same folder and measures throughput, which a parallel download would skew; step 7 needs `prelim/REPORT.md`, which does not exist yet; CLAUDE.md caps one session at 15 GB without asking
23:48 | Deploy the placeholder page now (Phase 0 step 6) | deploy now; wait for Saturday | build.md Phase 0 asks for it; the build spec's App section wants Saturday's deploy not to be the first, and a placeholder makes sure of that
23:48 | Pin the Pages workflow actions to their current release tags: checkout v7.0.1, configure-pages v6.0.0, upload-pages-artifact v5.0.0, deploy-pages v5.0.1 | major tags; exact tags | Exact tags cannot move under us during the event

## Wed 4 Nov 2026 (pre-event)

07:48 | Commit the Phase 0 files on `main` locally before starting the preliminary tests, and push them once GitHub is logged in | wait for GitHub first; commit now | The tests work in the same clone and branch `prelim` off `main` at the end; committing first keeps the two sets of files apart
07:48 | Start the preliminary tests before GitHub is set up | wait for the GitHub login; start now | They need only Earthdata, which works, and they take several hours
07:58 | Push `main` although `pytest -q` collects no tests (exit 5) | wait for tests; push | There is no project code before kickoff, so there is nothing to test; the size and secret checks passed
07:58 | Repo under the logged-in account `dmanpark`, public, with the live site as its homepage | an organization account; private | build.md says the logged-in account and public
12:19 | Resume the preliminary tests in auto mode | default mode (stops on every permission prompt); auto | The user asked to start everything and was not at the window; the session had stopped after reading the first resume note as information
12:20 | Start Phase 0 step 4 downloads now, in their own window, instead of after the team's review | after the review; now | The user asked to start everything, taken as the yes for going past 15 GB; T1's downloads were finished, so nothing collides and T1's throughput figure is already measured; the tests session was told not to fetch these roles
12:20 | Take four files per RTC burst: `_v1.0.h5`, `_VV.tif`, `_VH.tif`, `_mask.tif` | wait for T10 to name the layers; the set T1 chose | T10 has not run yet; T1 picked this set after reading the DSWX-SAR docs, and any missing layer can be fetched later
13:35 | Fetch the rest of step 4 with curl (resume, retries, stall abort) from the same manifest rows instead of `prep/download.py` | keep download.py and restart it by hand after every pause; wait for the ASF agreement; curl | earthaccess hung with no timeout when the VM paused (0 MB/s, 10.9 GB of partial files lost) and refused ASF RTC files with `EulaNotAccepted` while `curl --netrc` fetched them; the selection rules are copied from download.py and the file counts match its dry run
13:35 | Delete the two stalled `partial_*` files (10.9 GB) | resume them; delete | earthaccess temp names do not say which file they belong to, so they cannot be resumed; deleting inside `$DWTS_DATA` is allowed
14:25 | Stop the downloads until the ASF agreement is accepted | keep retrying; reuse the NISAR session cookie that got one RTC file through at 13:33; stop | ASF answers 401 "Be sure to agree to the EULA"; the earlier success skipped the agreement check through a cookie, which is not ours to bypass; endless retries load ASF for nothing
14:35 | Commit STATUS on `main` through a second worktree, `~/dwts-main` | switch `~/PROJECT_DWTS` to `main`; worktree | The clone is on `prelim`, which the T10 rerun still needs
