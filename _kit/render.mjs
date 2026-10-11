// Renders every <section class="shot" id="x"> in <mod>/page.html to <mod>/images/x.png
// (the one with id "banner" to banner.jpg, quality 90).
//
//   node _kit/render.mjs Climate            # every shot
//   node _kit/render.mjs Climate rooms ice  # only these ids
//
// Needs Playwright for Node. It is found through $PLAYWRIGHT_MODULE, then a normal
// require, then the global npm root. Browsers come from $PLAYWRIGHT_BROWSERS_PATH
// (defaults to /opt/pw-browsers when that exists).
import { createRequire } from "node:module";
import { execSync } from "node:child_process";
import path from "node:path";
import fs from "node:fs";

const [modArg, ...only] = process.argv.slice(2);
if (!modArg) {
  console.error("usage: node _kit/render.mjs <ModFolder> [id ...]");
  process.exit(2);
}
const mod = path.resolve(modArg);
const pageFile = path.join(mod, "page.html");
if (!fs.existsSync(pageFile)) {
  console.error(`no page.html in ${mod}`);
  process.exit(2);
}
if (!process.env.PLAYWRIGHT_BROWSERS_PATH && fs.existsSync("/opt/pw-browsers")) {
  process.env.PLAYWRIGHT_BROWSERS_PATH = "/opt/pw-browsers";
}

function loadPlaywright() {
  const require = createRequire(import.meta.url);
  const tries = [process.env.PLAYWRIGHT_MODULE, "playwright"];
  try {
    tries.push(path.join(execSync("npm root -g", { encoding: "utf8" }).trim(), "playwright"));
  } catch {}
  for (const t of tries.filter(Boolean)) {
    try { return require(t); } catch {}
  }
  throw new Error("Playwright not found: npm i -g playwright, or set PLAYWRIGHT_MODULE");
}

const { chromium } = loadPlaywright();
const out = path.join(mod, "images");
fs.mkdirSync(out, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
await page.goto("file://" + pageFile);
await page.evaluate(() => document.fonts.ready);
// Every image must have loaded, or the shot would silently miss a sprite.
const broken = await page.$$eval("img", (imgs) => imgs.filter((i) => !i.complete || !i.naturalWidth).map((i) => i.src));
if (broken.length) {
  console.error("missing images:\n  " + broken.join("\n  "));
  process.exit(1);
}
// Transparent page so rounded panel corners blend into Steam's own background.
await page.addStyleTag({ content: "html, body { background: transparent !important }" });

let ids = await page.$$eval("section.shot", (els) => els.map((e) => e.id));
if (only.length) ids = ids.filter((id) => only.includes(id));
for (const id of ids) {
  const el = page.locator("#" + id);
  const box = await el.boundingBox();
  const jpg = id === "banner";
  const file = path.join(out, id + (jpg ? ".jpg" : ".png"));
  await el.screenshot(jpg ? { path: file, type: "jpeg", quality: 90 } : { path: file, omitBackground: true });
  const kb = Math.round(fs.statSync(file).size / 1024);
  console.log(`${path.relative(process.cwd(), file)}  ${Math.round(box.width)}x${Math.round(box.height)}  ${kb} KB${kb > 1000 ? "  (over 1 MB!)" : ""}`);
}
await browser.close();
