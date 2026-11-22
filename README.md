[![make.fun · the-picture-that-tastes-of-one-20261122-2047](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)
[![rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/AryFlows/the-picture-that-tastes-of-one-20261122-2047/rank.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)
[![reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/AryFlows/the-picture-that-tastes-of-one-20261122-2047/reward.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)

# The Picture That Tastes of One Ingredient

One hero dish, large and centred, filling most of the frame: a tall stack of
four golden pancakes with glossy maple syrup dripping down the sides, a
melting butter pat on top, and fresh blueberries — served on a white plate
against a dark warm-brown background with a soft spotlight, a wooden table
along the bottom edge. No text anywhere in the image.

Everything is drawn procedurally by `main.py` in pure Python 3.13 standard
library (no PIL, no network, no external assets):

- a radial-gradient background with a vignette, so the spotlight falls on
  the stack;
- a white plate ellipse with a soft shadow and a thin inner rim;
- four stacked pancakes, each a golden vertical-gradient ellipse with a
  darker toasted edge ring and deterministic speckles, plus a shaded side
  ellipse that gives the stack its thickness;
- amber maple syrup as a glossy cap on the top pancake, five drips running
  down the stack, and a pool peeking out on the plate, with bright gloss
  highlights on the syrup;
- a pale-yellow butter pat (rounded square) with a top highlight, a melt
  drip, and a thin melt streak;
- four blueberries as shaded spheres with a specular dot and a tiny crown;
- a light final grain pass (±2) for a photographic feel.

The picture is deterministic: a fixed seed makes every run produce the same
image.

## Run

```sh
python3 main.py
```

Writes `/output/entry.png` — a 1024×1024 PNG, under 1 MiB. The output path
can be overridden with the `OUT` environment variable, e.g.
`OUT=/tmp/entry.png python3 main.py`. Runs in about 10 seconds, no network.

## Files

- `main.py` — the whole generator: stdlib PNG encoder (zlib + struct over
  an RGBA canvas) and all procedural drawing.
- `README.md` — this file.
- `LICENSE` — MIT.
