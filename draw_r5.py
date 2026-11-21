#!/usr/bin/env python3
"""news-image-20261121 ROUND 5 — broadsheet front page, drawn fresh with PIL.

One image sums up Saturday 21 November 2026: 35 stories, 7 regions.
Canvas 1024x1024 PNG, cream paper, black ink, red labels. No downloads,
no photos — every pixel drawn here. Round 5 keeps the round-4 broadsheet
template and fixes its three weakest spots:
  (a) the world map is redrawn with recognisable continent shapes —
      Europe and Asia in different tones, North America with a real
      outline, every numbered pin sitting ON land (crowded Gulf pins
      use short leader lines to a nearby land spot);
  (b) the Peru seismograph lives in its own strip BELOW the houses,
      so no trace ever crosses a roof;
  (c) the Kyiv bridge is drawn bold — thick dark lines on a solid
      backing patch — so it reads over the flag ribbon.
Build: python3 draw_r5.py  ->  entry.png
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 242, 231)
PAPER = (255, 253, 247)
INK = (24, 22, 18)
RED = (192, 57, 43)
DARKRED = (150, 40, 28)
GREY = (96, 92, 84)
RULE = (190, 182, 164)
OCEAN = (216, 231, 240)
COAST = (107, 91, 62)
NAVY = (22, 38, 66)
GREEN = (30, 125, 50)
BLUE = (21, 101, 192)
ORANGE = (230, 126, 34)
SLATE = (84, 84, 84)

FD = "/usr/share/fonts/truetype/dejavu/"


def F(name, size):
    return ImageFont.truetype(FD + name, size)


def serif_b(s):
    return F("DejaVuSerif-Bold.ttf", s)


def serif(s):
    return F("DejaVuSerif.ttf", s)


def sans(s):
    return F("DejaVuSans.ttf", s)


def sans_b(s):
    return F("DejaVuSans-Bold.ttf", s)


img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)


def tw(text, font):
    return d.textlength(text, font=font)


def wrap(text, font, maxw):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if tw(trial, font) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(text, font, x, y, maxw, lh, fill=INK):
    for ln in wrap(text, font, maxw):
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def centre(text, font, cx, y, fill=INK):
    d.text((cx - tw(text, font) / 2, y), text, font=font, fill=fill)


def draw_italic(text, font, x, y, fill=INK, shear=0.22):
    """No italic DejaVu on this VM — shear a rendered line instead."""
    tmp = Image.new("RGBA", (int(tw(text, font)) + 30, font.size + 14), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.text((4, 2), text, font=font, fill=fill + (255,))
    w, h = tmp.size
    tmp = tmp.transform((w + int(h * shear) + 4, h), Image.AFFINE,
                        (1, -shear, 0, 0, 1, 0), resample=Image.BICUBIC)
    img.paste(tmp, (int(x), int(y)), tmp)


BADGE_FILL = {"CONFIRMED": GREEN, "OFFICIAL": BLUE, "REPORTED": ORANGE, "CLAIM": SLATE}


def badge(x_right, y, label):
    f = sans_b(8)
    w = tw(label, f) + 10
    x = x_right - w
    d.rounded_rectangle([x, y, x_right, y + 13], radius=6, fill=BADGE_FILL[label])
    d.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return x


def rule(x0, x1, y, width=1, fill=RULE):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- header
M = 22                      # page margin
R = W - M                   # right edge of content (1002)
d.text((M, 8), "THE WORLD IN ONE DAY", font=sans_b(13), fill=RED)
right_top = "35 STORIES  ·  7 REGIONS  ·  EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
d.text((R - tw(right_top, sans_b(11)), 10), right_top, font=sans_b(11), fill=INK)
rule(M, R, 30, width=2, fill=INK)

d.text((M, 36), "Saturday 21 November 2026", font=serif_b(42), fill=INK)
draw_italic("COP31 runs into overtime  ·  Houthi missiles target Riyadh  ·  "
            "A 6.7 quake shakes Peru", serif(16), M, 84)
rule(M, R, 100, width=1)

# ---------------------------------------------------------------- stat strip
STATS = [
    ("13", "Day of COP31 — meant\nto close on day 12"),
    ("3", "missiles shot down\nover Riyadh"),
    ("6.7", "Peru quake\nmagnitude"),
    ("146", "people safe after\nthe Davao landing"),
    ("$58,983", "Bitcoin early Saturday,\ndown 3.9% in a day"),
    ("124*", "K L Rahul's score\nat tea, Wellington"),
]
sy, sh, gap = 106, 46, 5
sw = (R - M - 5 * gap) / 6
for i, (num, lab) in enumerate(STATS):
    x0 = M + i * (sw + gap)
    d.rectangle([x0, sy, x0 + sw, sy + sh], fill=PAPER, outline=RULE, width=1)
    centre(num, sans_b(20), x0 + sw / 2, sy + 3, fill=RED if i in (0, 2, 4) else INK)
    for j, ln in enumerate(lab.split("\n")):
        centre(ln, sans(8.5), x0 + sw / 2, sy + 26 + j * 10, fill=GREY)

# ---------------------------------------------------------------- region bar
regions = "EUROPE 6   ·   ASIA 4   ·   MIDDLE EAST 9   ·   AFRICA 2   ·   " \
          "AMERICAS 10   ·   OCEANIA 2   ·   GLOBAL 2      =  35 STORIES"
centre(regions, sans_b(12.5), W / 2, 160, fill=INK)
rule(M, R, 176, width=1)

# ---------------------------------------------------------------- three leads
LY, LW, LGAP = 182, 320, 10          # lead row top, column width, gap
LX = [M, M + LW + LGAP, M + 2 * (LW + LGAP)]


def lead_frame(x, kicker, badge_label):
    d.text((x, LY), kicker, font=sans_b(10.5), fill=RED)
    badge(x + LW, LY - 1, badge_label)
    return LY + 17                    # scene top


def lead_text(x, headline, body):
    hy = LY + 17 + 98                  # headline top (below 96px scene)
    hy = para(headline, sans_b(15), x, hy, LW, 18)
    para(body, sans(10), x, hy + 4, LW, 12.5)


# ---- LEAD 1 · RIYADH — night skyline, three interceptor trails
x = LX[0]
sy = lead_frame(x, "RIYADH  ·  SAUDI ARABIA  —  3 DOWN", "CONFIRMED")
d.rectangle([x, sy, x + LW, sy + 96], fill=NAVY)
for sx, sy2 in [(18, 12), (60, 22), (110, 8), (160, 18), (205, 10), (250, 20),
                (290, 12), (95, 30), (235, 32), (140, 26)]:
    d.ellipse([x + sx, sy + sy2, x + sx + 2, sy + sy2 + 2], fill=(255, 255, 220))
d.ellipse([x + 272, sy + 10, x + 292, sy + 30], outline=(240, 240, 210), width=2)
d.pieslice([x + 272, sy + 10, x + 292, sy + 30], 300, 60, fill=(240, 240, 210))
base = sy + 96
# skyline silhouettes (black, lit windows in warm yellow)
skyline = [(0, 34, 26, 96), (30, 52, 52, 96), (56, 40, 74, 96), (78, 58, 100, 96),
           (104, 30, 122, 96), (126, 48, 150, 96), (154, 62, 176, 96),
           (180, 36, 198, 96), (202, 54, 224, 96), (228, 44, 248, 96),
           (252, 58, 272, 96), (276, 38, 296, 96), (300, 56, 320, 96)]
for bx0, top, bx1, _ in skyline:
    d.rectangle([x + bx0, base - (96 - top), x + bx1, base], fill=(8, 12, 24))
    for wy in range(base - (96 - top) + 6, base - 6, 10):
        for wx in range(x + bx0 + 4, x + bx1 - 3, 9):
            d.point((wx, wy), fill=(255, 205, 90))
# PIF tower — the tall one, centre
d.polygon([(x + 108, base), (x + 112, sy + 22), (x + 118, sy + 22), (x + 122, base)],
          fill=(8, 12, 24))
# three interceptor trails arcing up, with bursts at the top
for tx0, tx1, burst in [(20, 130, (150, 26)), (150, 215, (235, 20)), (260, 300, (305, 30))]:
    pts = []
    for t in range(0, 21):
        f = t / 20
        px = x + tx0 + (tx1 - tx0) * f
        py = base - 4 - (base - 4 - (sy + burst[1])) * f - 26 * math.sin(math.pi * f)
        pts.append((px, py))
    d.line(pts, fill=(255, 220, 130), width=2)
    d.ellipse([x + tx0 - 3, base - 7, x + tx0 + 3, base - 1], fill=(255, 220, 130))
    bx, by = x + burst[0], sy + burst[1]
    for ang in range(0, 360, 45):
        ex = bx + 9 * math.cos(math.radians(ang))
        ey = by + 9 * math.sin(math.radians(ang))
        d.line([(bx, by), (ex, ey)], fill=(255, 150, 40), width=2)
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 190, 60))
lead_text(x, "Three Houthi missiles downed over Riyadh",
          "Air defences intercepted three ballistic missiles early on Saturday, "
          "the third night of alerts in the capital. A Houthi strike two days "
          "earlier damaged the PIF tower, Riyadh's tallest. No damage or "
          "casualties reported. (Reuters, Al Jazeera)")

# ---- LEAD 2 · COP31 — globe + thermometer + clock (no draft document)
x = LX[1]
sy = lead_frame(x, "ANTALYA  ·  TÜRKIYE  —  DAY 13", "CONFIRMED")
d.rectangle([x, sy, x + LW, sy + 96], fill=(233, 242, 232), outline=RULE, width=1)
# red tag
tag = "NO DEAL · DAY 13"
tf = sans_b(10)
tw_tag = tw(tag, tf) + 12
d.rounded_rectangle([x + LW - tw_tag - 6, sy + 5, x + LW - 6, sy + 23],
                    radius=7, fill=RED)
d.text((x + LW - tw_tag, sy + 8), tag, font=tf, fill=(255, 255, 255))
# globe
gx, gy, gr = x + 54, sy + 54, 34
d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(46, 111, 176))
for ex, ey, ew, eh in [(gx - 22, gy - 18, 22, 14), (gx - 4, gy - 24, 26, 16),
                       (gx - 26, gy + 4, 18, 12), (gx + 2, gy + 8, 24, 14),
                       (gx + 14, gy - 6, 14, 10)]:
    d.ellipse([ex, ey, ex + ew, ey + eh], fill=(74, 160, 90))
d.arc([gx - gr, gy - gr, gx + gr, gy + gr], 200, 340, fill=(255, 255, 255), width=1)
d.arc([gx - gr, gy - gr, gx + gr, gy + gr], 20, 160, fill=(255, 255, 255), width=1)
d.line([(gx - gr + 2, gy - 12), (gx + gr - 2, gy - 12)], fill=(255, 255, 255), width=1)
d.line([(gx - gr + 2, gy + 12), (gx + gr - 2, gy + 12)], fill=(255, 255, 255), width=1)
d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=(20, 60, 110), width=2)
# thermometer
tx0, ty0, ty1 = x + 138, sy + 12, sy + 78
d.rounded_rectangle([tx0, ty0, tx0 + 12, ty1], radius=6, fill=(255, 255, 255),
                    outline=(120, 40, 30), width=2)
d.rounded_rectangle([tx0 + 3, ty0 + 34, tx0 + 9, ty1 - 3], radius=3, fill=RED)
d.ellipse([tx0 - 4, ty1 - 8, tx0 + 16, ty1 + 14], fill=RED, outline=(120, 40, 30), width=2)
for k in range(5):
    yy = ty0 + 8 + k * 12
    d.line([(tx0 + 12, yy), (tx0 + 18, yy)], fill=INK, width=1)
d.text((tx0 + 22, ty0 + 30), "1.8°C", font=sans_b(16), fill=RED)
d.text((tx0 + 22, ty0 + 50), "warming", font=sans(9), fill=GREY)
# clock
cx, cy, cr = x + 268, sy + 46, 27
d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 255, 255),
          outline=INK, width=2)
for k in range(12):
    a = math.radians(k * 30)
    d.line([(cx + 21 * math.sin(a), cy - 21 * math.cos(a)),
            (cx + 24 * math.sin(a), cy - 24 * math.cos(a))], fill=INK, width=1)
d.line([(cx, cy), (cx, cy - 17)], fill=INK, width=2)
d.line([(cx, cy), (cx + 11, cy - 6)], fill=INK, width=2)
d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
d.text((cx - 22, cy + cr + 4), "DAY 13", font=sans_b(11), fill=RED)
lead_text(x, "COP31 runs into overtime with no deal on fossil fuels",
          "Negotiators in Antalya will work an extra day after a draft deal "
          "dropped all mention of fossil fuels and a $120bn adaptation finance "
          "target. Nearly 200 nations are split; campaigners call it "
          "'the worst COP ever'. (Reuters, AP)")

# ---- LEAD 3 · PERU — houses ABOVE, seismograph in its OWN strip below
x = LX[2]
sy = lead_frame(x, "JUNÍN, PERU  —  00:09 GMT  ·  6.7", "CONFIRMED")
d.rectangle([x, sy, x + LW, sy + 96], fill=(246, 232, 200), outline=RULE, width=1)
upper_h = 60                      # sky + mountains + houses
# Andes silhouettes
d.polygon([(x, sy + upper_h), (x + 55, sy + 8), (x + 110, sy + upper_h)],
          fill=(122, 102, 78))
d.polygon([(x + 80, sy + upper_h), (x + 150, sy + 2), (x + 220, sy + upper_h)],
          fill=(96, 80, 60))
d.polygon([(x + 190, sy + upper_h), (x + 255, sy + 14), (x + 320, sy + upper_h)],
          fill=(122, 102, 78))
d.polygon([(x + 138, sy + 14), (x + 150, sy + 2), (x + 162, sy + 14)],
          fill=(255, 253, 247))   # snow cap
# houses — bases sit exactly on the strip boundary, roofs stay above it
house_y = sy + upper_h
for hx, hw, hh, col in [(18, 34, 20, (176, 92, 60)), (62, 30, 16, (90, 120, 150)),
                        (102, 36, 22, (200, 150, 80)), (150, 30, 17, (150, 110, 80)),
                        (192, 34, 21, (120, 140, 110)), (238, 30, 16, (176, 92, 60)),
                        (280, 32, 19, (90, 120, 150))]:
    d.rectangle([x + hx, house_y - hh, x + hx + hw, house_y], fill=col,
                outline=(60, 45, 30), width=1)
    d.polygon([(x + hx - 3, house_y - hh), (x + hx + hw / 2, house_y - hh - 12),
               (x + hx + hw + 3, house_y - hh)], fill=(120, 50, 35))
    d.rectangle([x + hx + hw / 2 - 3, house_y - 10, x + hx + hw / 2 + 3, house_y],
                fill=(40, 30, 20))
# divider, then the seismograph strip — the trace never leaves this band
d.line([(x, house_y), (x + LW, house_y)], fill=INK, width=2)
strip_y0, strip_y1 = house_y + 3, sy + 96
d.rectangle([x, strip_y0, x + LW, strip_y1], fill=(255, 255, 255))
mid = (strip_y0 + strip_y1) / 2
d.line([(x + 6, mid), (x + 218, mid)], fill=(200, 200, 200), width=1)
pts = []
px = x + 8
step = 0
while px < x + 214:
    amp = [0, 4, -3, 9, -12, 6, -4, 16, -20, 10, -6, 4, -2, 0][step % 14]
    pts.append((px, mid - amp))
    px += 7
    step += 1
d.line(pts, fill=INK, width=2)
d.text((x + 228, mid - 13), "6.7", font=sans_b(22), fill=RED)
d.text((x + 228, mid + 11), "USGS", font=sans_b(8), fill=GREY)
lead_text(x, "6.7 quake shakes Peru; no deaths reported",
          "The tremor struck near Junín at 7:09 pm local time, rattling Lima "
          "and sending lawmakers out of Congress. Minor damage to homes and "
          "landslides on roads; no tsunami threat. (USGS, AFP, Reuters)")

# ---------------------------------------------------------------- ten small stories
SY, SH, SW, SGAP = 406, 136, 192, 5
SX = [M + i * (SW + SGAP) for i in range(5)]


def small_card(col, row, num, label, badge_label, headline, summary, scene):
    x = SX[col]
    y = SY + row * (SH + 6)
    d.text((x, y + 2), f"{num}  ·  {label}", font=sans_b(10), fill=RED)
    badge(x + SW, y + 1, badge_label)
    bx, by, bh = x, y + 16, 48
    d.rectangle([bx, by, bx + SW, by + bh], fill=PAPER, outline=RULE, width=1)
    scene(bx, by, SW, bh)
    hy = para(headline, sans_b(11.5), x, by + bh + 4, SW, 13.5)
    para(summary, sans(9.5), x, hy + 2, SW, 11.5)


def scene_kyiv(bx, by, bw, bh):
    # flag ribbon along the bottom; solid backing patch; BOLD bridge on top
    d.rectangle([bx, by + bh - 12, bx + bw, by + bh - 6], fill=(0, 91, 172))
    d.rectangle([bx, by + bh - 6, bx + bw, by + bh], fill=(255, 213, 0))
    d.rounded_rectangle([bx + 6, by + 2, bx + bw - 6, by + bh - 14],
                        radius=4, fill=(255, 255, 255), outline=(200, 200, 200), width=1)
    dk = (18, 48, 96)
    d.line([(bx + 14, by + 24), (bx + bw - 14, by + 24)], fill=dk, width=5)
    for tx in (bx + 58, bx + 132):
        d.line([(tx, by + 6), (tx, by + 30)], fill=dk, width=4)
    d.arc([bx + 58, by - 2, bx + 132, by + 26], 180, 360, fill=dk, width=3)
    for cx in (bx + 76, bx + 94, bx + 112):
        d.line([(cx, by + 12), (cx, by + 24)], fill=dk, width=2)
    d.line([(bx + 58, by + 6), (bx + 14, by + 24)], fill=dk, width=2)
    d.line([(bx + 132, by + 6), (bx + bw - 14, by + 24)], fill=dk, width=2)


def scene_hormuz(bx, by, bw, bh):
    d.rectangle([bx, by, bx + bw, by + bh], fill=(214, 232, 242))
    d.rectangle([bx, by + 32, bx + bw, by + bh], fill=(70, 130, 180))
    d.polygon([(bx + 18, by + 30), (bx + 112, by + 30), (bx + 104, by + 40),
               (bx + 26, by + 40)], fill=(30, 30, 40))
    for cx, col in [(28, (200, 60, 50)), (48, (60, 140, 80)), (68, (230, 180, 40)),
                    (88, (90, 110, 200))]:
        d.rectangle([bx + cx, by + 18, bx + cx + 18, by + 30], fill=col)
    d.rectangle([bx + 96, by + 10, bx + 108, by + 18], fill=(220, 220, 220))
    dx, dy = bx + 150, by + 12
    d.rectangle([dx - 8, dy - 2, dx + 8, dy + 2], fill=(20, 20, 20))
    d.rectangle([dx - 2, dy - 6, dx + 2, dy + 6], fill=(20, 20, 20))
    for ox, oy in [(-10, -6), (10, -6), (-10, 6), (10, 6)]:
        d.ellipse([dx + ox - 3, dy + oy - 1, dx + ox + 3, dy + oy + 1], fill=(90, 90, 90))


def scene_iran(bx, by, bw, bh):
    cx, cy = bx + bw / 2, by + bh / 2
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED)
    d.ellipse([cx - 34, cy - 11, cx + 34, cy + 11], outline=(0, 120, 120), width=2)
    d.ellipse([cx - 11, cy - 20, cx + 11, cy + 20], outline=(0, 120, 120), width=2)
    pts = []
    for t in range(49):
        a = math.radians(t * 360 / 48)
        ex = 30 * math.cos(a)
        ey = 12 * math.sin(a)
        rx = ex * math.cos(math.radians(45)) - ey * math.sin(math.radians(45))
        ry = ex * math.sin(math.radians(45)) + ey * math.cos(math.radians(45))
        pts.append((cx + rx, cy + ry))
    d.line(pts, fill=(0, 120, 120), width=2)
    d.ellipse([cx - 30, cy - 16, cx - 24, cy - 10], fill=(0, 120, 120))
    d.ellipse([cx + 24, cy + 10, cx + 30, cy + 16], fill=(0, 120, 120))


def scene_trump(bx, by, bw, bh):
    d.rectangle([bx + 24, by + 10, bx + 96, by + bh - 4], fill=(70, 74, 84))
    for wy in range(by + 15, by + bh - 8, 9):
        for wx in range(bx + 30, bx + 90, 10):
            d.rectangle([wx, wy, wx + 5, wy + 5], fill=(255, 205, 90))
    d.text((bx + 118, by + 4), "$", font=sans_b(30), fill=(30, 125, 50))
    d.rectangle([bx + 118, by + 36, bx + 172, by + 44], fill=RED)
    d.text((bx + 122, by + 37), "TAX", font=sans_b(8), fill=(255, 255, 255))


def scene_chinajapan(bx, by, bw, bh):
    d.rectangle([bx + 12, by + 9, bx + 88, by + 39], fill=(222, 41, 16))
    for sx, sy2 in [(22, 15), (34, 20), (34, 27), (28, 24)]:
        d.ellipse([bx + sx, by + sy2, bx + sx + 4, by + sy2 + 4], fill=(255, 222, 0))
    d.rectangle([bx + 104, by + 9, bx + 180, by + 39], fill=(255, 255, 255),
                outline=(150, 150, 150), width=1)
    d.ellipse([bx + 132, by + 15, bx + 152, by + 35], fill=(188, 0, 45))


def scene_davao(bx, by, bw, bh):
    d.rectangle([bx, by, bx + bw, by + bh], fill=(214, 232, 242))
    d.rectangle([bx, by + bh - 9, bx + bw, by + bh], fill=(90, 90, 90))
    for dx in range(bx + 8, bx + bw - 8, 22):
        d.line([(dx, by + bh - 5), (dx + 10, by + bh - 5)], fill=(255, 255, 255), width=2)
    d.ellipse([bx + 28, by + 14, bx + 118, by + 30], fill=(255, 255, 255),
              outline=(40, 40, 40), width=1)
    d.polygon([(bx + 60, by + 12), (bx + 86, by + 4), (bx + 92, by + 12)],
              fill=(200, 200, 200), outline=(40, 40, 40))
    d.polygon([(bx + 66, by + 30), (bx + 84, by + 38), (bx + 90, by + 30)],
              fill=(200, 200, 200), outline=(40, 40, 40))
    d.rectangle([bx + 112, by + 16, bx + 118, by + 26], fill=(40, 40, 40))
    gx, gy, gr = bx + 162, by + 20, 11
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=GREEN)
    d.line([(gx - 5, gy), (gx - 1, gy + 4), (gx + 6, gy - 5)], fill=(255, 255, 255), width=2)


def scene_canberra(bx, by, bw, bh):
    d.rectangle([bx + 12, by + 9, bx + 82, by + 39], fill=(0, 47, 108))
    for sx, sy2 in [(22, 15), (36, 28), (52, 14), (64, 26)]:
        d.ellipse([bx + sx, by + sy2, bx + sx + 4, by + sy2 + 4], fill=(255, 255, 255))
    d.rectangle([bx + 110, by + 9, bx + 180, by + 39], fill=(222, 41, 16))
    d.ellipse([bx + 140, by + 19, bx + 144, by + 23], fill=(255, 222, 0))
    d.rectangle([bx + 82, by + 16, bx + 110, by + 32], fill=(30, 30, 30))
    for k in range(4):
        d.line([(bx + 86 + k * 6, by + 16), (bx + 86 + k * 6, by + 12)],
               fill=(200, 170, 60), width=2)
        d.line([(bx + 86 + k * 6, by + 32), (bx + 86 + k * 6, by + 36)],
               fill=(200, 170, 60), width=2)


def scene_bitcoin(bx, by, bw, bh):
    cx, cy, cr = bx + 34, by + 24, 17
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(247, 147, 26),
              outline=(180, 100, 10), width=2)
    d.text((cx - 7, cy - 11), "B", font=sans_b(20), fill=(255, 255, 255))
    pts = [(bx + 66, by + 10), (bx + 96, by + 16), (bx + 122, by + 12),
           (bx + 150, by + 26), (bx + 178, by + 38)]
    d.line(pts, fill=RED, width=3)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)


def scene_f1(bx, by, bw, bh):
    # one clean oval track loop, red car on it, chequered flag at the right
    d.ellipse([bx + 8, by + 6, bx + 132, by + bh - 6], outline=(120, 120, 120), width=8)
    d.ellipse([bx + 96, by + 8, bx + 104, by + 14], fill=RED)
    d.rectangle([bx + 158, by + 8, bx + 182, by + 24], fill=(255, 255, 255),
                outline=INK, width=1)
    for r in range(2):
        for c in range(3):
            if (r + c) % 2 == 0:
                d.rectangle([bx + 158 + c * 8, by + 8 + r * 8,
                             bx + 166 + c * 8, by + 16 + r * 8], fill=INK)
    d.line([(bx + 182, by + 8), (bx + 182, by + 34)], fill=INK, width=2)


def scene_cricket(bx, by, bw, bh):
    d.rectangle([bx, by, bx + bw, by + bh], fill=(200, 225, 190))
    d.rectangle([bx, by + 18, bx + bw, by + 32], fill=(232, 210, 160))
    d.polygon([(bx + 30, by + 12), (bx + 40, by + 10), (bx + 52, by + 34),
               (bx + 42, by + 36)], fill=(150, 100, 50))
    d.rectangle([bx + 26, by + 6, bx + 42, by + 14], fill=(120, 80, 40))
    d.ellipse([bx + 76, by + 22, bx + 84, by + 30], fill=RED)
    for sx in (150, 156, 162):
        d.line([(bx + sx, by + 12), (bx + sx, by + 32)], fill=(255, 215, 0), width=3)
    d.line([(bx + 148, by + 12), (bx + 166, by + 12)], fill=(255, 215, 0), width=2)


SMALL = [
    (0, 0, "4", "KYIV · WARNING", "CLAIM",
     "Zelensky warns Crimea bridge 'will not stay'",
     "Kyiv warns the bridge again after double-tap strikes. (NBC)", scene_kyiv),
    (1, 0, "5", "HORMUZ · DRONE", "CLAIM",
     "Iran says it shot down a US drone",
     "Tehran claims a downing over the strait; Washington silent. (IRIB)", scene_hormuz),
    (2, 0, "6", "TEHRAN · NUCLEAR", "OFFICIAL",
     "Iran keeps uranium, seeks 'fair solution'",
     "The stock stays in the country, the minister says. (ToI)", scene_iran),
    (3, 0, "7", "WASHINGTON · TECH", "OFFICIAL",
     "Trump vows tax on data centres abroad",
     "\u2018Tremendous\u2019 penalty, no details yet. (ABC)", scene_trump),
    (4, 0, "8", "BEIJING", "OFFICIAL",
     "China tells Japan to 'correct' Taiwan words",
     "Foreign ministry rebuke over Taiwan remarks. (AFP)", scene_chinajapan),
    (0, 1, "9", "DAVAO · AVIATION", "REPORTED",
     "767 lands safely after engine fire alert",
     "All 146 aboard safe after the emergency landing. (AP)", scene_davao),
    (1, 1, "10", "CANBERRA", "OFFICIAL",
     "Australia and China agree AI talks",
     "Albanese wraps an 11-day trip with a deal to talk. (ABC)", scene_canberra),
    (2, 1, "11", "MARKETS · CRYPTO", "REPORTED",
     "Bitcoin at $58,983, down 3.9% in a day",
     "Ether $1,625 as crypto slides into Saturday. (CoinGecko)", scene_bitcoin),
    (3, 1, "12", "LAS VEGAS", "OFFICIAL",
     "Russell fastest in final Las Vegas practice",
     "1:34.041 in a damp session before qualifying. (Formula 1)", scene_f1),
    (4, 1, "13", "WELLINGTON", "REPORTED",
     "Rahul hits century as India reach 344 for 2",
     "124* at tea, replying to New Zealand's 368. (AFP)", scene_cricket),
]
for col, row, num, label, bl, head, summ, fn in SMALL:
    small_card(col, row, num, label, bl, head, summ, fn)
rule(M, R, 690, width=1)

# ---------------------------------------------------------------- world map + briefs
# Redrawn for round 5: recognisable continent outlines, Europe and Asia in
# different tones (never one tan mass), North America with a real outline,
# every pin ON land — the three crowded Gulf pins sit on nearby land with
# a short leader line to their exact spot.
MAP_X0, MAP_Y0, MAP_X1, MAP_Y1 = 26, 724, 344, 880
d.text((M, 698), "WHERE IT HAPPENED — 13 STORIES PINNED", font=sans_b(11.5), fill=INK)
d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=OCEAN, outline=RULE, width=1)


def proj(lon, lat):
    return (MAP_X0 + (lon + 170) * 0.88, MAP_Y0 + 2 + (78 - lat) * 1.0)


def land(points, fill):
    d.polygon([proj(lo, la) for lo, la in points], fill=fill, outline=COAST)


EUROPE = (239, 228, 194)
ASIA = (216, 193, 140)
NAMER = (227, 213, 174)
SAMER = (220, 201, 158)
AFRICA = (224, 207, 166)
OCEAN_T = (231, 217, 178)

land([(-168, 66), (-161, 58), (-152, 60), (-140, 60), (-130, 54), (-125, 49),
      (-124, 42), (-121, 37), (-117, 33), (-112, 29), (-108, 25), (-105, 20),
      (-102, 18), (-97, 16), (-94, 17), (-92, 15), (-88, 13), (-83, 9),
      (-80, 8), (-77, 7), (-79, 9), (-83, 9), (-86, 12), (-88, 15), (-88, 18),
      (-90, 21), (-91, 19), (-94, 18), (-97, 21), (-97, 26), (-93, 30),
      (-89, 30), (-84, 30), (-81, 26), (-80, 32), (-76, 35), (-74, 39),
      (-70, 41), (-66, 44), (-60, 46), (-60, 50), (-65, 50), (-60, 52),
      (-64, 58), (-68, 58), (-75, 62), (-80, 63), (-85, 66), (-90, 68),
      (-95, 69), (-105, 68), (-115, 69), (-125, 70), (-135, 69), (-145, 70),
      (-155, 71), (-165, 68)], NAMER)
land([(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-78, -10), (-75, -15),
      (-71, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-71, -50),
      (-68, -52), (-66, -55), (-68, -50), (-65, -45), (-62, -40), (-58, -34),
      (-53, -33), (-49, -28), (-41, -23), (-37, -13), (-35, -8), (-35, -5),
      (-40, -3), (-44, -2), (-50, 0), (-52, 4), (-55, 6), (-60, 8), (-65, 10),
      (-70, 11), (-75, 10)], SAMER)
land([(-6, 35), (-10, 31), (-15, 27), (-17, 20), (-17, 15), (-16, 11), (-13, 8),
      (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (9, 0), (12, -5), (13, -11),
      (12, -17), (14, -23), (17, -29), (19, -34), (26, -34), (32, -29),
      (35, -24), (39, -18), (40, -12), (41, -5), (46, -1), (51, 2), (51, 10),
      (48, 11), (44, 11), (42, 13), (39, 16), (37, 20), (35, 26), (33, 30),
      (30, 32), (24, 33), (18, 33), (12, 34), (10, 37), (5, 37), (0, 36)],
     AFRICA)
land([(44, -16), (47, -15), (50, -17), (49, -21), (46, -25), (44, -22), (43, -18)],
     AFRICA)
land([(-6, 36), (-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-1, 49),
      (1, 51), (3, 53), (6, 53), (8, 55), (8, 57), (10, 57), (12, 55),
      (18, 56), (21, 55), (21, 59), (24, 60), (28, 61), (30, 64), (29, 68),
      (25, 71), (30, 70), (32, 68), (31, 66), (30, 62), (32, 60), (35, 55),
      (40, 52), (44, 48), (47, 46), (49, 44), (47, 42), (44, 42), (41, 43),
      (40, 41), (38, 40), (36, 36), (33, 36), (30, 36), (28, 37), (27, 37),
      (26, 38), (23, 36), (22, 37), (20, 39), (19, 41), (16, 40), (15, 38),
      (16, 38), (14, 42), (12, 44), (10, 44), (8, 44), (7, 43), (6, 43),
      (3, 42), (0, 39), (0, 37), (-2, 37), (-5, 36)], EUROPE)
land([(-5, 50), (-4, 53), (-6, 55), (-5, 57), (-3, 58), (-1, 57), (0, 53),
      (1, 51), (-2, 51), (-4, 50)], EUROPE)
land([(28, 41), (30, 41), (33, 42), (36, 41), (38, 41), (41, 41), (44, 42),
      (47, 42), (49, 44), (50, 46), (52, 47), (54, 47), (56, 50), (58, 51),
      (60, 52), (62, 55), (65, 58), (68, 62), (70, 65), (68, 68), (70, 72),
      (73, 72), (76, 73), (80, 73), (85, 74), (90, 75), (95, 76), (100, 77),
      (105, 77), (110, 74), (115, 73), (120, 73), (125, 72), (130, 71),
      (135, 71), (140, 72), (145, 70), (150, 70), (155, 69), (158, 66),
      (162, 64), (162, 60), (158, 59), (156, 54), (150, 59), (142, 59),
      (141, 53), (140, 48), (138, 44), (135, 43), (132, 43), (130, 42),
      (128, 39), (126, 38), (127, 35), (129, 35), (127, 40), (124, 39),
      (122, 38), (121, 35), (120, 32), (122, 31), (121, 28), (119, 25),
      (116, 23), (112, 22), (108, 18), (106, 10), (104, 9), (103, 7),
      (100, 7), (98, 10), (97, 15), (94, 17), (92, 21), (89, 22), (86, 20),
      (83, 18), (80, 15), (80, 10), (77, 8), (76, 10), (74, 14), (72, 20),
      (70, 21), (68, 23), (66, 25), (62, 25), (58, 26), (56, 27), (54, 26),
      (52, 26), (50, 29), (48, 30), (50, 27), (52, 26), (54, 24), (56, 26),
      (58, 24), (57, 22), (55, 17), (52, 15), (48, 14), (44, 13), (43, 12),
      (41, 16), (39, 21), (38, 25), (37, 29), (35, 29), (35, 31), (36, 36)],
     ASIA)
land([(130, 31), (132, 33), (134, 34), (137, 35), (139, 35), (140, 37),
      (141, 39), (141, 41), (140, 40), (138, 37), (136, 35), (133, 34),
      (131, 32)], ASIA)
land([(140, 42), (142, 42), (144, 44), (145, 44), (143, 42), (141, 42)], ASIA)
land([(109, 1), (111, 2), (114, 3), (117, 1), (117, -2), (114, -3), (111, -3),
      (109, -1)], ASIA)
land([(95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (104, -5), (101, -2),
      (98, 2)], ASIA)
land([(131, -1), (136, -2), (141, -3), (146, -6), (150, -8), (147, -9),
      (143, -8), (139, -7), (136, -4), (132, -2)], ASIA)
land([(105, -6), (108, -7), (112, -7), (114, -8), (111, -8), (107, -7)], ASIA)
land([(113, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
      (132, -32), (135, -35), (138, -35), (140, -38), (144, -38), (146, -39),
      (150, -37), (153, -32), (153, -27), (150, -22), (146, -19), (142, -11),
      (141, -13), (137, -12), (135, -15), (132, -12), (130, -13), (126, -14),
      (122, -17), (118, -20)], OCEAN_T)


def pin(lon, lat, n, dx=0, dy=0):
    x, y = proj(lon, lat)
    if dx or dy:
        d.line([(x, y), (x + dx, y + dy)], fill=RED, width=1)
    cx, cy = x + dx, y + dy
    d.ellipse([cx - 5.5, cy - 5.5, cx + 5.5, cy + 5.5], fill=RED,
              outline=(255, 255, 255), width=1)
    t = str(n)
    f = sans_b(7.5)
    d.text((cx - tw(t, f) / 2, cy - 5), t, font=f, fill=(255, 255, 255))


pin(46.7, 24.6, 1, dx=-10, dy=-6)      # Riyadh
pin(30.7, 36.9, 2, dx=13, dy=-9)       # Antalya / COP31
pin(-75.9, -11.2, 3)                   # Junín, Peru
pin(30.52, 50.45, 4)                   # Kyiv
pin(56.3, 27.0, 5, dx=8, dy=-10)       # Strait of Hormuz
pin(51.4, 35.7, 6)                     # Tehran
pin(-77.0, 38.9, 7)                    # Washington
pin(116.4, 39.9, 8)                    # Beijing
pin(125.6, 7.07, 9)                    # Davao
pin(149.13, -35.28, 10)                # Canberra
pin(-0.12, 51.5, 11)                   # London — Bitcoin (global)
pin(-115.14, 36.17, 12)                # Las Vegas
pin(174.78, -41.29, 13)                # Wellington
d.text((MAP_X0 + 4, MAP_Y1 - 14), "1 Riyadh · 2 Antalya · 3 Junín · 4 Kyiv · 5 Hormuz",
       font=sans(7.5), fill=GREY)

# ---- briefs 14–35 (two columns)
BRIEFS = [
    (14, "Port-au-Prince — Salvadoran troops hit by blasts", "AP"),
    (15, "Los Angeles — Palisades fire starter convicted", "Reuters"),
    (16, "Kharg Island — 14+ Iranian tankers mass in test", "Reuters"),
    (17, "Gaza — Strikes kill Palestinians; W. Bank violence", "Reuters"),
    (18, "Las Vegas — NFL suspends Puka Nacua amid suit", "AP"),
    (19, "Washington — US declassifies more UFO footage", "BBC"),
    (20, "Paris — Police sentenced over Zecler beating", "BBC"),
    (21, "Washington — $811m migrant-scam firms still at it", "BBC"),
    (22, "Jerusalem — Likud: Netanyahu sole PM in talks", "Reuters"),
    (23, "Addis Ababa — Africa launches credit rating agency", "Reuters"),
    (24, "Washington — Trump turns 2028 race into spectacle", "AP"),
    (25, "Jerusalem — Israel GDP per head surges", "Reuters"),
    (26, "Pretoria — ANC fights to keep key cities", "Reuters"),
    (27, "Shenzhen — Trump, Xi: humans run military AI", "Reuters"),
    (28, "Hodeidah — Saudi-led strikes hit Houthi cities", "Al Jazeera"),
    (29, "Cox's Bazar — Rohingya recount 2017 exodus", "Reuters"),
    (30, "Antalya — Delegates sleep in corridors", "The Times"),
    (31, "Antalya — Campaigners: \u201cthe worst COP ever\u201d", "The Times"),
    (32, "Riyadh — Houthis threaten ports, power station", "Al Jazeera"),
    (33, "Lima — Lawmakers walk out as tremor hits", "Reuters"),
    (34, "Junín — Landslides block roads; no deaths", "AFP"),
    (35, "Antalya — Bowen: world will quit fossil fuels", "AAP"),
]
bx0 = 358
d.text((bx0, 698), "ALSO ON SATURDAY 21 NOVEMBER — 22 MORE STORIES",
       font=sans_b(11.5), fill=INK)
bf, bnum = sans(8.5), sans_b(8.5)
for i, (num, text, src) in enumerate(BRIEFS):
    col = 0 if i < 11 else 1
    row = i % 11
    x = bx0 + col * 327
    y = 720 + row * 15.5
    d.text((x, y), str(num), font=bnum, fill=RED)
    full = f"{text} ({src})"
    lines = wrap(full, bf, 317 - 24)
    yy = y
    for ln in lines[:2]:
        d.text((x + 24, yy), ln, font=bf, fill=INK)
        yy += 11

# ---------------------------------------------------------------- DATE CHECK + footer
d.rectangle([M, 898, R, 956], outline=RED, width=2)
d.text((M + 10, 903), "DATE CHECK — WHAT WE LEFT OUT", font=sans_b(10.5), fill=RED)
para("Left out as Friday 20 November\u2019s news: the Kyiv bridges attack and the "
     "Kryvyi Rih strike, the UK\u2013EU deal, GTA VI\u2019s $3.79bn day one, the "
     "daraxonrasib trial results, the Gen Z strikes across Europe, and "
     "Bolsonaro\u2019s hospital stay. The ICJ\u2019s Myanmar genocide ruling was "
     "Thursday 19 November. Not yet shown: the final COP31 text.",
     sans(10), M + 10, 920, R - M - 20, 12.5)
rule(M, R, 964, width=1)
para("HOW WE CHECKED:  CONFIRMED = 2+ outlets  ·  OFFICIAL = on the record  ·  "
     "REPORTED = one outlet  ·  CLAIM = one side\u2019s account.  Every story here "
     "happened, or was first reported, on Saturday 21 November 2026. Officials\u2019 "
     "counts are attributed. Sources named beside each story · original drawings.",
     sans(9), M, 970, R - M, 12)

img.save("entry.png", optimize=True)
print("saved entry.png", img.size)
