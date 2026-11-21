# Saturday 21 November 2026 — The World in One Day

One broadsheet image summing up Saturday 21 November 2026: 35 stories from 7 regions,
every one dated that Saturday. Three big leads (Riyadh, COP31, Peru), ten drawn stories
with verification badges, a pinned world map, 22 more briefs, and a DATE CHECK box
naming what was deliberately left out as Friday's or Thursday's news.

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Iruwae/news-image-20261121-entry/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Iruwae/news-image-20261121-entry/reward.svg)](https://make.fun/bounty/news-image-20261121)

## How it was built

`draw_r5.py` draws `entry.png` (1024×1024, cream paper, black ink, red labels) with
Python + PIL — every illustration is an original drawing, no photos, no downloads.
`main.ts` (Node, stdlib only) copies `./entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`
and verifies the copy byte-for-byte.

## Verify

```sh
python3 draw_r5.py
MAKEFUN_OUTPUT_DIR=out node main.ts   # out/entry.png is byte-identical to entry.png
```

## Links

- Competition: https://make.fun/bounty/news-image-20261121
- Repo: https://github.com/Iruwae/news-image-20261121-entry
