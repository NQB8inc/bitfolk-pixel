#!/usr/bin/env python3
"""Builds Bitfolk Pixel from the glyph grids below.

    python3 source/build.py

Needs fonttools and brotli (pip install fonttools brotli). Writes fonts/BitfolkPixel.ttf, .otf and .woff2 next to this
folder. Inside the Bitfolk repository it also refreshes the copies the website serves (apps/web).

Each glyph is drawn on a grid: `#` is ink, `.` is blank. Rows 0-6 sit on the baseline (capitals are 7 tall, lowercase
x-height is rows 2-6) and rows 7-8, when present, hang below it. One blank row above the capitals completes a 10 row
em, so the font is crisp at any multiple of 10px. The letters b, i, t, f, o, l and k are the ones in the Bitfolk
wordmark; the rest are drawn to match them. Accented letters are composed from a base letter and a mark (see ACCENTS);
marks on capitals rise above the em.

Bitfolk Pixel is released under the SIL Open Font License 1.1 (OFL.txt).
"""
import json
import os
import zipfile
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

PX = 100  # font units per pixel
UPM = 1000
ASCENT_ROWS = 8  # 7 rows of capital plus one blank row
DESCENT_ROWS = 2

VERSION = "1.100"
# A fixed build date, so the same glyphs always produce the same bytes.
os.environ.setdefault("SOURCE_DATE_EPOCH", "1767225600")
PKG = Path(__file__).resolve().parents[1]
COPYRIGHT = (PKG / "OFL.txt").read_text().splitlines()[0]  # the licence file holds the copyright line

G = {}
# Row index of a glyph's first row, when it is not 0. Negative for marks that rise above the capitals.
TOP = {}


def g(chars, *rows):
    for ch in chars:
        G[ch] = list(rows)


# Capitals
g("A", ".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
g("B", "####.", "#...#", "#...#", "####.", "#...#", "#...#", "####.")
g("C", ".###.", "#...#", "#....", "#....", "#....", "#...#", ".###.")
g("D", "####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####.")
g("E", "#####", "#....", "#....", "####.", "#....", "#....", "#####")
g("F", "#####", "#....", "#....", "####.", "#....", "#....", "#....")
g("G", ".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###.")
g("H", "#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
g("I", "###", ".#.", ".#.", ".#.", ".#.", ".#.", "###")
g("J", "..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##..")
g("K", "#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#")
g("L", "#....", "#....", "#....", "#....", "#....", "#....", "#####")
g("M", "#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#")
g("N", "#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#")
g("O", ".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.")
g("P", "####.", "#...#", "#...#", "####.", "#....", "#....", "#....")
g("Q", ".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#")
g("R", "####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#")
g("S", ".####", "#....", "#....", ".###.", "....#", "....#", "####.")
g("T", "#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..")
g("U", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.")
g("V", "#...#", "#...#", "#...#", "#...#", ".#.#.", ".#.#.", "..#..")
g("W", "#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#")
g("X", "#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#")
g("Y", "#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..")
g("Z", "#####", "....#", "...#.", "..#..", ".#...", "#....", "#####")

# Lowercase
g("a", ".....", ".....", ".###.", "....#", ".####", "#...#", ".####")
g("b", "#....", "#....", "####.", "#...#", "#...#", "#...#", "####.")
g("c", "....", "....", ".###", "#...", "#...", "#...", ".###")
g("d", "....#", "....#", ".####", "#...#", "#...#", "#...#", ".####")
g("e", ".....", ".....", ".###.", "#...#", "#####", "#....", ".###.")
g("f", "..##", ".#..", "####", ".#..", ".#..", ".#..", ".#..")
g("g", ".....", ".....", ".####", "#...#", "#...#", "#...#", ".####", "....#", ".###.")
g("h", "#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#")
g("i", "#", ".", "#", "#", "#", "#", "#")
g("j", "..#", "...", "..#", "..#", "..#", "..#", "..#", "..#", "##.")
g("k", "#...", "#...", "#..#", "#.#.", "##..", "#.#.", "#..#")
g("l", "#.", "#.", "#.", "#.", "#.", "#.", ".#")
g("m", ".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#")
g("n", ".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#")
g("o", ".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###.")
g("p", ".....", ".....", "####.", "#...#", "#...#", "#...#", "####.", "#....", "#....")
g("q", ".....", ".....", ".####", "#...#", "#...#", "#...#", ".####", "....#", "....#")
g("r", "....", "....", "#.##", "##..", "#...", "#...", "#...")
g("s", ".....", ".....", ".####", "#....", ".###.", "....#", "####.")
g("t", ".#..", ".#..", "####", ".#..", ".#..", ".#..", "..##")
g("u", ".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####")
g("v", ".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#..")
g("w", ".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#.")
g("x", ".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#")
g("y", ".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####", "....#", ".###.")
g("z", ".....", ".....", "#####", "...#.", "..#..", ".#...", "#####")

# Figures, all one width so numbers line up in tables
g("0", ".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###.")
g("1", "..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###.")
g("2", ".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####")
g("3", ".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###.")
g("4", "...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#.")
g("5", "#####", "#....", "####.", "....#", "....#", "#...#", ".###.")
g("6", ".###.", "#....", "#....", "####.", "#...#", "#...#", ".###.")
g("7", "#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#..")
g("8", ".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###.")
g("9", ".###.", "#...#", "#...#", ".####", "....#", "....#", ".###.")

# Punctuation and symbols
g("  ", "...", "...", "...", "...", "...", "...", "...")
g("!", "#", "#", "#", "#", "#", ".", "#")
g('"', "#.#", "#.#", "...", "...", "...", "...", "...")
g("#", ".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#.")
g("$", "..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#..")
g("%", "##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##")
g("&", ".##..", "#..#.", "#..#.", ".##..", "#.#.#", "#..#.", ".##.#")
g("'", "#", "#", ".", ".", ".", ".", ".")
g("(", ".#", "#.", "#.", "#.", "#.", "#.", ".#")
g(")", "#.", ".#", ".#", ".#", ".#", ".#", "#.")
g("*", "...", "#.#", ".#.", "#.#", "...", "...", "...")
g("+", ".....", "..#..", "..#..", "#####", "..#..", "..#..", ".....")
g(",", "..", "..", "..", "..", "..", "..", ".#", "#.", "..")
g("-", "...", "...", "...", "...", "###", "...", "...")
g(".", ".", ".", ".", ".", ".", ".", "#")
g("/", "..#", "..#", ".#.", ".#.", ".#.", "#..", "#..")
g(":", ".", ".", ".", "#", ".", ".", "#")
g(";", "..", "..", "..", ".#", "..", "..", ".#", "#.", "..")
g("<", "...#", "..#.", ".#..", "#...", ".#..", "..#.", "...#")
g("=", "....", "....", "####", "....", "####", "....", "....")
g(">", "#...", ".#..", "..#.", "...#", "..#.", ".#..", "#...")
g("?", ".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#..")
g("@", ".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###.")
g("[", "##", "#.", "#.", "#.", "#.", "#.", "##")
g("\\", "#..", "#..", ".#.", ".#.", ".#.", "..#", "..#")
g("]", "##", ".#", ".#", ".#", ".#", ".#", "##")
g("^", ".#.", "#.#", "...", "...", "...", "...", "...")
g("_", ".....", ".....", ".....", ".....", ".....", ".....", ".....", "#####", ".....")
g("`", "#.", ".#", "..", "..", "..", "..", "..")
g("{", "..#", ".#.", ".#.", "#..", ".#.", ".#.", "..#")
g("|", "#", "#", "#", "#", "#", "#", "#")
g("}", "#..", ".#.", ".#.", "..#", ".#.", ".#.", "#..")
g("~", ".....", ".....", ".....", ".#..#", "#.##.", ".....", ".....")
g("–", "....", "....", "....", "....", "####", "....", "....")  # en dash
g("—", "......", "......", "......", "......", "######", "......", "......")  # em dash
g("‘", ".#", "#.", "#.", "..", "..", "..", "..")
g("’", ".#", ".#", "#.", "..", "..", "..", "..")
g("“", ".#.#", "#.#.", "#.#.", "....", "....", "....", "....")
g("”", ".#.#", ".#.#", "#.#.", "....", "....", "....", "....")
g("…", ".....", ".....", ".....", ".....", ".....", ".....", "#.#.#")
g("·", ".", ".", ".", ".", "#", ".", ".")  # middle dot
g("•", "..", "..", "..", "##", "##", "..", "..")  # bullet
g("×", "...", "...", "...", "#.#", ".#.", "#.#", "...")  # multiplication sign
g("→", ".....", ".....", "..#..", "...#.", "#####", "...#.", "..#..")
g("←", ".....", ".....", "..#..", ".#...", "#####", ".#...", "..#..")
g("↑", ".....", "..#..", ".###.", "#.#.#", "..#..", "..#..", "..#..")
g("↓", ".....", "..#..", "..#..", "..#..", "#.#.#", ".###.", "..#..")
g("✓", ".....", ".....", "....#", "...#.", "#.#..", ".#...", ".....")  # check mark

# More Latin: letters that are not a base plus a mark
g("Æ", ".######", "#..#...", "#..#...", "#####..", "#..#...", "#..#...", "#..####")  # AE
g("æ", ".......", ".......", ".##.##.", "...#..#", ".######", "#..#...", ".##.###")  # ae
g("Œ", ".######", "#..#...", "#..#...", "#..###.", "#..#...", "#..#...", ".######")  # OE
g("œ", ".......", ".......", ".##.##.", "#..#..#", "#..####", "#..#...", ".##.###")  # oe
g("Ø", ".####.", "#...##", "#..#.#", "#..#.#", "#.#..#", "##...#", ".####.")  # O slash
g("ø", ".....", ".....", ".###.", "#..##", "#.#.#", "##..#", ".###.")  # o slash
g("Ð", ".####.", ".#...#", ".#...#", "###..#", ".#...#", ".#...#", ".####.")  # Eth
g("ð", "..#.#", "...#.", "..#.#", ".####", "#...#", "#...#", ".###.")  # eth
g("Þ", "#....", "####.", "#...#", "#...#", "####.", "#....", "#....")  # Thorn
g("þ", "#....", "#....", "####.", "#...#", "#...#", "#...#", "####.", "#....", "#....")  # thorn
g("ß", ".##..", "#..#.", "#..#.", "#.#..", "#..#.", "#...#", "#.##.")  # sharp s

# More symbols
g("¡", ".", ".", "#", ".", "#", "#", "#", "#", "#")  # inverted !
g("¿", ".....", ".....", "..#..", ".....", "..#..", ".#...", "#....", "#...#", ".###.")  # inverted ?
g("«", "....", "....", "....", ".#.#", "#.#.", ".#.#", "....")
g("»", "....", "....", "....", "#.#.", ".#.#", "#.#.", "....")
g("€", "..###", ".#...", "####.", ".#...", "####.", ".#...", "..###")  # euro
g("£", "..##.", ".#..#", ".#...", "####.", ".#...", ".#...", "#####")  # pound
g("¥", "#...#", "#...#", ".#.#.", "#####", "..#..", "#####", "..#..")  # yen
g("©", ".#####.", "#.....#", "#..##.#", "#.#...#", "#..##.#", "#.....#", ".#####.")  # copyright
g("°", ".#.", "#.#", ".#.", "...", "...", "...", "...")  # degree
g("±", ".....", "..#..", ".###.", "..#..", ".....", ".###.", ".....")  # plus-minus
g("−", ".....", ".....", ".....", "#####", ".....", ".....", ".....")  # minus

# Marks are three rows: the mark, then (for all but the ring) a blank row between it and the letter.
MARKS = {
    "grave": ("#..", ".#.", "..."),
    "acute": ("..#", ".#.", "..."),
    "circumflex": (".#.", "#.#", "..."),
    "tilde": (".#.#", "#.#.", "...."),
    "dieresis": ("...", "#.#", "..."),
    "ring": (".#.", "#.#", ".#."),
    "caron": ("#.#", ".#.", "..."),
}
CEDILLA = ("..#", ".#.")  # hangs in the two rows below the baseline

ACCENTS = {
    "grave": "AEIOUaeiou",
    "acute": "AEIOUYaeiouy",
    "circumflex": "AEIOUaeiou",
    "tilde": "ANOano",
    "dieresis": "AEIOUYaeiouy",
    "ring": "Aa",
    "caron": "SZsz",
}
COMPOSED = {
    "grave": "ÀÈÌÒÙàèìòù",
    "acute": "ÁÉÍÓÚÝáéíóúý",
    "circumflex": "ÂÊÎÔÛâêîôû",
    "tilde": "ÃÑÕãñõ",
    "dieresis": "ÄËÏÖÜŸäëïöüÿ",
    "ring": "Åå",
    "caron": "ŠŽšž",
}


def pad(rows, width):
    """Centres rows in a wider box."""
    extra = width - len(rows[0])
    left = extra // 2
    return ["." * left + r + "." * (extra - left) for r in rows]


def compose():
    for mark, bases in ACCENTS.items():
        for base, ch in zip(bases, COMPOSED[mark]):
            rows = list(G[base])
            if base in "ij":
                rows[0] = rows[1] = "." * len(rows[0])  # the mark replaces the dot
            m = MARKS[mark]
            width = max(len(rows[0]), len(m[0]))
            rows, m = pad(rows, width), pad(list(m), width)
            if base.isupper():
                G[ch], TOP[ch] = m + rows, -3
            else:
                # Lowercase marks sit in the blank row above the capitals and the rows over the x-height.
                letter = rows[2:]
                top = [a if "#" in a else b for a, b in zip(m[1:], rows[:2])]
                G[ch], TOP[ch] = [m[0]] + top + letter, -1
    for base, ch in (("C", "Ç"), ("c", "ç")):
        rows = list(G[base])
        width = len(rows[0])
        G[ch] = rows + pad(list(CEDILLA), width)


compose()


def outline(ch):
    """Traces the union of the inked pixels as closed clockwise loops, so a glyph is one clean shape, not a pile of
    squares with seams between them."""
    edges = set()
    for r, row in enumerate(G[ch], TOP.get(ch, 0)):
        for c, cell in enumerate(row):
            if cell != "#":
                continue
            x0, x1 = c * PX, (c + 1) * PX
            y1 = (7 - r) * PX
            y0 = y1 - PX
            for edge in (((x0, y0), (x0, y1)), ((x0, y1), (x1, y1)), ((x1, y1), (x1, y0)), ((x1, y0), (x0, y0))):
                back = (edge[1], edge[0])
                if back in edges:
                    edges.remove(back)
                else:
                    edges.add(edge)
    out = {}
    for a, b in sorted(edges):
        out.setdefault(a, []).append(b)
    loops = []
    while out:
        start = next(iter(out))
        loop, at = [start], start
        while True:
            nxt = out[at].pop()
            if not out[at]:
                del out[at]
            if nxt == start:
                break
            loop.append(nxt)
            at = nxt
        # Drop points in the middle of a straight run.
        n = len(loop)
        corners = [
            p for i, p in enumerate(loop)
            if (p[0] - loop[i - 1][0]) * (loop[(i + 1) % n][1] - p[1]) != (p[1] - loop[i - 1][1]) * (loop[(i + 1) % n][0] - p[0])
        ]
        loops.append(corners)
    return loops


def draw(pen, ch, reverse=False):
    for loop in outline(ch):
        if reverse:  # CFF outlines wind the other way from TrueType ones
            loop = loop[::-1]
        pen.moveTo(loop[0])
        for p in loop[1:]:
            pen.lineTo(p)
        pen.closePath()


def name_of(ch):
    return "space" if ch == " " else f"uni{ord(ch):04X}"


NOTDEF = "￾"  # a private key for the missing-glyph box; never mapped to a character
G[NOTDEF] = ["#####", "#...#", "#...#", "#...#", "#...#", "#...#", "#####"]


def make(chars, cff):
    order = [".notdef"] + [name_of(c) for c in chars]
    names = {NOTDEF: ".notdef", **{c: name_of(c) for c in chars}}
    # One blank column after every glyph is the letter spacing.
    widths = {names[c]: (len(G[c][0]) + 1) * PX for c in names}
    top_row = min(TOP.values(), default=0)

    fb = FontBuilder(UPM, isTTF=not cff)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({ord(c): name_of(c) for c in chars})
    if cff:
        strings = {}
        for c, n in names.items():
            pen = T2CharStringPen(widths[n], None)
            draw(pen, c, reverse=True)
            strings[n] = pen.getCharString()
        fb.setupCFF("BitfolkPixel-Regular", {"FullName": "Bitfolk Pixel", "FamilyName": "Bitfolk Pixel", "Weight": "Regular"}, strings, {})
    else:
        glyphs = {}
        for c, n in names.items():
            pen = TTGlyphPen(None)
            draw(pen, c)
            glyphs[n] = pen.glyph()
        fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics({n: (w, 0) for n, w in widths.items()})
    fb.setupHorizontalHeader(ascent=ASCENT_ROWS * PX, descent=-DESCENT_ROWS * PX)
    fb.setupNameTable({
        "familyName": "Bitfolk Pixel",
        "styleName": "Regular",
        "uniqueFontIdentifier": f"Bitfolk Pixel Regular {VERSION}",
        "fullName": "Bitfolk Pixel",
        "psName": "BitfolkPixel-Regular",
        "version": f"Version {VERSION}",
        "copyright": COPYRIGHT,
        "manufacturer": "Bitfolk",
        "designer": "Bitfolk",
        "vendorURL": "https://bitfolk.ai",
        "designerURL": "https://bitfolk.ai/font",
        "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://openfontlicense.org",
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupOS2(
        sTypoAscender=ASCENT_ROWS * PX, sTypoDescender=-DESCENT_ROWS * PX, sTypoLineGap=0,
        # Marks on capitals rise above the em; the Windows ascent covers them so they are never clipped.
        usWinAscent=(7 - top_row) * PX, usWinDescent=DESCENT_ROWS * PX,
        version=4, sxHeight=5 * PX, sCapHeight=7 * PX, achVendID="BTFK", fsSelection=0x40 | 0x80, fsType=0,
    )
    fb.setupPost(underlinePosition=-PX, underlineThickness=PX)
    return fb.font


def build():
    for ch, rows in G.items():
        assert len({len(r) for r in rows}) == 1, f"{ch!r} has uneven rows"
        assert TOP.get(ch, 0) + len(rows) in (7, 9), f"{ch!r} ends on row {TOP.get(ch, 0) + len(rows)}"

    chars = sorted(c for c in G if c != NOTDEF)
    out = PKG / "fonts"
    out.mkdir(exist_ok=True)
    make(chars, cff=False).save(out / "BitfolkPixel.ttf")
    make(chars, cff=True).save(out / "BitfolkPixel.otf")
    web = TTFont(out / "BitfolkPixel.ttf")
    web.flavor = "woff2"
    web.save(out / "BitfolkPixel.woff2")
    for f in sorted(out.iterdir()):
        print(f"{f.name}: {f.stat().st_size} bytes")
    print(f"{len(chars)} glyphs")

    site = PKG.parents[1] / "apps/web"
    if site.is_dir():
        publish(site, out, chars)


def publish(site: Path, out: Path, chars):
    """Refreshes the website's copies: the font it loads, the downloads on /font and the character list shown there."""
    public = site / "public/font"
    public.mkdir(parents=True, exist_ok=True)
    files = [out / "BitfolkPixel.ttf", out / "BitfolkPixel.otf", out / "BitfolkPixel.woff2", PKG / "OFL.txt"]
    for f in files:
        (public / f.name).write_bytes(f.read_bytes())
    (site / "app/fonts/BitfolkPixel.woff2").write_bytes((out / "BitfolkPixel.woff2").read_bytes())
    with zipfile.ZipFile(public / "BitfolkPixel.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            info = zipfile.ZipInfo(f"BitfolkPixel/{f.name}", date_time=(2026, 1, 1, 0, 0, 0))  # fixed date: same bytes every build
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, f.read_bytes())
    shown = "".join(c for c in chars if c not in " \u00a0")
    (site / "app/lib/pixel-font.ts").write_text(
        "// Written by fonts/bitfolk-pixel/source/build.py. Do not edit by hand.\n"
        f"export const PIXEL_FONT_VERSION = {json.dumps(VERSION)};\n"
        "/** Every character Bitfolk Pixel draws, in code point order. */\n"
        f"export const PIXEL_FONT_CHARS = {json.dumps(shown, ensure_ascii=True)};\n"
    )
    print(f"website copies refreshed in {site}")


if __name__ == "__main__":
    build()
