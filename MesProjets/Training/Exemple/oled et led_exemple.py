
from pyb import LED, Pin
from  time import sleep
from math import pow
from math import exp
from machine import Pin, SoftI2C
import ssd1306


# led = LED(1) # 1=red, 2=green, 3=yellow, 4=blue
# led.toggle()
# led.on()
# led.off()

#  Pin assignment 
i2c = SoftI2C(scl=Pin("Y6"), sda=Pin("Y7"))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.text('Go', 0, 0)
oled.show()
#respiration
smoothness_pts = 250
ii=0
pwm_val=0
gamma = 0.1 #affects the width of peak (more or less darkness)
beta = 0.5 #shifts the gaussian to be symmetric
  
  
# LEDs 3 and 4 support PWM intensity (0-255)
LED(4).intensity()    # get intensity
LED(4).intensity(128) # set intensity to half

p_in = Pin('X2', Pin.IN, Pin.PULL_UP)


intensity = 100

while True:
    
    #gestion de la respiration
    if ii<smoothness_pts:
        ii+=1
    else:
        ii=0
    pwm_val = 200*(exp(-(pow(((ii/smoothness_pts)-beta)/gamma,2.0))/2.0))
    
    if p_in.value() == False:
        intensity+=10
        if intensity>250:
             intensity=0
    
    # LEDs 3 and 4 support PWM intensity (0-255)
    LED(4).intensity(intensity) # set intensity to half
    LED(2).intensity(int(pwm_val))
    oled.text('intensity  ----', 0, 10)
    oled.show()
    oled.text('intensity %r'%(int(intensity)), 0, 10)
    oled.text('              ',0,20)
    oled.text('pwm_val %r'%(int(pwm_val)), 0, 20)
    oled.show()
    sleep(0.1)