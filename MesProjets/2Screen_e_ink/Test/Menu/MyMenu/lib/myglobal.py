from machine import Pin
import time
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
screen.init()

#j'init le render d'écran
render = renderdisplay.Render(screen.get_buffer(), screen.width(), screen.height())
render.set_orientation(90) #a 90 pour les menu au debut, seul le reader peut pivoter
render.set_font("fonts/HersheySansMed.bin")

#les interfaces extérieurs
touch = GT911(touch_points=1)
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
    
def wait_touch():
    #je fais une boucle pour attendre un touc mais par précaution j'utilise un bouton externe pour pouvoir en sortir si besoin
    #l'objectif est d'avoir le branchement du touch ici, pour plustard utiliser un sleep profond
    # et pouvoir utilise le 10 pour le reveil et réduire la consomation elec.
    SLIDE_LIMITE = 40  # px minimum pour considérer un slide
    
    x2, y2, x1, y1=0,0,0,0
    
    touch_ok=False
    while bouton_1.value():
        time.sleep_ms(50)
        n, points = touch.read_points() #je lit le point
        if n>0 and touch_ok==False: #si j'ai au moins  point
            x1, y1 = HwOrientation(points[0][0], points[0][1]) #je lit
            x2, y2 = x1, y1
            touch_ok=True
        elif n>0 and touch_ok==True: #ensuite je continue a lire jusqu'au lever du doigt
            x2, y2 = HwOrientation(points[0][0], points[0][1]) #je lit
            touch_ok=True
        elif n==0 and touch_ok == True:
            break
            
    dx = x2 - x1
    dy = y2 - y1
 
    if abs(dx) < SLIDE_LIMITE and abs(dy) < SLIDE_LIMITE:
        return ("tap", x1, y1)
 
    if abs(dx) >= abs(dy):
        return ("D" if dx > 0 else "G", x1, y1)
    else:
        return ("B" if dy > 0 else "H", x1, y1)


def in_zone(pos, zone):
    tap,x,y=pos
    return zone[0] <= x <= zone[2] and zone[1] <= y <= zone[3]