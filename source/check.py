#!/usr/bin/env python3
"""Checks that the committed font files match the glyph grids in build.py, and that the versions agree.

    python3 source/check.py

Compares characters, outlines and widths, not bytes, so a different fonttools version does not fail it. The font
version in build.py is written X.YZZ and must equal package.json's X.Y.ZZ (1.100 is 1.1.0, 1.101 is 1.1.1).
"""
import json
import os
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

import build


def shapes(font):
    glyf, hmtx = font["glyf"], font["hmtx"]
    out = {}
    for code, name in font.getBestCmap().items():
        g = glyf[name]
        points = list(g.coordinates) if g.numberOfContours > 0 else []
        ends = list(g.endPtsOfContours) if g.numberOfContours > 0 else []
        out[code] = (points, ends, hmtx[name][0])
    return out


def main():
    problems = []
    major, frac = build.VERSION.split(".")
    semver = f"{major}.{int(frac[0])}.{int(frac[1:])}"
    package = json.loads((build.PKG / "package.json").read_text())["version"]
    if semver != package:
        problems.append(f"build.py VERSION {build.VERSION} is {semver}, but package.json says {package}")

    chars = sorted(c for c in build.G if c != build.NOTDEF)
    fresh = shapes(build.make(chars, cff=False))
    for name in ("BitfolkPixel.ttf", "BitfolkPixel.woff2"):
        committed = TTFont(build.PKG / "fonts" / name)
        if shapes(committed) != fresh:
            problems.append(f"fonts/{name} does not match the glyph grids: run python3 source/build.py and commit")
        version = committed["name"].getDebugName(5)
        if version != f"Version {build.VERSION}":
            problems.append(f"fonts/{name} says {version!r}, build.py says {build.VERSION}")
    otf = TTFont(build.PKG / "fonts/BitfolkPixel.otf")
    if set(otf.getBestCmap()) != set(fresh):
        problems.append("fonts/BitfolkPixel.otf has a different character set: run python3 source/build.py and commit")

    for p in problems:
        print(f"::error::{p}" if "GITHUB_ACTIONS" in os.environ else p)
    print(f"{len(fresh)} characters checked, version {semver}" if not problems else f"{len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
