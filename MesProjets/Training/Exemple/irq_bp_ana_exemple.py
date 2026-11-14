from machine import Pin # partie pour les io
import machine #pour les io
import time #pour le delai
import gc #garbage collector pour la memoire

machine.freq(216000000) #changement de la frequence du proc

  
def PrintIRQ(_):
  print('interruption sur bp K1')
  print('Ana2: %s' %(pinAna2.read_u16()))
  print('mem:%s'%(gc.mem_free))

pinTest = Pin('PE3', Pin.IN, Pin.PULL_UP) #definition du bp en entrer
pinTest.irq(trigger=Pin.IRQ_FALLING ,handler=PrintIRQ)# puis ratacher a une interruption

#analogique
pinAna2=machine.ADC('PA2')
