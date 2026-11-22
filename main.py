#!/usr/bin/env python3
"""The picture that tastes of one ingredient.

A tall stack of golden pancakes with glossy maple syrup dripping down
the sides, a melting butter pat on top, and fresh blueberries - on a
white plate, dark warm-brown background, soft spotlight, wooden table.

Pure standard library: a bytearray RGBA canvas, procedural drawing
(ellipses, discs, capsules, rounded rects, gradients) and a hand-rolled
PNG encoder (zlib + struct). Deterministic: fixed seeds throughout.

Run:  python3 main.py        (writes /output/entry.png)
       OUT=/tmp/entry.png python3 main.py
"""
import math
import os
import random
import struct
import time
import zlib

W = H = 1024
canvas = bytearray(W * H * 4)


def _clamp255(v):
    return 0 if v < 0 else (255 if v > 255 else v)


def fill_row(y, x0, x1, r, g, b, a=255):
    """Horizontal run. Fast slice when opaque, per-pixel blend otherwise."""
    if y < 0 or y >= H:
        return
    x0 = max(0, x0)
    x1 = min(W - 1, x1)
    if x1 < x0:
        return
    if a >= 255:
        i = (y * W + x0) * 4
        canvas[i:i + (x1 - x0 + 1) * 4] = bytes((r, g, b, 255)) * (x1 - x0 + 1)
    else:
        ia = 255 - a
        for x in range(x0, x1 + 1):
            i = (y * W + x) * 4
            canvas[i] = (r * a + canvas[i] * ia) // 255
            canvas[i + 1] = (g * a + canvas[i + 1] * ia) // 255
            canvas[i + 2] = (b * a + canvas[i + 2] * ia) // 255
            canvas[i + 3] = 255


def disc(cx, cy, rad, rgb, alpha=255):
    """Filled circle, flat colour."""
    r, g, b = rgb
    for y in range(max(0, cy - rad), min(H, cy + rad + 1)):
        dy = (y - cy) / rad
        s = 1.0 - dy * dy
        if s <= 0:
            continue
        dx = int(rad * math.sqrt(s))
        fill_row(y, cx - dx, cx + dx, r, g, b, alpha)


def ellipse(cx, cy, rx, ry, c_top, c_bot, alpha=255):
    """Vertical-gradient filled ellipse."""
    for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
        dy = (y - cy) / ry
        s = 1.0 - dy * dy
        if s <= 0:
            continue
        dx = int(rx * math.sqrt(s))
        t = (y - (cy - ry)) / (2.0 * ry)
        r = int(c_top[0] + (c_bot[0] - c_top[0]) * t)
        g = int(c_top[1] + (c_bot[1] - c_top[1]) * t)
        b = int(c_top[2] + (c_bot[2] - c_top[2]) * t)
        fill_row(y, cx - dx, cx + dx, r, g, b, alpha)


def capsule_v(x, y0, y1, w, rgb, alpha=255):
    """Vertical drip: rounded-end thick line."""
    rad = w // 2
    disc(x, y0, rad, rgb, alpha)
    disc(x, y1, rad, rgb, alpha)
    r, g, b = rgb
    for y in range(y0, y1 + 1):
        fill_row(y, x - rad, x + rad, r, g, b, alpha)


def rounded_rect(cx, cy, w, h, rad, c_top, c_bot, alpha=255):
    """Vertical-gradient rounded rectangle."""
    x0, y0 = cx - w // 2, cy - h // 2
    y1 = cy + h // 2
    for y in range(max(0, y0), min(H, y1 + 1)):
        t = (y - y0) / max(1, h)
        r = int(c_top[0] + (c_bot[0] - c_top[0]) * t)
        g = int(c_top[1] + (c_bot[1] - c_top[1]) * t)
        b = int(c_top[2] + (c_bot[2] - c_top[2]) * t)
        dx = w // 2
        if y < y0 + rad:
            d = rad - (y - y0)
            dx = int(w // 2 - rad + math.sqrt(max(0, rad * rad - d * d)))
        elif y > y1 - rad:
            d = rad - (y1 - y)
            dx = int(w // 2 - rad + math.sqrt(max(0, rad * rad - d * d)))
        fill_row(y, cx - dx, cx + dx, r, g, b, alpha)


def write_png(path):
    """Minimal PNG encoder: 8-bit RGBA, filter 0, zlib level 6."""
    raw = bytearray()
    stride = W * 4
    for y in range(H):
        raw.append(0)
        raw += canvas[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def draw_background():
    # Deep warm-brown vertical gradient.
    top = (34, 19, 9)
    bot = (66, 38, 17)
    for y in range(H):
        t = y / (H - 1)
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        fill_row(y, 0, W - 1, r, g, b)
    # Soft warm spotlight centred above the plate.
    scx, scy, srad = 512, 380, 560
    glow = (150, 96, 42)
    for y in range(max(0, scy - srad), min(H, scy + srad + 1)):
        dy = (y - scy) / srad
        rem = 1.0 - dy * dy
        if rem <= 0:
            continue
        dxmax = int(srad * math.sqrt(rem))
        for x in range(max(0, scx - dxmax), min(W, scx + dxmax + 1)):
            dx = (x - scx) / srad
            d2 = dx * dx + dy * dy
            if d2 >= 1.0:
                continue
            a = int(110 * (1.0 - d2) * (1.0 - d2))
            if a <= 0:
                continue
            i = (y * W + x) * 4
            ia = 255 - a
            canvas[i] = (glow[0] * a + canvas[i] * ia) // 255
            canvas[i + 1] = (glow[1] * a + canvas[i + 1] * ia) // 255
            canvas[i + 2] = (glow[2] * a + canvas[i + 2] * ia) // 255


def draw_table():
    # Wooden table along the bottom.
    top_y = 742
    for y in range(top_y, H):
        t = (y - top_y) / (H - top_y)
        r = int(74 + 26 * t)
        g = int(46 + 16 * t)
        b = int(22 + 8 * t)
        fill_row(y, 0, W - 1, r, g, b)
    # Plank seams with a faint light edge below each seam.
    for sy in (812, 884, 956):
        fill_row(sy, 0, W - 1, 38, 22, 10)
        fill_row(sy + 1, 0, W - 1, 96, 60, 30)
    # Vertical board joints, kept faint so the table does not read as tiles.
    for sx in (180, 700, 940):
        for y in range(top_y, H):
            fill_row(y, sx, sx + 1, 52, 32, 15, 90)
    # A few darker wood-grain streaks (fixed seed: deterministic).
    rng = random.Random(11)
    for _ in range(46):
        gy = rng.randrange(top_y + 6, H - 4)
        gx = rng.randrange(0, W - 200)
        gl = rng.randrange(60, 220)
        fill_row(gy, gx, gx + gl, 58, 34, 16, 70)


def draw_plate():
    # Soft shadow under the plate, then rim and inner well.
    ellipse(512, 672, 360, 96, (20, 10, 4), (20, 10, 4), alpha=110)
    ellipse(512, 650, 352, 108, (232, 224, 208), (196, 186, 166))
    ellipse(512, 646, 318, 94, (252, 247, 238), (224, 216, 200))
    # Faint rim highlight along the top edge of the plate.
    ellipse(512, 566, 300, 26, (255, 252, 244), (255, 252, 244), alpha=90)


def draw_pancakes():
    # Four golden pancakes, bottom first. Each gets a darker toasted
    # edge ring, a golden body, and a few toasted speckles.
    stack = [
        (512, 640, 258, 56),
        (510, 588, 250, 54),
        (514, 538, 242, 52),
        (512, 490, 232, 50),
    ]
    rng = random.Random(7)
    for cx, cy, rx, ry in stack:
        ellipse(cx, cy, rx + 5, ry + 5, (146, 90, 22), (110, 62, 14))
        ellipse(cx, cy, rx, ry, (238, 192, 106), (178, 118, 34))
        # Lighter golden sheen across the upper face.
        ellipse(cx, cy - int(ry * 0.35), int(rx * 0.82), int(ry * 0.42),
                (242, 202, 122), (232, 182, 96), alpha=130)
        # Toasted speckles.
        for _ in range(12):
            sx = rng.randrange(cx - rx + 22, cx + rx - 22)
            sy = rng.randrange(cy - ry + 10, cy + ry - 10)
            ndx = (sx - cx) / rx
            ndy = (sy - cy) / ry
            if ndx * ndx + ndy * ndy > 0.9:
                continue
            disc(sx, sy, rng.randrange(4, 10), (150, 92, 18), alpha=48)


def draw_syrup():
    amber = (178, 94, 8)
    # Glossy pool on the plate around the base of the stack.
    ellipse(512, 678, 255, 22, (190, 104, 12), (150, 76, 6), alpha=200)
    ellipse(512, 674, 225, 17, (205, 118, 16), (170, 90, 8), alpha=200)
    # A few stray syrup drops on the plate.
    disc(300, 700, 10, amber, alpha=200)
    disc(722, 706, 12, amber, alpha=200)
    disc(772, 672, 8, amber, alpha=200)
    # Drips running down the sides of the stack, with a bright
    # glossy centre line on each one.
    for (x, y1, w) in [(288, 640, 22), (340, 600, 16), (430, 550, 14),
                       (592, 580, 14), (668, 620, 18), (724, 560, 20)]:
        capsule_v(x, 486, y1, w, amber, alpha=235)
        capsule_v(x - w // 4, 492, y1 - 6, max(3, w // 3),
                  (240, 170, 60), alpha=110)
    # Glossy amber cap pooling on the top pancake.
    ellipse(512, 472, 205, 34, (214, 128, 22), (176, 92, 8), alpha=240)
    ellipse(512, 466, 170, 24, (232, 152, 40), (200, 114, 14), alpha=220)
    # Bright highlight streak across the cap.
    ellipse(470, 458, 90, 10, (255, 214, 110), (255, 214, 110), alpha=120)


def draw_butter():
    # Pale-yellow pat, melting: a soft rounded square with a melt
    # drip sliding down its right side onto the syrup.
    rounded_rect(512, 428, 120, 48, 12,
                 (255, 233, 150), (247, 205, 100))
    # Melt drip.
    capsule_v(548, 446, 474, 12, (250, 214, 110), alpha=230)
    # Glossy top highlight.
    ellipse(484, 412, 34, 8, (255, 248, 200), (255, 248, 200), alpha=130)
    # Soft shadow where the butter meets the syrup.
    ellipse(512, 452, 62, 8, (160, 90, 10), (160, 90, 10), alpha=70)


def blueberry(cx, cy, rad):
    """Shaded sphere: dark blue-purple, light from the upper left,
    bright specular dot, tiny crown at the top."""
    for y in range(max(0, cy - rad), min(H, cy + rad + 1)):
        dy = (y - cy) / rad
        for x in range(max(0, cx - rad), min(W, cx + rad + 1)):
            dx = (x - cx) / rad
            d2 = dx * dx + dy * dy
            if d2 > 1.0:
                continue
            t = 1.0 - d2
            # Highlight blob towards the upper left.
            hx, hy = dx + 0.38, dy + 0.42
            h = max(0.0, 1.0 - (hx * hx + hy * hy) * 2.2)
            r = _clamp255(int(28 + 66 * t + 95 * h))
            g = _clamp255(int(28 + 66 * t + 95 * h))
            b = _clamp255(int(84 + 86 * t + 110 * h))
            i = (y * W + x) * 4
            canvas[i] = r
            canvas[i + 1] = g
            canvas[i + 2] = b
            canvas[i + 3] = 255
    # Specular dot.
    disc(cx - int(rad * 0.36), cy - int(rad * 0.40), max(2, rad // 6),
         (235, 235, 255), alpha=220)
    # Crown: small dark star at the top of the berry.
    disc(cx, cy - rad + 4, 3, (16, 16, 44))
    for k in range(5):
        ang = -math.pi / 2 + k * (2 * math.pi / 5)
        disc(int(cx + 6 * math.cos(ang)), int(cy - rad + 4 + 6 * math.sin(ang)),
             2, (52, 52, 96))


def draw_blueberries():
    blueberry(428, 452, 26)
    blueberry(600, 448, 24)
    blueberry(742, 692, 22)
    blueberry(282, 700, 20)


def finish():
    """One combined pass: vignette (darken the corners) + fine grain."""
    rng = random.Random(20261123)
    cx, cy = W / 2, H / 2
    for y in range(H):
        dy = (y - cy) / (H * 0.62)
        for x in range(W):
            dx = (x - cx) / (W * 0.62)
            d2 = dx * dx + dy * dy
            vig = 1.0
            if d2 > 0.55:
                vig = 1.0 - 0.30 * min(1.0, (d2 - 0.55) / 0.45)
            g = rng.randint(-2, 2)
            i = (y * W + x) * 4
            canvas[i] = _clamp255(int(canvas[i] * vig) + g)
            canvas[i + 1] = _clamp255(int(canvas[i + 1] * vig) + g)
            canvas[i + 2] = _clamp255(int(canvas[i + 2] * vig) + g)


def main():
    t0 = time.time()
    draw_background()
    draw_table()
    draw_plate()
    draw_pancakes()
    draw_syrup()
    draw_butter()
    draw_blueberries()
    finish()
    out = os.environ.get("OUT", "/output/entry.png")
    size = write_png(out)
    print(f"wrote {out} {W}x{H} {size} bytes in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
