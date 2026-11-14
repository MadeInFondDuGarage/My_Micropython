import micropython

class HersheyFontPy:
    """
    Moteur de rendu pour fonte Hershey chargée depuis un module .py
    (debug, pédagogique, ou fonte freezée)
    """

    FONT_UNITS_HEIGHT = 120   # hauteur logique normalisée (TARGET_RANGE)
    FONT_SPACE = 10           # espace par défaut si glyph absent

    def __init__(self, font_module):
        # Différent du .bin :
        # ici la fonte est un MODULE Python déjà chargé
        self.font = font_module

    # ---------- Pixel ----------
    @micropython.native
    def draw_pixel(self, x, y, color, buf, width, height):
        color = 255 - color
        if x < 0 or x >= width or y < 0 or y >= height:
            return

        pos = (y * width // 2) + (x // 2)
        pixel = buf[pos]

        if x & 1:
            pixel = (pixel & 0x0F) | (color & 0xF0)
        else:
            pixel = (pixel & 0xF0) | (color >> 4)

        buf[pos] = pixel

    # ---------- Ligne ----------
    @micropython.native
    def draw_line(self, x1, y1, x2, y2, color, buf, width, height):
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy

        while True:
            self.draw_pixel(x1, y1, color, buf, width, height)

            if x1 == x2 and y1 == y2:
                break

            e2 = err << 1
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy

    # ---------- Mise à l’échelle ----------
    @micropython.native
    def compute_scale(self, font_height_px):
        # Q8.8 fixe – identique .py / .bin
        return (font_height_px << 8) // self.FONT_UNITS_HEIGHT
    
    @micropython.native
    def scale_coord(self, v, scale_q8):
        return (v * scale_q8) >> 8

    # ---------- Texte ----------
    @micropython.native
    def draw_text(self, x, y, text, color, buf, width, height, font_height_px):
        scale = self.compute_scale(font_height_px)
        cx = x

        for ch in text:
            code = ord(ch)

            if code not in self.font.GLYPH_INDEX:
                cx += font_height_px // 3
                continue

            # Différent du .bin :
            # on lit directement les structures Python
            glyph_id, advance, _ = self.font.GLYPH_INDEX[code]
            _, segments = self.font.GLYPH_DATA[glyph_id]

            for x1, y1, x2, y2 in segments:
                self.draw_line(
                    cx + self.scale_coord(x1, scale),
                    y  - self.scale_coord(y1, scale),
                    cx + self.scale_coord(x2, scale),
                    y  - self.scale_coord(y2, scale),
                    color, buf, width, height
                )

            cx += self.scale_coord(advance, scale)
            
class HersheyFontBin:
    """
    Moteur de rendu pour fonte Hershey au format .bin
    (production, dynamique, faible RAM)
    """

    FONT_UNITS_HEIGHT = 120
    FONT_SPACE = 10

    def __init__(self, filename):
        # Différent du .py :
        # on ouvre un FICHIER binaire
        self.f = open(filename, "rb")
        self._read_header()
        self._read_index()

    # ---------- Chargement ----------
    @micropython.native
    def _read_header(self):
        data = self.f.read(6)
        self.glyph_count = data[0] | (data[1] << 8)
        self.ascent = data[2] | (data[3] << 8)
        self.descent = data[4] | (data[5] << 8)
        
    @micropython.native
    def _read_index(self):
        # unicode → offset
        self.index = {}
        for _ in range(self.glyph_count):
            raw = self.f.read(6)
            code = raw[0] | (raw[1] << 8)
            offset = raw[2] | (raw[3] << 8) | (raw[4] << 16) | (raw[5] << 24)
            self.index[code] = offset

    # ---------- Pixel ----------
    @micropython.native
    def draw_pixel(self, x, y, color, buf, width, height):
        color = 255 - color
        if x < 0 or x >= width or y < 0 or y >= height:
            return

        pos = (y * width // 2) + (x // 2)
        pixel = buf[pos]

        if x & 1:
            pixel = (pixel & 0x0F) | (color & 0xF0)
        else:
            pixel = (pixel & 0xF0) | (color >> 4)

        buf[pos] = pixel

    # ---------- Ligne ----------
    @micropython.native
    def draw_line(self, x1, y1, x2, y2, color, buf, width, height):
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy

        while True:
            self.draw_pixel(x1, y1, color, buf, width, height)

            if x1 == x2 and y1 == y2:
                break

            e2 = err << 1
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy
                
    # ---------- Utilitaires ----------
    @micropython.native
    def compute_scale(self, font_height_px):
        return (font_height_px << 8) // self.FONT_UNITS_HEIGHT
    
    @micropython.native
    def scale_coord(self, v, scale_q8):
        return (v * scale_q8) >> 8
    
    @micropython.native
    def read_int8(self):
        v = self.f.read(1)[0]
        return v - 256 if v > 127 else v

    # ---------- Texte ----------
    @micropython.native
    def draw_text(self, x, y, text, color, buf, width, height, font_height_px):
        scale = self.compute_scale(font_height_px)
        cx = x

        for ch in text:
            code = ord(ch)

            if code not in self.index:
                cx += font_height_px // 3
                continue

            # Différence MAJEURE avec .py :
            # on va lire la fonte à la volée
            self.f.seek(self.index[code])

            advance = self.f.read(1)[0]
            seg_count = self.f.read(1)[0]

            for _ in range(seg_count):
                x1 = self.read_int8()
                y1 = self.read_int8()
                x2 = self.read_int8()
                y2 = self.read_int8()

                self.draw_line(
                    cx + self.scale_coord(x1, scale),
                    y  - self.scale_coord(y1, scale),
                    cx + self.scale_coord(x2, scale),
                    y  - self.scale_coord(y2, scale),
                    color, buf, width, height
                )


            cx += self.scale_coord(advance, scale)
