import socket
import sys
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('192.168.0.101', 10010)
print('starting up on %s port %s' % server_address, file=sys.stderr)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

#Open output pcm file
f = open("mic_separated.pcm", "wb")

try:
    while True:
        # Wait for a connection
        print('waiting for a connection', file=sys.stderr)
        connection, client_address = sock.accept()

        # Check variable for terminal output
        check = 0
        
        try:
            print('connection from', client_address, file=sys.stderr)

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(1024)
                if data:
                    if (check<1): print("receiving data ...")
                    f.write(data)
                    check+= 1

                else:
                    print('no more data from', client_address, file=sys.stderr)
                    break   
        
        finally:
            # Clean up the connection
            connection.close()
            f.close()

except KeyboardInterrupt:
    print('Interrupted')