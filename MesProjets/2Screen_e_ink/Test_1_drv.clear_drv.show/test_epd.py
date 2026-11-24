# Test HAL + natmod epd_wave. A lancer dans le REPL : import test_epd
# Le natmod doit etre importable (romfs ou /lib). Les tests sont du plus simple au plus complet.
import gc, time, esp32
import t547

def libre():
    return sum(h[1] for h in esp32.idf_heap_info(esp32.HEAP_DATA))

def ok(nom, cond):
    print(("OK   " if cond else "FAIL ") + nom)
    return cond

# ---------------------------------------------------------------- 1. sans ecran
print("== 1. HAL / natmod sans ecran")
tab = t547.table()
ok("table() non nulle", tab != 0)

epd = t547.T547()
epd.init()
fb = epd.get_buffer()
ok("framebuffer 960/2*540", len(fb) == 480 * 540)

import epd_wave as drv

try:
    drv.show(fb)
    ok("show avant init refuse", False)
except ValueError:
    ok("show avant init refuse", True)

drv.init(tab)
drv.deinit()
gc.collect()
avant = libre()
for _ in range(20):
    drv.init(tab)     # alloue la LUT 64 Ko
    drv.init(tab)     # re-init : ne doit pas fuir
    drv.deinit()
gc.collect()
apres = libre()
ok("pas de fuite init/deinit (delta=%d o)" % (avant - apres), abs(avant - apres) < 1024)

drv.init(tab)
try:
    drv.show(fb, 0, 0, 10, 10, 99)
    ok("mode invalide refuse", False)
except ValueError:
    ok("mode invalide refuse", True)

# ---------------------------------------------------------------- image de test
# degrade horizontal 16 niveaux (0 noir .. 15 blanc), 60 px par bande
row = bytearray(480)
for k in range(480):
    v0 = (2 * k) // 60
    v1 = (2 * k + 1) // 60
    row[k] = v0 | (v1 << 4)
for y in range(540):
    fb[y * 480:(y + 1) * 480] = row

def afficher(nom, *args):
    t0 = time.ticks_us()
    drv.show(fb, *args)      # le driver gère l'alimentation
    dt = time.ticks_diff(time.ticks_us(), t0)
    print("%s : %d ms" % (nom, dt // 1000))
    return dt

# ---------------------------------------------------------------- 2. avec ecran
print("== 2. Ecran : nettoyage")
drv.clear()

print("== 3. Plein ecran : doit afficher 16 bandes du noir au blanc")
t_plein = afficher("plein ecran")

print("== 4. Zone alignee (x pair, largeur paire)")
drv.clear()
afficher("zone 120,100 300x200", 120, 100, 300, 200)

print("== 5. Zone x impair, largeur impaire (chemin nibble_shift)")
drv.clear()
afficher("zone 101,51 201x151", 101, 51, 201, 151)

print("== 6. Mode WHITE_ON_BLACK")
drv.clear()
afficher("white_on_black", 0, 0, 960, 540, drv.WHITE_ON_BLACK)

print("== 7. Rotation (driver -> HAL), clean buffer, push")
drv.orientation(90)
epd.clean(0, 0, 200, 100, 0)       # buffer seulement, rotation du HAL fournie par le driver
ok('get_orientation', drv.get_orientation() == 90)
drv.push(100, 1, 0, 0, 100, 100)  # push zone avec rotation 90
drv.orientation(0)
afficher("apres clean buffer")

print("== Fin. Reference ancien firmware : comparer le temps du plein ecran (%d ms)" % (t_plein // 1000))
drv.deinit()
