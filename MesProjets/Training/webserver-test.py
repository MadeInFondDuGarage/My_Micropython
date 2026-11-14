mport network
import usys
try:
    import usocket as socket
except:
    import socket

def connect(SSID,PASS):
    AP = network.WLAN(network.AP_IF)
    if AP.isconnected():
        print("Already connected.")
        return AP
    else:
        AP.active(True)
        AP.connect(SSID,PASS)
        while not AP.isconnected():
            print(".",end="")
            utime.sleep(0.5)
    
    if AP.isconnected():
        print("Network connection is established.")
        return AP
    else:
        print("Connection failed.")
        return False

wifi = connect("myssid","mypass")
if not wifi:
    usys.exit(0)

html_strings = """
<!DOCTYPE html>
<html lang='ja'>
    <head>
        <meta charset='utf-8'>
        <title>SERVER TEST</title>
    </head>
    <body>
        <h1>SERVER TEST</h1>
    </body>
</html>
"""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addr = socket.getaddrinfo("127.0.0.1", 80)
s.bind(addr)
s.listen(1)
print("Linstening on ", addr)

while True:
    conn,addr = s.accept()
    print("connected from : ",addr)
    request = conn.recv(1024)
    response = html_strings
    conn.send("HTTP/1.0 200 OK\r\n")
    conn.send("Content-type: text/html\r\n")
    conn.send("\r\n")
    conn.send(response)
    conn.close()
