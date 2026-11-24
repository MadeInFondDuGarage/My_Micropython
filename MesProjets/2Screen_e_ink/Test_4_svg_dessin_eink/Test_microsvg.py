import dessin
from gfx_prims import GfxCanvas
from vec_player import render_py_drawing

import t547 #hal de l'écran
import epd_wave as drv # on import le driver, ici la version wave
import render_draw_4bpp as gfx_pixels

class MonEcran(GfxCanvas):
    def __init__(self, w, h):
        super().__init__(w, h)
        # Exemple : framebuffer simple ou appel direct driver
        self.buf = bytearray(w * h)

    def pixel(self, x, y, color):
        # color est déjà en 0..15
        self.buf[y * self.width + x] = color & 0x0F


#init de l'écran
table=t547.table() #récupération de la table hal
screen = t547.T547()
screen.init()
buf=screen.get_buffer()

drv.init(table)
drv.clear()

ecran = MonEcran(dessin.WIDTH, dessin.HEIGHT)
render_py_drawing(dessin, ecran)
