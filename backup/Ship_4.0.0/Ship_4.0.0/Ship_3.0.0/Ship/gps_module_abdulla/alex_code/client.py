import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pi_host = '172.20.10.14'  # Replace with Raspberry Pi's IP address
pi_port = 49159 # Must be the same port as the server
client_socket.connect((pi_host, pi_port))
