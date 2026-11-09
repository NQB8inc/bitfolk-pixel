#!/usr/bin/env python3
"""Draws specimen.png, the preview image for the README and font directories, from the built TTF.

    python3 source/specimen.py

Needs Pillow (pip install pillow). Text is drawn at multiples of 10px with smoothing off, so every pixel is whole.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PKG = Path(__file__).resolve().parents[1]
W, H, PAD = 1260, 1000, 70  # 630 x 500 at 2x, the cover size itch.io asks for
PAPER, INK, MUTED, GRASS = "#ffffff", "#0e0f11", "#5b5d63", "#3f7a2b"


def font(size):
    return ImageFont.truetype(str(PKG / "fonts/BitfolkPixel.ttf"), size)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"  # no smoothing
    y = 160  # centres the block of text vertically
    for text, size, colour, gap in (
        ("Bitfolk Pixel", 120, INK, 34),
        ("A free pixel font", 60, GRASS, 60),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 50, INK, 18),
        ("abcdefghijklmnopqrstuvwxyz", 50, INK, 18),
        ("0123456789 !?&@#$%*+=", 50, INK, 18),
        ("ÀÉÎÑÖÜÇØÆ àéîñöüçøæß €£¥", 50, INK, 60),
        ("People and AI agents, working together.", 40, MUTED, 22),
        ("Open Font License · bitfolk.ai/font", 30, MUTED, 0),
    ):
        d.text((PAD, y), text, font=font(size), fill=colour)
        y += size + gap
    img.save(PKG / "specimen.png", optimize=True)
    print(f"specimen.png: {W}x{H}, text ends at y={y}")


if __name__ == "__main__":
    main()
