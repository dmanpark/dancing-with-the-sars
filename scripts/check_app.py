from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

STEPS = [1, 2, 3, 4, 5]


def screens_dir() -> Path:
    out = Path(os.environ.get("DWTS_OUT", "~/dwts-out")).expanduser() / "screens"
    out.mkdir(parents=True, exist_ok=True)
    return out


def wait_step(page, target: str, timeout: int = 20000) -> None:
    page.wait_for_function(f"window.__dwts && window.__dwts.ready && window.__dwts.step === {target}", timeout=timeout)
    page.evaluate("window.__dwts.waitIdle(10000)")


def visible_map_point(page) -> tuple[float, float]:
    """A point in the middle of the part of the map the card does not cover."""
    box = page.locator("#maps").bounding_box()
    card = page.locator("#card").bounding_box()
    x = box["x"] + box["width"] / 2
    bottom = box["y"] + box["height"]
    if card and card["y"] > box["y"] + 10 and card["x"] <= box["x"] + 1:  # bottom sheet on a phone
        bottom = card["y"]
    y = box["y"] + (bottom - box["y"]) / 2
    return x, y


def check_viewport(browser, name: str, ctx_args: dict, base: str, out: Path) -> dict:
    ctx = browser.new_context(**ctx_args)
    page = ctx.new_page()
    console_errors: list[str] = []
    resource_errors: list[str] = []
    page_errors: list[str] = []
    http_errors: list[str] = []

    def on_console(msg):
        if msg.type != "error":
            return
        text = msg.text
        loc = msg.location.get("url", "") if msg.location else ""
        if text.startswith("Failed to load resource"):
            resource_errors.append(f"{text} {loc}".strip())
        else:
            console_errors.append(f"{text} {loc}".strip())

    page.on("console", on_console)
    page.on("pageerror", lambda e: page_errors.append(str(e)))
    page.on("response", lambda r: http_errors.append(f"{r.status} {r.url}") if r.status >= 400 else None)

    result: dict = {"viewport": name, "steps": {}, "screenshots": []}
    t0 = time.time()
    page.goto(base, wait_until="domcontentloaded")
    page.wait_for_function("window.__dwts && window.__dwts.firstDrawMs !== null", timeout=30000)
    result["first_draw_ms"] = page.evaluate("window.__dwts.firstDrawMs")
    result["style_load_ms"] = page.evaluate("window.__dwts.styleLoadMs")
    result["load_wall_s"] = round(time.time() - t0, 2)
    result["layers_listed"] = len(page.evaluate("window.__dwts.layers || []"))
    result["has_results"] = page.evaluate("window.__dwts.hasResults")

    def shot(label: str) -> None:
        path = out / f"{name}_{label}.png"
        page.screenshot(path=str(path))
        result["screenshots"].append(str(path))

    # Step 1: let the dance run once (about one date per second), then capture.
    wait_step(page, "1")
    page.wait_for_timeout(1500)
    result["steps"]["1"] = {"date_badge": page.locator("#date-badge").is_visible()}
    page.wait_for_function("!document.querySelector('#replay') || !document.querySelector('#replay').disabled", timeout=20000)
    shot("step1")

    # Next button works
    page.click("#btn-next")
    wait_step(page, "2")

    for n in STEPS[1:]:
        if n != 2:
            page.evaluate(f"location.hash = '#step={n}'")
            wait_step(page, str(n))
        info: dict = {"title": page.locator("#card-title").inner_text()}
        if n == 2:
            page.wait_for_selector(".maplibregl-compare .compare-swiper-vertical", timeout=15000)
            page.evaluate("window.__dwts.waitIdle(10000)")
            before = page.evaluate("window.__dwts.sliderPos()")
            sw = page.locator(".compare-swiper-vertical").bounding_box()
            mx, my = sw["x"] + sw["width"] / 2, sw["y"] + sw["height"] / 2
            maps = page.locator("#maps").bounding_box()
            page.mouse.move(mx, my)
            page.mouse.down()
            for k in range(1, 11):
                page.mouse.move(mx - (mx - maps["x"] - maps["width"] * 0.25) * k / 10, my)
            page.mouse.up()
            after = page.evaluate("window.__dwts.sliderPos()")
            info["slider_before"] = round(before, 3) if before is not None else None
            info["slider_after"] = round(after, 3) if after is not None else None
            info["slider_moved"] = before is not None and after is not None and abs(after - before) > 0.1
            page.evaluate("window.__dwts.waitIdle(8000)")
        if n == 3:
            info["badge"] = page.locator(".badge-veg").inner_text()
            info["diagrams"] = page.locator(".diagram svg").count()
        if n == 4:
            x, y = visible_map_point(page)
            if ctx_args.get("has_touch"):
                page.touchscreen.tap(x, y)
            else:
                page.mouse.click(x, y)
            page.wait_for_function("window.__dwts.lastSample !== undefined", timeout=15000)
            sample = page.evaluate("window.__dwts.lastSample")
            info["tap_status"] = sample.get("status")
            info["chart_drawn"] = page.locator("#chart-box svg.chart").count() == 1
            info["mute_visible"] = page.locator("#mute").is_visible()
            info["audio_before_click"] = page.evaluate("window.__dwts.audioState()")
            listen = page.locator("#listen")
            if listen.is_enabled():
                listen.click()
                page.wait_for_timeout(600)
                info["audio_after_click"] = page.evaluate("window.__dwts.audioState()")
                page.click("#mute")
                info["muted"] = page.locator("#mute").get_attribute("aria-pressed") == "true"
                page.click("#mute")
                page.wait_for_timeout(200)
        if n == 5:
            page.click(".seg button[data-mode='naive']")
            page.evaluate("window.__dwts.waitIdle(8000)")
            shot("step5_naive")
            page.click(".seg button[data-mode='trust']")
            page.evaluate("window.__dwts.waitIdle(8000)")
            info["limits_items"] = page.locator(".limits li").count()
            info["numbers"] = page.locator(".numbers p").all_inner_texts()
        # build.md rule 3: no placeholder visible in the rendered page (details panels opened first)
        page.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")
        text = page.evaluate("document.body.innerText")
        info["placeholders"] = sorted({w for w in ("___", "TODO", "TBD", "computing", "not available") if w in text})
        result.setdefault("placeholders_seen", []).extend(f"step{n}:{w}" for w in info["placeholders"])
        result["steps"][str(n)] = info
        shot(f"step{n}")

    page.evaluate("location.hash = '#explore'")
    wait_step(page, "'explore'")
    page.wait_for_timeout(800)
    boxes = page.locator(".layer-list input[type=checkbox]:not(:disabled):not(:checked)")
    if boxes.count():
        boxes.first.check()
        page.evaluate("window.__dwts.waitIdle(8000)")
    result["steps"]["explore"] = {
        "layers": page.locator(".layer-list li").count(),
        "unavailable": page.locator(".layer-list li.na").count(),
        "pins": page.locator(".pin").count(),
    }
    shot("explore")

    result["missing_layers"] = page.evaluate("window.__dwts.missing")
    result["app_errors"] = page.evaluate("window.__dwts.errors")
    result["console_errors"] = console_errors
    result["page_errors"] = page_errors
    result["missing_files"] = sorted(set(http_errors))
    result["resource_console_lines"] = len(resource_errors)
    ctx.close()
    return result


def check_video(browser, base: str, out: Path) -> dict:
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = ctx.new_page()
    errs: list[str] = []
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" and not m.text.startswith("Failed to load resource") else None)
    page.on("pageerror", lambda e: errs.append(str(e)))
    sep = "&" if "?" in base else "?"
    page.goto(f"{base}{sep}video=1", wait_until="domcontentloaded")
    page.wait_for_function("window.__dwts && window.__dwts.videoStartMs != null", timeout=60000)
    t = time.time()
    page.wait_for_function("window.__dwts.videoDone === true", timeout=60000)
    run_s = round(time.time() - t, 2)
    path = out / "video_end.png"
    page.screenshot(path=str(path))
    res = {"video_run_s": run_s, "screenshot": str(path), "console_errors": errs, "app_errors": page.evaluate("window.__dwts.errors")}
    ctx.close()
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("base", help="base URL of the app, e.g. http://localhost:8765/")
    ap.add_argument("--video", action="store_true", help="also run the ?video=1 storyboard once at 1920 x 1080")
    ap.add_argument("--strict", action="store_true", help="also fail on HTTP 404s")
    args = ap.parse_args()
    out = screens_dir()
    summary: dict = {"base": args.base, "viewports": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        configs = [
            ("iphone13", dict(p.devices["iPhone 13"])),
            ("desktop", {"viewport": {"width": 1440, "height": 900}}),
        ]
        for name, ctx_args in configs:
            summary["viewports"].append(check_viewport(browser, name, ctx_args, args.base, out))
        if args.video:
            summary["video"] = check_video(browser, args.base, out)
        browser.close()
    bad = 0
    for v in summary["viewports"]:
        bad += len(v["console_errors"]) + len(v["page_errors"]) + len(v["app_errors"]) + len(v.get("placeholders_seen", []))
        if args.strict:
            bad += len(v["missing_files"])
    if "video" in summary:
        bad += len(summary["video"]["console_errors"]) + len(summary["video"]["app_errors"])
    summary["ok"] = bad == 0
    print(json.dumps(summary, indent=2))
    for v in summary["viewports"]:
        for e in v["console_errors"] + v["page_errors"] + v["app_errors"]:
            print(f"[{v['viewport']}] ERROR {e}", file=sys.stderr)
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
