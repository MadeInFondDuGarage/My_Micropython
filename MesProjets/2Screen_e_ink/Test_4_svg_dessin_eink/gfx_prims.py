# gfx_prims.py - Primitives graphiques construites uniquement sur pixel(x, y, color)


class GfxCanvas:
    """Base graphique ne reposant que sur self.pixel(x, y, color)."""

    def __init__(self, width=None, height=None):
        self.width = width
        self.height = height

    def pixel(self, x, y, color):
        raise NotImplementedError("Implémenter pixel(x, y, color)")

    def _px(self, x, y, color):
        x = int(x)
        y = int(y)
        if self.width is not None and (x < 0 or x >= self.width):
            return
        if self.height is not None and (y < 0 or y >= self.height):
            return
        self.pixel(x, y, color)

    def _hline(self, x1, x2, y, color):
        if x1 > x2:
            x1, x2 = x2, x1
        if self.height is not None and (y < 0 or y >= self.height):
            return
        if self.width is not None:
            if x1 < 0:
                x1 = 0
            if x2 >= self.width:
                x2 = self.width - 1
        for x in range(int(x1), int(x2) + 1):
            self.pixel(x, int(y), color)

    def _stamp_brush(self, cx, cy, color, sw):
        if sw <= 1:
            self._px(cx, cy, color)
            return
        r = (sw - 1) / 2.0
        r2 = r * r
        ir = int(r) + 1
        for dy in range(-ir, ir + 1):
            for dx in range(-ir, ir + 1):
                if dx * dx + dy * dy <= r2:
                    self._px(cx + dx, cy + dy, color)

    # --------------------------------------------------------
    # LIGNE (Bresenham + épaisseur sw)
    # --------------------------------------------------------
    def line(self, x1, y1, x2, y2, color, sw=1):
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        sw = max(1, int(sw))

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            self._stamp_brush(x1, y1, color, sw)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    # --------------------------------------------------------
    # RECTANGLE (plein ou contour)
    # --------------------------------------------------------
    def rect(self, x, y, w, h, color, filled=0, sw=1):
        x, y, w, h = int(x), int(y), int(w), int(h)
        if w <= 0 or h <= 0:
            return
        if filled:
            for yy in range(y, y + h):
                self._hline(x, x + w - 1, yy, color)
        else:
            x2 = x + w - 1
            y2 = y + h - 1
            self.line(x, y, x2, y, color, sw)
            self.line(x2, y, x2, y2, color, sw)
            self.line(x2, y2, x, y2, color, sw)
            self.line(x, y2, x, y, color, sw)

    # --------------------------------------------------------
    # CERCLE (Midpoint / Bresenham + épaisseur sw)
    # --------------------------------------------------------
    def circle(self, cx, cy, r, color, filled=0, sw=1):
        cx, cy, r = int(cx), int(cy), int(r)
        if r < 0:
            return
        if r == 0:
            self._stamp_brush(cx, cy, color, sw)
            return

        if filled:
            x = r
            y = 0
            err = 1 - x
            while x >= y:
                self._hline(cx - x, cx + x, cy + y, color)
                self._hline(cx - x, cx + x, cy - y, color)
                self._hline(cx - y, cx + y, cy + x, color)
                self._hline(cx - y, cx + y, cy - x, color)
                y += 1
                if err < 0:
                    err += 2 * y + 1
                else:
                    x -= 1
                    err += 2 * (y - x) + 1
        else:
            sw = max(1, int(sw))
            # Pour un contour épais, on trace l'anneau entre r_out et r_in
            r_out = r + (sw - 1) / 2.0
            r_in = max(0.0, r - (sw + 1) / 2.0)
            ro2 = r_out * r_out
            ri2 = r_in * r_in
            bound = int(r_out) + 1
            for dy in range(-bound, bound + 1):
                for dx in range(-bound, bound + 1):
                    d2 = dx * dx + dy * dy
                    if d2 <= ro2 and (r_in == 0.0 or d2 >= ri2):
                        self._px(cx + dx, cy + dy, color)

    # --------------------------------------------------------
    # TRIANGLE (plein ou contour)
    # --------------------------------------------------------
    def tri(self, x1, y1, x2, y2, x3, y3, color, filled=0, sw=1):
        x1, y1 = int(x1), int(y1)
        x2, y2 = int(x2), int(y2)
        x3, y3 = int(x3), int(y3)

        if not filled:
            self.line(x1, y1, x2, y2, color, sw)
            self.line(x2, y2, x3, y3, color, sw)
            self.line(x3, y3, x1, y1, color, sw)
            return

        pts = sorted([(x1, y1), (x2, y2), (x3, y3)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            self._hline(min(ax, bx, cx), max(ax, bx, cx), ay, color)
            return

        def edge_x(p0, p1, y):
            x0, y0 = p0
            x1_, y1_ = p1
            if y1_ == y0:
                return x0
            return x0 + (x1_ - x0) * (y - y0) / (y1_ - y0)

        for y in range(ay, cy + 1):
            xa = edge_x((ax, ay), (cx, cy), y)
            if y < by:
                xb = edge_x((ax, ay), (bx, by), y)
            else:
                xb = edge_x((bx, by), (cx, cy), y)
            self._hline(round(xa), round(xb), y, color)

    # --------------------------------------------------------
    # POLYGONE / CHEMIN (contour ou remplissage even-odd)
    # --------------------------------------------------------
    def poly(self, pts, color, filled=0, sw=1):
        n = len(pts)
        if n == 0:
            return
        if n == 1:
            self._stamp_brush(pts[0][0], pts[0][1], color, sw)
            return

        if not filled:
            for i in range(n - 1):
                x1, y1 = pts[i]
                x2, y2 = pts[i + 1]
                self.line(x1, y1, x2, y2, color, sw)
            return

        # Remplissage even-odd par balayage horizontal
        ys = [p[1] for p in pts]
        ymin = int(min(ys))
        ymax = int(max(ys))
        if ymin == ymax:
            xs = [p[0] for p in pts]
            self._hline(min(xs), max(xs), ymin, color)
            return

        # Fermer le polygone si non fermé
        ring = list(pts)
        if ring[0] != ring[-1]:
            ring.append(ring[0])

        for y in range(ymin, ymax + 1):
            yf = y + 0.5
            intersections = []
            for i in range(len(ring) - 1):
                x0, y0 = ring[i]
                x1, y1 = ring[i + 1]
                if (y0 <= yf < y1) or (y1 <= yf < y0):
                    t = (yf - y0) / (y1 - y0)
                    intersections.append(x0 + t * (x1 - x0))
            intersections.sort()
            for i in range(0, len(intersections) - 1, 2):
                self._hline(round(intersections[i]), round(intersections[i + 1]), y, color)
