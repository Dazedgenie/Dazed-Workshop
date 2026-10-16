# Dark brick wall tile for the neon look (behind the mod logos). Tileable, 320x136.
#   python3 _kit/neon/brick.py   -> _kit/neon/brick.png
import random, os
from PIL import Image, ImageDraw, ImageFilter
random.seed(7)
W, H, BW, BH, M = 320, 136, 80, 34, 3
img = Image.new("RGB", (W, H), (9, 8, 13))
d = ImageDraw.Draw(img)
for row in range(H // BH):
    off = 0 if row % 2 == 0 else BW // 2
    for i in range(-1, W // BW + 1):
        x0 = i * BW + off
        base = random.randint(20, 30)
        col = (base + random.randint(0, 4), base - 4 + random.randint(0, 3), base + 6 + random.randint(0, 5))
        for dx in (0, W, -W):
            d.rounded_rectangle([x0 + dx + M // 2, row * BH + M // 2, x0 + dx + BW - M, row * BH + BH - M], radius=3, fill=col)
px = img.load()
for y in range(H):
    for x in range(W):
        n = random.randint(-5, 5)
        r, g, b = px[x, y]
        px[x, y] = (max(0, r + n), max(0, g + n), max(0, b + n))
img = img.filter(ImageFilter.GaussianBlur(0.6))
img.save(os.path.join(os.path.dirname(__file__), "brick.png"))
