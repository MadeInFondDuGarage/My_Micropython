import t547
import time
import render_image_4bpp as bitmap
import epd_wave_tuning as drv # on import le driver, ici la version wave

BASE_DARK= (12, 12, 8, 8, 12, 12, 12, 16, 16, 20, 20, 20, 40, 80, 120)

decal_x=100
decal_y=100

startime= time.ticks_ms()

screen = t547.T547()
screen.init()

drv.init(t547.get_connector())
drv.set_contrast(BASE_DARK)

bitmap.set_context(*drv.get_context())

startime= time.ticks_ms()
drv.clean_screen()
elapsed_clear = time.ticks_diff(time.ticks_ms(), startime)

# #copie du buffer bmp vrs le buffer screen.
startime= time.ticks_ms()

bitmap.load_bmp("oeil.bmp")
bitmap.draw_bmp(decal_x, decal_y, 0)

elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("load:", elapsed , "ms")

startime= time.ticks_ms()
drv.show()
    
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("show:", elapsed , "ms")

drv.deinit()
screen.deinit()