from time import sleep_ms
from machine import Pin

led=Pin(14,Pin.OUT)

for i in range(10):
    sleep_ms(500)
    led.value(not led.value())