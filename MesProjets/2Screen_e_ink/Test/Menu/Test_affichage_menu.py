from machine import ADC,Pin
from RealTimeClock import RTC

import t547
import renderdisplay

    
screen = t547.T547()
screen.init()
screen.clear()
buf=screen.get_buffer()


renderfont = renderdisplay.Render(buf,screen.width(),screen.height())
renderfont.set_orientation(90)

renderfont.set_font("HersheySansMed.bin")



def MenuLigne(render,bmp,texte,size,Numligne, ecart):
    pos=Numligne*ecart
    render.set_bmp(bmp)
    render.draw_bmp(10,pos,"C")
    render.set_font_size(size)
    render.set_text(texte)
    render.draw_text(render.BmpWIDTH +12 ,pos,0,15,"L","C")    


MenuLigne(renderfont,"Icones/H.bmp","Home",25,1,30)

#Livres en cours
MenuLigne(renderfont,"Icones/Livres ouvert.bmp","Livres en cours",40,2,100)

#Livres en cours
MenuLigne(renderfont,"Icones/Parcourir la carte SD.bmp","Parcourir la carte",40,4,100)


screen.show()




