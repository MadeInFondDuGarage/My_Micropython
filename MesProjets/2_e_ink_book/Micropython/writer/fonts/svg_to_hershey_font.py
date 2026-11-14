#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import struct
import re
from pathlib import Path

SVG_NS = "{http://www.w3.org/2000/svg}"

SVG_UNITS_PER_EM = 1000
TARGET_RANGE = 120

PATH_RE = re.compile(r'([ML])\s*(-?\d+(?:\.\d+)?)\s*(-?\d+(?:\.\d+)?)')


def normalize(v):
    v = round(v / SVG_UNITS_PER_EM * TARGET_RANGE)
    return max(-127, min(127, int(v)))


def parse_path(d):
    segments = []
    last = None
    for cmd, xs, ys in PATH_RE.findall(d):
        x = float(xs)
        y = float(ys)
        if cmd == "M":
            last = (x, y)
        elif cmd == "L" and last:
            segments.append((*last, x, y))
            last = (x, y)
    return segments


def convert(svg_path: Path):
    tree = ET.parse(svg_path)
    root = tree.getroot()

    font = root.find(".//" + SVG_NS + "font")
    face = font.find(SVG_NS + "font-face")

    ascent = int(float(face.attrib["ascent"]))
    descent = int(float(face.attrib["descent"]))

    glyphs = []

    for g in font.findall(SVG_NS + "glyph"):
        if "unicode" not in g.attrib or "d" not in g.attrib:
            continue
        if len(g.attrib["unicode"]) != 1:
            continue

        advance = float(g.attrib.get("horiz-adv-x", "500"))
        segments = parse_path(g.attrib["d"])
        if not segments:
            continue

        glyphs.append({
            "unicode": ord(g.attrib["unicode"]),
            "advance": max(1, int(round(advance / SVG_UNITS_PER_EM * TARGET_RANGE))),
            "segments": tuple(
                (normalize(x1), normalize(y1), normalize(x2), normalize(y2))
                for x1, y1, x2, y2 in segments
            )
        })

    # ========== BIN ==========
    bin_path = svg_path.with_suffix(".bin")
    with open(bin_path, "wb") as f:
        f.write(struct.pack("<Hhh", len(glyphs), ascent, descent))
        idx_pos = f.tell()
        for _ in glyphs:
            f.write(struct.pack("<HI", 0, 0))

        offsets = []
        for g in glyphs:
            offsets.append(f.tell())
            f.write(struct.pack("<BB", g["advance"], len(g["segments"])))
            for s in g["segments"]:
                f.write(struct.pack("<bbbb", *s))

        f.seek(idx_pos)
        for g, off in zip(glyphs, offsets):
            f.write(struct.pack("<HI", g["unicode"], off))

    # ========== PY ==========
    py_path = svg_path.with_suffix(".py")
    with open(py_path, "w", encoding="utf-8") as f:
        f.write("# Auto-generated Hershey font (debug / MicroPython compatible)\n\n")
        f.write(f"FONT_HEADER = {{'glyph_count': {len(glyphs)}, 'ascent': {ascent}, 'descent': {descent}}}\n\n")

        f.write("GLYPH_INDEX = {\n")
        for i, g in enumerate(glyphs):
            ch = chr(g["unicode"])
            f.write(f"    0x{g['unicode']:04X}: ({i}, {g['advance']}, {len(g['segments'])}),  # '{ch}'\n")
        f.write("}\n\n")

        f.write("GLYPH_DATA = [\n")
        for g in glyphs:
            f.write(f"    ({g['advance']}, {g['segments']}),\n")
        f.write("]\n")

    print(f"✅ {svg_path.name} → {bin_path.name} + {py_path.name}")


if __name__ == "__main__":
    for svg in Path('.').glob("*.svg"):
        convert(svg)