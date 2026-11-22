#!/usr/bin/env python3
"""The picture that tastes of one ingredient.

A tall stack of golden pancakes with glossy maple syrup dripping down the
sides, a melting butter pat on top, and fresh blueberries, on a white plate
against a dark warm-brown background with a soft spotlight.

Pure standard library: a zlib + struct PNG encoder over an RGBA bytearray
canvas, everything drawn procedurally. Deterministic (fixed seed).
"""
import os
import random
import struct
import time
import zlib

W = H = 1024
OUT = os.environ.get("OUT") or "/output/entry.png"

buf = bytearray(W * H * 4)


def clamp(v, lo=0, hi=255):
    return lo if v < lo else hi if v > hi else v


def lerp(a, b, t):
    return int(a + (b - a) * t)


def mix(c1, c2, t):
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


def put(x, y, r, g, b):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 4
        buf[i] = r
        buf[i + 1] = g
        buf[i + 2] = b
        buf[i + 3] = 255


def blend(x, y, r, g, b, a):
    """Source-over onto the opaque canvas; a in 0..255."""
    if 0 <= x < W and 0 <= y < H and a > 0:
        i = (y * W + x) * 4
        ia = 255 - a
        buf[i] = (r * a + buf[i] * ia) // 255
        buf[i + 1] = (g * a + buf[i + 1] * ia) // 255
        buf[i + 2] = (b * a + buf[i + 2] * ia) // 255


def ellipse(cx, cy, rx, ry, color_fn):
    """Fill an ellipse; color_fn(x, y, nx, ny, r2) -> (r, g, b) or None."""
    x0 = max(0, int(cx - rx))
    x1 = min(W - 1, int(cx + rx) + 1)
    y0 = max(0, int(cy - ry))
    y1 = min(H - 1, int(cy + ry) + 1)
    for y in range(y0, y1 + 1):
        ny = (y - cy) / ry
        ny2 = ny * ny
        if ny2 > 1.0:
            continue
        half = rx * (1.0 - ny2) ** 0.5
        xa = int(cx - half)
        xb = int(cx + half)
        if xa < x0:
            xa = x0
        if xb > x1:
            xb = x1
        row = y * W * 4
        for x in range(xa, xb + 1):
            nx = (x - cx) / rx
            col = color_fn(x, y, nx, ny, nx * nx + ny2)
            if col is not None:
                i = row + x * 4
                buf[i] = col[0]
                buf[i + 1] = col[1]
                buf[i + 2] = col[2]
                buf[i + 3] = 255


def rrect(x0, y0, x1, y1, rad, color_fn):
    """Fill a rounded rectangle; color_fn(x, y) -> (r, g, b) or None."""
    for y in range(max(0, y0), min(H - 1, y1) + 1):
        dy = max(y0 + rad - y, 0, y - (y1 - rad))
        for x in range(max(0, x0), min(W - 1, x1) + 1):
            dx = max(x0 + rad - x, 0, x - (x1 - rad))
            if dx * dx + dy * dy <= rad * rad:
                col = color_fn(x, y)
                if col is not None:
                    put(x, y, col[0], col[1], col[2])


def capsule(cx, y0, y1, w, color_fn):
    """Vertical rounded bar (a syrup drip); color_fn(x, y) -> (r, g, b)."""
    rad = w // 2
    for y in range(y0, y1 + 1):
        for xx in range(cx - rad, cx + rad + 1):
            dx = (xx - cx) / rad
            if dx * dx > 1.0:
                continue
            col = color_fn(xx, y)
            if col is not None:
                put(xx, y, col[0], col[1], col[2])
    # rounded bottom cap
    for yy in range(y1, y1 + rad + 1):
        dy = (yy - y1) / rad
        if dy * dy > 1.0:
            continue
        half = rad * (1.0 - dy * dy) ** 0.5
        for xx in range(int(cx - half), int(cx + half) + 1):
            col = color_fn(xx, yy)
            if col is not None:
                put(xx, yy, col[0], col[1], col[2])


def write_png(path):
    raw = bytearray()
    stride = W * 4
    for y in range(H):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def draw_background():
    cx, cy = 512, 420
    for y in range(H):
        dy = (y - cy) / 780.0
        dy2 = dy * dy
        row = y * W * 4
        for x in range(W):
            dx = (x - cx) / 780.0
            d = dx * dx + dy2
            if d > 1.0:
                d = 1.0
            t = d * d * (3.0 - 2.0 * d)  # smoothstep falloff
            i = row + x * 4
            buf[i] = lerp(118, 24, t)
            buf[i + 1] = lerp(82, 14, t)
            buf[i + 2] = lerp(52, 7, t)
            buf[i + 3] = 255


def draw_table():
    rng = random.Random(7)
    streaks = [(rng.randrange(0, W), rng.randrange(0, 46) + 6,
                rng.randrange(60, 220)) for _ in range(90)]
    for y in range(810, H):
        seam = 1.0
        for sy in (862, 922, 982):
            if abs(y - sy) <= 1:
                seam = 0.55
        row = y * W * 4
        for x in range(W):
            v = ((x * 73 + y * 131) % 97) / 97.0 - 0.5
            r = int((96 + v * 22) * seam)
            g = int((60 + v * 15) * seam)
            b = int((32 + v * 9) * seam)
            i = row + x * 4
            buf[i] = clamp(r)
            buf[i + 1] = clamp(g)
            buf[i + 2] = clamp(b)
            buf[i + 3] = 255
    # soft horizontal grain streaks on the wood
    for (sx, sy, ln) in streaks:
        for k in range(ln):
            x = sx + k
            if x >= W:
                break
            blend(x, 810 + sy, 60, 36, 18, 26)


def draw_plate():
    # soft shadow under the plate (blended, fading toward its edge)
    for yy in range(750, 927):
        ny = (yy - 838) / 88.0
        ny2 = ny * ny
        if ny2 > 1.0:
            continue
        half = 445 * (1.0 - ny2) ** 0.5
        for xx in range(int(512 - half), int(512 + half) + 1):
            nx = (xx - 512) / 445.0
            r2 = nx * nx + ny2
            if r2 <= 1.0:
                blend(xx, yy, 22, 12, 6, int(85 * (1.0 - r2)))
    # outer rim, slightly grey
    ellipse(512, 800, 432, 106,
            lambda x, y, nx, ny, r2: mix((214, 208, 198), (196, 190, 180),
                                         (ny + 1) / 2))
    # inner white dish with a faint warm sheen at the top
    def dish(x, y, nx, ny, r2):
        t = (ny + 1) / 2
        c = mix((252, 250, 246), (228, 224, 216), t)
        if r2 > 0.94:  # thin inner rim ring
            c = mix(c, (198, 192, 182), 0.6)
        return c
    ellipse(512, 796, 406, 96, dish)


def pancake_face(x, y, nx, ny, r2):
    t = (ny + 1) / 2
    c = mix((236, 182, 96), (178, 118, 46), t)
    if r2 > 0.80:  # toasted outer ring
        c = mix(c, (140, 86, 28), (r2 - 0.80) / 0.20 * 0.85)
    # golden speckles, deterministic hash
    h = (x * 73856093 ^ y * 19349663) % 1000
    if h < 14:
        c = mix(c, (120, 70, 20), 0.55)
    elif h < 26:
        c = mix(c, (248, 205, 130), 0.5)
    return c


def pancake_side(x, y, nx, ny, r2):
    t = (ny + 1) / 2
    return mix((196, 134, 58), (128, 76, 26), t)


def draw_pancakes():
    # bottom to top so upper pancakes overlap the lower ones
    for cy in (700, 645, 590, 535):
        ellipse(512, cy + 24, 300, 50, pancake_side)
        ellipse(512, cy, 300, 52, pancake_face)


def syrup_color(x, y, nx, ny, r2, bright_spot=None):
    t = (ny + 1) / 2
    c = mix((226, 148, 26), (158, 88, 8), t)
    if bright_spot is not None:
        bx, by, br = bright_spot
        d = ((x - bx) / br) ** 2 + ((y - by) / br) ** 2
        if d < 1.0:
            c = mix(c, (255, 205, 100), (1.0 - d) * 0.85)
    return c


def draw_syrup():
    # pool on the plate first: pancakes cover its middle, crescents show
    ellipse(512, 762, 352, 26,
            lambda x, y, nx, ny, r2: syrup_color(
                x, y, nx, ny, r2, bright_spot=(400, 756, 60)))
    # glossy cap on the top pancake
    ellipse(512, 528, 284, 48,
            lambda x, y, nx, ny, r2: syrup_color(
                x, y, nx, ny, r2, bright_spot=(440, 512, 90)))
    # drips running down the stack
    for (cx, y0, y1, w) in ((300, 545, 690, 26),
                            (382, 552, 640, 22),
                            (470, 556, 720, 28),
                            (600, 550, 668, 24),
                            (700, 545, 620, 22)):
        capsule(cx, y0, y1, w,
                lambda x, y, nx=None, ny=None, r2=None, cx=cx, w=w:
                syrup_color(x, y, 0, 0, 0,
                            bright_spot=(cx - w // 4, y, w // 2))
                if abs(x - (cx - w // 4)) < 3 else
                mix((226, 148, 26), (158, 88, 8), (y - 540) / 200.0))
    # bright gloss streak across the cap
    for k in range(150):
        x = 400 + k
        y = 506 + int(k * 0.10)
        blend(x, y, 255, 214, 120, 110)
        blend(x, y + 1, 255, 214, 120, 60)


def draw_butter():
    def butter_face(x, y):
        t = (y - 442) / 50.0
        c = mix((252, 228, 138), (236, 196, 92), t)
        if y < 452:  # top highlight
            c = mix(c, (255, 246, 190), 0.7)
        return c
    rrect(462, 442, 562, 494, 14, butter_face)
    # melt drip sliding off the butter's lower-right edge
    ellipse(548, 500, 20, 11,
            lambda x, y, nx, ny, r2: (240, 205, 100))
    capsule(548, 498, 516, 12,
            lambda x, y: (242, 210, 105))
    # thin melt streak running down onto the syrup
    for k in range(26):
        blend(556, 512 + k, 244, 214, 110, 200 - k * 6)


def blueberry(cx, cy, r):
    def face(x, y, nx, ny, r2):
        # shaded sphere: lighter blue upper-left, near-black rim
        c = mix((88, 106, 180), (16, 22, 62), r2 ** 0.7)
        # specular dot
        d = ((nx + 0.38) ** 2 + (ny + 0.38) ** 2)
        if d < 0.10:
            c = mix(c, (235, 240, 255), (1.0 - d / 0.10) * 0.9)
        return c
    ellipse(cx, cy, r, r, face)
    # tiny dark crown at the top
    for k in range(-4, 5):
        blend(cx + k, cy - r + 6, 10, 12, 34, 220)
        blend(cx, cy - r + 6 + k, 10, 12, 34, 220)


def draw_blueberries():
    blueberry(398, 502, 34)
    blueberry(622, 506, 32)
    blueberry(792, 748, 30)
    blueberry(228, 752, 28)


def add_grain():
    rng = random.Random(20261123)
    for i in range(0, len(buf), 4):
        n = rng.randint(-2, 2)
        if n:
            buf[i] = clamp(buf[i] + n)
            buf[i + 1] = clamp(buf[i + 1] + n)
            buf[i + 2] = clamp(buf[i + 2] + n)


def main():
    t0 = time.time()
    draw_background()
    draw_table()
    draw_plate()
    draw_pancakes()
    draw_syrup()
    draw_butter()
    draw_blueberries()
    add_grain()
    size = write_png(OUT)
    print(f"wrote {OUT} {size} bytes in {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
