import socket
client_socket = socket.create_connection(('192.168.1.17', 87))
client_socket.send('hello'.encode())