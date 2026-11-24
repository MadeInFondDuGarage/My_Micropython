#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import re
import struct
from pathlib import Path
import inkex
from inkex.paths import Path as InkexPath
from inkex.transforms import Transform
from lxml import etree

WHITE= 0 # blanc par défaut
BLACK = 1 #noir par défaut

def get_glyph_groups(root):
    return [e for e in root.iter() if e.get("id", "").startswith("glyph_U+")]


def get_metrics_map(root):
    return {
        e.get("id").replace("metrics_", "glyph_"): e
        for e in root.iter()
        if e.get("id", "").startswith("metrics_U+")
    }


def parse_translate(transform_str):
    if not transform_str:
        return 0.0, 0.0
    nums = re.findall(r"-?\d*\.?\d+", transform_str)
    if len(nums) >= 2:
        return float(nums[0]), float(nums[1])
    return 0.0, 0.0


def collect_paths(elem):
    tag = etree.QName(elem.tag).localname if "}" in elem.tag else elem.tag
    if tag == "path":
        d = elem.get("d", "").strip()
        return [d] if d else []
    d_parts = []
    for child in elem.iter():
        ctag = etree.QName(child.tag).localname if "}" in child.tag else child.tag
        if ctag == "path":
            d = child.get("d", "").strip()
            if d:
                d_parts.append(d)
    return d_parts


def flatten_path_to_subpaths(d, steps=14):
    """
    Convertit un chemin SVG en liste de sous-chemins (chaque sous-chemin est une liste de points (x, y)).
    Ferme automatiquement chaque sous-chemin pour le remplissage scanline.
    """
    subpaths = []
    current = []
    last = None
    start_subpath = None

    def flush():
        nonlocal current
        if len(current) >= 2:
            if current[0] != current[-1]:
                current.append(current[0])
            subpaths.append(current)
        current = []

    for seg in InkexPath(d).to_absolute():
        name = type(seg).__name__
        if name == "Move":
            flush()
            pt = (seg.arg1.real, seg.arg1.imag)
            current = [pt]
            last = pt
            start_subpath = pt
        elif name == "Line":
            pt = (seg.arg1.real, seg.arg1.imag)
            if last is None:
                current = [pt]
                start_subpath = pt
            current.append(pt)
            last = pt
        elif name == "Quadratic":
            if last is not None:
                p0 = last
                p1 = (seg.arg1.real, seg.arg1.imag)
                p2 = (seg.arg2.real, seg.arg2.imag)
                for i in range(1, steps + 1):
                    t = i / steps
                    mt = 1.0 - t
                    x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
                    y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
                    current.append((x, y))
                last = p2
        elif name == "Curve":
            if last is not None:
                p0 = last
                p1 = (seg.arg1.real, seg.arg1.imag)
                p2 = (seg.arg2.real, seg.arg2.imag)
                p3 = (seg.arg3.real, seg.arg3.imag)
                for i in range(1, steps + 1):
                    t = i / steps
                    mt = 1.0 - t
                    x = (mt**3) * p0[0] + 3 * (mt**2) * t * p1[0] + 3 * mt * (t**2) * p2[0] + (t**3) * p3[0]
                    y = (mt**3) * p0[1] + 3 * (mt**2) * t * p1[1] + 3 * mt * (t**2) * p2[1] + (t**3) * p3[1]
                    current.append((x, y))
                last = p3
        elif name == "ZoneClose":
            if last is not None and start_subpath is not None:
                current.append(start_subpath)
                last = start_subpath
            flush()

    flush()
    return subpaths


def fill_subpaths_scanline(grid, w, h, subpaths,invert=False):
    """Remplit l'intérieur des chemins fermés selon la règle even-odd (gère les trous comme le 'O' ou 'e')."""
    edges = []
    if invert:
        fg_color=WHITE
    else:
        fg_color=BLACK

    for poly in subpaths:
        for i in range(len(poly) - 1):
            x0, y0 = poly[i]
            x1, y1 = poly[i + 1]
            if y0 != y1:
                edges.append((y0, x0, y1, x1))

    if not edges:
        return

    for py in range(h):
        scan_y = py + 0.5
        xs = []
        for y0, x0, y1, x1 in edges:
            # Convention demi-ouverte pour éviter les doubles comptages aux sommets
            if (y0 <= scan_y < y1) or (y1 <= scan_y < y0):
                t = (scan_y - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            x_start = max(0, int(math.ceil(xs[i])))
            x_end = min(w - 1, int(math.floor(xs[i + 1])))
            for px in range(x_start, x_end + 1):
                grid[py][px] = fg_color


def draw_thick_line(grid, w, h, x0, y0, x1, y1, radius=0.5,invert=False):
    """Trace un segment avec épaisseur (radius en pixels) dans une grille."""

    dist = math.hypot(x1 - x0, y1 - y0)
    steps = max(1, int(math.ceil(dist * 2.0)))
    r2 = radius * radius
    r_ceil = int(math.ceil(radius))

    if invert:
        fg_color=WHITE
    else:
        fg_color=BLACK

    for i in range(steps + 1):
        t = i / steps
        cx = x0 + (x1 - x0) * t
        cy = y0 + (y1 - y0) * t
        ix, iy = int(round(cx)), int(round(cy))
        for dy in range(-r_ceil, r_ceil + 1):
            py = iy + dy
            if py < 0 or py >= h:
                continue
            for dx in range(-r_ceil, r_ceil + 1):
                px = ix + dx
                if px < 0 or px >= w:
                    continue
                if (px - cx) ** 2 + (py - cy) ** 2 <= r2:
                    grid[py][px] = fg_color


def write_bmp_1bit(filepath, grid, invert=False):
    """Écrit un fichier BMP monochrome 1-bit standard (bottom-up, aligné 4 octets)."""
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    row_bytes = ((w + 31) // 32) * 4
    pixel_array_size = row_bytes * h
    header_size = 14 + 40 + 8
    file_size = header_size + pixel_array_size

    palette = struct.pack("<BBBBBBBB", 0, 0, 0, 0, 255, 255, 255, 0)
    #palette = struct.pack("<BBBBBBBB", 255, 255, 255, 0, 0, 0, 0, 0)

    file_header = struct.pack("<2sIHHI", b"BM", file_size, 0, 0, header_size)
    dib_header = struct.pack(
        "<IiiHHIIiiII",
        40,
        w,
        h,
        1,
        1,
        0,
        pixel_array_size,
        2835, 2835,
        2,
        2,
    )

    rows_data = bytearray()
    for y in range(h - 1, -1, -1):
        row = bytearray(row_bytes)
        for x in range(w):
            if grid[y][x]:
                row[x >> 3] |= (0x80 >> (x & 7))
        rows_data.extend(row)

    with open(filepath, "wb") as f:
        f.write(file_header)
        f.write(dib_header)
        f.write(palette)
        f.write(rows_data)


def build_bmp_font(
    root,
    font_name,
    output_dir,
    target_height=24,
    stroke_px=1.4,
    do_fill=True,
    do_stroke=False,
    invert=False,
):
    glyph_groups = get_glyph_groups(root)
    metrics_map = get_metrics_map(root)

    safe_font_name = re.sub(r'[<>:"/\\|?*]', "_", font_name).strip()
    out_folder = Path(output_dir) / f"Font{safe_font_name}"
    out_folder.mkdir(parents=True, exist_ok=True)

    count = 0
    index_lines = ["# Index des glyphes BMP générés (code_hex -> fichier, largeur, hauteur)\n"]

    # +1 ligne blanche en bas du buffer (toujours laissée à 0 dans grid)
    glyph_h = max(1, int(round(target_height)))
    bmp_h = glyph_h + 1

    for g in glyph_groups:
        gid = g.get("id", "")
        m = re.search(r"U\+([0-9A-Fa-f]{4,})", gid)
        if not m:
            continue

        code_hex = m.group(1).upper()
        code_int = int(code_hex, 16)
        char = chr(code_int)

        mg = metrics_map.get(gid)
        if mg is None:
            continue

        rect = next((e for e in mg.iter() if etree.QName(e.tag).localname == "rect"), None)
        if rect is None:
            continue

        rx = float(rect.get("x", 0))
        ry = float(rect.get("y", 0))
        rw = float(rect.get("width", 10))
        rh = float(rect.get("height", 10))
        tx, ty = parse_translate(mg.get("transform", ""))

        ox = tx + rx
        oy = ty + ry

        scale = glyph_h / rh
        bmp_w = max(1, int(round(rw * scale)))

        d_parts = collect_paths(g)
        if not d_parts:
            continue

        transform = Transform((scale, 0, 0, scale, -ox * scale, -oy * scale))

        # Buffer de hauteur bmp_h (la dernière ligne index bmp_h - 1 reste vide / fond)
        if invert:
            bk_color=BLACK
        else:
            bk_color=WHITE

        grid = [[bk_color] * bmp_w for _ in range(bmp_h)]
        radius = max(0.5, stroke_px / 2.0)

        for d in d_parts:
            transformed_d = str(InkexPath(d).transform(transform))
            subpaths = flatten_path_to_subpaths(transformed_d)

            if do_fill:
                fill_subpaths_scanline(grid, bmp_w, glyph_h, subpaths,invert=invert)

            if do_stroke:
                for poly in subpaths:
                    for i in range(len(poly) - 1):
                        x0, y0 = poly[i]
                        x1, y1 = poly[i + 1]
                        draw_thick_line(grid, bmp_w, glyph_h, x0, y0, x1, y1, radius=radius,invert=invert)

        bmp_filename = f"U+{code_hex}.bmp"
        bmp_path = out_folder / bmp_filename
        write_bmp_1bit(bmp_path, grid, invert=invert)

        index_lines.append(f"0x{code_hex}: ('{bmp_filename}', {bmp_w}, {bmp_h}),  # '{char}'\n")
        count += 1

    # Espace vide U+0020.bmp (avec la même ligne blanche en bas)
    space_w = max(1, int(round(glyph_h * 0.4)))
    space_grid = [[0] * space_w for _ in range(bmp_h)]
    write_bmp_1bit(out_folder / "U+0020.bmp", space_grid, invert=invert)
    index_lines.append(f"0x0020: ('U+0020.bmp', {space_w}, {bmp_h}),  # ' '\n")

    with open(out_folder / "font_index.py", "w", encoding="utf-8") as f:
        f.writelines(index_lines)

    return count, out_folder


class ExportBMPFont(inkex.Effect):

    def add_arguments(self, pars):
        pars.add_argument("--font-family",    type=str,           dest="font_family",    default="Arial")
        pars.add_argument("--output-file",    type=str,           dest="output_path",    default="./")
        pars.add_argument("--bmp-height",     type=int,           dest="bmp_height",     default=24)
        pars.add_argument("--bmp-stroke",     type=float,         dest="bmp_stroke",     default=1.4)
        pars.add_argument("--bmp-fill",       type=inkex.Boolean, dest="bmp_fill",       default=True)
        pars.add_argument("--bmp-outline",    type=inkex.Boolean, dest="bmp_outline",    default=False)
        pars.add_argument("--bmp-invert",     type=inkex.Boolean, dest="bmp_invert",     default=False)

    def effect(self):
        font_name = self.options.font_family
        try:
            count, out_folder = build_bmp_font(
                self.document.getroot(),
                font_name,
                self.options.output_path,
                target_height=self.options.bmp_height,
                stroke_px=self.options.bmp_stroke,
                do_fill=self.options.bmp_fill,
                do_stroke=self.options.bmp_outline,
                invert=self.options.bmp_invert,
            )
            inkex.utils.debug(f"OK {count} glyphes BMP générés dans -> {out_folder}")
        except Exception as e:
            import traceback
            inkex.utils.debug(f"ERREUR: {e}\n{traceback.format_exc()}")


if __name__ == "__main__":
    ExportBMPFont().run()
