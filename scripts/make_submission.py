"""Write SUBMISSION.md from results.json and the fixed text below (prompts/build.md Phase 6 step 3).

usage: python scripts/make_submission.py [--video URL]
Every number comes from app/data/results.json. The human-voice quote is used only if docs/quote.md exists.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dwts import config as C  # noqa: E402
from dwts.words import f2, km2, line1, line1a, line2, signed  # noqa: E402

APP_URL = "https://dmanpark.github.io/dancing-with-the-sars/"
REPO_URL = "https://github.com/dmanpark/dancing-with-the-sars"


def limits_box() -> str:
    text = (ROOT / "docs" / "overview.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*What this can't tell you\*\*[^\n]*\n\n((?:- .*\n)+)", text)
    if not m:
        raise SystemExit("limits box not found in docs/overview.md")
    return m.group(1).rstrip("\n")


def utc(iso: str) -> str:
    import datetime as dt
    d = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return f"{d.day} {d.strftime('%b')} {d.strftime('%H:%M')} UTC"


def scenes() -> list[str]:
    out = []
    for d in C.SERIES:
        out.append(C.nisar_file(d).stem)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default="https://youtu.be/80nnnIlPmLc", help="public video link (uploaded by a team member on 15 Nov 2026)")
    a = ap.parse_args(argv)
    res = json.loads((ROOT / "app" / "data" / "results.json").read_text())
    c1, c1a, c2 = res["claim1"], res["claim1a"], res["claim2"]
    v, crop = c2["vegetation"], c2["cropland"]
    quote = ROOT / "docs" / "quote.md"
    q = quote.read_text(encoding="utf-8").strip() if quote.exists() else None
    off = res["time_offsets_h"]
    fg = res["failure_gallery"]
    cal = res["calibration"]["lead"]
    video = a.video
    md = f"""# Submission: Dancing with the SARS: The Hidden Steps

Every number below comes from `app/data/results.json` (commit {res['commit']}, generated {res['generated_utc']}). Paste each field into the team's project page on the Space Apps site.

## Project name

Dancing with the SARS: The Hidden Steps

## Summary

{line1(res)}

{line2(res)} Recall was low for every radar map, OPERA's own Sentinel-1 product included, most likely because the optical check had no clear pre-flood image and counted water that was already standing.

On 27 Sep 2026 the Gandak river in Bihar broke its flood record, and NASA-ISRO's new NISAR radar imaged it the next day, with Europe's Sentinel-1 {round(off['s1']):.0f} hours later. Today's global radar flood maps use Sentinel-1's short C-band waves, which bounce off leaves, so water under trees often goes unmapped; NISAR's longer L-band waves reach the ground underneath. Our app lets anyone watch the flood spread every 12 days, slide between the two radars' flood maps, tap a field and hear its radar signal change, and see how we checked it.
{f'''
{q}
''' if q else ''}
## Demo link (video)

{video}

## Final project link (app)

{APP_URL}

Code and data processing: {REPO_URL}

## Details

**What it does.** A one-page web app with five steps: (1) NISAR's view of the Gandak every 12 days from 6 Jul to 22 Oct 2026, animated; (2) a slider between Sentinel-1's flood map ({utc(res['passes']['s1_post'])}) and NISAR's ({utc(res['passes']['nisar_post'])}), made with the same rules; (3) the hidden steps: low ground under trees where NISAR flagged flooded vegetation and Sentinel-1 saw dry land, labelled "evidence, not verified"; (4) listen: tap any spot to see and hear its HH and HV radar brightness across the seven dates; (5) how we know: the optical check, both numbers with their intervals, a toggle that shows the fake change a naive difference makes at NISAR's swath gaps, and the limits below. An Explore mode shows every layer with a legend. It is static files on GitHub Pages, works on a phone, and needs no login.

**How we made the maps.** NISAR L2 GCOV (provisional, frequency A, HH and HV) for seven dates on track 149, frame 75, averaged 2 x 2 in linear power to 40 m. A pixel counts only where both dates' masks say fully focused and slope is at most 10 degrees, away from permanent water. Calibration offsets were measured on stable ground (high ground and raised towns) and removed per part of the 28 Sep frame, which was acquired in two parts (lead pair HH offsets {signed(cal['offsets_subtracted']['hh'].get('upper', cal['offsets_subtracted']['hh'].get('frame', {})).get('offset_db', 0))} and {signed(cal['offsets_subtracted']['hh'].get('lower', cal['offsets_subtracted']['hh'].get('frame', {})).get('offset_db', 0))} dB). Dark-water thresholds come from 10 km tiles that pass a bimodality test (Gaussian mixture, Ashman D above 2), with Kittler-Illingworth per tile. New open water is an HH drop of at least 3 dB to below the dark-water threshold, with HV also below its threshold. Flooded vegetation is an HH rise of at least 3 dB that exceeds the HV change by at least 2 dB (double bounce off trunks). The same open-water rule runs on Sentinel-1 VV and VH from OPERA RTC-S1. Every cut was fixed before the event on physical reasoning; we found no published L-band flood threshold to cite.

**How we checked it.** Claim 1 scores both radars on the same {c1['n_pixels']:,} pixels against an optical referee: water in both Landsat 9 (27 Sep, {abs(off['optical_post_before']):.0f} h before NISAR) and Sentinel-2C (1 Oct, {off['optical_post_after']:.0f} h after) OPERA DSWx-HLS maps, both clear, where JRC's water history (occurrence below 25%) stands in for a pre-flood map ({c1['n_new_water']:,} new-water pixels). NISAR F1 {f2(c1['nisar_twosided']['f1'])} (95% interval {f2(c1['nisar_twosided']['ci95'][0])} to {f2(c1['nisar_twosided']['ci95'][1])}), Sentinel-1 F1 {f2(c1['s1_twosided']['f1'])} (95% interval {f2(c1['s1_twosided']['ci95'][0])} to {f2(c1['s1_twosided']['ci95'][1])}); OPERA's own DSWx-S1 F1 {f2(c1['others']['dswx_s1']['f1'])}. The non-inferiority margin was fixed at {signed(c1['margin'])} in advance: {'passed' if c1['noninferior'] else 'not passed, so on this referee NISAR did not keep up with Sentinel-1 on open water'}. Recall is low for every method (NISAR {f2(c1['nisar_twosided']['recall'])}, Sentinel-1 {f2(c1['s1_twosided']['recall'])}, DSWx-S1 {f2(c1['others']['dswx_s1']['recall'])}), and {100 * fg['referee_only_dark_on_16sep'] / fg['referee_only_px']:.0f}% of the referee's new-water pixels that NISAR missed were already dark on 16 Sep ({100 * fg['s1_referee_only_dark_on_17sep'] / fg['s1_referee_only_px']:.0f}% of those Sentinel-1 missed were already dark on 17 Sep): with no clear pre-flood optical map, the referee likely counts water that was already standing, which a change detector does not call new. Claim 1a: {line1a(res)} Claim 2 compares NISAR's flooded-vegetation flags on 16 to 28 Sep with the 12 days before (23 Aug to 4 Sep) on the same {v['n_pixels']:,} pixels of tree cover, shrubland and wetland below 2 m above the nearest drainage, where OPERA's DSWx-S1 said dry: {km2(v['flood_km2'])} km² flagged against {km2(v['control_km2'])} km², an excess of {km2(v['excess_km2'])} km² (95% interval {km2(v['ci95'][0])} to {km2(v['ci95'][1])} km²). A caution on that number: {100 * fg['hidden_near_builtup_px'] / fg['hidden_px']:.0f}% of the flagged pixels lie within about 140 m of buildings, against {100 * fg['claim2_set_near_builtup_px'] / fg['claim2_set_px']:.0f}% of all the pixels tested, so some flags may come from walls beside trees rather than water; this is why the app labels the layer "evidence, not verified". Cropland alone: {km2(crop['excess_km2'])} km² (95% interval {km2(crop['ci95'][0])} to {km2(crop['ci95'][1])} km²){', so on cropland the test shows no hidden-water signal' if not crop['passes'] else ''}. With every calibration offset shifted by half its tile spread, the vegetation excess is {km2(c2['sensitivity']['offsets_up']['vegetation']['excess_km2'])} km² (offsets up) and {km2(c2['sensitivity']['offsets_down']['vegetation']['excess_km2'])} km² (offsets down). The planned secondary test (the flag-rate contrast between low and high ground) was dropped by the team's decision of 4 Nov, because the preliminary tests found high, gentle ground under 5% of every class; the build's recount on its own valid pixels, which leave out slopes over 10 degrees, gives {100 * c2['secondary']['classes']['10']['share_of_valid']:.1f}% for tree cover and {100 * c2['secondary']['classes']['20']['share_of_valid']:.1f}% for shrubland, above the 5% cut, so the test could have run; we kept the pre-event decision and report no contrast (the build's first run computed one before the code was brought in line with the decision; its values were discarded unread). Intervals come from a paired bootstrap over 5 km blocks (1,000 draws, seed 2026). DSWx-NI, OPERA's NISAR water product code, was dropped before the event: it needed more memory than our machine allowed and a land-cover file its schema calls optional. Tier 3 (a trust map and a check-first list) was cut when the build started late.

**What this can't tell you**

{limits_box()}

**Tools.** Python (numpy, scipy, h5py, rasterio, GDAL, scikit-learn, matplotlib), MapLibre GL JS, PMTiles, the Web Audio API, Playwright and ffmpeg for the video, GitHub Pages.

## NASA data

- NISAR L2 GCOV PROVISIONAL (ASF DAAC), track 149, frame 75: {', '.join(scenes())}.
- OPERA L3 DSWx-S1 v1 (PO.DAAC), 17 and 29 Sep 2026 00:18 UTC.
- OPERA L3 DSWx-HLS v1 (PO.DAAC), 16, 17, 27 and 29 Sep and 1 Oct 2026, built from HLS (Landsat 8 and 9, Sentinel-2B and 2C).
- OPERA L2 RTC-S1 v1 (ASF DAAC), 54 bursts on each of 17 and 29 Sep 2026.

## Other data and tools

- ESA WorldCover 2021 v200; JRC Global Surface Water occurrence v1.4; Copernicus GLO-30 DEM and GLO-30 HAND; GHSL GHS-BUILT-S E2020 R2023A.
- OPERA DSWX-SAR (tag DSWx-NI-v1.0), installed before the event for the preliminary tests.
- The team's pre-event search and download scripts in `prep/` (written before the event, cited here).
- News reports of the flood: NASA Earth Observatory, Daijiworld (1 Oct 2026), Telangana Today (1 Oct and 10 Sep 2026). Full list in `CITATIONS.md`.
- Space Apps guidance used to plan the project: the NASA Space Apps Challenge Participant FAQ (2022, legacy site, https://legacy.spaceappschallenge.org/resources/faq/) and the Judging & Awards Guide (2024 edition, https://www.spaceappschallenge.org/resources/judging-awards-guide).

## AI use

The team used an AI coding assistant (Claude) to accelerate development. Its role was limited to UI scaffolding, writing test harnesses, and debugging the pipeline. The team designed and authored all scientific logic, including the thresholding, the bimodality gate, and the optical-reference validation. No generative image, video, or audio model was used; the two diagrams are SVG drawings coded from basic shapes and marked "Diagram made with AI assistance".
"""
    (ROOT / "SUBMISSION.md").write_text(md, encoding="utf-8")
    print("wrote", ROOT / "SUBMISSION.md")


if __name__ == "__main__":
    main()
