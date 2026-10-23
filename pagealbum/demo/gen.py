#!/usr/bin/env python3
"""ストアのスクリーンショット用のデモ画像を書き出す（PageAlbum の R8-3: 自分で作った画像だけを使う）。

山の重なりと空のグラデーションだけで描く、架空の風景の画集。乱数の種を固定しているので、何度実行しても同じ画像になる。
`python3 pagealbum/demo/gen.py`（Pillow が必要）
"""
import math
import pathlib
import random

from PIL import Image, ImageDraw, ImageFilter

OUT = pathlib.Path(__file__).resolve().parent / "img"

# (名前, 空の上, 空の下, 山の手前の色, 太陽か月の色, 縦長か)
SCENES = [
    ("dawn", (250, 214, 180), (252, 240, 222), (64, 70, 96), (255, 246, 230), True),
    ("noon", (150, 196, 230), (226, 238, 246), (52, 92, 84), (255, 255, 250), True),
    ("dusk", (92, 70, 128), (244, 156, 120), (40, 30, 58), (255, 214, 170), True),
    ("night", (14, 22, 48), (44, 64, 104), (8, 12, 26), (236, 236, 220), True),
    ("fog", (210, 214, 216), (238, 240, 240), (120, 128, 134), (250, 250, 248), True),
    ("autumn", (240, 206, 150), (250, 236, 210), (120, 54, 36), (255, 244, 220), True),
    ("snow", (196, 214, 232), (240, 246, 250), (150, 170, 192), (255, 255, 255), True),
    ("sea", (120, 176, 204), (230, 240, 240), (30, 70, 96), (255, 250, 236), True),
    ("forest", (196, 220, 196), (236, 244, 232), (28, 64, 44), (250, 250, 236), True),
    ("desert", (236, 176, 120), (250, 226, 190), (150, 84, 50), (255, 238, 200), True),
    ("aurora", (16, 40, 52), (40, 120, 110), (6, 16, 22), (220, 250, 236), False),
    ("lake", (176, 196, 222), (232, 236, 244), (60, 72, 104), (255, 252, 240), False),
]


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def ridge(rng, w, base, amp, rough):
    """山の稜線（x ごとの高さ）。周波数の違う sin を重ねる。"""
    waves = [(rng.uniform(0.6, 1.4) * f, rng.uniform(0, math.tau), amp / (i + 1) ** rough) for i, f in enumerate([1, 2.3, 5.1, 11.7])]
    return [base - sum(a * math.sin(x / w * math.tau * f + p) for f, p, a in waves) for x in range(w + 1)]


def scene(i, name, top, bottom, ink, light, portrait):
    rng = random.Random(1000 + i)
    w, h = (1200, 1680) if portrait else (1680, 1050)
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp(top, bottom, (y / h) ** 0.8))

    # 太陽か月（ぼかした光の輪のあとに本体）
    cx, cy, r = rng.uniform(0.25, 0.75) * w, rng.uniform(0.18, 0.32) * h, w * rng.uniform(0.05, 0.08)
    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse([cx - r * 2.4, cy - r * 2.4, cx + r * 2.4, cy + r * 2.4], fill=90)
    img.paste(light, mask=glow.filter(ImageFilter.GaussianBlur(r)))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=light)

    # 山を奥から手前へ。奥ほど空の色に近づける（空気遠近）
    layers = 5
    for k in range(layers):
        t = (k + 1) / layers
        color = lerp(lerp(bottom, top, 0.3), ink, t ** 1.4)
        base = h * (0.48 + 0.1 * k)
        pts = ridge(rng, w, base, h * (0.09 - 0.012 * k), 1.2 + 0.3 * k)
        d.polygon([(0, h)] + [(x, y) for x, y in enumerate(pts)] + [(w, h)], fill=color)
    return img


OUT.mkdir(parents=True, exist_ok=True)
for i, s in enumerate(SCENES):
    path = OUT / f"{i + 1:02d}-{s[0]}.jpg"
    scene(i, *s).save(path, quality=86, optimize=True, progressive=True)
    print(f"wrote {path.name}")
