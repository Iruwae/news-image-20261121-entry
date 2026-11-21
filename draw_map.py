#!/usr/bin/env python3
"""Round 3 entry for make.fun news-image-20261121: THE WORLD ON ONE MAP.

One day of news - Saturday 21 November 2026 - as a map-led broadsheet:
13 verified stories, every one pinned on a dominant world map, then 13
large readable callouts below. Drawn from scratch with PIL, no photos,
no downloads, no network.
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 242, 231)
INK = (20, 20, 20)
RED = (192, 57, 43)
TAN = (220, 199, 155)
TAN_LINE = (172, 150, 96)
SEA = (222, 232, 230)
GRID = (201, 191, 168)
FAINT = (120, 110, 95)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)


def wrap_text(text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, fnt, max_w, max_lines):
    """Wrap to at most max_lines; shrink font one step if it still overflows."""
    lines = wrap_text(text, fnt, max_w)
    size = fnt.size
    while len(lines) > max_lines and size > 12:
        size -= 1
        fnt = SANS_B(size) if "Bold" in fnt.path else SANS(size)
        lines = wrap_text(text, fnt, max_w)
    return lines, fnt


def halo_text(d, xy, text, fnt, fill, halo=CREAM):
    x, y = xy
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text((x + dx, y + dy), text, font=fnt, fill=halo)
    d.text((x, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- map geometry
MAP = (24, 210, 1000, 596)  # x0, y0, x1, y1


def project(lon, lat):
    x0, y0, x1, y1 = MAP
    x = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    y = y0 + (78.0 - lat) / 136.0 * (y1 - y0)
    return (x, y)


def poly(points):
    return [project(lon, lat) for lon, lat in points]


CONTINENTS = [
    # Asia (drawn first so Europe overlaps its western edge)
    [(30, 70), (35, 68), (42, 68), (50, 68), (60, 69), (68, 70), (76, 72),
     (86, 74), (96, 76), (106, 77), (116, 76), (126, 73), (136, 72),
     (146, 72), (156, 70), (163, 68), (171, 66), (178, 65), (178, 62),
     (170, 60), (162, 58), (158, 52), (150, 50), (142, 50), (140, 45),
     (138, 40), (135, 35), (130, 33), (127, 35), (122, 38), (120, 32),
     (118, 28), (112, 22), (108, 18), (105, 10), (103, 8), (100, 7),
     (98, 10), (97, 15), (94, 17), (91, 22), (88, 22), (86, 20), (82, 17),
     (80, 13), (77, 8), (75, 12), (72, 20), (68, 23), (65, 25), (61, 25),
     (57, 26), (54, 27), (52, 28), (50, 29), (48, 30), (44, 30), (42, 32),
     (40, 34), (36, 36), (33, 36), (30, 36), (28, 38), (26, 40), (24, 40),
     (27, 42), (28, 45), (30, 48), (32, 52), (35, 55), (38, 58), (40, 62),
     (38, 66), (35, 68), (30, 70)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-12, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (9, -1), (12, -5),
     (13, -10), (12, -17), (14, -22), (16, -28), (19, -34), (26, -34),
     (32, -29), (35, -24), (40, -16), (40, -10), (42, -4), (46, -2),
     (51, 2), (51, 10), (48, 11), (44, 12), (40, 15), (38, 18), (37, 22),
     (35, 28), (34, 31), (32, 31), (28, 32), (22, 33), (15, 32), (11, 34),
     (10, 37), (5, 37), (0, 36), (-6, 35)],
    # Europe
    [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-1, 50), (2, 51),
     (5, 53), (8, 55), (8, 57), (10, 59), (12, 56), (18, 56), (21, 55),
     (24, 58), (28, 59), (30, 60), (30, 62), (25, 65), (20, 68), (18, 70),
     (25, 71), (30, 70), (35, 68), (40, 66), (44, 68), (48, 68), (50, 69),
     (44, 67), (40, 64), (35, 62), (32, 60), (30, 58), (28, 56), (26, 54),
     (24, 52), (22, 50), (20, 48), (18, 46), (16, 44), (14, 42), (12, 44),
     (10, 44), (8, 44), (6, 43), (3, 42), (0, 40), (-2, 37), (-6, 36),
     (-9, 37)],
    # North America
    [(-168, 66), (-161, 58), (-152, 60), (-140, 60), (-135, 57), (-130, 54),
     (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24), (-105, 20),
     (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9), (-80, 8),
     (-77, 7), (-79, 9), (-82, 10), (-84, 12), (-87, 15), (-88, 18),
     (-90, 21), (-91, 19), (-97, 19), (-97, 22), (-97, 26), (-93, 30),
     (-89, 30), (-84, 30), (-81, 26), (-80, 32), (-76, 35), (-74, 39),
     (-70, 42), (-68, 45), (-65, 44), (-60, 47), (-55, 52), (-60, 55),
     (-64, 58), (-68, 55), (-72, 58), (-78, 62), (-85, 66), (-92, 66),
     (-95, 69), (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68),
     (-168, 66)],
    # Greenland
    [(-45, 60), (-40, 65), (-32, 68), (-25, 70), (-20, 74), (-25, 77),
     (-35, 80), (-50, 80), (-58, 76), (-55, 70), (-52, 64), (-45, 60)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
     (-66, -55), (-68, -50), (-65, -45), (-62, -41), (-57, -38), (-52, -33),
     (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3),
     (-44, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11),
     (-72, 12), (-76, 10), (-79, 9)],
    # Australia
    [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (146, -39), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -12), (132, -11), (130, -13), (126, -14), (122, -14),
     (118, -20), (113, -22)],
    # United Kingdom, Japan, Madagascar, Borneo, Sumatra, New Guinea, NZ
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-3, 50)],
    [(130, 31), (132, 33), (134, 34), (137, 35), (140, 38), (141, 41),
     (143, 43), (145, 44), (142, 42), (140, 38), (137, 35), (134, 34),
     (131, 32)],
    [(44, -16), (47, -15), (50, -17), (49, -22), (45, -25), (43, -21),
     (44, -16)],
    [(109, 1), (113, 4), (117, 2), (119, -2), (116, -4), (111, -3), (109, 1)],
    [(95, 5), (100, 0), (104, -3), (106, -5), (103, -4), (98, 2), (95, 5)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (146, -8),
     (141, -8), (136, -7), (131, -4)],
    [(167, -45), (170, -42), (173, -40), (175, -38), (178, -37), (176, -40),
     (173, -42), (170, -45), (167, -46)],
]

# (number, lon, lat, label, label_xy, leader_end_xy)
PINS = [
    (1, 30.7, 36.9, "1 ANTALYA", (612, 338), (610, 344)),
    (2, -75.9, -11.2, "2 JUN\u00cdN, PERU", (150, 470), (258, 474)),
    (3, 46.7, 24.6, "3 RIYADH", (655, 372), (653, 376)),
    (4, -74.0, 40.7, "4 NEW YORK", (150, 292), (252, 300)),
    (6, 30.5, 50.4, "6 KYIV", (612, 272), (610, 278)),
    (7, -81.0, 34.0, "7 WASHINGTON", (150, 352), (255, 356)),
    (8, -66.0, 33.5, "8 WASHINGTON", (345, 372), (346, 374)),
    (9, 12.6, 55.7, "9 COPENHAGEN", (505, 240), (540, 254)),
    (10, -70.0, 47.0, "10 NEW YORK", (330, 262), (334, 276)),
    (11, -2.0, 40.4, "11 MADRID", (390, 300), (488, 305)),
    (12, 85.3, 27.7, "12 KATHMANDU", (760, 372), (758, 376)),
    (13, 28.0, -26.2, "13 JOHANNESBURG", (605, 500), (603, 504)),
]

STORIES = [
    ("1 ANTALYA \u00b7 CLIMATE \u2014 REUTERS, AP",
     "COP31 runs into overtime with no deal on fossil fuels",
     "Draft drops fossil fuels and a $120bn target."),
    ("2 JUN\u00cdN, PERU \u00b7 EARTHQUAKE \u2014 USGS, AFP",
     "6.7 quake shakes Peru; no deaths reported",
     "Struck 00:09 GMT; lawmakers left Congress."),
    ("3 RIYADH \u00b7 MISSILES \u2014 REUTERS, AL JAZEERA",
     "Three Houthi missiles downed over Riyadh",
     "Third night of alerts; no damage reported."),
    ("4 NEW YORK \u00b7 MARKETS, FRI CLOSE \u2014 REUTERS, FT",
     "Wall Street slides into correction",
     "S&P -3.7%, Nasdaq -5.28%; Nvidia sank 13%."),
    ("5 MERCURY \u00b7 SPACE \u2014 ESA, USA TODAY",
     "BepiColombo reaches Mercury after 8 years",
     "Captured by Mercury's gravity; science in April."),
    ("6 KYIV \u00b7 DIPLOMACY \u2014 BBC",
     "Zelensky calls Putin a \u2018killer\u2019",
     "After Trump called Putin a friend; Tusk warns."),
    ("7 WASHINGTON \u00b7 TECH \u2014 REUTERS",
     "FBI probes second hack of crime database",
     "Second hack of national crime database probed."),
    ("8 WASHINGTON \u00b7 TECH \u2014 FT",
     "Trump threatens tax on data centres abroad",
     "\u2018Tremendous\u2019 tax on US firms building abroad."),
    ("9 COPENHAGEN \u00b7 SECURITY \u2014 BBC",
     "Denmark expels a Russian diplomat",
     "Accused of plotting to kill a US-Ukrainian rapper."),
    ("10 NEW YORK \u00b7 POLITICS \u2014 BBC",
     "Mamdani to close Rikers by 2032",
     "Mayor-elect plans to shut the jail by 2032."),
    ("11 MADRID \u00b7 POLITICS \u2014 REUTERS",
     "Spain heads to a 29 November election",
     "Conservatives gain ahead of the 29 Nov vote."),
    ("12 KATHMANDU \u00b7 POLITICS \u2014 BBC",
     "Nepal\u2019s new PM faces his India test",
     "Balendra Shah makes his first visit to India."),
    ("13 JOHANNESBURG \u00b7 SOCIETY \u2014 BBC",
     "Nearly 600 women killed in 3 months",
     "South Africa\u2019s femicide toll in new figures."),
]


def draw_map(d):
    x0, y0, x1, y1 = MAP
    d.rectangle([x0, y0, x1, y1], fill=SEA, outline=INK, width=2)
    # faint graticule
    for lon in range(-150, 181, 30):
        gx = x0 + (lon + 180) / 360 * (x1 - x0)
        d.line([(gx, y0), (gx, y1)], fill=(200, 214, 211), width=1)
    for lat in (60, 30, 0, -30):
        gy = y0 + (78 - lat) / 136 * (y1 - y0)
        d.line([(x0, gy), (x1, gy)], fill=(200, 214, 211), width=1)
    # equator, dashed
    gy = y0 + 78 / 136 * (y1 - y0)
    for sx in range(x0, x1, 12):
        d.line([(sx, gy), (sx + 6, gy)], fill=(170, 185, 182), width=1)
    for cont in CONTINENTS:
        d.polygon(poly(cont), fill=TAN, outline=TAN_LINE)
    # Mercury glyph: story 5 happens in space, not on Earth - draw it as a
    # small planet in the empty South Pacific with its own pin.
    mx, my = 170, 540
    d.ellipse([mx - 13, my - 13, mx + 13, my + 13], fill=(196, 164, 120),
              outline=(120, 95, 60), width=2)
    for cx, cy, cr in ((-5, -3, 3), (5, 4, 2), (-1, 6, 2)):
        d.ellipse([mx + cx - cr, my + cy - cr, mx + cx + cr, my + cy + cr],
                  fill=(150, 118, 78))
    d.ellipse([mx - 20, my - 20, mx + 20, my + 20], outline=(150, 118, 78),
              width=1)
    # pins + leader lines + labels
    lab_f = SANS_B(11)
    for num, lon, lat, label, (lx, ly), (ex, ey) in PINS:
        px, py = project(lon, lat)
        d.line([(px, py), (ex, ey)], fill=(90, 80, 70), width=1)
        halo_text(d, (lx, ly), label, lab_f, RED)
        r = 9
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=2)
        nf = SANS_B(9 if num >= 10 else 10)
        tw = nf.getlength(str(num))
        d.text((px - tw / 2, py - 7), str(num),
               font=nf, fill=(255, 255, 255))
    # Mercury pin + label
    halo_text(d, (196, 533), "5 MERCURY \u00b7 SPACE", lab_f, RED)
    d.line([(mx + 13, my - 6), (194, 538)], fill=(90, 80, 70), width=1)
    r = 10
    d.ellipse([mx - r, my - r, mx + r, my + r], outline=RED, width=3)
    d.ellipse([mx - 4, my - 4, mx + 4, my + 4], fill=RED)
    d.text((mx - 3, my - 24), "5", font=SANS_B(11), fill=RED)


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- top kicker + masthead
    d.text((24, 12), "THE WORLD IN ONE DAY", font=SANS_B(15), fill=RED)
    right = "13 STORIES \u00b7 6 REGIONS \u00b7 EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    rf = SANS_B(12)
    d.text((1000 - rf.getlength(right), 14), right, font=rf, fill=INK)
    d.line([(24, 34), (1000, 34)], fill=INK, width=2)
    d.text((24, 38), "Saturday 21 November 2026", font=SERIF_B(56), fill=INK)
    d.text((24, 100), "COP31 runs into overtime \u00b7 A 6.7 quake shakes Peru \u00b7 "
                      "Houthi missiles target Riyadh",
           font=SERIF(19), fill=INK)
    d.line([(24, 126), (1000, 126)], fill=INK, width=2)

    # ---- stat strip: 5 boxes
    stats = [
        ("3", "Houthi missiles downed over Riyadh"),
        ("6.7", "Peru quake magnitude, near Jun\u00edn"),
        ("-3.7%", "S&P 500, Friday\u2019s close"),
        ("8 yrs", "BepiColombo\u2019s journey to Mercury"),
        ("~200", "nations at COP31, Antalya"),
    ]
    d.line([(24, 130), (1000, 130)], fill=INK, width=2)
    for i, (num, label) in enumerate(stats):
        bx = 24 + i * 196
        if i:
            d.line([(bx - 4, 134), (bx - 4, 180)], fill=GRID, width=1)
        d.text((bx, 132), num, font=SANS_B(26), fill=INK)
        for j, line in enumerate(wrap_text(label, SANS(11), 188)):
            d.text((bx, 160 + j * 12), line, font=SANS(11), fill=INK)
    d.line([(24, 186), (1000, 186)], fill=INK, width=1)

    # ---- map header
    d.text((24, 192), "WHERE IT HAPPENED \u2014 13 STORIES ON ONE MAP",
           font=SANS_B(16), fill=INK)
    regions = "Europe 4 \u00b7 Asia 1 \u00b7 Middle East 1 \u00b7 Africa 1 \u00b7 Americas 5 \u00b7 Global 1"
    rf2 = SANS(12)
    d.text((1000 - rf2.getlength(regions), 195), regions, font=rf2, fill=INK)

    draw_map(d)

    # ---- story grid header
    d.text((24, 604), "THE 13 STORIES", font=SANS_B(15), fill=INK)
    gh = "Every story verified for Saturday 21 November 2026"
    gf = SANS(12)
    d.text((1000 - gf.getlength(gh), 606), gh, font=gf, fill=INK)
    d.line([(24, 622), (1000, 622)], fill=INK, width=2)

    # ---- 13 callouts: 3 columns x 4 rows, story 13 spans the last row
    col_x = [24, 352, 680]
    col_w = 320
    row_y, row_h = 626, 64
    for idx, (label, headline, summary) in enumerate(STORIES):
        if idx < 12:
            cx = col_x[idx % 3]
            cy = row_y + (idx // 3) * row_h
            cw = col_w
        else:
            cx, cy, cw = 24, row_y + 4 * row_h, 976
        d.text((cx, cy + 2), label, font=SANS_B(11), fill=RED)
        hf = SANS_B(18 if idx == 12 else 17)
        lines, hf = fit_lines(headline, hf, cw, 2)
        for j, line in enumerate(lines):
            d.text((cx, cy + 14 + j * 18), line, font=hf, fill=INK)
        sum_y = cy + 40 if idx == 12 else cy + 50
        d.text((cx, sum_y), summary, font=SANS(12), fill=INK)
    # grid rules
    for r in range(1, 5):
        y = row_y + r * row_h
        d.line([(24, y), (1000, y)], fill=GRID, width=1)
    for gx in (346, 674):
        d.line([(gx, row_y), (gx, row_y + 4 * row_h)], fill=GRID, width=1)
    d.line([(24, row_y + 5 * row_h), (1000, row_y + 5 * row_h)],
           fill=INK, width=2)

    # ---- DATE CHECK box
    box_y0, box_y1 = 946, 990
    d.rectangle([24, box_y0, 1000, box_y1], outline=RED, width=2)
    check = ("DATE CHECK \u2014 Left out as Friday 20 November\u2019s news: the Kyiv "
             "bridges attack and the Kryvyi Rih strike, the UK\u2013EU deal, GTA VI\u2019s "
             "$3.79bn day one, the daraxonrasib trial results, the Gen Z strikes "
             "across Europe, and Bolsonaro\u2019s hospital stay. The ICJ\u2019s Myanmar "
             "genocide ruling was Thursday 19 November. Not yet shown: the final "
             "COP31 text.")
    for j, line in enumerate(wrap_text(check, SANS(11), 940)):
        d.text((34, box_y0 + 4 + j * 12), line, font=SANS(11), fill=INK)

    # ---- footer
    d.text((24, 994), "Every story here happened, or was first reported, on "
                      "Saturday 21 November 2026. Officials\u2019 counts are attributed.",
           font=SANS(11), fill=INK)
    d.text((24, 1007), "Sources named beside each story \u00b7 original drawings",
           font=SANS(11), fill=INK)

    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
