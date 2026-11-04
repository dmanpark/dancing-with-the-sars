# AI use

What AI tools and models this project used, before and during NASA Space Apps 2026, and for what. Kept current as the work goes on.

## Tools and models

- **Claude Code** (Anthropic), model **Claude Opus 5.5** (`claude-opus-5-5`). Checked 3 Nov 2026.

No generative image, video or audio models are used. The two diagrams in the app are simple SVG drawings coded from basic shapes; each carries a visible note "Diagram made with AI assistance", and the team may redraw them.

## Before the event (to 14 Nov 2026, 09:00 local)

- **Planning and data lists.** Every commit up to 4 Nov 2026 (UTC) has Claude Opus 5.5 as co-author: the planning documents in `docs/`, the scene and reference lists in `data/`, the search and download tools in `prep/`, the quicklook images in `quicklooks/` (plotted from radar data by `prep/quicklook.py`, not generated) and the Claude Code prompts in `prompts/`. The team reviewed and directed the work.
- **Machine setup**, 3 Nov 2026. Claude Code ran `prompts/setup.md` and the pre-event part of `prompts/build.md` on the team's 3090 machine: WSL2 checks, Miniforge, the `dwts` conda env, Claude Code inside Ubuntu, and this repository's GitHub setup and placeholder page. People typed every password and login themselves.
- **Preliminary tests.** Claude Code runs `prompts/prelim-tests.md`; its code in `prelim/` is throwaway and is not reused in the submission.

## During the event

Filled in as the build goes.
