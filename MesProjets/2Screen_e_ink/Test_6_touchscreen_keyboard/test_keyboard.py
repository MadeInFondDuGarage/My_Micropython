from gt911 import GT911
from keyboard_touch import TouchKeyboard
import machine
from machine import ADC,Pin,Timer, I2C,SPI
from time import sleep

def init_touch(point=1):
    # Touch screen
    BOARD_SCL =17
    BOARD_SDA =18
    TOUCH_INT =47
    #--préparation du touchscreen
    touch = GT911(I2C(scl=Pin(BOARD_SCL), sda=Pin(BOARD_SDA), freq=400000), reset_pin=TOUCH_INT, irq_pin=TOUCH_INT, touch_points=point) #on peut monter avec plus de point
    return touch

def touch_screen_irq(t):
    xy=touch.read_xy()
    print(keys.handle_keypress(xy))
        
def touch_irq():
    TOUCH_INT =47
    irq_touch=Pin(TOUCH_INT,Pin.IN)
    irq_touch.irq(trigger=Pin.IRQ_FALLING, handler=touch_screen_irq)

#interruption pour le touch screen
#irq_touch.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=touch_screen)

if __name__ == "__main__":
    BOARD_SCL =17
    BOARD_SDA =18
    TOUCH_INT =47
    touch = GT911(I2C(scl=Pin(BOARD_SCL), sda=Pin(BOARD_SDA), freq=400000), reset_pin=TOUCH_INT, irq_pin=TOUCH_INT, touch_points=1) #on peut monter avec plus de point
    TOUCH_INT =47
    irq_touch=Pin(TOUCH_INT,Pin.IN)
    irq_touch.irq(trigger=Pin.IRQ_FALLING, handler=touch_screen_irq)
    keys=TouchKeyboard()