from machine import ADC,Pin
from realtimeclock import RTC

import t547
import renderdisplay_v4 as renderdisplay                      

#from gt911 import GT911

#import HersheySansMed2 as font2
#import hershey_gothic_german as font2
#import EMSElfin as font
#import AkayaKanadaka_Regular as font

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

font= "fonts/HersheyScriptMed.bin"

screen = t547.T547()
screen.init()
screen.clear()
buf=screen.get_buffer()

renderfont = renderdisplay.Render(buf,screen.width(),screen.height())
renderfont.set_orientation(180)

renderfont.set_font(font)

renderfont.set_font_size(500)

#touch = GT911(touch_points=2)

renderfont.set_text("Ten")

renderfont.draw_text(0,100,0,15,"G","B") # je nettoie le buffer avec des 0, si je met -1 je ne touche pas au buffer, je supperpose a ce qui existe
renderfont.draw_text(150,100,0,15,"C","C")
renderfont.draw_text(50,100,0,15,"D","H")

renderfont.draw_line(0,100,960,100,255)
screen.show()



