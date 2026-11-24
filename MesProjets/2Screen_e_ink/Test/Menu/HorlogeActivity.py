from machine import ADC,Pin
from RealTimeClock import RTC

import t547
import VecteurFont
#import HersheyScriptMed as font
import HersheySansMed as font
#import hershey_gothic_german as font
#import EMSElfin as font

def bat_voltage():
    #Batterie
    BATT_PIN =14
    adc = ADC(BATT_PIN)        # create an ADC object acting on a pin
    #---------------mesure de la baterie
    val = adc.read_uv()//5000   # valeur lue en microvolts et ramener en volt
    pc=(val-320)
    return pc

def read_time():
    i2c_rtc=RTC()
    i2c_rtc.Set_AddrRtc(81,0x02)
    return i2c_rtc.read_time()


def datetime_pc():
    
    renderfont.set_font(font)
    renderfont.set_orientation(orientation)
    screen.orientation(renderfont.ORIENTATION)
    renderfont.set_font_size(20)
    
    #j'écrit l'heure
    renderfont.set_text("%s" %(read_time()))
    renderfont.draw_text(5,renderfont.FONT_SIZE,255,0)

    #j'ecrit la valeur de la batterie
    renderfont.set_text("[%s %%]>" %(bat_voltage()))
    zone=renderfont.get_zone()
    renderfont.draw_text(renderfont.WIDTH-zone[2],renderfont.FONT_SIZE,255,0)

    #je clean
    screen.clean(0,zone[1],screen.height(),zone[3],0,0) # je nettoie l'écran sur la zone de l'affichage

    #j'affiche
    screen.show()

screen = t547.T547()
screen.init()
screen.clear()
buf=screen.get_buffer()
fontsize=25
orientation=90

renderfont = VecteurFont.VecteurFontPy(buf,screen.width(),screen.height())
renderfont.set_orientation(orientation)
screen.orientation(renderfont.ORIENTATION)
renderfont.set_font(font)

datetime_pc()
renderfont.set_font_size(30)
renderfont.set_titre(1)
renderfont.set_text("Essai de titre")
renderfont.draw_text(200,200,255,0,"D")
renderfont.draw_text(200,300,255,0,"G")
renderfont.draw_text(200,400,0,150,"C")
screen.show()



