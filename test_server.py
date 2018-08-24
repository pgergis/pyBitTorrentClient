import socket
from threading import Thread

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 8000))
serversocket.listen(5) # become a server socket, maximum 5 connections

def handle(connection, address):
    print('Received connection from {}'.format(address))
    running = True
    received = b''
    while running:
        buf = connection.recv(2048)
        if len(buf) > 0:
            print(buf)
        received += buf
        if b'FINISHED' in received:
            running = False
    print('Closing connection from {}'.format(address))

while True:
    connection, address = serversocket.accept()
    t = Thread(target=handle, args=(connection, address))
    t.start()
