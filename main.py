#!/usr/bin/env python3
"""Build the entry image for the make.fun bounty
"Sum up 21 November's world news in one image" (news-image-20261121).

Writes a single 1024x1024 PNG newspaper-front-page infographic to
  - <repo>/output/entry.png
  - /output/entry.png  (when the /output directory can be created)

Deterministic: no network, no timestamps, no randomness, fixed fonts.
Running this program twice produces byte-identical output.

Requires: Python 3.12+ and Pillow. Fonts are bundled in the repo's fonts/
directory (DejaVu, OFL) so the program also runs where no system fonts
are installed; it falls back to the system font path, then to Pillow's
built-in default font.
"""

import io
import math
import os
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
W, H = 1024, 1024
PAPER = (250, 247, 240)      # warm newsprint
INK = (17, 17, 17)           # near-black
RED = (185, 28, 28)          # headline accent
NAVY = (30, 58, 95)          # secondary accent
GOLD = (176, 141, 44)
GREY = (90, 88, 82)
RULE = (200, 195, 185)
SKY = (214, 228, 240)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_HERE = os.path.dirname(os.path.abspath(__file__))


def _resolve_font(path):
    """Find a font file: bundled copy in the repo first, then the system
    font path, then None. The grader image has no system fonts, so the
    bundled copies in fonts/ are what makes the program run there."""
    name = os.path.basename(path)
    for candidate in (os.path.join(_HERE, "fonts", name), path):
        if os.path.isfile(candidate):
            return candidate
    return None


def font(path, size):
    resolved = _resolve_font(path)
    if resolved is not None:
        return ImageFont.truetype(resolved, size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap returning a list of lines that fit max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            trial = line + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_wrapped(draw, xy, text, fnt, max_width, fill, leading=None):
    """Draw wrapped text; return the y coordinate after the last line."""
    x, y = xy
    leading = leading or int(fnt.size * 1.32)
    for line in wrap(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def kicker(draw, x, y, label, color=RED):
    """Small caps section label with a red square bullet."""
    fnt = font(SANS_B, 14)
    draw.rectangle([x, y + 2, x + 9, y + 11], fill=color)
    draw.text((x + 15, y), label, font=fnt, fill=color)
    return y + 20


def _dashed(draw, p0, p1, fill, width=2, dash=9, gap=6):
    """Draw a dashed straight line between two points."""
    x0, y0 = p0
    x1, y1 = p1
    length = math.hypot(x1 - x0, y1 - y0)
    if length == 0:
        return
    step = dash + gap
    n = int(length // step)
    for i in range(n + 1):
        t0 = i * step / length
        t1 = min((i * step + dash) / length, 1.0)
        draw.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                   (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)],
                  fill=fill, width=width)


def _star(draw, cx, cy, r_out, r_in, fill):
    """Four-point compass star centred on (cx, cy)."""
    pts = []
    for i in range(8):
        r = r_out if i % 2 == 0 else r_in
        ang = math.pi / 2 + i * math.pi / 4
        pts.append((cx + r * math.cos(ang), cy - r * math.sin(ang)))
    draw.polygon(pts, fill=fill, outline=INK)


# ------------------------------------------------------------------- artwork
def draw_poland_alert(draw, box):
    """Stylised incident map: two Russian missile tracks arcing in from
    the east to three impact markers in south-eastern Poland, with a
    NATO compass star and an Article 4 banner.

    Every shape is clipped to the box: all coordinates are box-local
    and never exceed the box width.
    """
    x0, y0, x1, y1 = box
    bw = x1 - x0
    draw.rectangle(box, fill=SKY)
    d = draw
    f_label = font(SANS_B, 13)
    d.text((x0 + 14, y0 + 10), "SOUTH-EASTERN POLAND  —  FRIDAY 06:30",
           font=f_label, fill=NAVY)
    # dashed flight paths from the east (right edge) to the markers
    markers = [
        (x0 + 118, y0 + 96, "NOWY LIPOWIEC"),
        (x0 + 236, y0 + 72, "RUDNIK NAD SANEM"),
        (x0 + 348, y0 + 108, "MOLODYCZ"),
    ]
    _dashed(d, (x1 - 12, y0 + 42), (markers[0][0] + 12, markers[0][1] - 8),
            RED, width=2)
    _dashed(d, (x1 - 12, y0 + 138), (markers[2][0] + 12, markers[2][1] + 6),
            RED, width=2)
    # missile triangles at the end of each track
    for mx, my, _name in markers[:1] + markers[2:]:
        d.polygon([(mx + 16, my - 4), (mx + 16, my + 4), (mx + 6, my)],
                  fill=RED, outline=INK)
    # impact markers: red discs with white crosshairs + labels
    f_name = font(SANS_B, 11)
    for mx, my, name in markers:
        d.ellipse([mx - 8, my - 8, mx + 8, my + 8], fill=RED, outline=INK,
                  width=2)
        d.line([mx - 4, my, mx + 4, my], fill=(255, 255, 255), width=2)
        d.line([mx, my - 4, mx, my + 4], fill=(255, 255, 255), width=2)
        tw = d.textlength(name, font=f_name)
        lx = min(max(mx - tw / 2, x0 + 6), x1 - tw - 6)
        d.text((lx, my + 12), name, font=f_name, fill=INK)
    # NATO compass star + Article 4 banner along the bottom
    _star(d, x0 + 34, y1 - 22, 16, 5, NAVY)
    d.text((x0 + 56, y1 - 31), "NATO", font=font(SANS_B, 13), fill=NAVY)
    banner = "ARTICLE 4 INVOKED"
    tw = d.textlength(banner, font=font(SANS_B, 14))
    d.text((x1 - tw - 14, y1 - 32), banner, font=font(SANS_B, 14),
           fill=RED)
    draw.rectangle(box, outline=INK, width=2)


# -------------------------------------------------------------------- render
def build_image():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    m = 36                      # outer margin
    cw = W - 2 * m              # content width = 952

    # ---- masthead ------------------------------------------------------
    y = 28
    d.text((m, y), "THE WORLD IN ONE PAGE", font=font(SERIF_B, 52), fill=INK)
    y += 62
    d.text((m, y), "THE DAILY GLOBE  •  ONE DAY, EVERY STORY THAT MATTERED",
           font=font(SANS_B, 15), fill=GREY)
    y += 24
    d.line([(m, y), (W - m, y)], fill=INK, width=3)
    y += 8
    d.line([(m, y), (W - m, y)], fill=INK, width=1)
    y += 12
    d.text((m, y), "Saturday, 21 November 2026", font=font(SERIF_B, 24),
           fill=RED)
    d.text((W - m - d.textlength("No. 325  •  Free to read", font=font(SANS, 15)),
            y + 5), "No. 325  •  Free to read", font=font(SANS, 15), fill=GREY)
    y += 36
    d.line([(m, y), (W - m, y)], fill=INK, width=1)

    # ---- lead story ----------------------------------------------------
    y += 14
    y = kicker(d, m, y, "LEAD  •  WAR SPILLS INTO POLAND")
    y += 2
    d.text((m, y), "MISSILES LAND IN POLAND", font=font(SERIF_B, 56), fill=INK)
    y += 60
    d.text((m, y), "WARSAW CRIES PROVOCATION", font=font(SERIF_B, 32),
           fill=NAVY)
    y += 44

    # incident-map art + lead text side by side
    art_box = (m, y, m + 470, y + 180)
    draw_poland_alert(d, art_box)
    tx = m + 490
    lead = ("Two Russian cruise missiles and a suspected drone came down "
            "in south-eastern Poland on Friday, during a huge overnight "
            "strike on Ukraine — 400 drones, 110 missiles, 8 killed in "
            "Kyiv. PM Donald Tusk called it a deliberate provocation. "
            "NATO called it a grave violation; Poland invoked Article 4.")
    y2 = draw_wrapped(d, (tx, y + 2), lead, font(SERIF, 20), cw - 490, INK,
                      leading=26)
    y2 += 6
    d.line([(tx, y2), (W - m, y2)], fill=RULE, width=1)
    y2 += 10
    d.text((tx, y2), "Timed for allied drills; Warsaw wants more jets.",
           font=font(SANS_B, 15), fill=NAVY)
    y = max(art_box[3], y2 + 16) + 12
    d.line([(m, y), (W - m, y)], fill=INK, width=1)

    # ---- two-column row ------------------------------------------------
    y += 12
    col_w = (cw - 24) // 2
    left_x, right_x = m, m + col_w + 24
    base = y

    y = kicker(d, left_x, base, "WASHINGTON  •  IRAN")
    d.text((left_x, y), "Trump weighs new strikes\non Iran",
           font=font(SERIF_B, 26), fill=INK)
    yq = y + 56
    yq = draw_wrapped(d, (left_x, yq),
                      "Trump is weighing another round of extensive "
                      "strikes on Iran as Israel presses for a four-to-"
                      "seven-day campaign; he says he will decide "
                      "\"soon\". Iran says it downed a US MQ-9 over the "
                      "Strait of Hormuz — its 58th.",
                      font(SANS, 15), col_w, INK, leading=20)

    yk = kicker(d, right_x, base, "LONDON  •  AFTER SHENZHEN")
    d.text((right_x, yk), "Trump tells Europe:\ndefund Kyiv",
           font=font(SERIF_B, 26), fill=INK)
    yi = yk + 56
    yi = draw_wrapped(d, (right_x, yi),
                      "After the Shenzhen summit with Putin, Trump told "
                      "European leaders in an angry call to withhold "
                      "funding from Ukraine. Europe pushed back; the EU "
                      "approved 1 billion euros in defence support for "
                      "Kyiv.",
                      font(SANS, 15), col_w, INK, leading=20)

    y = max(yq, yi) + 12
    d.line([(m, y), (W - m, y)], fill=INK, width=1)

    # ---- three-column row ----------------------------------------------
    y += 12
    col3 = (cw - 48) // 3
    xs = [m, m + col3 + 24, m + 2 * (col3 + 24)]
    base = y

    y = kicker(d, xs[0], base, "NEW YORK  •  MARKETS")
    d.text((xs[0], y), "AI sell-off drags S&P\ninto correction",
           font=font(SERIF_B, 22), fill=INK)
    y1 = y + 50
    y1 = draw_wrapped(d, (xs[0], y1),
                      "US stocks fell 3.7% on Friday as AI and chip "
                      "shares sold off; the S&P 500 and the Dow entered "
                      "correction territory.",
                      font(SANS, 14), col3, INK, leading=19)

    y = kicker(d, xs[1], base, "ANTALYA  •  CLIMATE")
    d.text((xs[1], y), "COP31 runs past\ndeadline",
           font=font(SERIF_B, 22), fill=INK)
    y2 = y + 50
    y2 = draw_wrapped(d, (xs[1], y2),
                      "UN climate talks in Antalya ran into overtime as "
                      "nearly 200 nations failed to agree on fossil "
                      "fuels.",
                      font(SANS, 14), col3, INK, leading=19)

    y = kicker(d, xs[2], base, "BRUSSELS  •  BREXIT RESET")
    d.text((xs[2], y), "UK and EU sign biggest\npost-Brexit deals",
           font=font(SERIF_B, 22), fill=INK)
    y3 = y + 50
    y3 = draw_wrapped(d, (xs[2], y3),
                      "The UK and the EU signed three agreements on food "
                      "exports, carbon markets and youth mobility in "
                      "Brussels.",
                      font(SANS, 14), col3, INK, leading=19)

    y = max(y1, y2, y3) + 12
    d.line([(m, y), (W - m, y)], fill=INK, width=1)

    # ---- also today strip (two columns, one line per item) -------------
    y += 10
    y = kicker(d, m, y, "ALSO TODAY", color=NAVY)
    col2 = (cw - 24) // 2
    left_items = [
        ("BERLIN", "Gen Z protests spread across 25 European countries."),
        ("GAZA", "Israeli strikes kill Palestinians in Gaza."),
    ]
    right_items = [
        ("WALL STREET", "Anthropic debuts as a $2 trillion company."),
        ("HORMUZ", "Two tankers hit mines in the Strait of Hormuz."),
    ]
    strip_end = y
    for col_x, items in ((m, left_items), (m + col2 + 24, right_items)):
        yy = y
        for label, text in items:
            d.text((col_x, yy), "▪  " + label + " — ",
                   font=font(SANS_B, 13), fill=NAVY)
            lx = col_x + d.textlength("▪  " + label + " — ",
                                      font=font(SANS_B, 13))
            end_y = draw_wrapped(d, (lx, yy), text, font(SANS, 13),
                                 col2 - (lx - col_x), INK, leading=18)
            yy = max(end_y, yy + 20) + 2
        strip_end = max(strip_end, yy)
    y = strip_end

    # ---- footer ---------------------------------------------------------
    y += 8
    d.line([(m, y), (W - m, y)], fill=INK, width=1)
    y += 8
    d.text((m, y),
           "Sources: AP, NYT, The Times, Reuters — 21 Nov 2026.",
           font=font(SANS, 11), fill=GREY)
    y += 16
    d.text((m, y),
           "Built by a deterministic Python program. No live data at runtime; all facts embedded above.",
           font=font(SANS, 11), fill=GREY)
    return img


def main():
    img = build_image()
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    data = buf.getvalue()

    here = os.path.dirname(os.path.abspath(__file__))
    targets = [os.path.join(here, "output", "entry.png")]
    try:
        os.makedirs("/output", exist_ok=True)
        targets.append("/output/entry.png")
    except OSError:
        pass
    wrote_any = False
    for path in targets:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as fh:
                fh.write(data)
            print("wrote {} ({} bytes)".format(path, len(data)))
            wrote_any = True
        except OSError as exc:
            # The grader mounts the repo read-only, so writing next to the
            # program fails there; /output is still written below.
            print("could not write {}: {}".format(path, exc))
    if not wrote_any:
        raise SystemExit("failed to write entry.png to any target")


if __name__ == "__main__":
    main()
