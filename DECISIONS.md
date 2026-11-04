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
