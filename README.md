# The World on One Map — Saturday 21 November 2026

One day of world news as a single map-led broadsheet: 13 verified stories from Saturday 21 November 2026, every one pinned on a dominant world map, then told again as 13 large, readable callouts below it.

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Iruwae/news-image-20261121-entry/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Iruwae/news-image-20261121-entry/reward.svg)](https://make.fun/bounty/news-image-20261121)

[View the bounty on make.fun](https://make.fun/bounty/news-image-20261121)

## What is on the page

- **The date, huge:** Saturday 21 November 2026, with a DATE CHECK box that names exactly what was left out because it happened on Friday 20 November (or Thursday 19th).
- **The map:** 13 numbered red pins across 6 regions — COP31 in Antalya, the 6.7 quake near Junín in Peru, three Houthi missiles downed over Riyadh, Wall Street's Friday slide, BepiColombo reaching Mercury after 8 years, and eight more.
- **The 13 stories:** each with its place, field, headline, one-line summary and named source. Every headline is set large enough to read at thumbnail size; there is no fine-print list.
- **The numbers, one consistent set:** Peru 6.7 (USGS, not the 6.8 GFZ figure); market closes labelled as Friday's close; ~200 nations at COP31.

## How it was made

`draw_map.py` draws the whole page from scratch with Python + PIL — cream paper, black ink, red labels, DejaVu fonts, simplified continents, no photos and no downloads. `main.ts` copies the finished `entry.png` into the grader's output directory and verifies the copy byte-for-byte.

## Run it

```sh
python3 draw_map.py        # renders entry.png (1024x1024)
MAKEFUN_OUTPUT_DIR=out node main.ts   # copies entry.png to out/entry.png
```
