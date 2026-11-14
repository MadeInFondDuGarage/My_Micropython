    
#import hershey_gothic_german as font

import t547
import HersheyFont_viper as HersheyFont
#import HersheyFont
import time



screen = t547.T547()
screen.init()
screen.clear()
buf=screen.get_buffer()

startime= time.ticks_ms()
import HersheyScriptMed as font
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("import py:", elapsed , "ms")

startime= time.ticks_ms()
renderer = HersheyFont.HersheyFontPy(font)
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("load py:", elapsed , "ms")

startime= time.ticks_ms()
rendererbin = HersheyFont.HersheyFontBin("HersheyScriptMed.bin")
elapsed = time.ticks_diff(time.ticks_ms(), startime)
print("load bin:", elapsed , "ms")

# renderer.draw_text(10,100,"Bonjour l'été, je suis enfin a lire du texte",255,buf,screen.width(),screen.height(),20)

#renderer.draw_text(10,300,"voir XXL",255,buf,screen.width(),screen.height(),80)

for i in range(0,5):
    startime= time.ticks_ms()
    renderer.draw_text(10,50+50*i,"Et ici en grande taille, avec 43 caractères .PY",255,buf,screen.width(),screen.height(),50)
    elapsed = time.ticks_diff(time.ticks_ms(), startime)
    print("render py:", elapsed , "ms")

    startime= time.ticks_ms()
    rendererbin.draw_text(10,300+50*i,"Et ici en grande taille, avec 43 caractères .BIN",255,buf,screen.width(),screen.height(),50)
    elapsed = time.ticks_diff(time.ticks_ms(), startime)
    print("render bin:", elapsed , "ms")

screen.show()
