# !/usr/bin/python
"""Example using a character LCD connected to an ESP8266."""

from time import sleep
from LCD import CharLCD

lcd = CharLCD(rs='Y1', en='Y2', d4='Y3', d5='Y4', d6='Y5', d7='Y6',
                  cols=20, rows=4)

    # Print a 2 line centered message
for i in range(50):
    #lcd.clear()
    lcd.set_line(0)
    lcd.message('%r' %(i))
    lcd.set_line(3)
    lcd.message('test')
    #sleep(0.1)


    
