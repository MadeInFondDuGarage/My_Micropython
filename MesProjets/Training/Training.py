
from machine import Pin # partie pour les io
import machine #pour les io
import pyb

irq_t4=False

def tick1(_):
    print('timer_1')
  
    
def tick2(_):
    print('timer_2')
    
def tick3(_):
    print('timer_3')

def tick4(_):
    print('timer_4')
    irq_t4=True
  
rtc = machine.RTC()
rtc.init()
rtc.datetime((2020, 12, 9, 7, 25, 0, 0, 0))
#tim1=pyb.Timer(1,period=1000,callback=tick1)
#tim2=pyb.Timer(2,period=15000,callback=tick2)
#tim3=pyb.Timer(3,period=22000,callback=tick3)
tim4=pyb.Timer(4,period=2000,callback=tick4)

print(rtc.datetime())

while 1:
  if irq_t4:
    print(rtc.datetime())
    irq_t4=False
  machine.sleep(1)
