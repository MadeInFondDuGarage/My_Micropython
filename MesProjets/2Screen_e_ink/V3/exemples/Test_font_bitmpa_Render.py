from machine import ADC,Pin
from realtimeclock import RTC
import gc

print(gc.mem_free())
import t547
print(gc.mem_free())
import renderdisplay_v5 as renderdisplay
#import renderdisplay
print(gc.mem_free())
import render_glyph_4bpp as rg

print(gc.mem_free())
screen = t547.T547()
print(gc.mem_free())
screen.init()
screen.clear()
print(gc.mem_free())
buf=screen.get_buffer()
#fontsize=50
print(gc.mem_free())
renderfont = renderdisplay.Render(buf,screen.width(),screen.height())
renderfont.set_orientation(0)
print(gc.mem_free())
renderfont.set_font("fonts/HersheySansMed.bin")
print(gc.mem_free())
renderfont.set_font_size(50)
texttemp="Test <i>d'un</i> <b>texte</b> é,è, ê ° à, &"
renderfont.set_text(texttemp)
print(gc.mem_free())
renderfont.set_bmp("themes/cyberpunk/Livres ouvert.bmp")
renderfont.draw_bmp(0,100,"C")
renderfont.draw_text(renderfont.BmpWIDTH +2 ,100,15,0,"L","C")
print(gc.mem_free())
rg.set_context(buf,screen.width(),screen.height())
rg.set_orientation(0)
rg.set_font("fonts/HersheyScriptMed.bin")
rg.set_font_size(50)
#rg.set_text("Test <i>d'un</i> <b>texte</b>")
rg.draw_text("Test <i>d'un</i> <b>texte</b> é,è, ê ° à, &",100,400,0,15,3,1)
#rg.set_font("fonts/EMSElfin.bin")
#rg.draw_text("Test <i>d'un</i> <b>texte</b>",100,200,0,15,3,1)
print(gc.mem_free())
#rg.set_font("fonts/hershey_gothic_german.bin")
#rg.draw_text("Test <i>d'un</i> <b>texte</b>",100,300,10,0,3,1)


screen.show()



