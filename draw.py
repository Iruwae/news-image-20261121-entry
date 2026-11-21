#!/usr/bin/env python3
"""Round 2 entry for make.fun news-image-20261121.

Draws a 1024x1024 newspaper front page summing up Saturday 21 November
2026: 3 big leads, 10 small stories, a world map with pins 1-13, and a
numbered list of 22 more stories (35 total). Everything is flat vector
art drawn with PIL; no network, no photos, no downloaded images.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
M = 14                      # side margin
CW = W - 2 * M              # content width = 996

PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (192, 57, 43)
MUTED = (90, 90, 90)
RULE = (26, 26, 26)
SEA = (215, 229, 227)
LAND = (227, 211, 168)
LAND_LINE = (190, 172, 120)
NAVY = (20, 33, 61)

FDIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
WARN = []


def wrap(text, f, width):
    """Greedy word wrap; returns list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if f.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(x, y, text, f, width, fill=INK, lh=None, max_lines=None, name=""):
    """Draw wrapped text; returns (lines_used, bottom_y). Records warnings."""
    if lh is None:
        lh = int(f.size * 1.32)
    lines = wrap(text, f, width)
    if max_lines is not None and len(lines) > max_lines:
        WARN.append(f"{name}: {len(lines)} lines > max {max_lines} :: {text[:60]}")
        lines = lines[:max_lines]
    for i, line in enumerate(lines):
        if f.getlength(line) > width + 1:
            WARN.append(f"{name}: line too wide :: {line[:60]}")
        d.text((x, y + i * lh), line, font=f, fill=fill)
    return len(lines), y + len(lines) * lh


def text_w(text, f):
    return f.getlength(text)


def rule_y(y, x0=M, x1=W - M, w=2, fill=RULE):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)


def rrect(x0, y0, x1, y1, fill, outline=None, radius=3, width=1):
    d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                        outline=outline, width=width)


def italic_text(x, y, text, f, fill):
    """Fake oblique: draw on a layer, shear it, paste back."""
    tw = int(f.getlength(text)) + 6
    th = f.size + 10
    layer = Image.new("RGBA", (tw + 40, th), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((20, 2), text, font=f, fill=fill)
    shear = 0.16
    layer = layer.transform((tw + 40, th), Image.AFFINE,
                            (1, shear, -shear * th, 0, 1, 0),
                            resample=Image.BICUBIC)
    img.paste(layer, (x - 18, y), layer)


def tag(x, y, text, f, fill=RED, fg=(255, 255, 255), pad_x=7, h=None):
    """Small filled label; returns its width."""
    tw = int(f.getlength(text))
    hh = h if h is not None else f.size + 8
    rrect(x, y, x + tw + 2 * pad_x, y + hh, fill=fill, radius=2)
    d.text((x + pad_x, y + (hh - f.size) // 2 - 1), text, font=f, fill=fg)
    return tw + 2 * pad_x


# ---------------------------------------------------------------- top line
f_top_l = SANS_B(13)
f_top_r = SANS_B(11)
d.text((M, 10), "THE WORLD IN ONE DAY", font=f_top_l, fill=RED)
right_top = "35 STORIES \u00b7 6 REGIONS \u00b7 EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
d.text((W - M - text_w(right_top, f_top_r), 12), right_top,
       font=f_top_r, fill=INK)
rule_y(30)

# ---------------------------------------------------------------- masthead
d.text((M, 34), "Saturday 21 November 2026", font=SERIF_B(58), fill=INK)
italic_text(M, 98,
            "COP31 runs into overtime \u00b7 A 6.7 quake shakes Peru "
            "\u00b7 Houthi missiles target Riyadh",
            SANS(19), INK)
rule_y(122)

# ---------------------------------------------------------------- stat strip
STATS = [
    ("3", "Houthi missiles intercepted over Riyadh"),
    ("6.7", "magnitude of the Peru quake, near Jun\u00edn"),
    ("-3.7%", "S&P 500, Friday's close in New York"),
    ("8 yrs", "BepiColombo's journey to Mercury"),
    ("~200", "nations negotiating at COP31 in Antalya"),
    ("0", "deaths reported in the Peru quake"),
]
stat_w = CW // 6
f_num = SANS_B(28)
f_cap = SANS(10)
for i, (num, cap) in enumerate(STATS):
    x0 = M + i * stat_w
    if i:
        d.line([(x0, 128), (x0, 186)], fill=(200, 190, 170), width=1)
    d.text((x0 + 8, 126), num, font=f_num, fill=INK)
    block(x0 + 8, 158, cap, f_cap, stat_w - 16, lh=12, max_lines=2,
          name=f"stat{i}")

# ---------------------------------------------------------------- region bar
REGIONS = [
    ("Europe 7", 7, (47, 111, 178)),
    ("Asia 3", 3, (192, 57, 43)),
    ("Middle East 8", 8, (176, 141, 15)),
    ("Africa 3", 3, (46, 125, 50)),
    ("Americas 12", 12, (123, 75, 166)),
    ("Global 2", 2, (102, 102, 102)),
]
rx = M
ry, rh = 192, 28
for label, count, color in REGIONS:
    seg_w = CW * count / 35.0
    d.rectangle([rx, ry, rx + seg_w - 1, ry + rh], fill=color)
    f_reg = SANS_B(11 if label.startswith("Global") else 12)
    d.text((rx + (seg_w - text_w(label, f_reg)) / 2, ry + 7),
           label, font=f_reg, fill=(255, 255, 255))
    rx += seg_w

# ---------------------------------------------------------------- lead art
def lead_cop31(x, y, w, h):
    """Big simple draft document: FOSSIL FUELS struck through in red."""
    d.rectangle([x, y, x + w, y + h], fill=(233, 228, 210))
    # paper sheet with shadow
    px, py, pw, ph = x + 12, y + 12, w - 24, h - 20
    d.rectangle([px + 4, py + 4, px + pw + 4, py + ph + 4], fill=(190, 182, 160))
    d.rectangle([px, py, px + pw, py + ph], fill=(255, 255, 255))
    # folded corner
    d.polygon([(px + pw, py), (px + pw - 22, py),
               (px + pw, py + 22)], fill=(225, 222, 210))
    d.text((px + 16, py + 8), "DRAFT TEXT", font=SANS_B(11), fill=MUTED)
    f_big = SERIF_B(25)
    word = "FOSSIL FUELS"
    wx = px + (pw - text_w(word, f_big)) / 2
    wy = py + 24
    d.text((wx, wy), word, font=f_big, fill=INK)
    # thick red strike through the words
    d.line([(wx - 8, wy + 16), (wx + text_w(word, f_big) + 8, wy + 10)],
           fill=RED, width=6)
    d.line([(wx - 8, wy + 21), (wx + text_w(word, f_big) + 8, wy + 15)],
           fill=RED, width=3)
    d.text((px + (pw - text_w("\u2014 removed \u2014", SANS_B(13))) / 2, wy + 40),
           "\u2014 removed \u2014", font=SANS_B(13), fill=RED)
    f_mid = SANS_B(15)
    word2 = "$120bn ADAPTATION"
    wx2 = px + (pw - text_w(word2, f_mid)) / 2
    wy2 = wy + 60
    d.text((wx2, wy2), word2, font=f_mid, fill=INK)
    d.line([(wx2 - 6, wy2 + 9), (wx2 + text_w(word2, f_mid) + 6, wy2 + 7)],
           fill=RED, width=4)
    tag(x + w - 168, y + 0, "DAY 15 \u00b7 OVERTIME", SANS_B(12))


def lead_quake(x, y, w, h):
    """Mountains, red seismograph zigzag, big 6.7 badge."""
    d.rectangle([x, y, x + w, y + h], fill=(223, 233, 236))
    # pale sun
    d.ellipse([x + w - 52, y + 8, x + w - 14, y + 46], fill=(240, 214, 130))
    # mountains
    d.polygon([(x, y + h), (x + 70, y + 34), (x + 140, y + h)], fill=(138, 122, 99))
    d.polygon([(x + 90, y + h), (x + 190, y + 22), (x + w, y + h)],
              fill=(111, 98, 80))
    d.polygon([(x + 210, y + h), (x + 270, y + 48), (x + w, y + h)],
              fill=(138, 122, 99))
    # snow caps
    d.polygon([(x + 178, y + 34), (x + 190, y + 22), (x + 202, y + 34),
               (x + 196, y + 30), (x + 190, y + 36), (x + 184, y + 30)],
              fill=(250, 250, 248))
    # seismograph line
    pts = [(x + 6, y + 62), (x + 40, y + 62), (x + 52, y + 44),
           (x + 64, y + 82), (x + 76, y + 52), (x + 88, y + 72),
           (x + 100, y + 58), (x + 130, y + 62), (x + 142, y + 30),
           (x + 154, y + 92), (x + 166, y + 50), (x + 178, y + 70),
           (x + 190, y + 60), (x + 220, y + 62), (x + 232, y + 46),
           (x + 244, y + 78), (x + 256, y + 60), (x + 290, y + 62),
           (x + w - 6, y + 62)]
    d.line(pts, fill=RED, width=3, joint="curve")
    # big magnitude badge
    rrect(x + w - 92, y + h - 44, x + w - 8, y + h - 8, fill=NAVY, radius=4)
    d.text((x + w - 84, y + h - 42), "6.7", font=SANS_B(26), fill=(255, 255, 255))
    tag(x + 8, y + h - 28, "USGS", SANS_B(11), fill=NAVY)


def lead_riyadh(x, y, w, h):
    """Night skyline, three interception arcs with starbursts."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    # stars
    for sx, sy in [(24, 14), (70, 26), (150, 10), (210, 22), (260, 12),
                   (300, 30), (40, 44), (120, 40), (240, 44)]:
        d.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=(255, 255, 255))
    # crescent moon
    d.ellipse([x + 18, y + 10, x + 48, y + 40], fill=(240, 230, 180))
    d.ellipse([x + 28, y + 6, x + 56, y + 38], fill=NAVY)
    # skyline
    buildings = [(0, 58, 44, 62), (48, 40, 42, 80), (94, 66, 38, 54),
                 (136, 30, 46, 90), (186, 52, 40, 68), (230, 44, 44, 76),
                 (278, 62, 46, 58)]
    for bx, bt, bw, bh in buildings:
        d.rectangle([x + bx, y + bt, x + bx + bw, y + h], fill=(13, 21, 38))
        for wy in range(y + bt + 8, y + h - 8, 12):
            for wx in range(x + bx + 6, x + bx + bw - 4, 11):
                if (wx + wy) % 3 == 0:
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=(240, 200, 90))
    # interception arcs + bursts
    for cx, cy, r in [(90, 78, 46), (170, 66, 52), (255, 74, 48)]:
        d.arc([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
              start=200, end=340, fill=(255, 255, 255), width=2)
        bx, by = x + cx, y + cy - r + 4
        for ang in range(0, 360, 45):
            import math
            a = math.radians(ang)
            d.line([(bx, by), (bx + 9 * math.cos(a), by + 9 * math.sin(a))],
                   fill=(255, 200, 60), width=2)
        d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(255, 200, 60))
    tag(x + w - 138, y + 6, "3 INTERCEPTED", SANS_B(12))


LEADS = [
    ("1 ANTALYA, TURKEY \u00b7 CLIMATE", "OVERTIME \u00b7 DAY 15",
     "COP31 runs into overtime with no deal on fossil fuels",
     "Negotiators in Antalya will work an extra day after a draft deal "
     "dropped all mention of fossil fuels and a $120bn adaptation finance "
     "target. Nearly 200 nations are split; a third draft is due Saturday "
     "morning and Panama threatens to block any text without fossil-fuel "
     "language. Campaigners call it 'the worst COP ever'. (Reuters, AP)",
     lead_cop31),
    ("2 JUN\u00cdN, PERU \u00b7 EARTHQUAKE", "00:09 GMT",
     "6.7 quake shakes Peru; no deaths reported",
     "The tremor struck near Jun\u00edn at 7:09 pm local time, rattling Lima "
     "and sending lawmakers out of Congress. Minor damage to homes and "
     "landslides on roads; no tsunami threat. A magnitude-5 aftershock "
     "followed at 05:12 UTC. (USGS, AFP, Reuters, GDACS)",
     lead_quake),
    ("3 RIYADH \u00b7 MISSILES", "3 INTERCEPTED",
     "Three Houthi missiles downed over Riyadh",
     "Air defences intercepted three ballistic missiles early on Saturday, "
     "the third night of alerts in the capital. The coalition also "
     "destroyed a drone aimed at the south and two missiles fired toward "
     "Jazan. Two days earlier a Houthi strike damaged the PIF tower, "
     "Riyadh's tallest. No damage or casualties reported. "
     "(Reuters, Al Jazeera)",
     lead_riyadh),
]

lead_w = (CW - 2 * 12) // 3
LY = 226
for i, (label, _kick, head, body, art) in enumerate(LEADS):
    x0 = M + i * (lead_w + 12)
    art(x0, LY, lead_w, 120)
    d.text((x0, LY + 126), label, font=SANS_B(12), fill=RED)
    block(x0, LY + 142, head, SANS_B(20), lead_w, lh=22, max_lines=2,
          name=f"lead{i} head")
    block(x0, LY + 188, body, SANS(11), lead_w, lh=14, max_lines=6,
          name=f"lead{i} body")
rule_y(500)

# ---------------------------------------------------------------- small icons
def icon_markets(x, y, w, h):
    d.line([(x + 8, y + h - 10), (x + w - 8, y + h - 10)], fill=INK, width=2)
    d.line([(x + 8, y + 6), (x + 8, y + h - 10)], fill=INK, width=2)
    pts = [(x + 12, y + 12), (x + 40, y + 18), (x + 62, y + 14),
           (x + 90, y + 30), (x + 118, y + 26), (x + 150, y + 40),
           (x + w - 14, y + h - 16)]
    d.line(pts, fill=RED, width=3, joint="curve")
    d.polygon([(x + w - 22, y + h - 22), (x + w - 8, y + h - 22),
               (x + w - 14, y + h - 8)], fill=RED)


def icon_mercury(x, y, w, h):
    # ringed planet, left; small probe, right
    cx, cy, r = x + 52, y + h // 2 + 2, 24
    d.ellipse([cx - r - 34, cy - 8, cx + r + 34, cy + 8], outline=(150, 120, 80),
              width=3)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(176, 141, 94))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 90, 55), width=2)
    for dx, dy, dr in [(-10, -8, 4), (8, 6, 5), (2, -14, 3), (-4, 12, 3)]:
        d.ellipse([cx + dx - dr, cy + dy - dr, cx + dx + dr, cy + dy + dr],
                  fill=(140, 105, 65))
    # probe: body + panels + dish
    px, py = x + 128, y + 14
    d.rectangle([px, py, px + 26, py + 16], fill=(90, 110, 130))
    d.rectangle([px - 22, py + 3, px - 2, py + 13], fill=(47, 111, 178))
    d.rectangle([px + 28, py + 3, px + 48, py + 13], fill=(47, 111, 178))
    d.line([(px + 13, py), (px + 13, py - 10)], fill=INK, width=2)
    d.ellipse([px + 8, py - 16, px + 18, py - 6], outline=INK, width=2)


def icon_kyiv(x, y, w, h):
    # two BIG speech bubbles
    rrect(x + 2, y + 4, x + 96, y + 36, fill=(47, 111, 178), radius=8)
    d.polygon([(x + 20, y + 36), (x + 30, y + 36), (x + 16, y + 48)],
              fill=(47, 111, 178))
    d.text((x + 10, y + 10), "friend?", font=SANS_B(17), fill=(255, 255, 255))
    rrect(x + 92, y + 22, x + w - 2, y + 54, fill=RED, radius=8)
    d.polygon([(x + w - 30, y + 54), (x + w - 20, y + 54), (x + w - 34, y + 64)],
              fill=RED)
    d.text((x + 102, y + 28), "killer", font=SANS_B(17), fill=(255, 255, 255))


def icon_fbi(x, y, w, h):
    # server stack + warning triangle
    for i in range(3):
        yy = y + 6 + i * 16
        rrect(x + 8, yy, x + 96, yy + 13, fill=(40, 44, 52), radius=2)
        d.ellipse([x + 14, yy + 4, x + 20, yy + 10], fill=(120, 200, 120))
        d.line([(x + 28, yy + 6), (x + 88, yy + 6)], fill=(150, 150, 150), width=2)
    # warning triangle
    tx, ty = x + 128, y + 8
    d.polygon([(tx + 26, ty), (tx + 52, ty + 44), (tx, ty + 44)],
              fill=(240, 200, 40), outline=INK)
    d.text((tx + 21, ty + 14), "!", font=SANS_B(22), fill=INK)


def icon_datacentre(x, y, w, h):
    for j, rx in enumerate([x + 8, x + 66]):
        rrect(rx, y + 4, rx + 50, y + h - 6, fill=(40, 44, 52), radius=3)
        for k in range(4):
            yy = y + 10 + k * 12
            d.line([(rx + 6, yy), (rx + 44, yy)], fill=(150, 150, 150), width=2)
            d.ellipse([rx + 38, yy + 3, rx + 43, yy + 8], fill=(120, 200, 120))
    d.ellipse([x + 128, y + 8, x + 176, y + 56], fill=(46, 125, 50))
    d.ellipse([x + 128, y + 8, x + 176, y + 56], outline=INK, width=2)
    d.text((x + 146, y + 14), "$", font=SANS_B(28), fill=(255, 255, 255))


def icon_plane(x, y, w, h):
    # clean plane silhouette, nose right
    d.polygon([(x + 20, y + 30), (x + 120, y + 22), (x + 150, y + 28),
               (x + 150, y + 34), (x + 120, y + 38), (x + 20, y + 36)],
              fill=(30, 40, 60))
    d.polygon([(x + 70, y + 28), (x + 92, y + 8), (x + 104, y + 8),
               (x + 96, y + 28)], fill=(30, 40, 60))
    d.polygon([(x + 66, y + 34), (x + 82, y + 52), (x + 94, y + 52),
               (x + 90, y + 34)], fill=(30, 40, 60))
    d.polygon([(x + 20, y + 30), (x + 8, y + 16), (x + 16, y + 16),
               (x + 28, y + 28)], fill=(30, 40, 60))
    d.ellipse([x + 128, y + 27, x + 134, y + 33], fill=(255, 255, 255))
    # red X
    cx, cy = x + w - 16, y + 14
    d.line([(cx - 8, cy - 8), (cx + 8, cy + 8)], fill=RED, width=4)
    d.line([(cx - 8, cy + 8), (cx + 8, cy - 8)], fill=RED, width=4)


def icon_rikers(x, y, w, h):
    for i in range(7):
        bx = x + 12 + i * 22
        d.rectangle([bx, y + 4, bx + 8, y + h - 14], fill=(40, 44, 52))
    d.rectangle([x + 6, y + 2, x + w - 6, y + 8], fill=(40, 44, 52))
    d.rectangle([x + 6, y + h - 16, x + w - 6, y + h - 10], fill=(40, 44, 52))
    d.text((x + w - 52, y + h - 12), "2032", font=SANS_B(13), fill=RED)


def icon_ballot(x, y, w, h):
    # big simple ballot box + paper going in
    d.polygon([(x + 66, y + 2), (x + 96, y + 2), (x + 88, y + 22),
               (x + 74, y + 22)], fill=(255, 255, 255), outline=INK)
    d.rectangle([x + 30, y + 22, x + 132, y + h - 6], fill=(196, 164, 110))
    d.rectangle([x + 30, y + 22, x + 132, y + h - 6], outline=INK, width=2)
    d.rectangle([x + 62, y + 22, x + 100, y + 28], fill=INK)
    d.text((x + 62, y + 34), "\u2713", font=SANS_B(26), fill=RED)
    tag(x + w - 62, y + 2, "29 NOV", SANS_B(11))


def icon_flags(x, y, w, h):
    # Nepal flag (crimson double pennon) + India tricolor
    d.line([(x + 30, y + 4), (x + 30, y + h - 4)], fill=INK, width=3)
    d.polygon([(x + 30, y + 8), (x + 78, y + 20), (x + 30, y + 30)],
              fill=(220, 20, 60), outline=INK)
    d.polygon([(x + 30, y + 30), (x + 72, y + 40), (x + 30, y + 50)],
              fill=(220, 20, 60), outline=INK)
    d.ellipse([x + 38, y + 14, x + 46, y + 22], fill=(255, 255, 255))
    d.ellipse([x + 38, y + 36, x + 46, y + 44], fill=(255, 255, 255))
    d.line([(x + 112, y + 4), (x + 112, y + h - 4)], fill=INK, width=3)
    fx = x + 112
    d.rectangle([fx, y + 8, fx + 62, y + 20], fill=(255, 153, 51))
    d.rectangle([fx, y + 20, fx + 62, y + 32], fill=(255, 255, 255))
    d.rectangle([fx, y + 32, fx + 62, y + 44], fill=(19, 136, 8))
    d.ellipse([fx + 25, y + 20, fx + 37, y + 32], outline=(0, 0, 128), width=2)


def icon_candle(x, y, w, h):
    rrect(x + 6, y + 2, x + w - 6, y + h - 2, fill=(26, 26, 26), radius=4)
    # candle + flame
    d.rectangle([x + 34, y + 20, x + 52, y + h - 14], fill=(245, 245, 240))
    d.ellipse([x + 38, y + 6, x + 48, y + 20], fill=(255, 170, 40))
    d.ellipse([x + 41, y + 10, x + 45, y + 17], fill=(255, 220, 100))
    d.text((x + 66, y + 12), "600", font=SANS_B(34), fill=(255, 255, 255))


SMALL = [
    ("4 NEW YORK \u00b7 MARKETS", "Friday's close",
     "Wall Street slides into correction",
     "S&P 500 \u22123.7%, Nasdaq \u22125.28%; Nvidia \u221213%, SEC probe. "
     "(Reuters, FT)", icon_markets),
    ("5 MERCURY \u00b7 SPACE", None,
     "BepiColombo reaches Mercury after 8 years",
     "ESA-JAXA craft captured by Mercury's gravity; science starts in "
     "April. (ESA)", icon_mercury),
    ("6 KYIV \u00b7 DIPLOMACY", None,
     "Zelensky calls Putin a 'killer'",
     "Zelensky hit back after Trump called Putin a friend. (BBC)",
     icon_kyiv),
    ("7 WASHINGTON \u00b7 TECH", None,
     "FBI probes second hack of crime database",
     "FBI investigates another attack on its national crime database. "
     "(Reuters)", icon_fbi),
    ("8 WASHINGTON \u00b7 TECH", None,
     "Trump threatens tax on data centres abroad",
     "Trump threatens 'tremendous' tax on AI centres built abroad. (FT)",
     icon_datacentre),
    ("9 COPENHAGEN \u00b7 SECURITY", None,
     "Denmark expels a Russian diplomat",
     "Denmark says Moscow plotted to kill a US-Ukrainian rapper. "
     "(BBC)", icon_plane),
    ("10 NEW YORK \u00b7 POLITICS", None,
     "Mamdani to close Rikers by 2032",
     "Mayor-elect plans to shut New York's jail complex within six years. "
     "(BBC)", icon_rikers),
    ("11 MADRID \u00b7 POLITICS", "29 NOV",
     "Spain heads to a 29 November election",
     "Conservatives gain ahead of the 29 November election. (Reuters)",
     icon_ballot),
    ("12 KATHMANDU \u00b7 POLITICS", None,
     "Nepal's new PM faces his India test",
     "Balendra Shah makes his first visit to India as prime minister. "
     "(BBC)", icon_flags),
    ("13 JOHANNESBURG \u00b7 SOCIETY", None,
     "Nearly 600 women killed in 3 months",
     "South Africa's femicide toll is laid bare in new figures. (BBC)",
     icon_candle),
]

small_w = (CW - 4 * 8) // 5
for row in range(2):
    y0 = 504 + row * 150
    for col in range(5):
        i = row * 5 + col
        label, _kick, head, summ, art = SMALL[i]
        x0 = M + col * (small_w + 8)
        art(x0, y0, small_w, 56)
        d.text((x0, y0 + 60), label, font=SANS_B(11), fill=RED)
        block(x0, y0 + 76, head, SANS_B(14), small_w, lh=16, max_lines=2,
              name=f"small{i + 4} head")
        block(x0, y0 + 112, summ, SANS(9.5), small_w, lh=12, max_lines=2,
              name=f"small{i + 4} summ")

# ---------------------------------------------------------------- map + list
d.text((M, 800), "WHERE IT HAPPENED", font=SANS_B(13), fill=INK)
d.text((286, 800), "ALSO ON SATURDAY 21 NOVEMBER \u2014 22 MORE STORIES",
       font=SANS_B(13), fill=INK)
rule_y(820)

MAP_X, MAP_Y, MAP_W, MAP_H = M, 826, 260, 109
LAT_TOP, LAT_BOT = 82.0, -58.0


def proj(lon, lat):
    return (MAP_X + (lon + 180.0) / 360.0 * MAP_W,
            MAP_Y + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * MAP_H)


NA = [(-168, 66), (-158, 58), (-152, 60), (-140, 60), (-135, 58), (-130, 54),
      (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24), (-105, 20),
      (-97, 16), (-92, 15), (-86, 12), (-83, 9), (-79, 9), (-81, 13),
      (-86, 15), (-90, 14), (-92, 15), (-95, 18), (-97, 16), (-90, 21),
      (-86, 22), (-84, 30), (-81, 26), (-80, 32), (-76, 35), (-74, 40),
      (-70, 42), (-68, 44), (-65, 44), (-60, 47), (-55, 52), (-60, 55),
      (-65, 60), (-70, 62), (-78, 62), (-85, 66), (-92, 66), (-95, 69),
      (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68), (-168, 66)]
SA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
      (-70, -24), (-70, -32), (-72, -38), (-73, -45), (-74, -50),
      (-70, -54), (-66, -55), (-65, -50), (-62, -44), (-58, -38),
      (-52, -33), (-48, -28), (-41, -23), (-39, -17), (-35, -9),
      (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-53, 4), (-58, 6),
      (-62, 9), (-68, 11), (-72, 12), (-77, 8), (-79, 9)]
EU = [(-10, 36), (-9, 43), (-2, 44), (-4, 48), (-1, 50), (3, 51), (5, 53),
      (8, 55), (8, 57), (11, 58), (18, 56), (21, 55), (24, 58), (28, 60),
      (30, 64), (28, 69), (32, 70), (40, 68), (48, 69), (55, 69), (62, 69),
      (68, 68), (60, 65), (52, 64), (45, 63), (40, 61), (35, 59), (30, 57),
      (25, 54), (20, 54), (15, 54), (12, 54), (8, 54), (5, 53), (2, 51),
      (0, 50), (-2, 49), (-5, 48), (-2, 46), (-1, 44), (-3, 43), (-9, 43),
      (-9, 38), (-6, 36)]
AF = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
      (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (12, 0),
      (9, -2), (12, -5), (13, -10), (12, -15), (13, -18), (12, -22),
      (14, -27), (16, -29), (19, -34), (26, -34), (32, -29), (35, -24),
      (40, -16), (40, -10), (42, -4), (46, -1), (51, 2), (51, 10),
      (44, 11), (40, 15), (38, 18), (37, 22), (34, 27), (32, 31),
      (30, 32), (25, 32), (20, 32), (15, 32), (11, 34), (10, 37),
      (5, 37), (0, 36), (-6, 35)]
AS = [(30, 36), (36, 36), (36, 33), (35, 30), (34, 28), (35, 29), (39, 31),
      (42, 34), (44, 37), (48, 38), (50, 37), (53, 37), (54, 38), (57, 38),
      (58, 39), (61, 40), (64, 40), (66, 41), (68, 42), (70, 41), (72, 42),
      (75, 40), (78, 39), (80, 38), (82, 38), (85, 39), (88, 39), (90, 40),
      (92, 41), (95, 40), (98, 39), (100, 38), (103, 38), (105, 39),
      (108, 39), (110, 40), (113, 38), (116, 38), (118, 39), (120, 38),
      (122, 40), (124, 40), (127, 40), (129, 38), (131, 38), (132, 43),
      (135, 44), (138, 45), (140, 46), (142, 45), (142, 50), (140, 55),
      (138, 58), (136, 60), (133, 62), (130, 65), (128, 68), (130, 70),
      (135, 72), (140, 72), (145, 72), (150, 70), (155, 70), (160, 69),
      (165, 66), (170, 66), (175, 65), (178, 65), (180, 65), (178, 62),
      (175, 60), (170, 60), (166, 60), (162, 60), (160, 58), (158, 55),
      (155, 53), (152, 50), (148, 46), (145, 43), (142, 42), (140, 40),
      (138, 38), (135, 35), (132, 33), (130, 32), (128, 31), (126, 30),
      (124, 30), (122, 28), (120, 27), (118, 25), (116, 23), (114, 22),
      (112, 21), (110, 20), (108, 18), (106, 17), (105, 15), (104, 13),
      (103, 10), (102, 8), (100, 7), (98, 8), (96, 10), (94, 12), (92, 15),
      (90, 18), (88, 20), (86, 20), (84, 18), (82, 16), (80, 15),
      (78, 13), (76, 10), (75, 8), (73, 10), (72, 12), (70, 15), (68, 18),
      (66, 20), (64, 22), (62, 25), (60, 25), (58, 25), (56, 26),
      (54, 27), (52, 26), (50, 26), (48, 28), (46, 29), (44, 29),
      (42, 29), (40, 28), (38, 28), (36, 27), (35, 28), (34, 29),
      (33, 30), (32, 31), (31, 32), (30, 34), (30, 36)]
AU = [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33),
      (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
      (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
      (146, -19), (142, -15), (142, -11), (137, -12), (135, -12),
      (132, -11), (130, -13), (126, -14), (122, -17), (118, -20),
      (114, -21), (113, -22)]

d.rectangle([MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H], fill=SEA,
            outline=(160, 160, 160))
for poly in (NA, SA, EU, AF, AS, AU):
    d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
              outline=LAND_LINE)

# pins: (number, lon, lat, dx, dy) — dx/dy spread crowded clusters
PINS = [
    (1, 30.7, 36.9, 16, 14),
    (2, -75.2, -11.2, 0, 6),
    (3, 46.7, 24.7, 20, -10),
    (4, -74.0, 40.7, -12, -12),
    (5, 8.65, 49.87, -22, -14),
    (6, 30.5, 50.45, 4, -16),
    (7, -77.0, 38.9, -14, 10),
    (8, -77.0, 38.9, 10, 12),
    (9, 12.57, 55.68, -6, -16),
    (10, -74.0, 40.7, 12, -6),
    (11, -3.7, 40.4, -16, 8),
    (12, 85.3, 27.7, 14, 2),
    (13, 28.05, -26.2, 0, 0),
]
f_pin = SANS_B(11)
for num, lon, lat, dx, dy in PINS:
    tx, ty = proj(lon, lat)
    px, py = tx + dx, ty + dy
    if dx or dy:
        d.line([(tx, ty), (px, py)], fill=(120, 120, 120), width=1)
        d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=INK)
    d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED, outline=(255, 255, 255))
    nw = text_w(str(num), f_pin)
    d.text((px - nw / 2, py - 7), str(num), font=f_pin, fill=(255, 255, 255))

# ---------------------------------------------------------------- also list
ALSO = [
    (14, "Port-au-Prince", "Salvadoran troops lose soldiers to explosives", "AP"),
    (15, "Los Angeles", "Man convicted of starting the Palisades fire", "Reuters"),
    (16, "Kharg Island", "14+ Iranian tankers mass to test the US blockade", "Reuters"),
    (17, "Gaza", "Israeli strikes kill Palestinians; West Bank violence", "Reuters"),
    (18, "Las Vegas", "NFL suspends Puka Nacua amid an antisemitism lawsuit", "AP"),
    (19, "Washington", "US declassifies more UFO footage from the Middle East", "BBC"),
    (20, "Paris", "Police sentenced over beating of producer Michel Zecler", "BBC"),
    (21, "Washington", "Firms fined $811m for conning migrants keep scamming", "BBC"),
    (22, "Jerusalem", "Likud wants Netanyahu as sole PM in unity talks", "Reuters"),
    (23, "Addis Ababa", "Africa launches its own credit rating agency", "Reuters"),
    (24, "Washington", "Trump turns the 2028 succession race into a spectacle", "AP"),
    (25, "Jerusalem", "Israel's GDP per head surges, living standards up", "Reuters"),
    (26, "Pretoria", "ANC fights to keep key cities after election setback", "Reuters"),
    (27, "Shenzhen", "Trump, Xi: humans must stay in charge of military AI", "Reuters"),
    (28, "Hodeidah", "Saudi-led strikes hit Houthi-held cities in Yemen", "Al Jazeera"),
    (29, "Cox's Bazar", "Rohingya recount 2017 exodus as Hague rules", "Reuters"),
    (30, "Antalya", "Delegates sleep in corridors as COP31 drags on", "The Times"),
    (31, "Antalya", "Campaigners call COP31 \u201cthe worst COP ever\u201d", "The Times"),
    (32, "Riyadh", "Houthis threaten Saudi ports and a power station", "Al Jazeera"),
    (33, "Lima", "Lawmakers walk out of Congress as the tremor hits", "Reuters"),
    (34, "Jun\u00edn", "Landslides block roads after the quake; no deaths reported", "AFP"),
    (35, "Damascus", "23,000+ Syrian children killed since 2011", "Arab News"),
]
assert len(ALSO) == 22, len(ALSO)

LIST_X, LIST_W, COL_GAP = 286, 724, 12
col_w = (LIST_W - COL_GAP) // 2
# auto-fit: shrink the list font until the longest line fits its column
f_list = SANS(9)
f_list_b = SANS_B(9)
while True:
    widest = 0
    for num, place, text, src in ALSO:
        line = f"{num} {place} \u2014 {text} ({src})"
        widest = max(widest, text_w(line, f_list))
    if widest <= col_w or f_list.size <= 8:
        break
    f_list = SANS(f_list.size - 1)
    f_list_b = SANS_B(f_list_b.size - 1)
if widest > col_w:
    WARN.append(f"also list: longest line {widest:.0f}px > col {col_w}px")
row_h = MAP_H / 11.0
for ci in range(2):
    cx = LIST_X + ci * (col_w + COL_GAP)
    for ri in range(11):
        num, place, text, src = ALSO[ci * 11 + ri]
        y = MAP_Y + ri * row_h
        d.text((cx, y), f"{num}", font=f_list_b, fill=RED)
        nx = cx + text_w(f"{num} ", f_list_b)
        d.text((nx, y), f"{place} \u2014 {text} ({src})", font=f_list,
               fill=INK)

# ---------------------------------------------------------------- date check
dc_text = ("DATE CHECK \u2014 Left out as Friday 20 November's news: the Kyiv "
           "bridges attack and the Kryvyi Rih strike, the UK\u2013EU deal, "
           "GTA VI's $3.79bn day one, the daraxonrasib trial results, the "
           "Gen Z strikes across Europe, and Bolsonaro's hospital stay. "
           "The ICJ's Myanmar genocide ruling was Thursday 19 November. "
           "Not yet shown: the final COP31 text.")
f_dc = SANS(11)
dc_lines = wrap(dc_text, f_dc, CW - 24)
dc_h = len(dc_lines) * 14 + 14
dc_y = 944
d.rectangle([M, dc_y, W - M, dc_y + dc_h], outline=RED, width=2)
for i, line in enumerate(dc_lines):
    d.text((M + 12, dc_y + 7 + i * 14), line, font=f_dc, fill=INK)

# ---------------------------------------------------------------- footer
fy = dc_y + dc_h + 6
f_foot = SANS(10)
left_f = ("Every story here happened, or was first reported, on Saturday "
          "21 November 2026. Officials' counts are attributed.")
right_f = "Sources named beside each story \u00b7 original drawings"
d.text((M, fy), left_f, font=f_foot, fill=INK)
d.text((W - M - text_w(right_f, f_foot), fy), right_f, font=f_foot, fill=INK)

img.save(OUT, optimize=True)
print("saved", OUT, os.path.getsize(OUT), "bytes,", img.size)
print("list font size:", f_list.size)
print("date-check lines:", len(dc_lines))
for w_ in WARN:
    print("WARN:", w_)
print("warnings:", len(WARN))
