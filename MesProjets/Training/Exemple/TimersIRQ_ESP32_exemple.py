
from machine import Pin,Timer # partie pour les io



def tick1(t):
    print('timer_1')

    

tim=Timer(1) # de 1 a 4 pour l'esp32
tim.init(mode=Timer.PERIODIC, period=1000, callback=tick1) #create tim object,and init timer id = 2 , frequency = 2
    

