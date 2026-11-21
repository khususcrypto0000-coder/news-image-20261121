#!/usr/bin/env python3
"""Front page for 21 November 2026 — a one-page newspaper infographic.

Built for the make.fun bounty "Sum up 21 November's world news in one
image" (news-image-20261121). The program renders a 1024x1024 PNG of a
newspaper front page and saves it to output/entry.png (plus /output
when that directory is writable).

Everything is baked in: no network access, no clock, no randomness,
fonts bundled in fonts/. Two runs therefore produce the exact same
bytes. Requires Python 3.12+ and Pillow.
"""

import io
import math
import os
from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ layout
CANVAS = (1024, 1024)          # sheet size in pixels
EDGE = 36                      # margin on every side

PALETTE = {
    "paper": (250, 247, 240),   # warm newsprint
    "ink": (17, 17, 17),        # near-black
    "red": (185, 28, 28),       # headline accent
    "navy": (30, 58, 95),       # secondary accent
    "gold": (176, 141, 44),     # spare accent (unused, kept for the palette)
    "grey": (90, 88, 82),       # captions and meta text
    "rule": (200, 195, 185),    # hairlines inside the page
    "sky": (214, 228, 240),     # incident-map background
    "white": (255, 255, 255),   # crosshair marks on the map
}

# Typefaces the page uses. The value is the system path; the bundled
# copy in fonts/ is preferred at runtime (see _find_face).
SYSTEM_FONTS = {
    "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "serif_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

_HERE = os.path.dirname(os.path.abspath(__file__))


def _find_face(system_path):
    """Locate a font file: bundled copy in fonts/ first, then the system
    path. The grading image has no system fonts installed, so the
    bundled copies are what the program actually runs on there."""
    base = os.path.basename(system_path)
    for probe in (os.path.join(_HERE, "fonts", base), system_path):
        if os.path.isfile(probe):
            return probe
    return None


def typeface(kind, size):
    """Return a Pillow font for face kind at the requested point size."""
    found = _find_face(SYSTEM_FONTS[kind])
    if found is not None:
        return ImageFont.truetype(found, size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # very old Pillow has no size argument
        return ImageFont.load_default()


# ------------------------------------------------------------- text helpers
def _flow(draw, text, fnt, limit):
    """Split text into lines that fit inside limit pixels (greedy wrap)."""
    out = []
    for chunk in text.split("\n"):
        words = chunk.split()
        if not words:
            out.append("")
            continue
        current = words[0]
        for nxt in words[1:]:
            trial = current + " " + nxt
            if draw.textlength(trial, font=fnt) <= limit:
                current = trial
            else:
                out.append(current)
                current = nxt
        out.append(current)
    return out


def _para(draw, pos, text, fnt, limit, fill, leading=None):
    """Draw wrapped text starting at pos; return the row below it."""
    x, y = pos
    step = leading if leading is not None else int(fnt.size * 1.32)
    for row in _flow(draw, text, fnt, limit):
        draw.text((x, y), row, font=fnt, fill=fill)
        y += step
    return y


def _tag(draw, x, y, caption, color):
    """Section label: small coloured square bullet + bold caps text."""
    fnt = typeface("sans_bold", 14)
    draw.rectangle([x, y + 2, x + 9, y + 11], fill=color)
    draw.text((x + 15, y), caption, font=fnt, fill=color)
    return y + 20


# ------------------------------------------------------------ shape helpers
def _dotted(draw, start, end, color, width=2, dash=9, gap=6):
    """A dashed straight line from start to end."""
    x0, y0 = start
    x1, y1 = end
    span = math.hypot(x1 - x0, y1 - y0)
    if span == 0:
        return
    stride = dash + gap
    count = int(span // stride)
    for k in range(count + 1):
        a = k * stride / span
        b = min((k * stride + dash) / span, 1.0)
        draw.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a),
                   (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)],
                  fill=color, width=width)


def _rose(draw, cx, cy, outer, inner, color):
    """Four-point compass star centred on (cx, cy)."""
    verts = []
    for k in range(8):
        r = outer if k % 2 == 0 else inner
        ang = math.pi / 2 + k * math.pi / 4
        verts.append((cx + r * math.cos(ang), cy - r * math.sin(ang)))
    draw.polygon(verts, fill=color, outline=PALETTE["ink"])


def _incident_map(draw, frame):
    """Stylised map of south-eastern Poland: two Russian missile tracks
    arcing in from the east to three impact markers, a NATO compass
    star and an Article 4 banner. All coordinates stay inside frame."""
    x0, y0, x1, y1 = frame
    draw.rectangle(frame, fill=PALETTE["sky"])
    draw.text((x0 + 14, y0 + 10), "SOUTH-EASTERN POLAND  —  FRIDAY 06:30",
              font=typeface("sans_bold", 13), fill=PALETTE["navy"])
    pins = [
        (x0 + 118, y0 + 96, "NOWY LIPOWIEC"),
        (x0 + 236, y0 + 72, "RUDNIK NAD SANEM"),
        (x0 + 348, y0 + 108, "MOLODYCZ"),
    ]
    # dashed flight paths in from the east (right edge)
    _dotted(draw, (x1 - 12, y0 + 42), (pins[0][0] + 12, pins[0][1] - 8),
            PALETTE["red"], width=2)
    _dotted(draw, (x1 - 12, y0 + 138), (pins[2][0] + 12, pins[2][1] + 6),
            PALETTE["red"], width=2)
    # missile triangles at the end of each track
    for px, py, _label in pins[:1] + pins[2:]:
        draw.polygon([(px + 16, py - 4), (px + 16, py + 4), (px + 6, py)],
                     fill=PALETTE["red"], outline=PALETTE["ink"])
    # impact markers: red discs with white crosshairs and a name label
    name_font = typeface("sans_bold", 11)
    for px, py, label in pins:
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=PALETTE["red"],
                     outline=PALETTE["ink"], width=2)
        draw.line([px - 4, py, px + 4, py], fill=PALETTE["white"], width=2)
        draw.line([px, py - 4, px, py + 4], fill=PALETTE["white"], width=2)
        tw = draw.textlength(label, font=name_font)
        lx = min(max(px - tw / 2, x0 + 6), x1 - tw - 6)
        draw.text((lx, py + 12), label, font=name_font, fill=PALETTE["ink"])
    # NATO compass star and the Article 4 banner along the bottom
    _rose(draw, x0 + 34, y1 - 22, 16, 5, PALETTE["navy"])
    draw.text((x0 + 56, y1 - 31), "NATO", font=typeface("sans_bold", 13),
              fill=PALETTE["navy"])
    banner = "ARTICLE 4 INVOKED"
    bw = draw.textlength(banner, font=typeface("sans_bold", 14))
    draw.text((x1 - bw - 14, y1 - 32), banner, font=typeface("sans_bold", 14),
              fill=PALETTE["red"])
    draw.rectangle(frame, outline=PALETTE["ink"], width=2)


# ------------------------------------------------------------------- page
class FrontPage:
    """Assembles the whole sheet from top to bottom, tracking one cursor
    row (self.row) as sections are laid out."""

    def __init__(self):
        self.sheet = Image.new("RGB", CANVAS, PALETTE["paper"])
        self.pen = ImageDraw.Draw(self.sheet)
        self.row = 28
        self.span = CANVAS[0] - 2 * EDGE   # usable width: 952

    def rule(self, weight=1):
        """Full-width black hairline at the current row."""
        self.pen.line([(EDGE, self.row), (CANVAS[0] - EDGE, self.row)],
                      fill=PALETTE["ink"], width=weight)

    # ------------------------------------------------------------ masthead
    def masthead(self):
        d = self.pen
        d.text((EDGE, self.row), "THE WORLD IN ONE PAGE",
               font=typeface("serif_bold", 52), fill=PALETTE["ink"])
        self.row += 62
        d.text((EDGE, self.row),
               "THE DAILY GLOBE  •  ONE DAY, EVERY STORY THAT MATTERED",
               font=typeface("sans_bold", 15), fill=PALETTE["grey"])
        self.row += 24
        self.rule(3)
        self.row += 8
        self.rule(1)
        self.row += 12
        d.text((EDGE, self.row), "Saturday, 21 November 2026",
               font=typeface("serif_bold", 24), fill=PALETTE["red"])
        tag = "No. 325  •  Free to read"
        d.text((CANVAS[0] - EDGE - d.textlength(tag, font=typeface("sans", 15)),
                self.row + 5), tag, font=typeface("sans", 15),
               fill=PALETTE["grey"])
        self.row += 36
        self.rule(1)

    # ------------------------------------------------------------ lead story
    def lead(self):
        d = self.pen
        self.row += 14
        self.row = _tag(d, EDGE, self.row, "LEAD  •  WAR SPILLS INTO POLAND",
                        PALETTE["red"])
        self.row += 2
        d.text((EDGE, self.row), "MISSILES LAND IN POLAND",
               font=typeface("serif_bold", 56), fill=PALETTE["ink"])
        self.row += 60
        d.text((EDGE, self.row), "WARSAW CRIES PROVOCATION",
               font=typeface("serif_bold", 32), fill=PALETTE["navy"])
        self.row += 44
        # incident-map artwork on the left, lead text on the right
        frame = (EDGE, self.row, EDGE + 470, self.row + 180)
        _incident_map(d, frame)
        tx = EDGE + 490
        body = ("Two Russian cruise missiles and a suspected drone came down "
                "in south-eastern Poland on Friday, during a huge overnight "
                "strike on Ukraine — 400 drones, 110 missiles, 8 killed in "
                "Kyiv. PM Donald Tusk called it a deliberate provocation. "
                "NATO called it a grave violation; Poland invoked Article 4.")
        end = _para(d, (tx, self.row + 2), body, typeface("serif", 20),
                    self.span - 490, PALETTE["ink"], leading=26)
        end += 6
        d.line([(tx, end), (CANVAS[0] - EDGE, end)], fill=PALETTE["rule"],
               width=1)
        end += 10
        d.text((tx, end), "Timed for allied drills; Warsaw wants more jets.",
               font=typeface("sans_bold", 15), fill=PALETTE["navy"])
        self.row = max(frame[3], end + 16) + 12
        self.rule(1)

    # -------------------------------------------------------- two-column row
    def pair(self):
        d = self.pen
        self.row += 12
        half = (self.span - 24) // 2
        lx, rx = EDGE, EDGE + half + 24
        top = self.row
        self.row = _tag(d, lx, top, "WASHINGTON  •  IRAN", PALETTE["red"])
        d.text((lx, self.row), "Trump weighs new strikes\non Iran",
               font=typeface("serif_bold", 26), fill=PALETTE["ink"])
        left_end = _para(d, (lx, self.row + 56),
                         "Trump is weighing another round of extensive "
                         "strikes on Iran as Israel presses for a four-to-"
                         "seven-day campaign; he says he will decide "
                         "\"soon\". Iran says it downed a US MQ-9 over the "
                         "Strait of Hormuz — its 58th.",
                         typeface("sans", 15), half, PALETTE["ink"],
                         leading=20)
        top2 = _tag(d, rx, top, "LONDON  •  AFTER SHENZHEN", PALETTE["red"])
        d.text((rx, top2), "Trump tells Europe:\ndefund Kyiv",
               font=typeface("serif_bold", 26), fill=PALETTE["ink"])
        right_end = _para(d, (rx, top2 + 56),
                          "After the Shenzhen summit with Putin, Trump told "
                          "European leaders in an angry call to withhold "
                          "funding from Ukraine. Europe pushed back; the EU "
                          "approved 1 billion euros in defence support for "
                          "Kyiv.",
                          typeface("sans", 15), half, PALETTE["ink"],
                          leading=20)
        self.row = max(left_end, right_end) + 12
        self.rule(1)

    # ------------------------------------------------------ three-column row
    def trio(self):
        d = self.pen
        self.row += 12
        third = (self.span - 48) // 3
        cols = [EDGE, EDGE + third + 24, EDGE + 2 * (third + 24)]
        top = self.row
        stories = [
            ("NEW YORK  •  MARKETS",
             "AI sell-off drags S&P\ninto correction",
             "US stocks fell 3.7% on Friday as AI and chip "
             "shares sold off; the S&P 500 and the Dow entered "
             "correction territory."),
            ("ANTALYA  •  CLIMATE",
             "COP31 runs past\ndeadline",
             "UN climate talks in Antalya ran into overtime as "
             "nearly 200 nations failed to agree on fossil "
             "fuels."),
            ("BRUSSELS  •  BREXIT RESET",
             "UK and EU sign biggest\npost-Brexit deals",
             "The UK and the EU signed three agreements on food "
             "exports, carbon markets and youth mobility in "
             "Brussels."),
        ]
        ends = []
        for cx, (label, head, body) in zip(cols, stories):
            after = _tag(d, cx, top, label, PALETTE["red"])
            d.text((cx, after), head, font=typeface("serif_bold", 22),
                   fill=PALETTE["ink"])
            ends.append(_para(d, (cx, after + 50), body,
                              typeface("sans", 14), third, PALETTE["ink"],
                              leading=19))
        self.row = max(ends) + 12
        self.rule(1)

    # ---------------------------------------------------------- also-today
    def also(self):
        d = self.pen
        self.row += 10
        self.row = _tag(d, EDGE, self.row, "ALSO TODAY", PALETTE["navy"])
        half = (self.span - 24) // 2
        left_items = [
            ("BERLIN", "Gen Z protests spread across 25 European countries."),
            ("GAZA", "Israeli strikes kill Palestinians in Gaza."),
        ]
        right_items = [
            ("WALL STREET", "Anthropic debuts as a $2 trillion company."),
            ("HORMUZ", "Two tankers hit mines in the Strait of Hormuz."),
        ]
        bottom = self.row
        for col_x, items in ((EDGE, left_items),
                             (EDGE + half + 24, right_items)):
            yy = self.row
            for label, text in items:
                prefix = "▪  " + label + " — "
                d.text((col_x, yy), prefix, font=typeface("sans_bold", 13),
                       fill=PALETTE["navy"])
                lx = col_x + d.textlength(prefix,
                                          font=typeface("sans_bold", 13))
                end_y = _para(d, (lx, yy), text, typeface("sans", 13),
                              half - (lx - col_x), PALETTE["ink"], leading=18)
                yy = max(end_y, yy + 20) + 2
            bottom = max(bottom, yy)
        self.row = bottom

    # ---------------------------------------------------------------- footer
    def footer(self):
        d = self.pen
        self.row += 8
        self.rule(1)
        self.row += 8
        d.text((EDGE, self.row),
               "Sources: AP, NYT, The Times, Reuters — 21 Nov 2026.",
               font=typeface("sans", 11), fill=PALETTE["grey"])
        self.row += 16
        d.text((EDGE, self.row),
               "Built by a deterministic Python program. No live data at "
               "runtime; all facts embedded above.",
               font=typeface("sans", 11), fill=PALETTE["grey"])

    def build(self):
        self.masthead()
        self.lead()
        self.pair()
        self.trio()
        self.also()
        self.footer()
        return self.sheet


# --------------------------------------------------------------------- main
def _render_png():
    """Render the front page and return the PNG bytes."""
    page = FrontPage()
    img = page.build()
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def main():
    data = _render_png()
    here = os.path.dirname(os.path.abspath(__file__))
    dests = [os.path.join(here, "output", "entry.png")]
    try:
        os.makedirs("/output", exist_ok=True)
        dests.append("/output/entry.png")
    except OSError:
        pass
    done = False
    for path in dests:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as fh:
                fh.write(data)
            print("wrote {} ({} bytes)".format(path, len(data)))
            done = True
        except OSError as exc:
            # The grader mounts the repo read-only, so writing next to the
            # program fails there; /output is still written below.
            print("could not write {}: {}".format(path, exc))
    if not done:
        raise SystemExit("failed to write entry.png to any target")


if __name__ == "__main__":
    main()
