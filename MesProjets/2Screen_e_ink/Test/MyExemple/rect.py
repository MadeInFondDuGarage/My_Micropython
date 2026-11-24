import t547
from time import sleep
import random

display = t547.T547()
display.init()
display.power(True)
display.clear()
gris=[0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240]

for x in range(16):
    display.fill_rect(x*20,20,20,20, gris[x])  

display.show()


