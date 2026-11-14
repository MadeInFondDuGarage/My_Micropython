import network

  # start up network in access point mode  
wlan = network.WLAN(network.AP_IF)
wlan.config(essid="MonESP32")
#wlan.config(security=0) # disable password
wlan.active(True)