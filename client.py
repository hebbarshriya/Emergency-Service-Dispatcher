import socket
import time

# The client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print('Waiting for connection')
try:
    client_socket.connect(('192.168.224.35', 12354))
except socket.error as e:
    print(str(e))


# Send the emergency request to the server

emergency_type = input("Enter type of emergency:\n 1:fire\n 2:police\n 3:medical\n")
client_socket.send(str(emergency_type).encode())
address = input("Enter address:")
client_socket.send(( address).encode())

name=client_socket.recv(1024).decode()
print(name+' has been notified\n')

# Receive the ETA from the server
eta = float(client_socket.recv(1024).decode())
# Print the ETA
print('Estimated time of arrivalin minutes : ', eta)
time.sleep(eta)

status=input("Enter anything when help has arrived\n")
client_socket.send(str(status).encode())

# Close the client socket
client_socket.close()
