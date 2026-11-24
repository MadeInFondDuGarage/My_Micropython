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
#import HersheyScriptMed as font
#import HersheySansMed as font
import hershey_gothic_german as font
#import EMSElfin as font


screen = t547.T547()
screen.init()
screen.clear()
buf=screen.get_buffer()

renderer = HersheyFont.HersheyFontPy(font)
renderer.orientation(90)
renderer.set_screen(buf,screen.width(),screen.height())
for i in range(0,6):
    renderer.set_text('¼¼¼¼¼¼¼¼¼0')
    renderer.set_size(i*10)
    renderer.draw_text(10,6+(10*i)*i,255)
screen.show()
print(renderer.get_max())



