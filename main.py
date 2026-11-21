#!/usr/bin/env python3
"""THE WORLD TODAY - Saturday 21 November 2026.

A program that draws one newspaper front page summing up the world news
of Saturday 21 November 2026 and writes it to /output/entry.png.

Pure standard library: the raster canvas, the 5x7 bitmap font and the PNG
encoder are all written here, so the program runs with nothing installed.
The output is fully deterministic: the same bytes on every run.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (248, 243, 232)
INK = (25, 21, 18)
RED = (158, 27, 27)
NAVY = (29, 47, 77)
NAVY_DARK = (18, 30, 52)
GOLD = (176, 132, 30)
GREY = (110, 104, 92)
LIGHT = (233, 226, 210)
WHITE = (250, 248, 243)

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 cells, '#' = on, '.' = off.
# ---------------------------------------------------------------------------
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '\u00b7': ("00000", "00000", "00000", "01100", "01100", "00000", "00000"),
}

CHAR_W = 6  # 5 glyph cells + 1 spacing, in font units


def text_width(text, scale):
    """Width in pixels of text drawn at the given scale."""
    return len(text) * CHAR_W * scale - scale


def draw_text(px, x, y, scale, color, text):
    """Draw one line of text (uppercased) at font scale `scale`."""
    for ci, ch in enumerate(text.upper()):
        glyph = FONT.get(ch, FONT[' '])
        cx = x + ci * CHAR_W * scale
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    fill_rect(px, cx + col * scale, y + row * scale,
                              scale, scale, color)


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.upper().split(' ')
    lines, cur = [], ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(px, x, y, scale, color, text, max_width, line_gap=4):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    lines = wrap_text(text, scale, max_width)
    for i, line in enumerate(lines):
        draw_text(px, x, y + i * (7 * scale + line_gap), scale, color, line)
    return y + len(lines) * (7 * scale + line_gap)


# ---------------------------------------------------------------------------
# Raster canvas
# ---------------------------------------------------------------------------
def new_canvas():
    px = bytearray(W * H * 3)
    for i in range(0, len(px), 3):
        px[i], px[i + 1], px[i + 2] = PAPER
    return px


def set_px(px, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def fill_rect(px, x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i], px[i + 1], px[i + 2] = color


def draw_line(px, x0, y0, x1, y1, color, thick=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        fill_rect(px, x - thick // 2, y - thick // 2, thick, thick, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def fill_circle(px, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(px, xx, yy, color)


def draw_circle(px, cx, cy, r, color, thick=2):
    for a in range(360):
        import math
        x = int(cx + r * math.cos(math.radians(a)))
        y = int(cy + r * math.sin(math.radians(a)))
        fill_rect(px, x - thick // 2, y - thick // 2, thick, thick, color)


def fill_poly(px, points, color):
    """Scanline fill of a simple polygon (list of (x, y))."""
    if not points:
        return
    ys = [p[1] for p in points]
    for y in range(max(0, min(ys)), min(H, max(ys)) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for j in range(0, len(xs) - 1, 2):
            for x in range(max(0, int(xs[j])), min(W, int(xs[j + 1]) + 1)):
                set_px(px, x, y, color)


def star_points(cx, cy, r_outer, r_inner, spikes=8):
    import math
    pts = []
    for i in range(spikes * 2):
        r = r_outer if i % 2 == 0 else r_inner
        a = math.pi * i / spikes - math.pi / 2
        pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
    return pts


# ---------------------------------------------------------------------------
# PNG encoder (pure stdlib, filter 0 rows, zlib level 9)
# ---------------------------------------------------------------------------
def _chunk(kind, data):
    out = struct.pack('>I', len(data)) + kind + data
    out += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(px, path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(px[y * W * 3:(y + 1) * W * 3])
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    data = (b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', ihdr)
            + _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + _chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(data)
    return len(data)


# ---------------------------------------------------------------------------
# Illustrations
# ---------------------------------------------------------------------------
def draw_lead_scene(px, x, y, w, h):
    """Night sky over Poland: missile trails arc down to bursts on the
    horizon, with a NATO compass star in the corner."""
    fill_rect(px, x, y, w, h, NAVY_DARK)
    # stars
    for sx, sy, r in [(x + 30, y + 26, 2), (x + 90, y + 60, 1), (x + 150, y + 20, 2),
                      (x + 220, y + 48, 1), (x + 300, y + 24, 2), (x + 360, y + 70, 1),
                      (x + 60, y + 100, 1), (x + 260, y + 110, 1), (x + 330, y + 130, 2)]:
        fill_circle(px, sx, sy, r, WHITE)
    # moon
    fill_circle(px, x + w - 52, y + 44, 22, (240, 230, 200))
    fill_circle(px, x + w - 60, y + 38, 18, NAVY_DARK)
    # ground silhouette
    fill_poly(px, [(x, y + h), (x, y + h - 58), (x + 90, y + h - 88),
                   (x + 190, y + h - 62), (x + 300, y + h - 96),
                   (x + w, y + h - 70), (x + w, y + h)], (12, 20, 36))
    # missile trails arcing down to the horizon
    draw_line(px, x + 60, y + 30, x + 150, y + h - 96, (255, 210, 90), 3)
    draw_line(px, x + 60, y + 30, x + 150, y + h - 96, (255, 240, 180), 1)
    draw_line(px, x + 260, y + 18, x + 210, y + h - 78, (255, 210, 90), 3)
    draw_line(px, x + 260, y + 18, x + 210, y + h - 78, (255, 240, 180), 1)
    # missile heads
    fill_circle(px, x + 60, y + 30, 5, (255, 240, 180))
    fill_circle(px, x + 260, y + 18, 5, (255, 240, 180))
    # explosion bursts where the missiles land
    for bx, by, r in [(x + 150, y + h - 96, 34), (x + 210, y + h - 78, 26)]:
        fill_poly(px, star_points(bx, by, r, r // 2, 8), (255, 120, 40))
        fill_poly(px, star_points(bx, by, r // 2, r // 4, 8), (255, 210, 90))
    # NATO compass star badge, top-left corner
    bx, by = x + 46, y + 150
    draw_circle(px, bx, by, 30, WHITE, 3)
    fill_poly(px, star_points(bx, by, 26, 7, 4), WHITE)
    fill_circle(px, bx, by, 6, NAVY_DARK)
    draw_text(px, bx - 24, by + 38, 2, WHITE, "NATO")
    # caption strip
    fill_rect(px, x, y + h - 30, w, 30, (12, 20, 36))
    draw_text(px, x + 12, y + h - 22, 2, WHITE,
              "POLAND - NEAR THE UKRAINE BORDER")


def draw_scales(px, x, y, s):
    """Scales of justice icon, drawn in INK at scale s."""
    cx = x + 22 * s
    draw_line(px, cx, y, cx, y + 34 * s, INK, 2 * s)
    draw_line(px, cx - 18 * s, y + 6 * s, cx + 18 * s, y + 6 * s, INK, 2 * s)
    draw_line(px, cx - 18 * s, y + 6 * s, cx - 26 * s, y + 20 * s, INK, 2 * s)
    draw_line(px, cx - 18 * s, y + 6 * s, cx - 10 * s, y + 20 * s, INK, 2 * s)
    draw_line(px, cx + 18 * s, y + 6 * s, cx + 10 * s, y + 20 * s, INK, 2 * s)
    draw_line(px, cx + 18 * s, y + 6 * s, cx + 26 * s, y + 20 * s, INK, 2 * s)
    fill_poly(px, [(cx - 26 * s, y + 20 * s), (cx - 10 * s, y + 20 * s),
                   (cx - 18 * s, y + 30 * s)], INK)
    fill_poly(px, [(cx + 10 * s, y + 20 * s), (cx + 26 * s, y + 20 * s),
                   (cx + 18 * s, y + 30 * s)], INK)
    fill_rect(px, cx - 14 * s, y + 34 * s, 28 * s, 3 * s, INK)
    fill_rect(px, x, y + 40 * s, 44 * s, 2 * s, RED)


def draw_chart(px, x, y, s):
    """Falling market bars with a red down arrow."""
    heights = [30, 26, 24, 18, 12, 8]
    for i, hh in enumerate(heights):
        fill_rect(px, x + i * 8 * s, y + 34 * s - hh * s, 5 * s, hh * s,
                  INK if i < 3 else RED)
    draw_line(px, x, y + 2 * s, x + 46 * s, y + 30 * s, RED, 3 * s)
    fill_poly(px, [(x + 46 * s, y + 30 * s), (x + 36 * s, y + 26 * s),
                   (x + 44 * s, y + 38 * s)], RED)
    fill_rect(px, x, y + 40 * s, 44 * s, 2 * s, RED)


def draw_flags(px, x, y, s):
    """Three small flags on poles: US, China, Russia (abstract marks)."""
    cols = [(178, 34, 52), (222, 41, 16), (0, 57, 166)]
    for i, c in enumerate(cols):
        fx = x + i * 16 * s
        draw_line(px, fx, y, fx, y + 34 * s, INK, 2 * s)
        fill_rect(px, fx + 2 * s, y, 12 * s, 9 * s, c)
        fill_rect(px, fx + 2 * s, y + 9 * s, 12 * s, 3 * s, WHITE)
        fill_rect(px, fx + 2 * s, y + 12 * s, 12 * s, 3 * s, c)
    fill_rect(px, x, y + 40 * s, 44 * s, 2 * s, RED)


def draw_cyclone(px, x, y, s):
    """Spiral storm: concentric arcs with rain slashes."""
    import math
    cx, cy = x + 22 * s, y + 18 * s
    for r in (6 * s, 11 * s, 16 * s):
        for a in range(0, 300, 4):
            px_x = int(cx + r * math.cos(math.radians(a)))
            px_y = int(cy + r * math.sin(math.radians(a)))
            fill_rect(px, px_x, px_y, 2 * s, 2 * s, NAVY)
    fill_circle(px, cx, cy, 3 * s, RED)
    for rx in (x + 2 * s, x + 16 * s, x + 34 * s):
        draw_line(px, rx, y + 34 * s, rx - 3 * s, y + 40 * s, NAVY, 2 * s)
    fill_rect(px, x, y + 44 * s, 44 * s, 2 * s, RED)


def draw_eu_stars(px, x, y, s):
    """Circle of twelve stars (EU) with a small Union Jack cross."""
    import math
    cx, cy = x + 22 * s, y + 18 * s
    draw_circle(px, cx, cy, 17 * s, GOLD, 2 * s)
    for k in range(12):
        a = math.radians(k * 30 - 90)
        sx = int(cx + 12 * s * math.cos(a))
        sy = int(cy + 12 * s * math.sin(a))
        fill_poly(px, star_points(sx, sy, 3 * s, 1 * s, 5), GOLD)
    fill_rect(px, x + 30 * s, y + 26 * s, 14 * s, 3 * s, RED)
    fill_rect(px, x + 36 * s, y + 20 * s, 3 * s, 14 * s, RED)
    fill_rect(px, x, y + 40 * s, 44 * s, 2 * s, RED)


def draw_globe(px, x, y, s):
    """Globe with latitude lines and a leaf."""
    cx, cy = x + 22 * s, y + 18 * s
    draw_circle(px, cx, cy, 16 * s, NAVY, 2 * s)
    draw_line(px, cx - 16 * s, cy, cx + 16 * s, cy, NAVY, 2 * s)
    draw_line(px, cx, cy - 16 * s, cx, cy + 16 * s, NAVY, 2 * s)
    for dy in (-8 * s, 8 * s):
        draw_line(px, cx - 13 * s, cy + dy, cx + 13 * s, cy + dy, NAVY, 2 * s)
    fill_poly(px, [(x + 36 * s, y + 8 * s), (x + 44 * s, y + 16 * s),
                   (x + 36 * s, y + 24 * s), (x + 30 * s, y + 16 * s)],
              (46, 125, 50))
    fill_rect(px, x, y + 40 * s, 44 * s, 2 * s, RED)


# ---------------------------------------------------------------------------
# Front-page layout
# ---------------------------------------------------------------------------
def story_card(px, x, y, w, icon_fn, kicker, headline, body):
    """One small story: icon, kicker, headline, body text."""
    icon_fn(px, x + 4, y + 6, 1)
    draw_text(px, x + 58, y + 10, 2, RED, kicker)
    draw_line(px, x, y + 52, x + w, y + 52, LIGHT, 2)
    yy = draw_para(px, x, y + 62, 3, INK, headline, w, line_gap=3)
    draw_para(px, x, yy + 6, 2, (60, 54, 46), body, w, line_gap=3)


def build_page():
    px = new_canvas()
    mx = 28  # margin
    right = W - mx

    # ---- masthead ------------------------------------------------------
    fill_rect(px, mx, 22, right - mx, 3, INK)
    title = "THE WORLD TODAY"
    tw = text_width(title, 9)
    draw_text(px, (W - tw) // 2, 34, 9, INK, title)
    fill_rect(px, mx, 104, right - mx, 3, INK)
    fill_rect(px, mx, 110, right - mx, 1, INK)
    date_line = "SATURDAY 21 NOVEMBER 2026"
    draw_text(px, mx, 120, 2, INK, date_line)
    tag = "ONE DAY IN ONE IMAGE"
    draw_text(px, right - text_width(tag, 2), 120, 2, RED, tag)

    # ---- lead story ----------------------------------------------------
    ly = 150
    lx = mx
    lw = 520
    draw_text(px, lx, ly, 2, RED, "WAR IN EUROPE - POLAND")
    draw_para(px, lx, ly + 26, 5, INK, "MISSILES FALL ON POLAND", lw, line_gap=6)
    sub = draw_para(px, lx, ly + 118, 3, (60, 54, 46),
                    "NATO CALLS IT A GRAVE VIOLATION AS THE WAR SPILLS OVER THE BORDER",
                    lw, line_gap=4)
    draw_para(px, lx, sub + 10, 2, INK,
              "TWO RUSSIAN MISSILES AND A SUSPECTED DRONE CAME DOWN IN POLAND. "
              "WARSAW CALLED IT A DELIBERATE PROVOCATION AND NATO CALLED IT A "
              "GRAVE VIOLATION OF ALLIED AIRSPACE, AS THE WAR IN UKRAINE "
              "REACHES A NATO ALLY.", lw, line_gap=4)
    draw_lead_scene(px, lx + lw + 20, ly, right - (lx + lw + 20), 330)

    # ---- divider + section head ---------------------------------------
    fill_rect(px, mx, 502, right - mx, 2, INK)
    draw_text(px, mx, 516, 2, INK, "THE DAY IN BRIEF - SIX MORE STORIES")
    draw_text(px, right - text_width("SATURDAY 21 NOVEMBER 2026", 2), 516, 2,
              GREY, "SATURDAY 21 NOVEMBER 2026")

    # ---- grid of six stories ------------------------------------------
    col_w = 306
    gap = 25
    cols = [mx, mx + col_w + gap, mx + 2 * (col_w + gap)]
    row1, row2 = 544, 772
    story_card(px, cols[0], row1, col_w, draw_scales, "THE HAGUE - WORLD COURT",
               "MYANMAR GUILTY OF GENOCIDE",
               "THE ICJ RULED MYANMAR COMMITTED GENOCIDE AGAINST THE ROHINGYA "
               "IN 2017, THE FIRST TIME A STATE HAS BEEN HELD LIABLE.")
    story_card(px, cols[1], row1, col_w, draw_chart, "WALL STREET",
               "STOCKS SLIDE INTO CORRECTION",
               "THE S&P 500 AND THE DOW FELL ABOUT 3.7 PERCENT AS AI SHARES "
               "SOLD OFF, PUSHING THE BENCHMARKS INTO CORRECTION.")
    story_card(px, cols[2], row1, col_w, draw_flags, "SHENZHEN - SUMMIT",
               "THREE LEADERS, FEW RESULTS",
               "TRUMP, XI AND PUTIN LEFT THE FIRST TRILATERAL SUMMIT WITH FEW "
               "CONCRETE RESULTS AFTER TALKS IN SHENZHEN.")
    story_card(px, cols[0], row2, col_w, draw_cyclone, "INDIA - WEATHER",
               "CYCLONE AKVAN SLAMS THE COAST",
               "SEVERE CYCLONE AKVAN CROSSED THE ODISHA AND ANDHRA PRADESH "
               "COAST NEAR GOPALPUR, WITH 300,000 PEOPLE EVACUATED.")
    story_card(px, cols[1], row2, col_w, draw_eu_stars, "BRUSSELS",
               "UK AND EU SIGN NEW DEALS",
               "BRITAIN AND THE EU SIGNED DEALS ON FOOD TRADE, CARBON MARKETS "
               "AND YOUTH MOBILITY AT A SUMMIT IN BRUSSELS.")
    story_card(px, cols[2], row2, col_w, draw_globe, "TURKEY - CLIMATE",
               "CLIMATE TALKS IN FINAL STRETCH",
               "NEGOTIATORS AT THE COP31 SUMMIT IN TURKEY PRESSED ON IN A "
               "CRUCIAL FINAL STAGE, WITH FOSSIL FUELS AND FINANCE UNRESOLVED.")

    # ---- footer ---------------------------------------------------------
    fill_rect(px, mx, 996, right - mx, 2, INK)
    foot = "THE WORLD TODAY - SATURDAY 21 NOVEMBER 2026 - SEVEN STORIES FROM ONE DAY"
    draw_text(px, (W - text_width(foot, 2)) // 2, 1006, 2, GREY, foot)
    return px


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    px = build_page()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(px, path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
