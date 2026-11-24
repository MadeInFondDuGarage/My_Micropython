import micropython

@micropython.viper
def scale_coord(v: int, scale_q8: int) -> int:
    return (v * scale_q8) >> 8

class HersheyFontPy:
    """
    Moteur de rendu pour fonte Hershey chargée depuis un module .py
    (debug, pédagogique, ou fonte freezée)
    """

    FONT_UNITS_HEIGHT = 120   # hauteur logique normalisée (TARGET_RANGE)
    FONT_SPACE = 10           # espace par défaut si glyph absent
    DEG=0
    TEXT=""
    SCALE=1
    FONT_HEIGHT=30
    BUF=""
    WIDTH=0
    HEIGHT=0
    
    def __init__(self, font_module):
        # Différent du .bin :
        # ici la fonte est un MODULE Python déjà chargé
        self.font = font_module
        
    def set_screen(self,buf,width,height):
        self.BUF=buf
        self.WIDTH=width
        self.HEIGHT=height        
        
    # -----------Rotate ---------
    @micropython.native
    def _rotate(self,x,y):
        phyX=x
        phyY=y
        
        if self.DEG==0:
            phyX=x
            phyY=y
        elif self.DEG== 90:
            phyX = y
            phyY = self.HEIGHT - 1 - x
        elif self.DEG == 180:
            phyX = self.WIDTH - 1 - x
            phyY = self.HEIGHT - 1 - y
        elif self.DEG ==270:
            phyX = self.WIDTH - 1 - y
            phyY = x
        return phyX,phyY
    
    def orientation(self,deg):
        self.DEG=deg
        
    # ---------- Pixel ----------
    @micropython.native
    def draw_pixel(self, x, y, color):
        color = 255 - color
        
        if x < 0 or x >= self.WIDTH or y < 0 or y >= self.HEIGHT:
            return

        pos = (y * self.WIDTH // 2) + (x // 2)
        pixel = self.BUF[pos]

        if x & 1:
            pixel = (pixel & 0x0F) | (color & 0xF0)
        else:
            pixel = (pixel & 0xF0) | (color >> 4)

        self.BUF[pos] = pixel

    # ---------- Ligne ----------
    @micropython.native
    def draw_line(self, xx1, yy1, xx2, yy2, color):
        x1,y1=self._rotate(xx1,yy1)
        x2,y2=self._rotate(xx2,yy2)
        
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy

        while True:
            self.draw_pixel(x1, y1, color)

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
    
    # ---------- Texte ----------
    @micropython.native
    def set_text(self,text):
        self.TEXT=text
        self.SCALE = self.compute_scale(self.FONT_HEIGHT)
    
    @micropython.native
    def set_size(self,font_height_px):
        self.FONT_HEIGHT=font_height_px
        self.SCALE = self.compute_scale(self.FONT_HEIGHT)
        
    @micropython.native
    def draw_text(self, x, y, color):
        scale=self.SCALE
        
        cx = x
        
        for ch in self.TEXT:
            code = ord(ch)

            if code not in self.font.GLYPH_INDEX:
                cx += self.FONT_HEIGHT // 3
                continue

            # Différent du .bin :
            # on lit directement les structures Python
            glyph_id, advance, _ = self.font.GLYPH_INDEX[code]
            _, segments = self.font.GLYPH_DATA[glyph_id]

            for x1, y1, x2, y2 in segments:
                self.draw_line(
                    cx + scale_coord(x1, scale),
                    y  - scale_coord(y1, scale),
                    cx + scale_coord(x2, scale),
                    y  - scale_coord(y2, scale),
                    color
                )

            cx += scale_coord(advance, scale)
            
    @micropython.native
    def get_size(self):
        size=0
        for ch in self.TEXT:
            code = ord(ch)
            if code not in self.font.GLYPH_INDEX:
                continue
            glyph, advance, _ = self.font.GLYPH_INDEX[code]
            size+=scale_coord(advance, self.SCALE)
        return size
    
    @micropython.native
    def get_text(self):
        size_total=0
        size=0
        if self.DEG == 0 or self.DEG==180:
            larg=self.WIDTH
        else:
            larg=self.HEIGHT
            
        for ch in range(0,len(self.TEXT)):
            code = ord(self.TEXT[ch])
            if code not in self.font.GLYPH_INDEX:
                continue
            glyph, advance, _ = self.font.GLYPH_INDEX[code]
            size=scale_coord(advance, self.SCALE)
            if (size_total+size)> larg:
                return self.TEXT[:ch],self.TEXT[ch:]
            else:
                size_total=size_total+size
        
        return self.TEXT
    
    def get_max(self):
        size_max=0
        for code in self.font.GLYPH_INDEX:
            glyph, advance, _ = self.font.GLYPH_INDEX[code]
            if advance > size_max:
                size_max=advance
                car=code
        size=scale_coord(size_max, self.SCALE)
        
        #la je doit divise par la longeur ou larguer suivant l'orientation
        if self.DEG == 0 or self.DEG==180:
            nbr_max=self.WIDTH//size
        else:
            nbr_max=self.HEIGHT//size
        
        return nbr_max,size,size_max,car
        
                
            


