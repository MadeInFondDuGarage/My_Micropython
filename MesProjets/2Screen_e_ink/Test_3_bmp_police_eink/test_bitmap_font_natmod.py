import t547
import time
import render_image_4bpp as bitmap
import epd_wave as drv # on import le driver, ici la version wave

decal_x=100
decal_y=100

texte= "ABCDabcde"
startime= time.ticks_ms()

screen = t547.T547()
screen.init()

drv.init(t547.get_connector())

startime= time.ticks_ms()
drv.clean_screen()
elapsed_clear = time.ticks_diff(time.ticks_ms(), startime)

# #copie du buffer bmp vrs le buffer screen.
startime= time.ticks_ms()
bitmap.set_context(*drv.get_context())

for car in texte:
    if car==' ':
        decal_x+=20
    else:
        bitmap.load_bmp(f"FontArial/U+{ord(car):04X}.bmp")
        bpp,w,h=bitmap.get_size()
        decal_x+=w
        bitmap.draw_bmp(decal_x, decal_y, 0)
    
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("draw:", elapsed , "ms")

startime= time.ticks_ms()
drv.show()
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("show:", elapsed , "ms")

#on finie
drv.deinit()
screen.deinit()
