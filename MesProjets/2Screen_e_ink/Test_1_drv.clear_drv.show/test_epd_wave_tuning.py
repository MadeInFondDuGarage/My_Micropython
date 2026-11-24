# Réglage du contraste de epd_wave a l'exécution (sans recompiler).
# Usage : import epd_wave_tuning as t ; t.essai(fb, blacks=0.7)
# Les réglages sont perdus a drv.init() / drv.deinit() (retour aux défauts du natmod).
import t547 #hal de l'écran
import epd_wave_tuning as drv # on import le driver, ici la version wave
import machine
BASE_DARK= (12, 12, 8, 8, 12, 12, 12, 16, 16, 20, 20, 20, 40, 80, 120)
#BASE_DARK  = (30, 30, 20, 20, 30, 30, 30, 40, 40, 50, 50, 50, 100, 200, 300)
BASE_WHITE = (10, 10, 8, 8, 8, 8, 8, 10, 10, 15, 15, 20, 20, 100, 300)

def table(dark=None, white=None):
    """Applique les tables (15 valeurs, 1/10 us). None = inchangé."""
    if dark is not None:
        drv.set_contrast(dark)
    if white is not None:
        drv.set_contrast(white, True)

def calcul(scale=1.0, blacks=1.0, lights=1.0, base=BASE_DARK):
    """scale: tout, blacks: 3 dernières frames (noirs), lights: 4 premières (hautes lumières)."""
    out = []
    for i, v in enumerate(base):
        f = scale
        if i >= 12:
            f *= blacks
        if i < 4:
            f *= lights
        out.append(max(1, min(65535, int(v * f))))
    return out

def cumul(t=None):
    """Temps cumulé par niveau de gris (15 = blanc .. 0 = noir) en BLACK_ON_WHITE."""
    t = t or drv.get_contrast()
    for v in range(15, -1, -1):
        print("niveau %2d : %4d" % (v, sum(t[:15 - v])))

def gradient(fb):
    """Dégradé horizontal 16 niveaux dans le framebuffer (4bpp, 960x540)."""
    row = bytearray(480)
    for k in range(480):
        row[k] = ((2 * k) // 60) | ((((2 * k + 1) // 60)) << 4)
    for y in range(540):
        fb[y * 480:(y + 1) * 480] = row

def essai(fb, scale=1, blacks=1, lights=1.0,dark=True,white=False):
    """Applique le réglage, nettoie, affiche le dégradé."""
    if dark:
        t_d = calcul(scale, blacks, lights,BASE_DARK)
    else:
        t_d=None
    if white:
        t_w = calcul(scale, blacks, lights,BASE_WHITE)
    else:
        t_w=None

    table(t_d,t_w)
    print(t_d,t_w)
    gradient(fb)
    drv.clean_screen()
    drv.show()

def defaut():
    table(BASE_DARK, BASE_WHITE)


#init de l'écran
screen = t547.T547()
screen.init()
fb=screen.get_buffer()
drv.init(t547.get_connector())

essai(fb,1)

drv.deinit()