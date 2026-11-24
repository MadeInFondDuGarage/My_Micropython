from machine import Pin, ADC
import micropython
import utime
from realtimeclock import RTC


import time

import myrenderdisplay as rd

from gt911 import GT911

import sauve_parametre.preferences as preferences #j'inmporte les préférences

#variable global
preferences.charge_prefs()
theme=f"themes/{preferences.get_pref('theme')}"
preferences.sauve_prefs()

sys_font=f"fonts/{preferences.get_pref('police_sys')}.bin"
rd.set_font(sys_font)

#les interfaces extérieurs
touch = GT911(touch_points=1)
bouton_1 = Pin(21,Pin.IN)

#init pour le rtc
i2c_rtc=RTC()
i2c_rtc.Set_AddrRtc(81,0x02)

def mesure_time(label=None):

    def decorator(func):
        name = label or func.__name__

        def wrapper(*args, **kwargs):
            start = utime.ticks_us()
            result = func(*args, **kwargs)
            end = utime.ticks_us()

            print("[TIME] {} -> {} ms".format(
                name,
                utime.ticks_diff(end, start)/1000
            ))

            return result

        return wrapper

    return decorator

#@mesure_time("menuligne")
@micropython.native
def MenuLigne(bmp,texte,size,Numligne, ecart):
    pos=Numligne*ecart
    d,w,h=rd.get_orientation()
    rd.set_bmp(bmp)
    rd.draw_bmp(15,pos,"C")
    rd.set_font_size(size)
    rd.draw_line(0,pos+50,w,pos+50,5)
    rd.draw_line(0,pos-50,w,pos-50,5)
    rd.set_font_size(size)
    rd.draw_text(texte,rd.BmpWIDTH +12 ,pos,0,15,"L","C")

#@mesure_time("paramligne")
def ParamLigne(texte,info,size,Numligne,ecart):
    pos=Numligne*ecart
    rd.set_font_size(size)
    rd.draw_text(texte,10,pos,0,15,"G","B")
    rd.draw_text(info,10,pos,0,15,"D","B")

#@mesure_time("simpleligne")
def SimpleLigne(texte,justif,size,Numligne,ecart):
    pos=Numligne*ecart
    rd.set_font_size(size)
    rd.draw_text(texte,10,pos,0,15,justif,"C")


@micropython.native
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
            x1, y1 = rd.get_HwOrientation(points[0][0], points[0][1]) #je lit
            x2, y2 = x1, y1
            touch_ok=True
        elif n>0 and touch_ok==True: #ensuite je continue a lire jusqu'au lever du doigt
            x2, y2 = rd.get_HwOrientation(points[0][0], points[0][1]) #je lit
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

@micropython.native
def in_zone(pos, zone):
    tap,x,y=pos
    return zone[0] <= x <= zone[2] and zone[1] <= y <= zone[3]

@micropython.native
def in_zone_line(pos, Numligne, ecart,espacement=75):
    tap,x,y=pos
    zone_y1=Numligne*ecart-espacement
    zone_y2=Numligne*ecart+espacement
    return zone_y1 <= y <= zone_y2

@micropython.native
def get_zone_line(pos, ecart):
    tap,x,y=pos
    ligne=y//ecart
    return ligne

@micropython.native
def show_clav_num(couleur=0):
    rd.set_font_size(70)
    rd.draw_text("<b>1    2    3</b>",0,700,couleur,15,"C","C")
    rd.draw_text("<b>4    5    6</b>",0,800,couleur,15,"C","C")
    rd.draw_text("<b>0   RT  OK</b>",0,900,couleur,15,"C","C")

@micropython.native
def val_clav_num(pos):
    #pos pour le retour touchscreen,
    d,w,h=rd.get_orientation()
    tiers= w//3
    val=-3
    if pos[1]<tiers:
        val=1
    elif tiers < pos[1] < tiers*2:
        val=2
    elif tiers*2 < pos[1] < tiers*3:
        val=3
    if in_zone_line(pos,7,100,50):
        return val
    if in_zone_line(pos,8,100,50):
        return val+3
    if in_zone_line(pos,9,100,50):
        if val==1: #0
            return 0
        elif val== 2:
            return -1
        elif val == 3: #ok
            return -2
    return -3

