import t547
import bitmap_viper as bitmap
import time

# #copie du buffer bmp vrs le buffer screen.
startime= time.ticks_ms()
bmp = bitmap.read_bmp("oeil.bmp")
height=bmp.height
width=bmp.width
#pixels=bmp.pixels() # en mode list de list
pixels=bmp.to4bpp() # en mode buff
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("load:", elapsed , "ms")
#print(pixels)

decal_x=100
decal_y=100

#buf = bytearray(960 * 540 // 2)
startime= time.ticks_ms()
screen = t547.T547()
screen.init()
screen.clear()
buf=screen.get_buffer()
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("screen:", elapsed , "ms")

# startime= time.ticks_ms()
# for xx in range(height):
#     for yy in range(width): 
#         posbuf=((decal_y + xx) * screen.width() )// 2 + (decal_x // 2) + (screen.height()-yy)//2
#         buf[posbuf]=pixels[xx][yy]
# elapsed = time.ticks_diff(time.ticks_ms(), startime)
# print("copy:", elapsed , "ms")

startime= time.ticks_ms()
screen.copy_bitmap(decal_x,decal_y,bmp.width,bmp.height,pixels)
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("copy:", elapsed , "ms")

startime= time.ticks_ms()
screen.show()
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("show:", elapsed , "ms")           