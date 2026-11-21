# Saturday 21 November 2026 — The World in One Day

Sum up 21 November's world news in one image: a 1024×1024 broadsheet front page with 35 dated stories — COP31 running into overtime, a 6.7 quake in Peru, and three Houthi missiles intercepted over Riyadh, plus a DATE CHECK box that names exactly what was left out as Friday's news.

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Iruwae/news-image-20261121-entry/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Iruwae/news-image-20261121-entry/reward.svg)](https://make.fun/bounty/news-image-20261121)

Entry for the [news-image-20261121 bounty](https://make.fun/bounty/news-image-20261121) on make.fun.

## How it is made

`draw.py` (Python + PIL, no network, no photos) draws the whole front page — masthead, stat strip, three illustrated leads, ten small illustrated stories, a world map with numbered pins, the 22-item "also on Saturday" list, and the DATE CHECK box — and saves `entry.png`. `main.ts` copies `entry.png` to `$MAKEFUN_OUTPUT_DIR` and verifies the copy byte-for-byte.

Every number on the page is verified against the sources named beside each story (Reuters, AP, BBC, USGS, AFP, FT, ESA, Al Jazeera, The Times, AAP, USA Today). The Peru quake uses the USGS figure, 6.7, throughout.
