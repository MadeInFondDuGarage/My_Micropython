from time import sleep_ms
from array import array
from machine import Pin, I2C
import micropython

"""
This file is part of the OpenMV project.

Copyright (c) 2023 Ibrahim Abdelkader <iabdalkader@openmv.io>
Copyright (c) 2023 Kwabena W. Agyeman <kwagyeman@openmv.io>

GT911 5-Point Capacitive Touch Controller driver for MicroPython.

l'éssai d'un rotation via le gt911 directement a echouer car il y a un soucis le 0 ne se fait pas correctement sur 90 et 270
"""

#adresse dansle controleur
_DEFAULT_ADDR = const(0x5D)
_COMMAND = const(0x8040)
_REFRESH_RATE = const(0x8056)
_RESOLUTION_X = const(0x8048)
_RESOLUTION_Y = const(0x804A)
_TOUCH_POINTS = const(0x804C)
_MODULE_SWITCH1 = const(0x804D)
_CONFIG_CHKSUM = const(0x80FF)
_CONFIG_FRESH = const(0x8100)
_POINT_DATA_START = const(0x8150)
_DATA_BUFFER = const(0x814E)

#valeur par defaut pour ce touchscreen
TOUCH_POINTS=1
ADRESS=const(0x5D)
HwWIDTH=960 #élément de référence initial
HwHEIGHT=540 #éléments de référence initial
REFRESH_RATE=240
TOUCH_CALLBACK=None
POINTS_DATA=None

I2C_TOUCH=None
RST_PIN=None
IRQ_PIN_LABEL=None
IRQ_PIN=None

def init_touch():
    global TOUCH_CALLBACK,irq,POINTS_DATA
    
    if TOUCH_CALLBACK is "in": #je dirige vers l'interieur
        TOUCH_CALLBACK=touch_irq
    elif TOUCH_CALLBACK is None: # pas d'interruption
        TOUCH_CALLBACK =None
    else:
        TOUCH_CALLBACK = TOUCH_CALLBACK #ou une interruption vers l'exterieur
    
    irq=False
    
    _set_i2c_bus()
    _set_reset_irq_pin()
    # Reset the touch panel controller.
    reset()

    # Write and update the config.
    _push_config()

    # Allocate scratch buffer.
    POINTS_DATA = [array("H", [0, 0, 0, 0]) for x in range(5)]
    
@micropython.native
def _read_reg(reg, size=1, buf=None):
    if buf is not None:
        I2C_TOUCH.readfrom_mem_into(ADRESS, reg, buf, addrsize=16)
    else:
        return I2C_TOUCH.readfrom_mem(ADRESS, reg, size, addrsize=16)

@micropython.native
def _write_reg( reg, val, size=1):
    buf = bytes([val & 0xFF]) if size == 1 else bytes([val & 0xFF, val >> 8])
    I2C_TOUCH.writeto_mem(ADRESS, reg, buf, addrsize=16)
   
def _update_config():
    # Read current config
    chksum = ~sum(_read_reg(0x8047, 184)) + 1
    # Calculate checksum
    _write_reg(_CONFIG_CHKSUM, chksum)
    # Update the config
    _write_reg(_CONFIG_FRESH, 0x01)

@micropython.native
def _push_config():
    # Write and update the config.
    _write_reg(_RESOLUTION_X, HwWIDTH, 2)
    _write_reg(_RESOLUTION_Y, HwHEIGHT, 2)
    _write_reg(_TOUCH_POINTS, TOUCH_POINTS)
    _write_reg(
        _MODULE_SWITCH1,
        (int(False) << 7) #REVERSE_Y
        | (int(False) << 6) #REVERSE_X
        | (int(True) << 3) #REVERSE_AXIS
        | (int(True) << 2) #SITO
        | 0x01,
    )
    _write_reg(_REFRESH_RATE, (1000 * 1000) // (REFRESH_RATE * 100)) #avant 240 de rate
    _write_reg(_COMMAND, 0x00)
    _update_config()
    
def set_touch_point(points):
    global TOUCH_POINTS
    TOUCH_POINTS=points
    _push_config()
    
def _set_i2c_bus(BOARD_SCL=17,BOARD_SDA=18):
    global I2C_TOUCH
    I2C_TOUCH=I2C(scl=Pin(BOARD_SCL), sda=Pin(BOARD_SDA), freq=400000)

@micropython.native
def _set_reset_irq_pin(reset_pin=47,irq_p=47):
    global RST_PIN,IRQ_PIN_LABEL,IRQ_PIN
    RST_PIN = Pin(reset_pin, Pin.OUT, value=0)
    IRQ_PIN = None
    IRQ_PIN_LABEL = irq_p

def read_id():
    return _read_reg(0x8140, 4)

@micropython.native
def read_xy():
    # on met un try pour eviter les moment on interroge la puce mais qu'elle n'est pas prete. cela ne fiat pas planter le tous
    global POINTS_DATA
    try:
        _read_reg(_POINT_DATA_START, buf=POINTS_DATA[0])
        # We read an extra reserved byte, shift track ID to fix it.
        POINTS_DATA[0][-1] = POINTS_DATA[0][-1] >> 8
        _write_reg(_DATA_BUFFER, 0)
    except OSError:
        POINTS_DATA[0][0]=0
        POINTS_DATA[0][1]=0
    irq=False
    sleep_ms(100)
    return  POINTS_DATA[0][0],POINTS_DATA[0][1]

@micropython.native
def read_points():
    global POINTS_DATA
    try:
        status = _read_reg(_DATA_BUFFER)[0]
        n_points = status & 0x0F
        if status & 0x80:
            for i in range(0, n_points):
                _read_reg(_POINT_DATA_START + i * 8, buf=POINTS_DATA[i])
                POINTS_DATA[i][-1] = POINTS_DATA[i][-1] >> 8
            _write_reg(_DATA_BUFFER, 0)
    except OSError:
        n_points = 0
        POINTS_DATA[0][0]=0
        POINTS_DATA[0][1]=0
    irq = False
    return n_points, POINTS_DATA

def reset():
    global IRQ_PIN
    if IRQ_PIN is not None:
        IRQ_PIN.irq(handler=None)
    RST_PIN(0)
    sleep_ms(10)
    IRQ_PIN = Pin(IRQ_PIN_LABEL, Pin.OUT, value=0)#ici j'ai aussi enlever le _PP sur le out
    sleep_ms(50)
    RST_PIN(1)
    # Note must wait for at least 50ms before switching the IRQ pin to input.
    sleep_ms(100)
    if TOUCH_CALLBACK is not None:
        IRQ_PIN = Pin(IRQ_PIN_LABEL, Pin.IN, Pin.PULL_UP)
        IRQ_PIN.irq(handler=TOUCH_CALLBACK, trigger=Pin.IRQ_FALLING)
    
def touch_irq(t):
    #c'est l'appel en interne pour une interruption simple, mais on peut mettre une version externe aussi via le paramétrage
    irq=True
    
@micropython.native
def get_HwOrientation(phyX,phyY,deg):
    #transforme les entrées physique vers les valeurs logique pour relier avec la position des menu
    x=phyX
    y=phyY
    if deg > 360:
        deg=deg-360
        
    if 0 <= deg < 90:
        x= phyX
        y=HwHEIGHT - 1 - phyY
    
    elif 90 <= deg < 180:
        x= phyY
        y= phyX

    elif 180 <= deg < 270:
        x = HwWIDTH - 1 - phyX
        y = phyY
        
    elif 270<= deg < 360:
        x = HwHEIGHT - 1 - phyY
        y = HwWIDTH - 1 - phyX
    
    return x,y

@micropython.native
def wait_touch(deg=0):
    #je fais une boucle pour attendre un touc mais par précaution j'utilise un bouton externe pour pouvoir en sortir si besoin
    #l'objectif est d'avoir le branchement du touch ici, pour plustard utiliser un sleep profond
    # et pouvoir utilise le 10 pour le reveil et réduire la consomation elec.
    SLIDE_LIMITE = 40  # px minimum pour considérer un slide
    
    bouton_1 = Pin(21,Pin.IN) #pour être sur que le bouton 1 soit bien init
    
    x2, y2, x1, y1=0,0,0,0
    
    touch_ok=False
    while bouton_1.value():
        sleep_ms(50)
        n, points = read_points() #je lit le point
        if n>0 and touch_ok==False: #si j'ai au moins  point
            x1, y1 = get_HwOrientation(points[0][0], points[0][1],deg) #je lit
            x2, y2 = x1, y1
            touch_ok=True
        elif n>0 and touch_ok==True: #ensuite je continue a lire jusqu'au lever du doigt
            x2, y2 = get_HwOrientation(points[0][0], points[0][1],deg) #je lit
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
def in_zone_col(pos, Numcol, ecart,espacement=75):
    tap,x,y=pos
    zone_x1=Numcol*ecart-espacement
    zone_x2=Numcol*ecart+espacement
    return zone_x1 <= x <= zone_x2

@micropython.native
def get_zone_line(pos, ecart,espacement=75):
    tap,x,y=pos
    ligne=y//ecart
    
    # vérification qu'on est bien dans la zone
    zone_y1 = ligne * ecart - espacement
    zone_y2 = ligne * ecart + espacement

    if zone_y1 <= y <= zone_y2:
        return ligne
    else:
        return None

@micropython.native
def get_zone_col(pos, ecart,espacement=75):
    tap,x,y=pos
    colonne=x//ecart
    
    # vérification qu'on est bien dans la zone
    zone_x1 = colonne * ecart - espacement
    zone_x2 = colonne * ecart + espacement

    if zone_x1 <= x <= zone_x2:
        return colonne
    else:
        return None
    
def get_zone(pos, ecart,espacement=75):
    ligne=get_zone_line(pos,ecart,espacement)
    colonne=get_zone_col(pos, ecart,espacement)
    return ligne,colonne
    
if __name__=="__main__":
    
    bouton_1 = Pin(21,Pin.IN)
    init_touch()
    mouv=None
    orientation =0
    while bouton_1.value():
        mouv,x,y=wait_touch(orientation)
        print(mouv,x,y,orientation)
        print(get_zone((mouv,x,y),100))
        if mouv=="H":
            orientation=orientation+90
            print(orientation)