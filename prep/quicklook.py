"""Download the public browse PNGs for a pre/post pair and save a side-by-side.

Browse images need no Earthdata login, so this is the fastest way to eyeball
a pair before committing to multi-GB HDF5 downloads. Note: the RGB composite
depends on the polarization mode, so colors are NOT comparable between a
quad-pol and a dual-pol date. Use it to check coverage, gaps and gross change.

Usage:
    python prep/quicklook.py PRE_SCENE POST_SCENE --out quicklooks/pair.png
"""
import argparse
import io
import urllib.request
from pathlib import Path

import asf_search as asf
from PIL import Image, ImageDraw


def latlon_browse(scene):
    g = asf.search(granule_list=[scene])[0]
    url = next(u for u in g.properties["browse"] if u.endswith("_LATLON.png"))
    with urllib.request.urlopen(url) as resp:
        return Image.open(io.BytesIO(resp.read())).convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pre")
    ap.add_argument("post")
    ap.add_argument("--out", default="quicklooks/pair.png")
    ap.add_argument("--scale", type=float, default=0.5)
    args = ap.parse_args()
    imgs = [latlon_browse(s) for s in (args.pre, args.post)]
    imgs = [im.resize((int(im.width * args.scale), int(im.height * args.scale))) for im in imgs]
    w, h = imgs[0].width, max(im.height for im in imgs)
    canvas = Image.new("RGB", (w * 2 + 10, h + 28), "white")
    draw = ImageDraw.Draw(canvas)
    for i, (im, scene) in enumerate(zip(imgs, (args.pre, args.post))):
        x = i * (w + 10)
        canvas.paste(im, (x, 28))
        f = scene.split("_")
        draw.text((x + 6, 8), f"{f[11][:8]}  T{f[5]} F{f[7]}  {f[8]} {f[9]}", fill="black")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out)
    print(args.out)


if __name__ == "__main__":
    main()
