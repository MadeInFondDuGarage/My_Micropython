from gt911 import GT911
from machine import I2C, Pin


def touch_screen_irq(t):
    n, points = touch.read_points()
    global touch_event
    touch_event=(n, points)
    for i in range(0, n):
        print(f"id {points[i][3]} x {points[i][0]} y {points[i][1]} size {points[i][2]}")

touch_event=None

if __name__ == "__main__":
    #touch = GT911(touch_points=2,touch_callback=touch_screen_irq)
    touch = GT911(touch_points=2)
    
    while 1:
        print(touch.read_points())



    