import sys
import socket
import selectors
import types

# Create the default selector (epoll, kqueue, or select based on OS)
sel = selectors.DefaultSelector()

# Define messages to be sent to the server
messages = [b'Message 1 from cleint 1', b'Message 2 from client 2']

def start_connections(host, port, num_conns):
    server_addr = (host, port)  # Server address as a tuple

    # Loop to start multiple client connections
    for i in range(num_conns):
        connid = i + 1  # Unique connection ID
        print(f'starting connection {connid} to {server_addr}')

        # Create a non-blocking TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)  # Non-blocking mode is essential for use with selectors

        # Initiate connection to the server (non-blocking version)
        sock.connect_ex(server_addr)

        # Register interest in both read and write events
        events = selectors.EVENT_READ | selectors.EVENT_WRITE

        # Create a SimpleNamespace to store connection-specific data
        data = types.SimpleNamespace(
            connid=connid,                            # Connection ID
            msg_total=sum(len(m) for m in messages), # Total number of bytes to send
            recv_total=0,                             # Total number of bytes received so far
            messages=messages.copy(),                 # Copy of the message list for this connection
            outb=b'',                                 # Buffer for outgoing data
        )

        # Register the socket with the selector and attach the connection data
        sel.register(sock, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
            print(f"Received {recv_data!r} from connection {data.connid}")
            data.recv_total += len(recv_data)
        else:
            print(f"Closing connection {data.connid}")
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
