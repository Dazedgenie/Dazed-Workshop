# Dazed-Workshop

Public images for the Dazed mods' Steam Workshop pages. Steam can only show images from a public link, so the mods' descriptions point at the files in `<Mod>/images/` on this repo's main branch.

- `_kit/`: shared styles, fonts and the renderer. See `_kit/README.md`.
- `<Mod>/page.html`: the source for that mod's images. `<Mod>/description.bbcode`: the Workshop description that uses them.

Re-render a mod from this folder: `python3 _kit/sprites.py <Mod>` then `node _kit/render.mjs <Mod>`.
