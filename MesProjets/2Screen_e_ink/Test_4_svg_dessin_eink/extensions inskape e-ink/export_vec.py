#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# export_vec.py - SVG Inkscape -> opcodes vectoriels 16 niveaux de gris (.bin + .py)

import math
import struct
from pathlib import Path

import inkex
from lxml import etree

NONE = 255
SHAPES = (
    inkex.PathElement,
    inkex.Rectangle,
    inkex.Circle,
    inkex.Ellipse,
    inkex.Line,
    inkex.Polyline,
    inkex.Polygon,
)
SKIP = {"defs", "clipPath", "mask", "pattern", "marker", "symbol"}

# Opcodes
OP_RECT = 1
OP_CIRCLE = 2
OP_LINE = 3
OP_TRI = 4
OP_POLY = 5

OP_NAMES = {
    OP_RECT: "RECT",
    OP_CIRCLE: "CIRCLE",
    OP_LINE: "LINE",
    OP_TRI: "TRI",
    OP_POLY: "POLY",
}


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def num(v, default=1.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def clamp16(v):
    return max(-32768, min(32767, int(round(v))))


def gray_level(color, opacity, invert):
    c = inkex.Color(color).to_rgb()
    lum = 0.299 * c.red + 0.587 * c.green + 0.114 * c.blue
    lum = 255 - (255 - lum) * opacity  # mélange sur fond blanc
    lvl = int(round(lum / 255 * 15))
    return 15 - lvl if invert else lvl


def paint(st, name, default, invert):
    v = str(st.get(name, default)).strip()
    if v in ("", "none") or v.startswith("url"):
        return NONE
    op = max(0.0, min(1.0, num(st.get("opacity")) * num(st.get(name + "-opacity"))))
    try:
        return gray_level(v, op, invert)
    except Exception:
        return NONE


def hidden(e):
    for a in (e, *e.iterancestors()):
        if etree.QName(a).localname in SKIP:
            return True
        if a.style.get("display") == "none" or a.get("display") == "none":
            return True
    return False


def closed_flags(path):
    flags = []
    for seg in path:
        if seg.letter in "Mm":
            flags.append(False)
        elif seg.letter in "Zz" and flags:
            flags[-1] = True
    return flags


def flatten_sub(sub, closed):
    pts = [tuple(sub[0][1])]
    for a, b in zip(sub, sub[1:]):
        p0, p1, p2, p3 = (tuple(v) for v in (a[1], a[2], b[0], b[1]))
        if p1 == p0 and p2 == p3:
            n = 1
        else:
            n = max(
                2,
                min(48, int((math.dist(p0, p1) + math.dist(p1, p2) + math.dist(p2, p3)) / 3)),
            )
        for i in range(1, n + 1):
            t = i / n
            u = 1 - t
            pts.append((
                u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
                u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1],
            ))
    out = []
    for x, y in pts:
        q = (clamp16(x), clamp16(y))
        if not out or out[-1] != q:
            out.append(q)
    if closed and len(out) > 1 and out[0] != out[-1]:
        out.append(out[0])
    return out


def is_axis_aligned_rect(pts, closed):
    if not closed or len(pts) not in (4, 5):
        return None
    ring = pts[:-1] if (len(pts) == 5 and pts[0] == pts[-1]) else pts
    if len(ring) != 4:
        return None
    xs = sorted({p[0] for p in ring})
    ys = sorted({p[1] for p in ring})
    if len(xs) != 2 or len(ys) != 2:
        return None
    expected = {(xs[0], ys[0]), (xs[1], ys[0]), (xs[1], ys[1]), (xs[0], ys[1])}
    if set(ring) != expected:
        return None
    w = xs[1] - xs[0]
    h = ys[1] - ys[0]
    if w <= 0 or h <= 0:
        return None
    return (xs[0], ys[0], w, h)


def is_triangle(pts, closed):
    if len(pts) == 4 and pts[0] == pts[-1]:
        tri = pts[:3]
    elif len(pts) == 3:
        tri = pts
    else:
        return None
    (x1, y1), (x2, y2), (x3, y3) = tri
    area2 = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
    if area2 == 0:
        return None
    return (x1, y1, x2, y2, x3, y3)


def build_primitive(e, m, filled):
    """Retourne un tuple (opcode, params_tuple) en coordonnées pixels."""
    # Cercle ou ellipse sans rotation/cisaillement
    if isinstance(e, (inkex.Circle, inkex.Ellipse)) and abs(m.b) < 1e-6 and abs(m.c) < 1e-6:
        cx = num(e.get("cx"), 0.0)
        cy = num(e.get("cy"), 0.0)
        if isinstance(e, inkex.Circle):
            r = num(e.get("r"), 0.0)
            rx = ry = r
        else:
            rx = num(e.get("rx"), 0.0)
            ry = num(e.get("ry"), 0.0)
        pcx, pcy = m.apply_to_point((cx, cy))
        prx = abs(rx * m.a)
        pry = abs(ry * m.d)
        if abs(prx - pry) <= 1.0 and prx >= 1:
            return (OP_CIRCLE, (clamp16(pcx), clamp16(pcy), clamp16(round((prx + pry) / 2))))

    # Ligne directe
    if isinstance(e, inkex.Line) and not filled:
        x1, y1 = m.apply_to_point((num(e.get("x1"), 0.0), num(e.get("y1"), 0.0)))
        x2, y2 = m.apply_to_point((num(e.get("x2"), 0.0), num(e.get("y2"), 0.0)))
        return (OP_LINE, (clamp16(x1), clamp16(y1), clamp16(x2), clamp16(y2)))

    # Aplatissement du chemin transformé
    p = e.path.to_absolute().transform(m)
    flags = closed_flags(p)
    subs = []
    for i, sub in enumerate(p.to_superpath()):
        closed = (i < len(flags) and flags[i]) or isinstance(e, (inkex.Rectangle, inkex.Polygon))
        pts = flatten_sub(sub, closed)
        if pts:
            subs.append((pts, closed))

    if not subs:
        return None

    # Si un seul sous-chemin, tenter la détection de primitive
    if len(subs) == 1:
        pts, closed = subs[0]
        if len(pts) == 2 and not closed:
            return (OP_LINE, (pts[0][0], pts[0][1], pts[1][0], pts[1][1]))
        rect = is_axis_aligned_rect(pts, closed)
        if rect:
            return (OP_RECT, rect)
        tri = is_triangle(pts, closed)
        if tri and (closed or filled):
            return (OP_TRI, tri)
        return (OP_POLY, tuple(pts))

    # Plusieurs sous-chemins -> polygone / chemin multi-parties
    all_pts = [pt for pts, _ in subs for pt in pts]
    return (OP_POLY, tuple(all_pts))


# ------------------------------------------------------------
# ECRITURE SÉPARÉE (.bin ET .py)
# ------------------------------------------------------------
# Format .bin (little endian) :
#   Header : u16 width, u16 height, u16 nb_cmds
#   Cmd    : u8 opcode, u8 filled (1=plein, 0=vide), u8 color (0..15), u8 stroke_w
#   Payload selon opcode :
#     OP_RECT   : h x, h y, H w, H h              (8 octets)
#     OP_CIRCLE : h cx, h cy, H r                (6 octets)
#     OP_LINE   : h x1, h y1, h x2, h y2           (8 octets)
#     OP_TRI    : h x1, h y1, h x2, h y2, h x3, h y3 (12 octets)
#     OP_POLY   : H nb_pts, nb_pts * (h x, h y)

def write_bin(path, w, h, cmds):
    with open(path, "wb") as f:
        f.write(struct.pack("<HHH", w, h, len(cmds)))
        for op, filled, color, sw, params in cmds:
            f.write(struct.pack("<BBBB", op, filled, color, sw))
            if op == OP_RECT:
                f.write(struct.pack("<hhHH", *params))
            elif op == OP_CIRCLE:
                f.write(struct.pack("<hhH", *params))
            elif op == OP_LINE:
                f.write(struct.pack("<hhhh", *params))
            elif op == OP_TRI:
                f.write(struct.pack("<hhhhhh", *params))
            elif op == OP_POLY:
                f.write(struct.pack("<H", len(params)))
                for x, y in params:
                    f.write(struct.pack("<hh", x, y))


def write_py(path, w, h, cmds):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Auto-generated MicroPython vector commands\n")
        f.write("OP_RECT, OP_CIRCLE, OP_LINE, OP_TRI, OP_POLY = 1, 2, 3, 4, 5\n")
        f.write(f"WIDTH = {w}\n")
        f.write(f"HEIGHT = {h}\n")
        f.write("CMDS = (\n")
        for op, filled, color, sw, params in cmds:
            name = OP_NAMES[op]
            if op == OP_POLY:
                pts_str = "".join(f"({x},{y})," for x, y in params)
                p_repr = f"(({pts_str}),)"
            else:
                p_repr = "(" + ", ".join(str(v) for v in params) + ")"
            f.write(f"    ({name}, {filled}, {color}, {sw}, {p_repr}),\n")
        f.write(")\n")


# ------------------------------------------------------------
# EXTENSION
# ------------------------------------------------------------

class ExportVec(inkex.EffectExtension):

    def add_arguments(self, pars):
        pars.add_argument("--name",    type=str, default="dessin")
        pars.add_argument("--out-dir", type=str, dest="out_dir", default="./")
        pars.add_argument("--mode",    type=str, default="auto")
        pars.add_argument("--invert",  type=inkex.Boolean, default=False)

    def effect(self):
        svg = self.svg
        unit = getattr(svg, "to_dimensionless", svg.unittouu)
        vx, vy, vw, vh = svg.get_viewbox()
        if not vw or not vh:
            vx = vy = 0.0
            vw = float(unit(svg.get("width") or "0"))
            vh = float(unit(svg.get("height") or "0"))

        # Coordonnées directes en pixels (échelle 1.0, alignées sur l'origine du viewBox)
        base = inkex.Transform(f"translate({-vx},{-vy})")
        mode = self.options.mode
        inv = self.options.invert

        cmds = []
        for e in svg.iter():
            if not isinstance(e, SHAPES) or hidden(e):
                continue
            st = e.specified_style()
            fill_lvl = paint(st, "fill", "black", inv)
            stroke_lvl = paint(st, "stroke", "none", inv)

            if mode == "fill":
                stroke_lvl = NONE
                if fill_lvl == NONE:
                    fill_lvl = gray_level("#000000", 1.0, inv)
            elif mode == "stroke":
                fill_lvl = NONE
                if stroke_lvl == NONE:
                    stroke_lvl = gray_level("#000000", 1.0, inv)

            if fill_lvl == NONE and stroke_lvl == NONE:
                continue

            m = base @ e.composed_transform()
            sw = max(
                1,
                int(round(unit(str(st.get("stroke-width", "1"))) * math.sqrt(abs(m.a * m.d - m.b * m.c)))),
            )
            sw = min(sw, 255)

            # Émission : plein (filled=1) puis contour (filled=0) si présents
            passes = []
            if fill_lvl != NONE:
                passes.append((1, fill_lvl, 0))
            if stroke_lvl != NONE:
                passes.append((0, stroke_lvl, sw))

            for filled, col, stroke_w in passes:
                prim = build_primitive(e, m, filled)
                if prim:
                    op, params = prim
                    cmds.append((op, filled, col, stroke_w, params))

        w = max(1, int(round(vw)))
        h = max(1, int(round(vh)))
        out = Path(self.options.out_dir).expanduser()
        out.mkdir(parents=True, exist_ok=True)
        write_bin(out / (self.options.name + ".bin"), w, h, cmds)
        write_py(out / (self.options.name + ".py"), w, h, cmds)
        inkex.utils.debug(f"OK {len(cmds)} cmds, {w}x{h} -> {out / self.options.name}")


if __name__ == "__main__":
    ExportVec().run()
