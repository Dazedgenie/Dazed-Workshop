#!/usr/bin/env python3
"""Cut the named sprites a page needs out of the mods' art into <mod>/sprites/.

    python3 _kit/sprites.py Climate            # reads Climate/sprites.json

sprites.json maps an output name to where the art lives. Paths are relative to the
folder holding the mod repos ("repos", default $DAZED_REPOS or /home/claude):

    {
      "repos": "/home/claude",
      "sprites": {
        "heater":  {"pack": "DazedPower/Contents/mods/DazedPower/common/media/texturepacks/dazedpower.pack",
                    "sprite": "dazedpower_02_153", "scale": 2},
        "thermo":  {"png": "DazedClimate/Contents/mods/DazedClimate/common/media/textures/Item_DazedThermometer.png",
                    "scale": 4, "filter": "nearest"}
      }
    }

A multi-tile object (a 2-tile tank, say) takes "layers": [[sprite, dx, dy], ...]
instead of "sprite", drawn in that order; in PZ's 2x1 iso the second tile sits at
(+64, +32) or (-64, +32).

Every sprite is trimmed to its visible pixels, then scaled: "smooth" (Lanczos, the
default, right for 128x256 isometric tiles) or "nearest" (crisp, for 32px item icons).
Writes <mod>/sprites/<name>.png. The pack reader is DazedCore's tools/pzformat; point
$PZFORMAT at it if it is not at the default place.
"""
from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

from PIL import Image

PZFORMAT = os.environ.get(
    "PZFORMAT", "/home/claude/DazedCore/tools/pzformat")
sys.path.insert(0, PZFORMAT)

_packs: dict[Path, dict] = {}


def pack_sprites(path: Path) -> dict:
    """Every sprite in a .pack, as {name: (page image, entry)}; read once per pack."""
    if path not in _packs:
        from packfile import TexturePack  # DazedCore/tools/pzformat
        found = {}
        for page in TexturePack.read(path).pages:
            img = Image.open(io.BytesIO(page.png)).convert("RGBA")
            for e in page.entries:
                found[e.name] = (img, e)
        _packs[path] = found
    return _packs[path]


def from_pack(path: Path, name: str) -> Image.Image:
    sprites = pack_sprites(path)
    if name not in sprites:
        raise SystemExit(f"{name} is not in {path}")
    img, e = sprites[name]
    cell = Image.new("RGBA", (e.ow, e.oh))
    cell.paste(img.crop((e.x, e.y, e.x + e.w, e.y + e.h)), (e.ox, e.oy))
    return cell


def build(spec: dict, repos: Path) -> Image.Image:
    if "pack" in spec and "layers" in spec:
        # A multi-tile object: [[sprite, dx, dy], ...] drawn back to front onto one canvas.
        layers = [(from_pack(repos / spec["pack"], n), dx, dy) for n, dx, dy in spec["layers"]]
        x0 = min(dx for _, dx, _ in layers)
        y0 = min(dy for _, _, dy in layers)
        w = max(dx - x0 + i.width for i, dx, _ in layers)
        h = max(dy - y0 + i.height for i, _, dy in layers)
        img = Image.new("RGBA", (w, h))
        for layer, dx, dy in layers:
            img.alpha_composite(layer, (dx - x0, dy - y0))
    elif "pack" in spec:
        img = from_pack(repos / spec["pack"], spec["sprite"])
    elif "png" in spec:
        img = Image.open(repos / spec["png"]).convert("RGBA")
    else:
        raise SystemExit(f"sprite needs 'pack' or 'png': {spec}")
    if "crop" in spec:  # [x0, y0, x1, y1] in source pixels, before trimming
        img = img.crop(tuple(spec["crop"]))
    box = img.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    if box:
        img = img.crop(box)
    scale = float(spec.get("scale", 1))
    if scale != 1:
        size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
        rs = Image.NEAREST if spec.get("filter") == "nearest" else Image.LANCZOS
        img = img.resize(size, rs)
    if spec.get("flip"):
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    mod = Path(sys.argv[1]).resolve()
    manifest = json.loads((mod / "sprites.json").read_text())
    repos = Path(manifest.get("repos") or os.environ.get("DAZED_REPOS", "/home/claude"))
    out = mod / "sprites"
    out.mkdir(exist_ok=True)
    for name, spec in manifest["sprites"].items():
        img = build(spec, repos)
        img.save(out / f"{name}.png", optimize=True)
        print(f"sprites/{name}.png  {img.width}x{img.height}")


if __name__ == "__main__":
    main()
