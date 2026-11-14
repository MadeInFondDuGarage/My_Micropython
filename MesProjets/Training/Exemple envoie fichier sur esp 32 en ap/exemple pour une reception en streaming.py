import socket
import io

def receive_file(conn):
    # Create a new BytesIO object
    buffer = io.BytesIO()

    # Receive data in chunks
    while True:
        data = conn.recv(1024)
        if not data:
            break
        buffer.write(data)

    # Get the file data
    file_data = buffer.getvalue()

    # Do something with the file data
    with open("music/file.mp3", "wb") as f:
        f.write(file_data)
    print("File received and saved")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
while True:
    conn, addr = s.accept()
    receive_file(conn)
    conn.close()

