import t547
import epd_wave_tuning as drv
import bitmap_viper as bitmap
import time

# #copie du buffer bmp vrs le buffer screen.
startime= time.ticks_ms()
bmp = bitmap.read_bmp("oeil.bmp")
height=bmp.height
width=bmp.width
pixels=bmp.pixels()
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("load:", elapsed , "ms")


decal_x=100
decal_y=100

startime= time.ticks_ms()
screen = t547.T547()
screen.init()

drv.init(t547.get_connector())
buf, w,h,deg=drv.get_context()

drv.clean_screen()

elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("screen:", elapsed , "ms")

startime= time.ticks_ms()
for xx in range(height):
    for yy in range(width): 
        posbuf=((decal_y + xx) * screen.WIDTH )// 2 + (decal_x // 2) + (screen.HEIGHT-yy)//2
        buf[posbuf]=pixels[xx][yy]
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("copy:", elapsed , "ms")

startime= time.ticks_ms()
drv.clean_screen()
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("clean:", elapsed , "ms")

startime= time.ticks_ms()
drv.show(buf)
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("show:", elapsed , "ms")

drv.deinit()
screen.deinit()