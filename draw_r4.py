#!/usr/bin/env python3
"""news-image-20261121 ROUND 4 — broadsheet front page, drawn with PIL.

One-day world news for Saturday 21 November 2026. Everything on this page is
drawn by this script: no photos, no downloads, no network. Canvas 1024x1024,
cream paper, black ink, red labels. DejaVu fonts only.

Template: the winners' broadsheet — giant masthead, 6-stat strip, region bar,
3 big leads with scene illustrations, 10 small stories with coherent mini-scenes
and a verification badge on every card, compact world map + 22 briefs, red
DATE CHECK box, footer with HOW WE CHECKED legend.

Fact set: 3 leads + briefs 14-35 verified live 2026-11-21; the 10 small stories
are the winners' consensus set. One consistent number set: Peru 6.7 (USGS),
Bitcoin $58,983 early Saturday, COP31 day 13 (meant to close day 12).
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
W, H = 1024, 1024
CREAM = (247, 242, 231)
INK = (18, 18, 18)
RED = (192, 57, 43)
RED_DARK = (150, 40, 30)
GREY = (90, 86, 78)
LINE = (60, 55, 48)
TAN = (232, 211, 163)
SEA = (188, 211, 222)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    if not words:
        return []
    lines, cur = [], words[0]
    for word in words[1:]:
        trial = cur + " " + word
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def wrap_n(draw, text, fnt, max_w, max_lines):
    """Wrap and truncate with an ellipsis if it would exceed max_lines."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    while lines and text_w(draw, lines[-1] + " ...", fnt) > max_w:
        lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else ""
    lines[-1] = (lines[-1] + " ...").strip()
    return lines


def draw_wrapped(draw, xy, lines, fnt, fill, lh, align="left", x_right=None):
    x, y = xy
    for line in lines:
        if align == "center":
            draw.text((x - text_w(draw, line, fnt) / 2, y), line, font=fnt, fill=fill)
        elif align == "right":
            draw.text((x_right - text_w(draw, line, fnt), y), line, font=fnt, fill=fill)
        else:
            draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


# ---------------------------------------------------------------- badges
BADGE_FILL = {
    "OFFICIAL": (31, 95, 168),    # blue — on the record
    "CONFIRMED": (30, 125, 50),   # green — 2+ outlets
    "REPORTED": (197, 90, 0),     # orange — one outlet
    "CLAIM": (123, 27, 154),      # purple — one side's account
}


def badge(draw, x_right, y, label):
    """Verification pill, right-aligned at x_right, top y. Returns its left x."""
    fnt = font(SANS_B, 9)
    tw = text_w(draw, label, fnt)
    w = int(tw + 12)
    h = 14
    x0 = int(x_right - w)
    draw.rounded_rectangle([x0, y, x_right, y + h], radius=7,
                           fill=BADGE_FILL[label])
    draw.text((x0 + 6, y + 2), label, font=fnt, fill=WHITE)
    return x0


def pill_label(draw, x, y, text, fnt, fg, bg):
    """Left-aligned label chip; returns right edge x."""
    tw = text_w(draw, text, fnt)
    w = int(tw + 12)
    h = int(fnt.size + 7)
    draw.rectangle([x, y, x + w, y + h], fill=bg)
    draw.text((x + 6, y + 3), text, font=fnt, fill=fg)
    return x + w


def caption_pill(draw, x, y, text):
    fnt = font(SANS_B, 9)
    tw = text_w(draw, text, fnt)
    w = int(tw + 12)
    h = 15
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=WHITE,
                           outline=(120, 115, 105))
    draw.text((x + 6, y + 2), text, font=fnt, fill=INK)
    return x + w


def dashed_line(draw, p0, p1, fill, width=2, dash=7, gap=5):
    """Straight dashed line between two points."""
    x0, y0 = p0
    x1, y1 = p1
    dist = math.hypot(x1 - x0, y1 - y0)
    if dist == 0:
        return
    ux, uy = (x1 - x0) / dist, (y1 - y0) / dist
    d = 0.0
    while d < dist:
        seg = min(dash, dist - d)
        draw.line([x0 + ux * d, y0 + uy * d,
                   x0 + ux * (d + seg), y0 + uy * (d + seg)],
                  fill=fill, width=width)
        d += dash + gap


def draw_italic(img, xy, text, fnt, fill, shear=0.22):
    """DejaVu Serif has no italic face here; fake it with a horizontal shear.

    Renders the text to a temp layer, shears it (top of glyphs shifts right),
    and pastes it. Used for the sub-headline only.
    """
    x, y = xy
    bbox = fnt.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad = int(th * shear) + 6
    tmp = Image.new("RGBA", (tw + pad + 8, th + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.text((4 - bbox[0], 4 - bbox[1]), text, font=fnt, fill=fill + (255,))
    # shear: output x maps to input x - shear*(height - y), so tops move right
    tmp = tmp.transform(tmp.size, Image.AFFINE,
                        (1, -shear, shear * tmp.size[1], 0, 1, 0),
                        resample=Image.BICUBIC)
    img.paste(tmp, (int(x), int(y) - 2), tmp)


def starburst(draw, cx, cy, r, fill, points=8):
    """Simple explosion star: alternating long/short spikes."""
    pts = []
    for i in range(points * 2):
        ang = math.pi * i / points - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def flag_china(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    # one big star + 4 small ones, approximated with 5-point stars
    def star(cx, cy, r):
        pts = []
        for i in range(10):
            ang = math.pi * i / 5 - math.pi / 2
            rr = r if i % 2 == 0 else r * 0.38
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        draw.polygon(pts, fill=(255, 222, 0))
    star(x + w * 0.22, y + h * 0.28, h * 0.20)
    for sx, sy in [(0.52, 0.16), (0.62, 0.30), (0.60, 0.48), (0.48, 0.60)]:
        star(x + w * sx, y + h * sy, h * 0.09)


def flag_japan(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=WHITE, outline=(150, 150, 150))
    draw.ellipse([x + w * 0.5 - h * 0.3, y + h * 0.2,
                  x + w * 0.5 + h * 0.3, y + h * 0.8], fill=(188, 0, 45))

# ---------------------------------------------------------------- lead scenes
# Each draws inside the given box (x, y, w, h) on the main image.


def scene_cop31(img, box):
    """Globe + red thermometer + clock, 'NO DEAL · DAY 13'. NO draft document."""
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(213, 232, 222))
    # --- globe, left
    gx, gy, gr = x + 52, y + h // 2 + 2, 34
    globe = Image.new("RGBA", (gr * 2 + 4, gr * 2 + 4), (0, 0, 0, 0))
    gd = ImageDraw.Draw(globe)
    gd.ellipse([2, 2, gr * 2 + 2, gr * 2 + 2], fill=(52, 130, 190))
    gd.ellipse([14, 12, 34, 28], fill=(74, 160, 90))
    gd.ellipse([30, 34, 56, 52], fill=(74, 160, 90))
    gd.ellipse([40, 10, 54, 24], fill=(74, 160, 90))
    gd.ellipse([16, 44, 30, 58], fill=(74, 160, 90))
    mask = Image.new("L", globe.size, 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([2, 2, gr * 2 + 2, gr * 2 + 2], fill=255)
    globe.putalpha(mask)
    img.paste(globe, (gx - gr - 2, gy - gr - 2), globe)
    d.ellipse([gx - gr - 2, gy - gr - 2, gx + gr + 2, gy + gr + 2],
              outline=(30, 60, 90), width=2)
    # --- thermometer, centre
    tx = x + w // 2 - 4
    d.rounded_rectangle([tx - 7, y + 16, tx + 7, y + h - 26], radius=7,
                        fill=WHITE, outline=(120, 40, 30), width=2)
    d.rounded_rectangle([tx - 4, y + 22, tx + 4, y + h - 30], radius=4,
                        fill=(192, 57, 43))
    d.ellipse([tx - 13, y + h - 38, tx + 13, y + h - 12], fill=(192, 57, 43),
              outline=(120, 40, 30), width=2)
    for i, yy in enumerate(range(y + 24, y + h - 34, 9)):
        d.line([tx + 7, yy, tx + 12, yy], fill=(120, 40, 30), width=1)
    d.text((tx + 16, y + 14), "1.8°C", font=font(SANS_B, 12), fill=RED_DARK)
    # --- clock, right
    cx, cy, cr = x + w - 52, y + h // 2 - 4, 27
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=WHITE,
              outline=INK, width=3)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        d.line([cx + (cr - 5) * math.sin(a), cy - (cr - 5) * math.cos(a),
                cx + (cr - 1) * math.sin(a), cy - (cr - 1) * math.cos(a)],
               fill=INK, width=2)
    # hands: five to midnight — overtime
    d.line([cx, cy, cx - 2, cy - cr + 9], fill=INK, width=3)
    d.line([cx, cy, cx + cr - 12, cy - 8], fill=INK, width=3)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
    d.text((cx - 22, cy + cr + 3), "DAY 13", font=font(SANS_B, 11), fill=RED_DARK)
    # --- ground line + tag
    d.line([x, y + h - 6, x + w, y + h - 6], fill=(120, 140, 120), width=2)


def scene_riyadh(img, box):
    """Night skyline, three interceptor trails arcing up, two bursts."""
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 52))
    # moon
    d.ellipse([x + w - 46, y + 10, x + w - 22, y + 34], fill=(240, 230, 190))
    # stars
    for sx, sy in [(0.12, 0.16), (0.30, 0.10), (0.55, 0.14), (0.72, 0.08),
                   (0.22, 0.30), (0.85, 0.28), (0.45, 0.06)]:
        px, py = x + int(w * sx), y + int(h * sy)
        d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(220, 220, 240))
    base = y + h
    # skyline silhouettes
    skyline = [(0, 46), (18, 46), (18, 30), (34, 30), (34, 52), (52, 52),
               (52, 22), (60, 14), (68, 22), (76, 22), (76, 58), (96, 58),
               (96, 34), (112, 34), (112, 62), (140, 62), (140, 26),
               (156, 26), (156, 48), (176, 48), (176, 38), (196, 38),
               (196, 56), (214, 56), (214, 28), (232, 28), (232, 60),
               (252, 60), (252, 40), (268, 40), (268, 66), (292, 66),
               (292, 44), (308, 44), (308, 70), (325, 70)]
    pts = [(x + px, base - py) for px, py in skyline]
    pts += [(x + w, base), (x, base)]
    d.polygon(pts, fill=(8, 12, 28))
    # lit windows
    for wx, wy in [(24, 40), (40, 42), (58, 34), (60, 46), (102, 46),
                   (120, 50), (146, 38), (162, 40), (182, 48), (220, 40),
                   (238, 44), (258, 50), (274, 52), (298, 54)]:
        d.rectangle([x + wx, base - wy, x + wx + 4, base - wy + 5],
                    fill=(255, 214, 110))
    # PIF-tower-style tall spire, centre-left
    d.polygon([(x + 148, base - 62), (x + 156, base - 108), (x + 164, base - 62)],
              fill=(10, 16, 36))
    d.rectangle([x + 154, base - 108, x + 158, base - 96], fill=(255, 214, 110))
    # three interceptor trails, dashed gold arcs rising to bursts
    for (sx, ex, ey) in [(40, 150, 26), (120, 210, 18), (210, 285, 30)]:
        mid_x, mid_y = (sx + ex) // 2, min(ey, 60) - 34
        steps = 24
        prev = None
        for i in range(steps + 1):
            t = i / steps
            px = int((1 - t) ** 2 * sx + 2 * (1 - t) * t * mid_x + t * t * ex)
            py = int((1 - t) ** 2 * (h - 4) + 2 * (1 - t) * t * mid_y + t * t * ey)
            if prev and i % 2 == 0:
                d.line([prev, (x + px, y + py)], fill=(255, 200, 80), width=2)
            prev = (x + px, y + py)
        starburst(d, x + ex, y + ey, 11, (255, 176, 40))
        starburst(d, x + ex, y + ey, 5, (255, 240, 180))


def scene_peru(img, box):
    """Andes peaks, red seismograph zigzag, houses, big 6.7."""
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(238, 224, 196))
    # sky band
    d.rectangle([x, y, x + w, y + 58], fill=(214, 226, 232))
    # Andes peaks
    d.polygon([(x, y + 58), (x + 55, y + 8), (x + 110, y + 58)], fill=(120, 104, 88))
    d.polygon([(x + 40, y + 22), (x + 55, y + 8), (x + 70, y + 22)],
              fill=WHITE)
    d.polygon([(x + 80, y + 58), (x + 150, y + 2), (x + 220, y + 58)],
              fill=(96, 82, 68))
    d.polygon([(x + 128, y + 20), (x + 150, y + 2), (x + 172, y + 20)],
              fill=WHITE)
    d.polygon([(x + 190, y + 58), (x + 250, y + 14), (x + 310, y + 58)],
              fill=(120, 104, 88))
    # ground
    d.rectangle([x, y + 58, x + w, y + h], fill=(196, 164, 120))
    # houses
    for hx, hw in [(18, 34), (66, 30), (238, 34), (282, 30)]:
        hy = y + h - 30
        d.rectangle([x + hx, hy, x + hx + hw, y + h - 6], fill=(250, 244, 230),
                    outline=(90, 70, 50), width=1)
        d.polygon([(x + hx - 3, hy), (x + hx + hw // 2, hy - 12),
                   (x + hx + hw + 3, hy)], fill=(150, 60, 40))
        d.rectangle([x + hx + hw // 2 - 4, y + h - 16, x + hx + hw // 2 + 4,
                     y + h - 6], fill=(90, 60, 40))
    # seismograph zigzag, red, across the middle
    pts = []
    zx = x + 6
    zy = y + 64
    seq = [0, -5, 6, -11, 21, -18, 10, -6, 3, -3, 14, -21, 8, -5, 2, 0]
    for i, dy in enumerate(seq):
        pts.append((zx + i * 19, zy + dy))
    d.line(pts, fill=RED, width=3, joint="curve")
    # big magnitude
    d.text((x + w - 108, y + 6), "6.7", font=font(SANS_B, 34), fill=RED_DARK)
    deep = "00:09 UTC · 108 KM DEEP"
    f_deep = font(SANS_B, 9)
    d.text((x + w - 8 - text_w(d, deep, f_deep), y + 44), deep,
           font=f_deep, fill=INK)


# ---------------------------------------------------------------- small scenes
# Each draws a literal mini-scene inside the banner box (x, y, w, h).


def sc_kyiv(img, box):
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w // 2, y + h], fill=(0, 91, 187))
    d.rectangle([x + w // 2, y, x + w, y + h], fill=(255, 213, 0))
    # bridge silhouette across the bands
    d.polygon([(x + 10, y + h - 8), (x + w // 2 - 8, y + 12),
               (x + w // 2 + 8, y + 12), (x + w - 10, y + h - 8),
               (x + w - 10, y + h), (x + 10, y + h)], fill=(30, 30, 40))
    d.line([x + 8, y + h - 12, x + w - 8, y + h - 12], fill=(30, 30, 40), width=3)
    for bx in range(30, w - 20, 22):
        d.line([x + bx, y + h - 12, x + bx, y + h - 26], fill=(30, 30, 40), width=2)


def sc_hormuz(img, box):
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(168, 205, 225))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(28, 90, 140))
    d.line([x, y + h - 14, x + w, y + h - 14], fill=WHITE, width=1)
    # tanker
    d.rectangle([x + 22, y + h - 30, x + w - 60, y + h - 14], fill=(40, 40, 48))
    d.rectangle([x + 30, y + h - 44, x + 90, y + h - 30], fill=(150, 60, 40))
    d.rectangle([x + 94, y + h - 44, x + 120, y + h - 30], fill=(40, 110, 70))
    d.rectangle([x + w - 56, y + h - 46, x + w - 40, y + h - 30], fill=(220, 220, 220))
    # drone above
    dx, dy = x + w - 42, y + 12
    d.ellipse([dx - 12, dy - 3, dx + 12, dy + 3], fill=(60, 60, 70))
    d.rectangle([dx - 3, dy + 2, dx + 3, dy + 9], fill=(60, 60, 70))
    d.line([dx - 14, dy - 6, dx + 14, dy - 6], fill=(60, 60, 70), width=2)
    d.ellipse([dx - 16, dy - 8, dx - 10, dy - 4], fill=(120, 120, 130))
    d.ellipse([dx + 10, dy - 8, dx + 16, dy - 4], fill=(120, 120, 130))
    dashed_line(d, (dx, dy + 10), (x + w - 48, y + h - 46), (120, 40, 30), 1, 4, 3)


def sc_iran(img, box):
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(24, 68, 72))
    cx, cy = x + w // 2, y + h // 2 + 1
    # atom: three elliptical orbits + nucleus
    for ang in (0, 60, 120):
        pts = []
        for t in range(0, 361, 6):
            a = math.radians(t)
            rx, ry = 34, 13
            px = rx * math.cos(a)
            py = ry * math.sin(a)
            ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            pts.append((cx + px * ca - py * sa, cy + px * sa + py * ca))
        d.line(pts, fill=(240, 200, 90), width=2)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(240, 200, 90))
    d.text((x + w - 26, y + h - 18), "U", font=font(SANS_B, 14), fill=(240, 200, 90))


def sc_trump(img, box):
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(20, 32, 64))
    # data-centre building
    d.rectangle([x + 14, y + 10, x + 96, y + h - 6], fill=(70, 90, 130),
                outline=(150, 170, 200), width=1)
    for r in range(3):
        for c in range(4):
            d.rectangle([x + 22 + c * 18, y + 16 + r * 9,
                         x + 34 + c * 18, y + 22 + r * 9], fill=(120, 220, 160))
    d.text((x + 104, y + 4), "%", font=font(SANS_B, 30), fill=(255, 200, 60))
    d.text((x + 104, y + h - 20), "TAX", font=font(SANS_B, 12), fill=(255, 200, 60))


def sc_chinajapan(img, box):
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    flag_china(d, x + 12, y + 20, 76, 18)
    flag_japan(d, x + w - 88, y + 20, 76, 18)
    d.line([x + w // 2 - 6, y + 28, x + w // 2 + 6, y + 28], fill=RED, width=3)
    d.polygon([(x + w // 2 + 6, y + 23), (x + w // 2 + 6, y + 33),
               (x + w // 2 + 14, y + 28)], fill=RED)
    d.line([x + w // 2 - 14, y + 28, x + w // 2 + 6, y + 28], fill=RED, width=3)


def sc_davao(img, box):
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(150, 195, 225))
    # clouds
    for cx, cy in [(30, 10), (150, 8)]:
        d.ellipse([x + cx, y + cy, x + cx + 26, y + cy + 10], fill=WHITE)
        d.ellipse([x + cx + 8, y + cy - 4, x + cx + 30, y + cy + 8], fill=WHITE)
    # runway
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(90, 90, 95))
    for rx in range(8, w - 8, 22):
        d.line([x + rx, y + h - 4, x + rx + 10, y + h - 4], fill=WHITE, width=2)
    # plane, white with red stripe, nose right
    px, py = x + 34, y + 16
    d.polygon([(px, py + 6), (px + 108, py + 6), (px + 126, py + 11),
               (px + 108, py + 16), (px, py + 16)], fill=WHITE)
    d.line([px + 8, py + 12, px + 118, py + 12], fill=(200, 40, 30), width=2)
    d.polygon([(px + 52, py + 6), (px + 66, py - 6), (px + 78, py + 6)],
              fill=(220, 225, 230))
    d.polygon([(px + 8, py + 16), (px + 20, py + 24), (px + 30, py + 16)],
              fill=(220, 225, 230))
    d.polygon([(px + 2, py + 6), (px + 12, py - 6), (px + 20, py + 6)],
              fill=(220, 225, 230))


def sc_canberra(img, box):
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    # Australian flag, simplified: blue field, union-jack corner, stars
    d.rectangle([x + 10, y + 20, x + 74, y + 38], fill=(0, 40, 120))
    d.line([x + 10, y + 20, x + 42, y + 38], fill=WHITE, width=2)
    d.line([x + 42, y + 20, x + 10, y + 38], fill=WHITE, width=2)
    d.line([x + 26, y + 20, x + 26, y + 38], fill=(200, 40, 30), width=2)
    d.line([x + 10, y + 29, x + 42, y + 29], fill=(200, 40, 30), width=2)
    for sx, sy in [(50, 23), (60, 29), (48, 33)]:
        d.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=WHITE)
    flag_china(d, x + w - 74, y + 20, 64, 18)
    # AI chip between the flags
    d.rectangle([x + w // 2 - 20, y + 22, x + w // 2 + 20, y + 38],
                fill=(30, 30, 40))
    d.text((x + w // 2 - 9, y + 23), "AI", font=font(SANS_B, 12),
           fill=(120, 220, 160))


def sc_bitcoin(img, box):
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(24, 28, 40))
    # falling chart
    pts = [(x + 10, y + 8), (x + 34, y + 12), (x + 52, y + 10),
           (x + 74, y + 20), (x + 96, y + 18), (x + 118, y + 30),
           (x + 140, y + 28), (x + 158, y + 38)]
    d.line(pts, fill=(230, 70, 50), width=3, joint="curve")
    d.polygon([(x + 158, y + 38), (x + 150, y + 32), (x + 150, y + 40)],
              fill=(230, 70, 50))
    # BTC coin
    cx, cy, cr = x + w - 34, y + h - 16, 15
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(247, 147, 26),
              outline=(200, 110, 10), width=2)
    d.text((cx - 6, cy - 11), "B", font=font(SANS_B, 16), fill=WHITE)
    d.text((x + 8, y + h - 18), "BTC  -3.9%", font=font(SANS_B, 10),
           fill=(230, 70, 50))


def sc_russell(img, box):
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(40, 44, 52))
    # track curve with dashed centre line
    d.line([(x, y + h - 8), (x + 60, y + h - 8), (x + 120, y + 18),
            (x + 190, y + 18)], fill=(70, 74, 84), width=10)
    dashed_line(d, (x + 4, y + h - 8), (x + 60, y + h - 8), WHITE, 2, 6, 5)
    dashed_line(d, (x + 62, y + h - 9), (x + 118, y + 19), WHITE, 2, 6, 5)
    dashed_line(d, (x + 122, y + 18), (x + 188, y + 18), WHITE, 2, 6, 5)
    # F1 car, red, nose right, on the straight
    cx, cy = x + 118, y + 24
    d.polygon([(cx - 34, cy - 2), (cx + 26, cy - 2), (cx + 38, cy + 3),
               (cx + 26, cy + 7), (cx - 34, cy + 7)], fill=(210, 30, 25))
    d.rectangle([cx - 44, cy - 6, cx - 30, cy + 8], fill=(160, 20, 15))
    d.ellipse([cx - 26, cy + 4, cx - 14, cy + 14], fill=BLACK)
    d.ellipse([cx + 14, cy + 4, cx + 26, cy + 14], fill=BLACK)
    d.rectangle([cx - 6, cy - 8, cx + 8, cy - 2], fill=(160, 20, 15))
    # chequered flag
    fx, fy = x + w - 30, y + 6
    for r in range(3):
        for c in range(4):
            if (r + c) % 2 == 0:
                d.rectangle([fx + c * 6, fy + r * 6, fx + c * 6 + 6,
                             fy + r * 6 + 6], fill=BLACK)
            else:
                d.rectangle([fx + c * 6, fy + r * 6, fx + c * 6 + 6,
                             fy + r * 6 + 6], fill=WHITE)


def sc_rahul(img, box):
    x, y, w, h = box
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(46, 125, 50))
    # pitch strip
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(210, 180, 120))
    # stumps
    for sx in (28, 36, 44):
        d.line([x + sx, y + h - 30, x + sx, y + h - 16], fill=(255, 220, 80),
               width=3)
    # bat, angled
    d.line([x + 96, y + 8, x + 128, y + 34], fill=(190, 140, 80), width=9)
    d.line([x + 128, y + 34, x + 136, y + 40], fill=(120, 80, 40), width=5)
    # ball
    d.ellipse([x + 138, y + 4, x + 150, y + 16], fill=(200, 40, 30))
    d.text((x + w - 66, y + h - 16), "124*", font=font(SANS_B, 13), fill=WHITE)

# ---------------------------------------------------------------- world map
# Simplified continents, equirectangular-ish. Pins sit on land, never in sea.

MAP_LON0, MAP_LON1 = -170.0, 190.0
MAP_LAT0, MAP_LAT1 = 78.0, -58.0


def map_xy(mx, my, mw, mh, lon, lat):
    x = mx + (lon - MAP_LON0) / (MAP_LON1 - MAP_LON0) * mw
    y = my + (MAP_LAT0 - lat) / (MAP_LAT0 - MAP_LAT1) * mh
    return x, y


def _poly_lonlat(d, mx, my, mw, mh, coords):
    d.polygon([map_xy(mx, my, mw, mh, lo, la) for lo, la in coords], fill=TAN)


def draw_map(d, mx, my, mw, mh):
    d.rectangle([mx, my, mx + mw, my + mh], fill=SEA)
    # Asia first (largest), then the rest on top
    _poly_lonlat(d, mx, my, mw, mh, [
        (30, 70), (45, 68), (60, 70), (75, 72), (90, 75), (105, 77),
        (120, 73), (135, 72), (150, 70), (162, 68), (170, 66), (178, 64),
        (170, 60), (160, 55), (155, 50), (150, 59), (142, 58), (140, 50),
        (135, 43), (128, 38), (122, 38), (120, 32), (120, 25), (112, 21),
        (108, 15), (105, 9), (100, 7), (97, 10), (94, 16), (90, 22),
        (86, 20), (80, 13), (76, 8), (73, 16), (70, 20), (66, 24),
        (62, 25), (57, 26), (53, 27), (50, 29), (48, 30), (44, 29),
        (40, 28), (38, 25), (35, 28), (34, 31), (30, 36), (28, 41),
        (25, 42), (22, 40), (25, 45), (28, 48), (30, 55), (32, 60),
        (30, 65)])
    _poly_lonlat(d, mx, my, mw, mh, [
        (-17, 15), (-16, 20), (-10, 31), (-5, 35), (0, 36), (10, 37),
        (11, 34), (20, 32), (30, 31), (32, 31), (35, 28), (37, 22),
        (40, 15), (43, 11), (48, 11), (51, 12), (48, 5), (42, 0),
        (40, -5), (40, -12), (36, -18), (33, -26), (28, -33), (20, -35),
        (16, -28), (12, -18), (12, -10), (9, 4), (4, 6), (-8, 5),
        (-13, 8), (-17, 15)])
    _poly_lonlat(d, mx, my, mw, mh, [
        (-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
        (-80, 62), (-75, 58), (-65, 60), (-55, 52), (-60, 45), (-70, 42),
        (-75, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 21), (-97, 16),
        (-92, 15), (-83, 9), (-79, 9), (-86, 13), (-92, 15), (-97, 26),
        (-105, 20), (-110, 24), (-114, 29), (-120, 34), (-125, 40),
        (-124, 48), (-130, 55), (-140, 60), (-155, 58), (-162, 55),
        (-168, 66)])
    _poly_lonlat(d, mx, my, mw, mh, [
        (-45, 60), (-30, 68), (-20, 70), (-25, 76), (-40, 80), (-58, 76),
        (-55, 70), (-50, 64)])
    _poly_lonlat(d, mx, my, mw, mh, [
        (-79, 9), (-72, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
        (-35, -8), (-40, -20), (-48, -28), (-52, -33), (-58, -38),
        (-65, -45), (-68, -52), (-70, -54), (-73, -50), (-73, -40),
        (-72, -30), (-70, -20), (-75, -15), (-80, -5), (-81, 0),
        (-80, 5), (-79, 9)])
    _poly_lonlat(d, mx, my, mw, mh, [
        (-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (3, 53),
        (8, 57), (10, 59), (5, 60), (12, 62), (18, 69), (25, 71),
        (30, 70), (40, 68), (45, 66), (40, 60), (35, 55), (30, 50),
        (28, 45), (23, 40), (20, 40), (15, 44), (12, 44), (8, 44),
        (3, 43), (-2, 37), (-6, 36), (-10, 36)])
    _poly_lonlat(d, mx, my, mw, mh, [
        (113, -22), (114, -30), (115, -35), (120, -34), (125, -33),
        (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
        (153, -32), (153, -27), (150, -23), (146, -19), (142, -15),
        (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
        (126, -14), (122, -17), (118, -20), (113, -22)])
    # islands: UK, Japan, Indonesia, Philippines, New Zealand
    for lo, la, r in [(0, 53, 3), (-2, 56, 3), (130, 31, 2), (138, 35, 2),
                      (141, 39, 2), (143, 43, 2), (100, 0, 2), (110, -6, 2),
                      (120, -8, 2), (130, -4, 2), (121, 14, 3), (122, 11, 3),
                      (124, 8, 3), (126, 7, 3), (167, -45, 3), (174, -41, 3)]:
        cx, cy = map_xy(mx, my, mw, mh, lo, la)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TAN)


# pin positions (lon, lat) + small pixel nudges so neighbours never overlap
PINS = {
    1: (30.7, 36.9, 0, 0),      # Antalya
    2: (46.7, 24.6, 0, 0),      # Riyadh
    3: (-76.0, -11.0, 0, 0),    # Junin, Peru
    4: (30.5, 50.4, 0, 0),      # Kyiv
    5: (56.5, 27.0, 5, 6),      # Strait of Hormuz (nudged off Tehran)
    6: (51.4, 35.7, -3, -3),    # Tehran
    7: (-77.0, 38.9, -4, 4),    # Washington
    8: (116.4, 39.9, 0, 0),     # Beijing
    9: (125.6, 7.1, 0, 0),      # Davao
    10: (149.1, -35.3, 0, 0),   # Canberra
    11: (-74.0, 40.7, 5, -5),   # New York (markets / Bitcoin)
    12: (-115.1, 36.2, 0, 0),   # Las Vegas
    13: (174.8, -41.3, 0, 0),   # Wellington
}


def draw_pins(d, mx, my, mw, mh):
    fnt = font(SANS_B, 8)
    for num, (lo, la, dx, dy) in PINS.items():
        cx, cy = map_xy(mx, my, mw, mh, lo, la)
        cx, cy = int(cx + dx), int(cy + dy)
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED,
                  outline=WHITE, width=1)
        label = str(num)
        tw = text_w(d, label, fnt)
        d.text((cx - tw / 2, cy - 5), label, font=fnt, fill=WHITE)


# ---------------------------------------------------------------- content data
STATS = [
    ("13", "Day of COP31, meant to close day 12"),
    ("3", "missiles shot down over Riyadh"),
    ("6.7", "magnitude of the Peru quake"),
    ("146", "people safe after Davao landing"),
    ("$58,983", "Bitcoin early Saturday, down 3.9% in a day"),
    ("124*", "K L Rahul's score at tea"),
]

# Region bar recounts to THIS page's own 35 stories (drawn 13 + briefs 22):
# drawn — Europe 2, Asia 2, Middle East 3, Africa 0, Americas 3, Oceania 2,
# Global 1; briefs — Europe 4, Asia 2, Middle East 6, Africa 2, Americas 7,
# Global 1. Totals: Europe 6, Asia 4, Middle East 9, Africa 2, Americas 10,
# Oceania 2, Global 2 = 35.
REGIONS = [
    ("EUROPE 6", (47, 111, 178), 140),
    ("ASIA 4", (192, 57, 43), 120),
    ("MIDDLE EAST 9", (217, 142, 4), 170),
    ("AFRICA 2", (123, 75, 168), 100),
    ("AMERICAS 10", (46, 125, 50), 170),
    ("OCEANIA 2", (14, 124, 123), 150),
    ("GLOBAL 2", (93, 109, 126), 142),
]

LEADS = [
    {
        "num": 1, "meta": "ANTALYA, TÜRKIYE · CLIMATE",
        "kicker": "COP31: OVERTIME", "caption": "Ongoing · AFP, Al Jazeera",
        "headline": "COP31 runs into overtime with no deal on fossil fuels",
        "body": ("Negotiators in Antalya will work an extra day after a draft "
                 "deal dropped all mention of fossil fuels and a $120bn "
                 "adaptation target. Nearly 200 nations split; "
                 "campaigners call it 'the worst COP ever'. (Reuters, AP)"),
        "badge": "CONFIRMED", "scene": scene_cop31,
    },
    {
        "num": 2, "meta": "RIYADH · WAR",
        "kicker": "SAUDI: MISSILES", "caption": "Coalition count · AFP",
        "headline": "Three Houthi missiles downed over Riyadh",
        "body": ("Air defences intercepted three ballistic missiles on "
                 "Saturday, the third night of alerts. Earlier a Houthi "
                 "strike damaged the PIF tower, Riyadh's tallest. No damage "
                 "or casualties reported. (Reuters, Al Jazeera)"),
        "badge": "CONFIRMED", "scene": scene_riyadh,
    },
    {
        "num": 3, "meta": "JUNÍN, PERU · EARTHQUAKE",
        "kicker": "PERU: QUAKE 6.7", "caption": "USGS · IGP",
        "headline": "6.7 quake shakes Peru; no deaths reported",
        "body": ("The tremor struck near Junín at 7:09 pm local time, "
                 "rattling Lima and sending lawmakers out of Congress. Minor "
                 "damage to homes and landslides on roads; no tsunami "
                 "threat. (USGS, AFP, Reuters)"),
        "badge": "CONFIRMED", "scene": scene_peru,
    },
]

SMALL = [
    {"num": 4, "meta": "KYIV · WAR", "kicker": "KYIV: WARNING",
     "headline": "Zelensky: Crimea bridge 'will not stay'",
     "summary": "He warns of double-tap strikes in an NBC interview. (NBC)",
     "badge": "REPORTED", "scene": sc_kyiv},
    {"num": 5, "meta": "STRAIT OF HORMUZ · WAR", "kicker": "HORMUZ: DRONE",
     "headline": "Iran says it shot down a US drone",
     "summary": "No confirmation from Washington. (IRIB)",
     "badge": "CLAIM", "scene": sc_hormuz},
    {"num": 6, "meta": "TEHRAN · DIPLOMACY", "kicker": "IRAN: URANIUM",
     "headline": "Iran: uranium stock stays in the country",
     "summary": "Minister still seeks a 'fair solution'. (ToI)",
     "badge": "REPORTED", "scene": sc_iran},
    {"num": 7, "meta": "WASHINGTON · TECHNOLOGY", "kicker": "TRUMP: AI TAX",
     "headline": "Trump vows tax on data centres abroad",
     "summary": "'Tremendous' penalty promised; no details yet. (ABC)",
     "badge": "REPORTED", "scene": sc_trump},
    {"num": 8, "meta": "BEIJING · DIPLOMACY", "kicker": "CHINA–JAPAN",
     "headline": "China tells Japan to 'correct' Taiwan words",
     "summary": "Tokyo says its stance is unchanged. (Ministry, AFP)",
     "badge": "OFFICIAL", "scene": sc_chinajapan},
    {"num": 9, "meta": "DAVAO · AVIATION", "kicker": "DAVAO: 146 SAFE",
     "headline": "Jet lands safely after engine fire alert",
     "summary": "Air Niugini 767 diverts after midnight; all 146 aboard safe. (AP)",
     "badge": "CONFIRMED", "scene": sc_davao},
    {"num": 10, "meta": "CANBERRA · DIPLOMACY", "kicker": "CANBERRA: AI",
     "headline": "Australia and China agree AI talks",
     "summary": "Albanese ends an 11-day trip. (ABC)",
     "badge": "REPORTED", "scene": sc_canberra},
    {"num": 11, "meta": "WORLD · MARKETS", "kicker": "BITCOIN: $58,983",
     "headline": "Bitcoin trades below $59,000 on Saturday",
     "summary": "Down 3.9% in 24 hours; ether $1,625. (CoinGecko)",
     "badge": "REPORTED", "scene": sc_bitcoin},
    {"num": 12, "meta": "LAS VEGAS · FORMULA ONE", "kicker": "RUSSELL: P1",
     "headline": "Russell fastest in final Las Vegas practice",
     "summary": "1:34.041 in a damp, messy session. (Formula 1)",
     "badge": "OFFICIAL", "scene": sc_russell},
    {"num": 13, "meta": "WELLINGTON · CRICKET", "kicker": "RAHUL: 124*",
     "headline": "Rahul hits century against New Zealand",
     "summary": "India 344 for 2 at tea, replying to 368. (AFP)",
     "badge": "REPORTED", "scene": sc_rahul},
]

BRIEFS = [
    (14, "Port-au-Prince", "Salvadoran troops in Haiti lose soldiers to explosives", "AP"),
    (15, "Los Angeles", "Man convicted of starting the deadly Palisades fire", "Reuters"),
    (16, "Kharg Island", "14+ Iranian tankers mass in a test of the US blockade", "Reuters"),
    (17, "Gaza", "Israeli strikes kill Palestinians; West Bank violence goes on", "Reuters"),
    (18, "Las Vegas", "NFL suspends Puka Nacua amid an antisemitism lawsuit", "AP"),
    (19, "Washington", "US declassifies more UFO footage filmed in the Middle East", "BBC"),
    (20, "Paris", "Police sentenced over beating of music producer Michel Zecler", "BBC"),
    (21, "Washington", "Firms fined $811m for conning detained migrants keep scamming", "BBC"),
    (22, "Jerusalem", "Likud demands Netanyahu serve as sole PM in unity talks", "Reuters"),
    (23, "Addis Ababa", "Africa launches its own credit rating agency", "Reuters"),
    (24, "Washington", "Trump turns the 2028 succession race into a spectacle", "AP"),
    (25, "Jerusalem", "Israel's GDP per head surges as living standards improve", "Reuters"),
    (26, "Pretoria", "ANC fights to keep control of key cities after election setback", "Reuters"),
    (27, "Shenzhen", "Trump and Xi agree humans must stay in charge of military AI", "Reuters"),
    (28, "Hodeidah", "Saudi-led strikes hit Houthi-held cities across Yemen", "Al Jazeera"),
    (29, "Cox's Bazar", "Rohingya survivors recount the 2017 exodus as Hague ruling lands", "Reuters"),
    (30, "Antalya", "Delegates sleep in corridors as COP31 drags on", "The Times"),
    (31, "Antalya", "Campaigners call COP31 \"the worst COP ever\"", "The Times"),
    (32, "Riyadh", "Houthis threaten Saudi ports and a power station", "Al Jazeera"),
    (33, "Lima", "Lawmakers walk out of Congress as the tremor hits", "Reuters"),
    (34, "Junín", "Landslides block roads after the quake; no deaths reported", "AFP"),
    (35, "Antalya", "Bowen: the world will quit fossil fuels regardless", "AAP"),
]

DATE_CHECK = ("Left out as Friday 20 November's news: the Kyiv bridges attack "
              "and the Kryvyi Rih strike, the UK–EU deal, GTA VI's $3.79bn day "
              "one, the daraxonrasib trial results, the Gen Z strikes across "
              "Europe, and Bolsonaro's hospital stay. The ICJ's Myanmar "
              "genocide ruling was Thursday 19 November. Not yet shown: the "
              "final COP31 text.")

# ---------------------------------------------------------------- layout
def prefixed_lines(d, prefix_runs, body, fnt, fnt_b, max_w, first_extra=0):
    """Wrap `body` where the first line is prefixed by bold runs.

    prefix_runs: list of (text, fill) drawn bold at the line start.
    Returns list of (runs, is_first) where runs = [(text, font, fill), ...].
    """
    prefix_w = sum(text_w(d, t, fnt_b) for t, _ in prefix_runs)
    words = body.split()
    lines = []
    cur_words, cur_w = [], 0.0
    first = True
    for word in words:
        ww = text_w(d, word + " ", fnt)
        avail = max_w - (prefix_w + first_extra if first else 0)
        if cur_w + ww <= avail or not cur_words:
            cur_words.append(word)
            cur_w += ww
        else:
            lines.append((cur_words, first))
            cur_words, cur_w, first = [word], ww, False
    lines.append((cur_words, first))
    out = []
    for words_in_line, is_first in lines:
        if is_first:
            runs = [(t, fnt_b, c) for t, c in prefix_runs]
            runs.append((" ".join(words_in_line), fnt, INK))
        else:
            runs = [(" ".join(words_in_line), fnt, INK)]
        out.append(runs)
    return out


def draw_prefixed(d, x, y, line_runs, lh):
    for runs in line_runs:
        cx = x
        for text, fnt, fill in runs:
            if text:
                d.text((cx, y), text, font=fnt, fill=fill)
                cx += text_w(d, text, fnt)
        y += lh
    return y


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    mx = 16  # left margin; content spans 16..1008

    # ---- top line
    f_top = font(SANS_B, 12)
    d.text((mx, 8), "THE WORLD IN ONE DAY", font=f_top, fill=RED)
    right_top = "35 STORIES · 7 REGIONS · EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    f_top_r = font(SANS_B, 11)
    d.text((1008 - text_w(d, right_top, f_top_r), 9), right_top,
           font=f_top_r, fill=INK)
    d.line([mx, 27, 1008, 27], fill=INK, width=2)

    # ---- masthead (auto-fit serif bold)
    mast = "Saturday 21 November 2026"
    size = 56
    while size > 40 and text_w(d, mast, font(SERIF_B, size)) > 988:
        size -= 1
    f_mast = font(SERIF_B, size)
    d.text(((W - text_w(d, mast, f_mast)) / 2, 30), mast, font=f_mast, fill=INK)

    # ---- italic sub-headline (sheared DejaVu Serif)
    sub = ("COP31 runs into overtime · Houthi missiles target Riyadh · "
           "A 6.7 quake shakes Peru")
    f_sub = font(SERIF, 19)
    sub_w = text_w(d, sub, f_sub)
    draw_italic(img, ((W - sub_w) / 2, 98), sub, f_sub, INK)
    d = ImageDraw.Draw(img)
    d.line([mx, 120, 1008, 120], fill=INK, width=1)

    # ---- 6-stat strip
    stat_y, stat_h = 126, 54
    box_w = 992 / 6
    for i, (num, label) in enumerate(STATS):
        bx = mx + i * box_w
        f_num = font(SERIF_B, 27)
        d.text((bx + 8, stat_y + 2), num, font=f_num, fill=RED)
        f_lab = font(SANS, 10)
        lines = wrap_n(d, label, f_lab, box_w - 14, 2)
        draw_wrapped(d, (bx + 8, stat_y + 32), lines, f_lab, INK, 11)
        if i:
            d.line([bx, stat_y + 4, bx, stat_y + stat_h - 4], fill=LINE, width=1)
    d.line([mx, stat_y + stat_h, 1008, stat_y + stat_h], fill=INK, width=1)

    # ---- region bar
    reg_y, reg_h = 184, 18
    rx = mx
    f_reg = font(SANS_B, 10)
    for label, color, rw in REGIONS:
        d.rectangle([rx, reg_y, rx + rw, reg_y + reg_h], fill=color)
        tw = text_w(d, label, f_reg)
        d.text((rx + (rw - tw) / 2, reg_y + 3), label, font=f_reg, fill=WHITE)
        rx += rw

    # ---- 3 big leads
    lead_y, lead_h = 208, 220
    lead_w = 325
    lead_x = [16, 350, 683]
    for lead, lx in zip(LEADS, lead_x):
        d.rectangle([lx, lead_y, lx + lead_w, lead_y + lead_h],
                    outline=(200, 195, 185), width=1)
        # banner scene
        lead["scene"](img, (lx + 1, lead_y + 1, lead_w - 2, 96))
        d = ImageDraw.Draw(img)
        pill_label(d, lx + 9, lead_y + 7, lead["kicker"], font(SANS_B, 10),
                   WHITE, RED)
        caption_pill(d, lx + 9, lead_y + 75, lead["caption"])
        # meta line + badge
        f_meta = font(SANS_B, 10)
        meta = "%d %s" % (lead["num"], lead["meta"])
        d.text((lx + 6, lead_y + 102), meta, font=f_meta, fill=RED)
        badge(d, lx + lead_w - 6, lead_y + 101, lead["badge"])
        # headline
        f_head = font(SANS_B, 17)
        lines = wrap_n(d, lead["headline"], f_head, lead_w - 12, 2)
        draw_wrapped(d, (lx + 6, lead_y + 116), lines, f_head, INK, 20)
        # body
        f_body = font(SANS, 10.5)
        lines = wrap_n(d, lead["body"], f_body, lead_w - 12, 4)
        draw_wrapped(d, (lx + 6, lead_y + 160), lines, f_body, INK, 13.5)

    # ---- 10 small stories, 2 rows of 5
    card_w, card_h, gap = 192, 104, 8
    for row in range(2):
        for col in range(5):
            s = SMALL[row * 5 + col]
            cx = 16 + col * (card_w + gap)
            cy = 434 + row * (card_h + 6)
            d.rectangle([cx, cy, cx + card_w, cy + card_h],
                        outline=(200, 195, 185), width=1)
            s["scene"](img, (cx + 1, cy + 1, card_w - 2, 38))
            d = ImageDraw.Draw(img)
            pill_label(d, cx + 5, cy + 3, s["kicker"], font(SANS_B, 9),
                       WHITE, RED)
            f_meta = font(SANS_B, 9)
            meta = "%d %s" % (s["num"], s["meta"])
            # meta may be long; shrink to fit before the badge
            badge_w = int(text_w(d, s["badge"], font(SANS_B, 9)) + 12)
            while text_w(d, meta, f_meta) > card_w - badge_w - 14 and f_meta.size > 7:
                f_meta = font(SANS_B, f_meta.size - 1)
            d.text((cx + 4, cy + 41), meta, font=f_meta, fill=RED)
            badge(d, cx + card_w - 4, cy + 40, s["badge"])
            f_head = font(SANS_B, 12)
            lines = wrap_n(d, s["headline"], f_head, card_w - 8, 2)
            draw_wrapped(d, (cx + 4, cy + 53), lines, f_head, INK, 14)
            f_sum = font(SANS, 10)
            lines = wrap_n(d, s["summary"], f_sum, card_w - 8, 2)
            draw_wrapped(d, (cx + 4, cy + 81), lines, f_sum, GREY, 11)

    # ---- bottom section headers
    f_sec = font(SANS_B, 11)
    d.text((16, 654), "WHERE IT HAPPENED", font=f_sec, fill=INK)
    d.text((352, 654), "ALSO ON SATURDAY 21 NOVEMBER — 22 MORE STORIES",
           font=f_sec, fill=INK)
    d.line([16, 668, 1008, 668], fill=INK, width=1)

    # ---- world map + pins
    map_x, map_y, map_w, map_h = 16, 674, 320, 170
    d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h],
                outline=(150, 145, 135), width=1)
    draw_map(d, map_x + 1, map_y + 1, map_w - 2, map_h - 2)
    draw_pins(d, map_x + 1, map_y + 1, map_w - 2, map_h - 2)
    f_cap = font(SANS, 9)
    cap = "Each number is the story with that number on this page."
    lines = wrap(d, cap, f_cap, map_w)
    draw_wrapped(d, (map_x, map_y + map_h + 6), lines, f_cap, GREY, 11)

    # ---- briefs 14–35, two columns, adaptive size
    brief_top, brief_bottom = 674, 936
    col_w = 322
    col_x = [352, 686]
    chosen = None
    for size in (10, 9.5, 9, 8.5):
        fnt = font(SANS, size)
        fnt_b = font(SANS_B, size)
        lh = size + 2
        cols = [[], []]
        for i, (num, place, text, src) in enumerate(BRIEFS):
            runs = [("%d " % num, RED), (place + " — ", INK)]
            body = text + " (" + src + ")"
            lines = prefixed_lines(d, runs, body, fnt, fnt_b, col_w)
            cols[0 if i < 11 else 1].append(lines)
        heights = [sum(len(it) for it in col) * lh + (len(col) - 1) * 2
                   for col in cols]
        if max(heights) <= brief_bottom - brief_top:
            chosen = (size, fnt, fnt_b, lh, cols)
            break
    if chosen is None:  # fall back to smallest and let it run long
        size = 8.5
        fnt = font(SANS, size)
        fnt_b = font(SANS_B, size)
        lh = size + 2
        cols = [[], []]
        for i, (num, place, text, src) in enumerate(BRIEFS):
            runs = [("%d " % num, RED), (place + " — ", INK)]
            lines = prefixed_lines(d, runs, text + " (" + src + ")", fnt,
                                   fnt_b, col_w)
            cols[0 if i < 11 else 1].append(lines)
        chosen = (size, fnt, fnt_b, lh, cols)
    _, fnt, fnt_b, lh, cols = chosen
    for ci, col in enumerate(cols):
        y = brief_top
        for item_lines in col:
            y = draw_prefixed(d, col_x[ci], y, item_lines, lh)
            y += 2

    # ---- DATE CHECK box
    dc_y, dc_h = 942, 36
    d.rectangle([16, dc_y, 1008, dc_y + dc_h], outline=RED, width=2)
    f_dc_lab = font(SANS_B, 10)
    lab = "DATE CHECK"
    lab_w = text_w(d, lab, f_dc_lab)
    d.text((24, dc_y + 11), lab, font=f_dc_lab, fill=RED)
    f_dc = font(SANS, 10)
    lines = wrap(d, DATE_CHECK, f_dc, 1008 - 24 - lab_w - 20 - 8)
    draw_wrapped(d, (24 + lab_w + 12, dc_y + 5), lines, f_dc, INK, 12.5)

    # ---- footer
    f_foot = font(SANS, 10)
    foot1 = ("Every story here happened, or was first reported, on Saturday "
             "21 November 2026. Officials' counts are attributed.")
    d.text(((W - text_w(d, foot1, f_foot)) / 2, 984), foot1, font=f_foot,
           fill=INK)
    f_foot2 = font(SANS, 9)
    foot2 = ("Sources named beside each story · original drawings · "
             "HOW WE CHECKED: CONFIRMED = 2+ outlets · OFFICIAL = on the "
             "record · REPORTED = one outlet · CLAIM = one side's account")
    d.text(((W - text_w(d, foot2, f_foot2)) / 2, 998), foot2, font=f_foot2,
           fill=GREY)
    return img


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    img = build()
    img.save(out, optimize=True)
    size = os.path.getsize(out)
    print("saved %s  %dx%d  %d bytes" % (out, img.width, img.height, size))
    assert img.width == 1024 and img.height == 1024
    assert size <= 1024 * 1024, "entry.png over 1 MiB"


if __name__ == "__main__":
    main()
