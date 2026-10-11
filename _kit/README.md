# Dazed Workshop art kit

Shared look for every Dazed mod's Steam Workshop images (1280 px wide: banner, section headers, content panels).

To make a page for a new mod, from the `workshop-art/` root:

1. `mkdir <Mod>` and write `<Mod>/sprites.json`: each name points at a sprite in a mod's `.pack` (or a plain PNG), with a scale (see the top of `sprites.py`; `Climate/sprites.json` is a full example).
2. `python3 _kit/sprites.py <Mod>`: cuts them, trimmed, into `<Mod>/sprites/`.
3. Copy `Climate/page.html` to `<Mod>/page.html`. It links `../_kit/suite.css`; keep one `<section class="shot" id="...">` per image: `banner` (`.banner`), `h-*` (`.hdr`: tile, num, h2, rule) and panels (`.panel` with `.card`, `.art`, `.bar`, `.pill`...). Put only mod-specific layout in its `<style>`.
4. `node _kit/render.mjs <Mod>` (or `node _kit/render.mjs <Mod> id1 id2` for a few): writes `<Mod>/images/<id>.png`, banner as `banner.jpg`. Panels get transparent corners.
5. Look at every image, then write `<Mod>/description.bbcode` with `[img]https://raw.githubusercontent.com/Dazedgenie/Dazed-Workshop/main/<Mod>/images/<file>[/img]` lines where the section headers go.

Needs Pillow, DazedCore's `tools/pzformat` (set `$PZFORMAT` if it is not under `/home/claude`), and Playwright for Node (found via `$PLAYWRIGHT_MODULE` or the global npm root; browsers via `$PLAYWRIGHT_BROWSERS_PATH`, default `/opt/pw-browsers`). The font is Source Sans 3 (SIL OFL, `fonts/`).
