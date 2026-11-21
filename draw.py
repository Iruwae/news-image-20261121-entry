#!/usr/bin/env python3
"""Draw the front page for news-image-20261121: Saturday 21 November 2026.

One self-contained PIL program. No network, no downloads, no photos:
every picture on the page is drawn here with rectangles, polygons and arcs.
All facts come from the coordinator's verified brief (FACTS.md).
Output: entry.png, 1024x1024, <= 1 MiB.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (17, 17, 17)
RED = (192, 57, 43)
GREY = (90, 86, 78)
TAN = (239, 230, 208)
DARK = (16, 28, 51)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)   # noqa: E731
SERIF = lambda s: font("DejaVuSerif.ttf", s)         # noqa: E731
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)     # noqa: E731
SANS = lambda s: font("DejaVuSans.ttf", s)           # noqa: E731


def wrap(d, text, fnt, max_w):
    """Greedy word wrap using real text widths; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, fnt, color, max_w, leading):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    for line in wrap(d, text, fnt, max_w):
        d.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def chip(d, x, y, text, fnt, bg, fg=(255, 255, 255)):
    """Small filled label; returns its width."""
    w = int(d.textlength(text, font=fnt)) + 12
    h = fnt.size + 8
    d.rectangle([x, y, x + w, y + h], fill=bg)
    d.text((x + 6, y + 4), text, font=fnt, fill=fg)
    return w


# ---------------------------------------------------------------- canvas
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
M = 24                      # side margin
CW = W - 2 * M              # content width = 976

# ---- top line -------------------------------------------------------
d.text((M, 10), "THE WORLD IN ONE DAY", font=SANS_B(14), fill=RED)
right = "35 STORIES · 6 REGIONS · EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
d.text((W - M - d.textlength(right, font=SANS_B(11)), 12),
       right, font=SANS_B(11), fill=INK)
d.line([M, 30, W - M, 30], fill=INK, width=2)

# ---- masthead -------------------------------------------------------
d.text((M, 34), "Saturday 21 November 2026", font=SERIF_B(56), fill=INK)
d.text((M, 98),
       "COP31 runs into overtime · A 6.7 quake shakes Peru · "
       "Houthi missiles target Riyadh",
       font=SERIF(17), fill=INK)
d.line([M, 122, W - M, 122], fill=INK, width=1)

# ---- stat strip -----------------------------------------------------
STATS = [
    ("3", "Houthi missiles intercepted over Riyadh"),
    ("6.7", "magnitude of the Peru quake, near Junín"),
    ("-3.7%", "S&P 500, Friday's close in New York"),
    ("8 yrs", "BepiColombo's journey to Mercury"),
    ("~200", "nations negotiating at COP31 in Antalya"),
    ("0", "deaths reported in the Peru quake"),
]
sy, sh, sw = 128, 64, CW // 6
for i, (num, label) in enumerate(STATS):
    x = M + i * sw
    d.text((x + 8, sy), num, font=SANS_B(28), fill=INK)
    para(d, x + 8, sy + 34, label, SANS(10), GREY, sw - 14, 12)
    if i:
        d.line([x, sy + 4, x, sy + sh - 4], fill=(200, 192, 172), width=1)
d.line([M, sy + sh + 4, W - M, sy + sh + 4], fill=INK, width=1)

# ---- region bar -----------------------------------------------------
REGIONS = [
    ("Europe 8", (46, 111, 176)),
    ("Asia 3", (192, 57, 43)),
    ("Middle East 7", (176, 137, 46)),
    ("Africa 3", (46, 125, 79)),
    ("Americas 12", (125, 79, 163)),
    ("Global 2", (85, 85, 85)),
]
ry, rh = 202, 22
for i, (label, color) in enumerate(REGIONS):
    x = M + i * (CW // 6)
    d.rectangle([x, ry, x + CW // 6 - 1, ry + rh], fill=color)
    tw = d.textlength(label, font=SANS_B(11))
    d.text((x + (CW // 6 - tw) / 2, ry + 4), label,
           font=SANS_B(11), fill=(255, 255, 255))

# ---------------------------------------------------------------- leads
LW = (CW - 16) // 3          # lead column width = 320
LX = [M, M + LW + 8, M + 2 * (LW + 8)]
LY = 232                     # illustration top
IH = 112                     # illustration height


def lead1(x, y, w, h):
    """COP31 negotiating hall: table, flags, draft paper with FOSSIL FUELS
    struck through in red."""
    d.rectangle([x, y, x + w, y + h], fill=(31, 111, 107))
    d.rectangle([x, y, x + w, y + 26], fill=(23, 84, 81))
    for i, c in enumerate([(192, 57, 43), (46, 111, 176), (176, 137, 46),
                           (46, 125, 79), (125, 79, 163)]):
        fx = x + 18 + i * 52
        d.rectangle([fx, y + 8, fx + 30, y + 18], fill=c)
    # negotiating table
    d.rectangle([x + 14, y + 82, x + w - 14, y + h - 8], fill=(122, 82, 52))
    d.rectangle([x + 14, y + 82, x + w - 14, y + 90], fill=(146, 100, 64))
    # delegates: heads + shoulders behind the table
    for cx in (x + 48, x + 96, x + 224, x + 272):
        d.ellipse([cx - 9, y + 58, cx + 9, y + 76], fill=(52, 40, 28))
        d.pieslice([cx - 16, y + 74, cx + 16, y + 104], 180, 360,
                   fill=(40, 40, 40))
    # draft document in the middle
    px, py, pw, ph = x + w // 2 - 60, y + 28, 120, 74
    d.rectangle([px, py, px + pw, py + ph], fill=(255, 255, 255),
                outline=(120, 120, 120), width=1)
    d.text((px + 8, py + 6), "DRAFT TEXT", font=SANS_B(10), fill=GREY)
    for k in range(2):
        d.line([px + 8, py + 26 + k * 9, px + pw - 8, py + 26 + k * 9],
               fill=(170, 170, 170), width=2)
    d.text((px + 8, py + 44), "FOSSIL FUELS", font=SANS_B(11), fill=INK)
    d.line([px + 6, py + 51, px + pw - 6, py + 51], fill=RED, width=3)
    d.text((px + 8, py + 58), "— removed —", font=SANS(9), fill=RED)


def lead2(x, y, w, h):
    """Peru quake: Andes peaks, red seismograph zigzag, big 6.7 badge."""
    d.rectangle([x, y, x + w, y + h], fill=(220, 233, 242))
    d.ellipse([x + w - 52, y + 10, x + w - 16, y + 46], fill=(240, 214, 130))
    peaks = [(x, y + h), (x + 70, y + 34), (x + 130, y + h),
             (x + 110, y + h), (x + 190, y + 18), (x + 260, y + h),
             (x + 240, y + h), (x + 300, y + 52), (x + w, y + h)]
    d.polygon(peaks, fill=(107, 93, 79))
    d.polygon([(x + 62, y + 42), (x + 70, y + 34), (x + 78, y + 42)],
              fill=(255, 255, 255))
    d.polygon([(x + 182, y + 26), (x + 190, y + 18), (x + 198, y + 26)],
              fill=(255, 255, 255))
    # seismograph trace
    pts = []
    xx = x + 8
    yy = y + h - 46
    spikes = [0, 2, -3, 14, -22, 30, -18, 8, -4, 2, 0, -6, 10, -8, 3, 0]
    for s in spikes:
        pts.append((xx, yy - s))
        xx += 18
    d.line(pts, fill=RED, width=3, joint="curve")
    d.rectangle([x + w - 92, y + h - 40, x + w - 8, y + h - 8], fill=DARK)
    d.text((x + w - 84, y + h - 36), "6.7", font=SANS_B(24), fill=(255, 255, 255))


def lead3(x, y, w, h):
    """Riyadh at night: dark skyline, three interceptor arcs, bursts."""
    d.rectangle([x, y, x + w, y + h], fill=(13, 22, 46))
    for sx, sy2 in ((x + 30, y + 8), (x + 150, y + 14), (x + 250, y + 6)):
        r = 2
        d.ellipse([sx - r, sy2 - r, sx + r, sy2 + r], fill=(255, 255, 255))
    # skyline
    base = y + h
    towers = [(0, 62, 34), (40, 88, 40), (86, 54, 30), (122, 96, 46),
              (174, 70, 36), (216, 100, 44), (266, 58, 30)]
    for ox, th, tw in towers:
        d.rectangle([x + ox, base - th, x + ox + tw, base], fill=(5, 8, 18))
        for wy in range(base - th + 8, base - 6, 12):
            for wx in range(x + ox + 5, x + ox + tw - 4, 10):
                d.rectangle([wx, wy, wx + 3, wy + 4], fill=(240, 214, 130))
    # interceptor arcs + bursts
    for ax, apex in ((x + 60, y + 26), (x + 160, y + 14), (x + 258, y + 30)):
        d.arc([ax - 46, apex, ax + 46, base - 20], 200, 340,
              fill=(255, 255, 255), width=2)
        bx, by = ax, apex + 12
        for ang in range(0, 360, 45):
            import math
            ex = bx + 9 * math.cos(math.radians(ang))
            ey = by + 9 * math.sin(math.radians(ang))
            d.line([bx, by, ex, ey], fill=(255, 170, 60), width=2)
        d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(255, 200, 90))


LEADS = [
    ("1 ANTALYA, TURKEY · CLIMATE", "OVERTIME · DAY 15",
     "COP31 runs into overtime with no deal on fossil fuels",
     "Negotiators in Antalya will work an extra day after a draft deal "
     "dropped all mention of fossil fuels and a $120bn adaptation finance "
     "target. Nearly 200 nations are split; campaigners call it "
     "'the worst COP ever'. (Reuters, AP)", lead1, "Draft text"),
    ("2 JUNÍN, PERU · EARTHQUAKE", "00:09 GMT",
     "6.7 quake shakes Peru; no deaths reported",
     "The tremor struck near Junín at 7:09 pm local time, rattling Lima "
     "and sending lawmakers out of Congress. Minor damage to homes and "
     "landslides on roads; no tsunami threat. (USGS, AFP, Reuters)",
     lead2, "USGS"),
    ("3 RIYADH · MISSILES", "3 INTERCEPTED",
     "Three Houthi missiles downed over Riyadh",
     "Air defences intercepted three ballistic missiles early on Saturday, "
     "the third night of alerts in the capital. Two days earlier a Houthi "
     "strike damaged the PIF tower, Riyadh's tallest. No damage or "
     "casualties reported. (Reuters, Al Jazeera)", lead3, "Coalition count"),
]
for (kicker, tag, head, body, draw_fn, caption), x in zip(LEADS, LX):
    draw_fn(x, LY, LW, IH)
    chip(d, x + 8, LY + IH - 26, caption, SANS_B(9), (0, 0, 0))
    chip(d, x + LW - 8 - (d.textlength(tag, font=SANS_B(9)) + 12),
         LY + 8, tag, SANS_B(9), RED)
    d.text((x, LY + IH + 8), kicker, font=SANS_B(11), fill=RED)
    y = LY + IH + 26
    y = para(d, x, y, head, SANS_B(19), INK, LW, 22)
    para(d, x, y + 4, body, SANS(12), INK, LW, 15)
d.line([M, 490, W - M, 490], fill=INK, width=1)

# ------------------------------------------------------- small stories
# Each cell: flat icon (48px), red kicker, bold headline, short summary.
SW = (CW - 4 * 8) // 5           # small-story column width = 189
SX = [M + i * (SW + 8) for i in range(5)]
ROW_Y = [498, 646]
ROWH = 148


def icon_bg(x, y, w, h, color=TAN):
    d.rectangle([x, y, x + w, y + h], fill=color,
                outline=(200, 192, 172), width=1)


def icon_chart(x, y, w, h):
    icon_bg(x, y, w, h)
    d.line([x + 12, y + h - 12, x + w - 12, y + h - 12], fill=INK, width=2)
    d.line([x + 12, y + 10, x + 12, y + h - 12], fill=INK, width=2)
    pts = [(x + 16, y + 14), (x + 48, y + 20), (x + 80, y + 18),
           (x + 112, y + 30), (x + 144, y + 26), (x + 172, y + 40)]
    d.line(pts, fill=RED, width=3, joint="curve")
    d.polygon([(x + 172, y + 40), (x + 164, y + 36), (x + 168, y + 44)],
              fill=RED)


def icon_mercury(x, y, w, h):
    icon_bg(x, y, w, h, (24, 32, 54))
    d.ellipse([x + 96, y + 8, x + 158, y + 40], fill=(176, 160, 140))
    d.ellipse([x + 110, y + 14, x + 122, y + 24], fill=(140, 124, 104))
    d.ellipse([x + 132, y + 22, x + 140, y + 30], fill=(140, 124, 104))
    d.rectangle([x + 30, y + 18, x + 52, y + 28], fill=(200, 200, 200))
    d.rectangle([x + 14, y + 21, x + 30, y + 25], fill=(120, 160, 220))
    d.rectangle([x + 52, y + 21, x + 68, y + 25], fill=(120, 160, 220))
    d.line([x + 68, y + 23, x + 92, y + 23], fill=(255, 200, 90), width=2)


def icon_talk(x, y, w, h):
    icon_bg(x, y, w, h)
    d.rounded_rectangle([x + 14, y + 8, x + 96, y + 30], radius=8,
                        fill=(46, 111, 176))
    d.polygon([(x + 26, y + 30), (x + 34, y + 40), (x + 40, y + 30)],
              fill=(46, 111, 176))
    d.rounded_rectangle([x + 92, y + 20, x + 174, y + 42], radius=8,
                        fill=(192, 57, 43))
    d.polygon([(x + 150, y + 42), (x + 142, y + 48), (x + 158, y + 42)],
              fill=(192, 57, 43))
    d.text((x + 22, y + 13), "friend?", font=SANS_B(10),
           fill=(255, 255, 255))
    d.text((x + 100, y + 25), "killer", font=SANS_B(10),
           fill=(255, 255, 255))


def icon_server(x, y, w, h):
    icon_bg(x, y, w, h)
    d.rectangle([x + 58, y + 6, x + 118, y + h - 6], fill=(40, 44, 52))
    for k in range(3):
        yy = y + 10 + k * 12
        d.rectangle([x + 64, yy, x + 112, yy + 7], fill=(90, 96, 110))
        d.ellipse([x + 66, yy + 2, x + 70, yy + 6], fill=(120, 220, 120))
    d.polygon([(x + 140, y + 10), (x + 164, y + 38), (x + 116, y + 38)],
              fill=(240, 200, 40), outline=INK)
    d.text((x + 136, y + 24), "!", font=SANS_B(14), fill=INK)


def icon_datacentre(x, y, w, h):
    icon_bg(x, y, w, h)
    d.rectangle([x + 60, y + 8, x + 128, y + h - 8], fill=(70, 76, 90))
    for r in range(3):
        for c in range(3):
            d.rectangle([x + 68 + c * 20, y + 14 + r * 11,
                         x + 80 + c * 20, y + 21 + r * 11],
                        fill=(140, 200, 240))
    d.ellipse([x + 132, y + 8, x + 172, y + 40], fill=(46, 125, 79))
    d.text((x + 144, y + 12), "$", font=SANS_B(20), fill=(255, 255, 255))


def icon_plane(x, y, w, h):
    icon_bg(x, y, w, h, (220, 233, 242))
    d.polygon([(x + 20, y + 26), (x + 120, y + 14), (x + 150, y + 20),
               (x + 120, y + 28), (x + 60, y + 34), (x + 44, y + 40),
               (x + 36, y + 32)], fill=(60, 60, 70))
    d.polygon([(x + 78, y + 18), (x + 92, y + 8), (x + 96, y + 20)],
              fill=(60, 60, 70))
    d.text((x + 152, y + 8), "✕", font=SANS_B(20), fill=RED)


def icon_prison(x, y, w, h):
    icon_bg(x, y, w, h)
    d.rectangle([x + 40, y + 6, x + 148, y + h - 6], fill=(120, 116, 108))
    for k in range(6):
        bx = x + 48 + k * 18
        d.rectangle([bx, y + 6, bx + 6, y + h - 6], fill=(40, 40, 40))
    d.rectangle([x + 40, y + 20, x + 148, y + 26], fill=(40, 40, 40))


def icon_ballot(x, y, w, h):
    icon_bg(x, y, w, h)
    d.rectangle([x + 62, y + 20, x + 126, y + h - 8], fill=(176, 137, 46))
    d.rectangle([x + 56, y + 14, x + 132, y + 22], fill=(140, 106, 32))
    d.rectangle([x + 84, y + 16, x + 104, y + 20], fill=(17, 17, 17))
    d.rectangle([x + 88, y + 2, x + 100, y + 16], fill=(255, 255, 255),
                outline=GREY)
    d.text((x + 90, y + 4), "✓", font=SANS_B(10), fill=RED)
    d.text((x + 138, y + 26), "29 NOV", font=SANS_B(11), fill=RED)


def icon_flags(x, y, w, h):
    icon_bg(x, y, w, h)
    d.rectangle([x + 52, y + 8, x + 56, y + h - 8], fill=INK)
    d.rectangle([x + 130, y + 8, x + 134, y + h - 8], fill=INK)
    d.polygon([(x + 56, y + 8), (x + 108, y + 14), (x + 56, y + 22)],
              fill=(192, 57, 43))
    d.polygon([(x + 134, y + 8), (x + 82, y + 14), (x + 134, y + 22)],
              fill=(46, 111, 176))
    d.ellipse([x + 88, y + 28, x + 100, y + 40], fill=(240, 214, 130))


def icon_candle(x, y, w, h):
    icon_bg(x, y, w, h, (40, 36, 44))
    d.ellipse([x + 86, y + 6, x + 102, y + 20], fill=(255, 170, 60))
    d.rectangle([x + 88, y + 20, x + 100, y + h - 8], fill=(240, 240, 230))
    d.rectangle([x + 78, y + h - 10, x + 110, y + h - 6], fill=(120, 116, 108))
    d.text((x + 116, y + 14), "600", font=SANS_B(16), fill=(255, 255, 255))


SMALL = [
    ("4 NEW YORK · MARKETS", "Wall Street slides into correction",
     "S&P 500 fell 3.7% on Friday, Nasdaq 5.28%, Dow 1.93%; Nasdaq erased "
     "all its 2026 gains. Nvidia sank 13% amid an SEC probe. "
     "(Reuters, FT)", icon_chart),
    ("5 MERCURY · SPACE", "BepiColombo reaches Mercury after 8 years",
     "The ESA-JAXA craft enters Mercury orbit at 19:24 CET, only the "
     "second mission ever; science starts in April. (ESA, USA Today)",
     icon_mercury),
    ("6 KYIV · DIPLOMACY", "Zelensky calls Putin a 'killer'",
     "After Trump called the Russian leader a friend, Zelensky hit back; "
     "Tusk called the Poland missile a deliberate provocation. (BBC)",
     icon_talk),
    ("7 WASHINGTON · TECH", "FBI probes a second hack of its crime database",
     "The bureau is investigating another cyberattack on its national "
     "crime database as US outages continue. (Reuters)", icon_server),
    ("8 WASHINGTON · TECH", "Trump threatens a tax on data centres abroad",
     "The president threatens a 'tremendous' tax on US firms building AI "
     "data centres overseas, to stop Beijing taking the lead. (FT)",
     icon_datacentre),
    ("9 COPENHAGEN · SECURITY", "Denmark expels a Russian diplomat",
     "Copenhagen accuses Moscow of plotting to assassinate a "
     "US-Ukrainian rapper. (BBC)", icon_plane),
    ("10 NEW YORK · POLITICS", "Mamdani to close Rikers by 2032",
     "The mayor-elect announces a plan to shut New York's jail complex "
     "within six years. (BBC)", icon_prison),
    ("11 MADRID · POLITICS", "Spain heads to a 29 November election",
     "Conservatives gain as the country heads to the polls at the end "
     "of the month. (Reuters)", icon_ballot),
    ("12 KATHMANDU · POLITICS", "Nepal's new PM faces his India test",
     "Balendra Shah makes his first visit to India as prime minister. "
     "(BBC)", icon_flags),
    ("13 JOHANNESBURG · SOCIETY", "Nearly 600 women killed in 3 months",
     "South Africa's femicide toll is laid bare in new figures. (BBC)",
     icon_candle),
]
for i, (kicker, head, body, draw_fn) in enumerate(SMALL):
    x = SX[i % 5]
    y = ROW_Y[i // 5]
    draw_fn(x, y, SW, 48)
    d.text((x, y + 52), kicker, font=SANS_B(9), fill=RED)
    yy = y + 64
    yy = para(d, x, yy, head, SANS_B(12), INK, SW, 14)
    para(d, x, yy + 2, body, SANS(10), INK, SW, 12)

# ------------------------------------------------- map + also-on list
AY = 800
d.text((M, AY), "WHERE IT HAPPENED", font=SANS_B(12), fill=INK)
d.text((M + 312, AY), "ALSO ON SATURDAY 21 NOVEMBER — 22 MORE STORIES",
       font=SANS_B(12), fill=INK)
d.line([M, AY + 16, W - M, AY + 16], fill=INK, width=1)
MY = AY + 20                       # map/list top
MH = 118                          # map/list height

# simplified world map
mx, my, mw, mh = M, MY, 288, MH
d.rectangle([mx, my, mx + mw, my + mh], fill=(200, 220, 230))
land = (220, 199, 156)
d.polygon([(mx + 18, my + 18), (mx + 66, my + 8), (mx + 96, my + 22),
           (mx + 84, my + 44), (mx + 52, my + 52), (mx + 26, my + 40)],
          fill=land)                                   # N America
d.polygon([(mx + 62, my + 62), (mx + 88, my + 58), (mx + 96, my + 84),
           (mx + 80, my + 112), (mx + 66, my + 92)], fill=land)  # S America
d.polygon([(mx + 138, my + 16), (mx + 168, my + 10), (mx + 176, my + 30),
           (mx + 158, my + 40), (mx + 140, my + 32)], fill=land)  # Europe
d.polygon([(mx + 140, my + 48), (mx + 172, my + 44), (mx + 184, my + 66),
           (mx + 168, my + 96), (mx + 148, my + 78)], fill=land)  # Africa
d.polygon([(mx + 182, my + 12), (mx + 262, my + 8), (mx + 276, my + 34),
           (mx + 252, my + 58), (mx + 214, my + 52), (mx + 190, my + 32)],
          fill=land)                                   # Asia
d.polygon([(mx + 246, my + 96), (mx + 272, my + 94), (mx + 276, my + 108),
           (mx + 252, my + 112)], fill=land)           # Australia
PINS = {1: (0.56, 0.28), 2: (0.20, 0.66), 3: (0.62, 0.40),
        4: (0.17, 0.28), 5: (0.92, 0.10), 6: (0.55, 0.20),
        7: (0.19, 0.36), 8: (0.24, 0.42), 9: (0.52, 0.13),
        10: (0.13, 0.35), 11: (0.47, 0.32), 12: (0.74, 0.38),
        13: (0.56, 0.68)}
for n, (fx, fy) in PINS.items():
    px, py = mx + int(fx * mw), my + int(fy * mh)
    d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
              outline=(255, 255, 255), width=1)
    t = str(n)
    d.text((px - d.textlength(t, font=SANS_B(8)) / 2, py - 6), t,
           font=SANS_B(8), fill=(255, 255, 255))

ALSO = [
    "14 Port-au-Prince — Salvadoran troops hit by explosives (AP)",
    "15 Los Angeles — Man convicted of starting Palisades fire (Reuters)",
    "16 Kharg Island — 14+ Iranian tankers mass in blockade test (Reuters)",
    "17 Gaza — Israeli strikes kill Palestinians; West Bank violence (Reuters)",
    "18 Las Vegas — NFL suspends Puka Nacua amid lawsuit (AP)",
    "19 Washington — US declassifies more UFO footage (BBC)",
    "20 Paris — Police sentenced over beating of Michel Zecler (BBC)",
    "21 Washington — Firms fined $811m keep scamming migrants (BBC)",
    "22 Jerusalem — Likud: Netanyahu must be sole PM (Reuters)",
    "23 Addis Ababa — Africa launches own credit rating agency (Reuters)",
    "24 Washington — Trump turns 2028 race into spectacle (AP)",
    "25 Jerusalem — Israel's GDP per head surges (Reuters)",
    "26 Pretoria — ANC fights to keep key cities after setback (Reuters)",
    "27 Shenzhen — Trump and Xi: humans must control military AI (Reuters)",
    "28 Hodeidah — Saudi-led strikes hit Houthi-held cities (Al Jazeera)",
    "29 Cox's Bazar — Rohingya recount 2017 exodus (Reuters)",
    "30 Antalya — Delegates sleep in corridors as COP31 drags on (The Times)",
    "31 Antalya — Campaigners call COP31 “the worst COP ever” (The Times)",
    "32 Riyadh — Houthis threaten Saudi ports and power station (Al Jazeera)",
    "33 Lima — Lawmakers walk out of Congress as tremor hits (Reuters)",
    "34 Junín — Landslides block roads after quake; no deaths (AFP)",
    "35 Antalya — Bowen: world will quit fossil fuels regardless (AAP)",
]
LX0, LW2 = M + 312, 336
for i, item in enumerate(ALSO):
    col, row = i // 11, i % 11
    d.text((LX0 + col * (LW2 + 8), MY + row * 11), item,
           font=SANS(9), fill=INK)

# ---- date check -----------------------------------------------------
DY = 946
d.rectangle([M, DY, W - M, DY + 34], outline=RED, width=2)
para(d, M + 8, DY + 4,
     "DATE CHECK — Left out as Friday 20 November's news: the Kyiv bridges "
     "attack and the Kryvyi Rih strike, the UK–EU deal, GTA VI's $3.79bn "
     "day one, the daraxonrasib trial results, the Gen Z strikes across "
     "Europe, and Bolsonaro's hospital stay. The ICJ's Myanmar genocide "
     "ruling was Thursday 19 November. Not yet shown: the final COP31 text.",
     SANS(10), INK, CW - 16, 13)

# ---- footer ---------------------------------------------------------
d.text((M, 990),
       "Every story here happened, or was first reported, on Saturday "
       "21 November 2026. Officials' counts are attributed.",
       font=SANS(10), fill=GREY)
d.text((W - M - d.textlength("Sources named beside each story · original drawings",
                             font=SANS(10)), 990),
       "Sources named beside each story · original drawings",
       font=SANS(10), fill=GREY)

img.save("entry.png", optimize=True)
print("saved entry.png", img.size)
