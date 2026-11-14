
from machine import Pin # partie pour les io
import machine #pour les io


def tick1(t):
    print('timer_1')

    

machine.Timer.init(mode=machine.Timer.ONE_SHOT, period=1000, callback=tick1) #create tim object,and init timer id = 2 , frequency = 2
    
pinTest = Pin('PE3', Pin.IN, Pin.PULL_UP) #definition du bp en entrer

pinAna3=machine.ADC('PA3')


