from machine import Pin

import t547
import renderdisplay

from gt911 import GT911

import sauve_parametre.preferences as preferences #j'inmporte les préférences

#variable global
preferences.charge_prefs()
theme=f"Icones/{preferences.get_pref('theme')}"
print(theme)

#j'instancie la gestion de l'écran
screen = t547.T547()
#screen.init()

#j'init le render d'écran
render = renderdisplay.Render(screen.get_buffer(), screen.width(), screen.height())
render.set_orientation(90) #a 90 pour les menu au debut, seul le reader peut pivoter
render.set_font("fonts/HersheySansMed.bin")

#les interfaces extérieurs
touch = GT911(touch_points=2)
bouton_1 = Pin(21,Pin.IN)

def HwOrientation(phyX,phyY):
    #transforme les entré physique vers les valeurs logique pour relier avec la position des menu
    global render
    x=phyX
    y=phyY
    deg=render.ORIENTATION
    W=render.WIDTH
    H=render.HEIGHT
    
    if deg==0:
        x=phyX
        y=H - 1 - phyY
    
    elif deg== 90:
        y= phyX
        x= phyY
        
    elif deg == 180:
        x = W - 1 - phyX
        y = phyY
        
    elif deg ==270:
        x = W - 1 - phyY
        y = H - 1 - phyX
        
    return x,y

def MenuLigne(bmp,texte,size,Numligne, ecart):
    global render
    pos=Numligne*ecart
    render.set_bmp(bmp)
    render.draw_bmp(15,pos,"C")
    render.set_font_size(size)
    render.set_text(texte)
    render.draw_line(0,pos+50,render.WIDTH,pos+50,5)
    render.draw_line(0,pos-50,render.WIDTH,pos-50,5)
    render.draw_text(render.BmpWIDTH +12 ,pos,0,15,"L","C")
    
def myprint(texte):
    global render, screen
    fontsize=render.FONT_SIZE
    render.set_font_size(30)
    render.set_text(texte)
    render.draw_text(0,0,0,15,"G","H")
    x,y,w,h=render.get_zone()
    screen.show(x,y,w,h)
    render.set_font_size(fontsize)