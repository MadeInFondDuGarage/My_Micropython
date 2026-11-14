import t547
import logo
import pic3
import time

def draw_pixel(x,y,color,buf,width,height):
    color=255-color
    if x < 0 or x >= width:
        return
    if y < 0 or y >= height:
        return
    pos=(y * width // 2) + (x // 2)
    pixel = buf[pos]
    if x % 2:
        pixel = (pixel & 0x0F) | (color & 0xF0)
    else:
        pixel = (pixel & 0xF0) | (color >> 4)
        
    buf[pos]=pixel

def draw_hline(x, y, length, color, buf,width,height):
    for i in range(length):
        draw_pixel(x + i, y, color, buf,width,height)


#buf = bytearray(960 * 540 // 2)
#for i in range(len(buf)):
#    buf[i]=255

screen = t547.T547()
screen.init()

startime= time.ticks_ms()
screen.clear()
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("clear:", elapsed , "ms")

buf=screen.get_buffer()   

#draw_hline(10,125,100,55,buf,screen.width(),screen.height())
#draw_hline(10,130,100,25,buf,screen.width(),screen.height())
#draw_hline(10,135,100,200,buf,screen.width(),screen.height())

#copie d'un fichier brute, image en py.
for xx in range(pic3.pic3_height):
    for yy in range(pic3.pic3_width):
        decal_x=0
        decal_y=0
        scale=10
        poslogo=(yy * pic3.pic3_width // 2) + (xx // 2)
        posbuf=(decal_y*screen.width() // 2)+(yy * screen.width() // 2) + decal_x//2+(xx // 2)
        buf[posbuf]=pic3.pic3_data[poslogo]
        if xx==200:
            break

screen.show()

startime= time.ticks_ms()
screen.clean() # par défaut n blanc
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("clean total:", elapsed , "ms")

screen.clean(450,300,50,50,screen.BLACK) #peut être mis en noir
screen.clean(450,300,50,50,screen.WHITE,screen.SCREEN_BUFFER) #nettoyage de l'écran et du buffer

startime= time.ticks_ms()
screen.show()
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("show complet:", elapsed , "ms")

startime= time.ticks_ms()
screen.clean(200,200,200,200)
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("clean partit:", elapsed , "ms")

startime= time.ticks_ms()
screen.show(200,200,200,200)
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("show partit:", elapsed , "ms")

startime= time.ticks_ms()

for i in range(25):
    screen.clean(25,i*25,25,25,0)
    
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("Temps moyen:", elapsed , "ms")
