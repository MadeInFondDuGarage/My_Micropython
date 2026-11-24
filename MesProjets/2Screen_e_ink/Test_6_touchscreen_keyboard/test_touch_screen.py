from gt911 import GT911
from machine import ADC,Pin,Timer, I2C,SPI

def init_touch(point=1):
    # Touch screen
    BOARD_SCL =17
    BOARD_SDA =18
    TOUCH_INT =47
    #--préparation du touchscreen
    touch = GT911(I2C(scl=Pin(BOARD_SCL), sda=Pin(BOARD_SDA), freq=400000), reset_pin=TOUCH_INT, irq_pin=TOUCH_INT, touch_points=point) #on peut monter avec plus de point
    return touch

def touch_screen_irq(t):
    n, points = touch.read_points()
    for i in range(0, n):
        print(f"id {points[i][3]} x {points[i][0]} y {points[i][1]} size {points[i][2]}")
        
def touch_irq():
    TOUCH_INT =47
    irq_touch=Pin(TOUCH_INT,Pin.IN)
    irq_touch.irq(trigger=Pin.IRQ_FALLING, handler=touch_screen_irq)

if __name__ == "__main__":
    #touch = GT911(I2C(scl=Pin(BOARD_SCL), sda=Pin(BOARD_SDA), freq=400000), reset_pin=TOUCH_INT, irq_pin=TOUCH_INT, touch_points=2) #on peut monter avec plus de point
    touch = init_touch(2)
    TOUCH_INT =47
    irq_touch=Pin(TOUCH_INT,Pin.IN)
    irq_touch.irq(trigger=Pin.IRQ_FALLING, handler=touch_screen_irq)

    