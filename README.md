# PROJECT_DWTS

Team repo for NASA Space Apps 2026, challenge **Dancing with the SARS**. Event: 14 to 15 Nov 2026. Submissions close Sunday 15 Nov at 11:59 PM local event time.

## The project

**Dancing with the SARS: The Hidden Steps.** NISAR's L-band radar finds the flood water that C-band flood maps largely miss under trees, tall crops and wetland grass. We test it on Bihar's record Gandak flood of 28 Sep 2026 against optical satellites, and turn it into a trust-rated list of places to verify first.

Start here:

- **[docs/overview.md](docs/overview.md)**: the problem, the four claims and how each could fail, the data, the demo and the 30-second video, judging fit, scope, the 39-hour schedule, risks, the pre-event checklist.
- **[docs/build-spec.md](docs/build-spec.md)**: decisions fixed before kickoff, file contracts between roles, each role's steps, done-criteria per tier, unknowns and the change log.
- **[prompts/setup.md](prompts/setup.md)**: a Claude Code prompt that sets up the 3090 machine (WSL2, Python, data folders, Earthdata login) and then starts the preliminary tests. Open Claude Code in this folder and say "Read prompts/setup.md and carry it out."
- **[prompts/prelim-tests.md](prompts/prelim-tests.md)**: the preliminary tests T0 to T12 on the real files; they write `prelim/REPORT.md` for the team to review by Sun 8 Nov.
- [docs/audit.md](docs/audit.md): the audit of version 1, scores and every fix.
- [docs/data.md](docs/data.md): verified NISAR scenes, reference products and their timing, data traps.
- [docs/review.md](docs/review.md): the critique of the original research line that started this.
- [docs/literature.md](docs/literature.md): literature matrix and the gap.
- [CLAUDE.md](CLAUDE.md): rules and conventions for Claude Code sessions in this repo.
- `docs/archive/`: superseded first drafts (the "Wallflower" concept and playbook).

![Gandak, same-mode NISAR browse images, 4 Sep, 28 Sep, 10 Oct 2026](quicklooks/gandak_T149_F075_DH_20260904_20260928_20261010.png)

Three same-mode NISAR browse images of the Gandak floodplain (track 149, frame 75). The dark vertical bands are swath gaps, and they move between dates.

## Status (3 Nov)

Pre-event. Data located, references located, plan audited and revised (version 2). Next: run the preliminary tests and hold the go or no-go review by Sun 8 Nov. No submission code: the Space Apps FAQ asks teams to start the actual work when the hackathon begins.

## Layout

```
CLAUDE.md               context and rules for Claude Code
data/events.json        candidate events (point, onset, search window)
data/scenes/            ASF query output: every NISAR granule per event, and pairs
data/refs/              CMR query output: Sentinel-1 and optical reference products near each NISAR date
data/manifest.csv       everything to download before the event, with roles and URLs
prep/                   pre-event reconnaissance tools (cite them if used during the event)
  find_scenes.py        search ASF for PROVISIONAL GCOV and pair pre/post scenes
  find_references.py    find DSWx-S1, DSWx-HLS, RTC-S1 and HLS near a NISAR time
  download.py           download manifest rows with an Earthdata login
  quicklook.py          side-by-side of the public browse PNGs for a pair
prompts/setup.md        Claude Code prompt: machine setup, then starts the tests
prompts/prelim-tests.md Claude Code prompt for the preliminary tests
prelim/                 created by the tests: throwaway code, figures, REPORT.md (outputs in prelim/out are git-ignored)
quicklooks/             saved browse comparisons
docs/                   plan, spec, audit, data notes, review, literature, archive
```

## Download roles in the manifest

| Role | What | About |
| --- | --- | --- |
| `lead-pre`, `lead-post` | Gandak 16 Sep (quad-pol) and 28 Sep (dual-pol), track 149 | 9.6 GB |
| `series`, `history` | Gandak 6 Jul, 23 Aug, 4 Sep, 10 Oct, 22 Oct: control pair, trust features, animation | 20.9 GB |
| `heldout-pre`, `heldout-post`, `heldout-history` | North Bihar 28 Aug, 9 Sep, 29 Jun, 11 Jul, track 48 (the trust-fit event; role names predate the audit) | 14.7 GB |
| `ref-pre`, `ref-post` | OPERA DSWx-HLS and DSWx-S1 water maps | small |
| `ref-pre-rtc`, `ref-post-rtc` | OPERA RTC-S1 bursts, Gandak 17 and 29 Sep, north Bihar 28 Aug and 9 Sep | a few GB |
| `fallback` | Ascending track 26, 19 Sep and 1 Oct | 13.8 GB |
| `tier3-phase` | Gandak 10 Oct quad-pol partial frame | 3.6 GB |
| `stretch`, `imagery` | Southeast Bangladesh pair; HLS imagery for figures | 12.1 GB |

## Quickstart

```bash
pip install -r requirements.txt
python prep/download.py --role lead-pre,lead-post --dry-run   # what the lead pair needs
python prep/download.py --role lead-pre,lead-post --out ~/dwts-data/downloads
```

Searching (ASF, CMR) and browse images need no login. Downloads need a free NASA Earthdata account in `~/.netrc`, which never goes in the repo. Keep data on the WSL2 ext4 disk, not on a Windows drive.

Space Apps distributes original submission content under Apache 2.0; add a LICENSE once the team agrees.
