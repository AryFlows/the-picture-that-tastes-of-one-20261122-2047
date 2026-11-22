# The Picture That Tastes of One Ingredient

A tall stack of golden pancakes with glossy maple syrup dripping down
the sides, a melting butter pat on top, and fresh blueberries — served
on a white plate against a dark warm-brown background with a soft
spotlight, over a wooden table.

One hero dish, large and centred, filling most of the frame. No text
anywhere in the image.

## How it is drawn

Pure Python 3 standard library — no PIL, no network, no external
assets. `main.py` paints a 1024×1024 RGBA canvas procedurally:

- radial-gradient background + vignette, warm spotlight above the plate
- white plate (rim, well, rim highlight, soft shadow)
- four stacked pancakes: vertical golden-brown gradients, darker
  toasted edge rings, toasted speckles, a lighter sheen on each face
- amber maple syrup: glossy cap on the top pancake, drips down the
  stack with bright centre highlights, a pool and stray drops on the plate
- butter: pale-yellow rounded square with a melt drip and top highlight
- blueberries: shaded spheres with a specular dot and tiny crown
- a final grain + vignette pass for a photographic feel

The PNG is encoded by hand (zlib + struct): 8-bit RGBA, filter 0.
The render is deterministic (fixed seeds) and runs in a few seconds.

## Run

```sh
python3 main.py
```

Writes `/output/entry.png` (1024×1024, under 1 MB). Set the `OUT`
environment variable to write somewhere else, e.g.:

```sh
OUT=/tmp/entry.png python3 main.py
```

## Files

- `main.py` — the renderer (stdlib only)
- `README.md` — this file
- `LICENSE` — MIT
