import os
from machine import Pin
import network 
from time import sleep

# Initialize the ESP32 as an access point

ap = network.WLAN(network.AP_IF)
ap.config(essid='ESP32-AP')
ap.active(True)

# Create a "music" directory if it does not exist
if 'music' not in os.listdir():
    os.mkdir('music')

# Start a simple HTTP server
import usocket as socket, ussl as ssl
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    # Wait for a client to connect
    conn, addr = s.accept()
    print("Connection from %s" % str(addr))

    # Read the request data
    request = conn.recv(1024).decode("latin-1")
    request_lines = request.split("\r\n")
    print(request_lines[0])

    # Check if the request is a GET request
    if request_lines[0].startswith("GET /"):
        # Open the index.html file
        try:
            with open("index.html", "r") as f:
                response = "HTTP/1.1 200 OK\r\n\r\n" + f.read()
        except:
            # If the file doesn't exist, send a 404 Not Found response
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

    elif request_lines[0].startswith("POST /music"):
        # Extract the filename from the request headers
        print(request_lines)
        for line in request_lines:
            if "filename" in line:
                filename = line.split(" ")[-1]
                break

        # Open the file for writing
        with open("music/" + filename, "wb") as f:
            # Read the file data from the request body
            while True:
                data = conn.recv(1024)
                if not data:
                    print("pas de data")
                    f.close()
                    break
                f.write(data)
        print("finie")       

        # Send a success response
        response = "HTTP/1.1 200 OK\r\n\r\n"
    else:
        # Send a 404 Not Found response
        response = "HTTP/1.1 404 Not Found\r\n\r\n"

    # Send the response
    conn.send(response.encode("utf-8"))

    # Close the connection
    conn.close()
