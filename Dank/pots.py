#!/usr/bin/env python3
"""Stand Dank's plant layers in their containers, the way the game draws them, into Dank/pots/<name>.png.

    python3 Dank/pots.py            # then python3 _kit/sprites.py Dank (sprites.json reads pots/*.png)

The game draws a plant as a layer over its plot, raised by Config.PLANT_LIFT (1x pixels, so x2 on the 128x256
tiles). XL pots use the 10% bigger layer sheet (dazeddank_overlay_02). Layer numbers follow
tools/make_overlay_sprites.py: seedling 0, female 1 + 4*shape + stage (Veg, PreFlower, Flowering, Ripe),
male 145 + 3*shape + stage (PreFlower, Flowering, Ripe), coloured 250 + 28*colour + 4*shape (+1 for Ripe).
Shapes: landrace haze hybrid kush afghan auto tree. Colours: purple frosty gold dark.
"""
import io, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, "/home/claude/DazedCore/Contents/mods/DazedCore/tools/pzformat")
from packfile import TexturePack

TP = Path("/home/claude/DazedDank/Contents/mods/DazedDank/42/media/texturepacks")
OUT = Path(__file__).parent / "pots"
SHAPES = ["landrace", "haze", "hybrid", "kush", "afghan", "auto", "tree"]
COLOURS = ["purple", "frosty", "gold", "dark"]
STAGES = ["veg", "pre", "flower", "ripe"]
# container: (sheet, tile, lift, xl)
POTS = {
    "ground": ("plants_01", 65, 0, False), "small": ("plants_01", 195, 13, False), "large": ("plants_01", 196, 20, False),
    "xlbag": ("hydro_01", 236, 28, True), "dwc": ("plants_01", 374, 20, False), "xldwc": ("hydro_01", 350, 27, True),
    "rdwc": ("hydro_01", 2, 20, False), "ebb": ("hydro_01", 123, 20.5, False), "none": None,
}
_cells = {}


def cell(sheet, n):
    key = f"dazeddank_{sheet}"
    if key not in _cells:
        found = {}
        for pg in TexturePack.read(TP / f"{key}.pack").pages:
            img = Image.open(io.BytesIO(pg.png)).convert("RGBA")
            for e in pg.entries:
                c = Image.new("RGBA", (e.ow, e.oh))
                c.paste(img.crop((e.x, e.y, e.x + e.w, e.y + e.h)), (e.ox, e.oy))
                found[e.name] = c
        _cells[key] = found
    return _cells[key][f"{key}_{n}"]


def layer(kind):
    """'seedling', 'f:<shape>:<stage>', 'm:<shape>:<stage>' or 'c:<colour>:<shape>:<flower|ripe>'."""
    p = kind.split(":")
    if p[0] == "seedling":
        return 0
    if p[0] == "f":
        return 1 + 4 * SHAPES.index(p[1]) + STAGES.index(p[2])
    if p[0] == "m":
        return 145 + 3 * SHAPES.index(p[1]) + STAGES.index(p[2]) - 1
    return 250 + 28 * COLOURS.index(p[1]) + 4 * SHAPES.index(p[2]) + (1 if p[3] == "ripe" else 0)


def compose(pot, plant):
    pdef = POTS[pot]
    xl = bool(pdef and pdef[3])
    top = 64
    out = Image.new("RGBA", (128, 256 + top))
    if pdef:
        out.alpha_composite(cell(pdef[0], pdef[1]), (0, top))
    if plant:
        lift = round(pdef[2] * 2) if pdef else 0
        out.alpha_composite(cell("overlay_02" if xl else "overlay_01", layer(plant)), (0, top - lift))
    return out


# name: (container, plant layer)
WANT = {
    # life cycle in a large bag
    "st-seedling": ("large", "seedling"), "st-veg": ("large", "f:hybrid:veg"), "st-pre": ("large", "f:hybrid:pre"),
    "st-flower": ("large", "f:hybrid:flower"), "st-ripe": ("large", "f:hybrid:ripe"),
    # the six starters in flower, standing in soil
    "s-knox": ("ground", "f:kush:flower"), "s-muldraugh": ("ground", "c:purple:afghan:flower"),
    "s-rosewood": ("ground", "c:dark:tree:flower"), "s-riverside": ("ground", "f:haze:flower"),
    "s-westpoint": ("ground", "c:frosty:landrace:flower"), "s-marchridge": ("ground", "c:gold:hybrid:flower"),
    "s-male": ("ground", "m:haze:flower"), "s-purple": ("ground", "c:purple:kush:ripe"),
    # containers
    "p-ground": ("ground", "f:kush:flower"), "p-small": ("small", "f:auto:flower"), "p-large": ("large", "f:hybrid:flower"),
    "p-xlbag": ("xlbag", "f:tree:veg"), "p-dwc": ("dwc", "f:kush:flower"), "p-xldwc": ("xldwc", "f:kush:veg"),
    "p-rdwc": ("rdwc", "c:frosty:landrace:flower"), "p-ebb": ("ebb", "f:afghan:flower"),
    # banner
    "b-1": ("dwc", "c:gold:hybrid:ripe"), "b-2": ("large", "f:kush:ripe"), "b-3": ("ground", "c:frosty:landrace:ripe"),
    "b-4": ("xlbag", "c:purple:afghan:ripe"), "b-5": ("ebb", "f:hybrid:flower"), "b-6": ("rdwc", "f:haze:ripe"),
    "b-7": ("small", "c:dark:tree:flower"),
    # cloning: a mother in veg
    "mother": ("xlbag", "f:hybrid:veg"), "c-sown": ("small", "f:auto:veg"),
}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, (pot, plant) in WANT.items():
        compose(pot, plant).save(OUT / f"{name}.png", optimize=True)
    print(len(WANT), "pots written to", OUT)
