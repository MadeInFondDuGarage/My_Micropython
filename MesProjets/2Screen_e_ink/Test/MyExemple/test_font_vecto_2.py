""" résultat des test sur esp 32 avec le mode viper en .py
partie ligne par ligne
affiche 5 pages en: 33844 ms
affiche 1 pages en: 6768.8 ms

partie page complet en une seul fois
affiche 5 pages en: 11865 ms
affiche 1 pages en: 2373.0 ms
"""   


import t547
import HersheyFont_viper as HersheyFont
import time
#import HersheyScriptMed as font
#import HersheySansMed as font
#import hershey_gothic_german as font
import EMSElfin as font

screen = t547.T547()
screen.init()
screen.clear()
buf=screen.get_buffer()

renderer = HersheyFont.HersheyFontPy(font)
startime= time.ticks_ms()

for cycle in range(5):
    for i in range(0,10):
        screen.clean(0,10+50*i,950,50,1,2)
        renderer.draw_text(10,50+50*i,"Et ici en grande taille, avec 45 caractères %s"%(i*cycle),255,buf,screen.width(),screen.height(),50)
        screen.show(0,10+50*i,950,50)
        
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("affiche 5 pages en:", elapsed , "ms")
print("affiche 1 pages en:", elapsed/5 , "ms")

screen.clear()

startime= time.ticks_ms()

for cycle in range(5):
    for i in range(0,10):      
        renderer.draw_text(10,50+50*i,"Et ici en grande taille, avec 45 caractères %s"%(i*cycle),255,buf,screen.width(),screen.height(),50)
    screen.show()
    time.sleep_ms(500)
    screen.clean(0,0,950,520,1,2)

elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("affiche 5 pages en:", elapsed -(500*5), "ms")
print("affiche 1 pages en:", (elapsed-500*5)/5 , "ms")

