import network
import webrepl
import time
from machine import Pin

led = Pin(2, Pin.OUT)

from machine import Pin
try:
  import usocket as socket
except:
  import socket


def web_page():
  html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
  <body><h1>Makerfabs Web Server</h1><a href=\"?led=on\"><button>ON</button></a>&nbsp;
  <a href=\"?led=off\"><button>OFF</button></a></body></html>"""
  return html


def app():
    wlan = network.WLAN(network.AP_IF)
    wlan.config(essid='monESP32')
    wlan.active(True)
    print(wlan.ifconfig())
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        #voir pour mettre un time outpour rafraichirles ensemble en dehors de la connexion.
        print('Got a connection from %s' % str(addr))
        led.value( not led.value())
        request = conn.recv(1024)
        request = str(request)
        print('Content = %s' % request)
        led_on = request.find('/?led=on')
        led_off = request.find('/?led=off')
        if led_on == 6:
          print('LED ON')
          led.value(0)
        if led_off == 6:
          print('LED OFF')
          led.value(1)
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()

app()