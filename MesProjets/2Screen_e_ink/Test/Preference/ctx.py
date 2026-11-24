from machine import ADC, Pin, I2C
from RealTimeClock import RTC
import t547
import renderdisplay
from gt911 import GT911

BOARD_SCL  = 17
BOARD_SDA  = 18
TOUCH_INT  = 47

display    = None
buf        = None
render     = None
rtc        = None
touch      = None
touch_event = None   # (x, y) rempli par l'ISR, remis à None après lecture

def _touch_irq(pin):
    global touch_event
    n, points = touch.read_points()
    if n > 0:
        touch_event = (points[0][0], points[0][1])

def init():
    global display, buf, render, rtc, touch

    rtc = RTC()

    display = t547.T547()
    display.init()
    display.clear()
    buf = display.get_buffer()

    render = renderdisplay.Render(buf, display.width(), display.height())
    render.set_orientation(90)
    render.set_font("HersheySansMed.bin")

    touch = GT911(I2C(scl=Pin(BOARD_SCL), sda=Pin(BOARD_SDA), freq=400000),
                  reset_pin=TOUCH_INT, irq_pin=TOUCH_INT, touch_points=1)
    Pin(TOUCH_INT, Pin.IN).irq(trigger=Pin.IRQ_FALLING, handler=_touch_irq)
