import network
from time import sleep

wlan=network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Fomenal_freebox","B7AF8307C6")

while wlan.isconnected== False:
    sleep(0.1)
    
print('wifi connecter')

import upip
upip.install("micropython-phrew")