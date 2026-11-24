from machine import ADC,Pin
from realtimeclock import RTC

import t547
import renderdisplay

    
screen = t547.T547()
screen.init()
screen.clear()
buf=screen.get_buffer()
fontsize=50

renderfont = renderdisplay.Render(buf,screen.width(),screen.height())
renderfont.set_orientation(90)

renderfont.set_font("fonts/HersheySansMed.bin")

renderfont.set_font_size(50)
texttemp="Test d'un <b>texte</b>"
renderfont.set_text(texttemp)


renderfont.set_bmp("Icones/Livres ouvert.bmp")
renderfont.draw_bmp(0,100,"C")
renderfont.draw_text(renderfont.BmpWIDTH +2 ,100,0,15,"L","C")


screen.show()



