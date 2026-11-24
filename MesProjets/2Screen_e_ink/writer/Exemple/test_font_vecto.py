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
    
screen = t547.T547()
screen.init()
screen.clear()
buf=screen.get_buffer()
fontsize=50

renderfont = VecteurFont.VecteurFontPy(buf,screen.width(),screen.height())
renderfont.set_orientation(270)
renderfont.set_font(font)

# renderfont.set_text('Test pour font normal')
# renderfont.set_size(fontsize)
# renderfont.draw_text(5,fontsize,255)
# renderfont.set_text('Test <b>pour <i>font</b> dingue</i> en gras')
# renderfont.draw_text(5,fontsize*2,255)
# renderfont.set_text("Test de <i>l'italic</i>")
# renderfont.draw_text(5,fontsize*3,255)
# renderfont.set_size(25)
#renderfont.set_text("%s      %s %%" %(read_time(),bat_voltage()))
#renderfont.draw_text(5,fontsize*5,255)
texttemp="<i>Truc phq</i>"


renderfont.set_text(texttemp)
renderfont.draw_text(50,50,200,0) # je nettoie le buffer avec des 0, si je met -1 je ne touche pas au buffer, je supperpose a ce qui existe
zone=renderfont.get_zone()
screen.orientation(renderfont.ORIENTATION)
screen.clean(zone[0],zone[1],zone[2],zone[3],0,0) # je nettoie l'écran sur la zone de l'affichage

# screen.orientation(90)
# screen.clean(100,100,100,200,100,2)
# renderfont.orientation(90)
# renderfont.set_text(texttemp)
# renderfont.draw_text(5,fontsize*3,255)
# screen.orientation(180)
# screen.clean(100,100,100,200,100,2)
# renderfont.orientation(180)
# renderfont.set_text(texttemp)
# renderfont.draw_text(5,fontsize*3,255)
# screen.orientation(270)
# screen.clean(100,100,100,200,100,2)
# renderfont.orientation(270)
# renderfont.set_text(texttemp)
# renderfont.draw_text(5,fontsize*3,255)

screen.show()



