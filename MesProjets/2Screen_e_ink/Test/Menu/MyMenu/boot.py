import machine
import time

#bouton physique pour bypass le main en cas de soucis
btn = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_UP)  # adapte le pin

time.sleep_ms(200)  # laisse le pin se stabiliser

if btn.value() == 0:  # bouton appuyé (pull-up donc actif bas)
    print("Safe mode - boot annulé")
else:
    print("Départ du main.py")
    #import main
