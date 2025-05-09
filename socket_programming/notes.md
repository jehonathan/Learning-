### Documentation for multiconn_server.py

---

#### **Overview**
This script implements a multi-connection TCP server using Python's `selectors` module for efficient I/O multiplexing. The server can handle multiple client connections simultaneously without blocking, making it scalable and suitable for high-performance networking applications.

---

### **How It Works**
1. **Listening Socket**:
   - The server creates a listening socket bound to a specified host and port.
   - The socket is set to non-blocking mode and registered with the selector to monitor for incoming connection events.

2. **Selector**:
   - The `selectors.DefaultSelector` is used to monitor multiple sockets for I/O events (read or write readiness).
   - The selector waits for events and dispatches them to appropriate handlers:
     - `accept_wrapper`: Handles new client connections.
     - `service_connection`: Handles I/O operations for existing client connections.

3. **Event Loop**:
   - The server runs an infinite loop, waiting for events on registered sockets.
   - Based on the event type, it either accepts a new connection or processes data for an existing connection.

4. **Graceful Shutdown**:
   - The server can be stopped with a keyboard interrupt (`Ctrl+C`), and resources are cleaned up properly.

---

### **Usage**
Run the script from the command line, providing the host and port as arguments:

```bash
python multiconn_server.py <host> <port>
```

- `<host>`: The IP address or hostname to bind the server (e.g., `127.0.0.1`).
- `<port>`: The port number to bind the server (e.g., `8080`).

Example:
```bash
python multiconn_server.py 127.0.0.1 8080
```

---

### **Code Breakdown**

#### **Imports**
```python
import sys
import socket
import selectors
import types
```
- `sys`: Used to read command-line arguments.
- `socket`: Provides low-level networking interfaces.
- `selectors`: Enables efficient I/O multiplexing.
- `types`: Used to create a namespace for storing connection-specific data.

---

#### **Global Variables**
```python
sel = selectors.DefaultSelector()
```
- `sel`: The selector object used to monitor sockets for I/O events.

---

#### **Listening Socket Setup**
```python
host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)
```
- A TCP socket is created, bound to the specified host and port, and set to listen for incoming connections.
- The socket is set to non-blocking mode and registered with the selector to monitor for `EVENT_READ` (incoming connections).

---

#### **Main Event Loop**
```python
try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting...")
finally:
    sel.close()
```
- The server continuously waits for events on registered sockets.
- If the event is on the listening socket (`key.data is None`), a new connection is accepted.
- If the event is on a client socket, the connection is serviced.

---

#### **Accepting New Connections**
```python
def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
```
- Accepts a new client connection.
- Sets the client socket to non-blocking mode.
- Creates a `SimpleNamespace` object to store connection-specific data:
  - `addr`: The client's address.
  - `inb`: Buffer for incoming data.
  - `outb`: Buffer for outgoing data.
- Registers the client socket with the selector to monitor for both `EVENT_READ` and `EVENT_WRITE`.

---

#### **Handling Client Connections**
```python
def service_connection(key, mask):
    socket = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = socket.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(socket)
            socket.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb} to {data.addr}")
            sent = socket.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
```
- **Read Events**:
  - Reads up to 1024 bytes of data from the client.
  - If data is received, it is appended to the `outb` buffer for echoing back to the client.
  - If no data is received, the client has disconnected, so the socket is unregistered and closed.
- **Write Events**:
  - Sends data from the `outb` buffer back to the client.
  - Removes the sent data from the buffer.

---

### **Key Features**
1. **Non-Blocking I/O**:
   - The server uses non-blocking sockets to handle multiple clients concurrently without blocking.

2. **Efficient I/O Multiplexing**:
   - The `selectors` module allows the server to monitor multiple sockets efficiently.

3. **Scalability**:
   - The server can handle many clients simultaneously without creating a thread or process for each connection.

4. **Graceful Shutdown**:
   - The server handles keyboard interrupts and cleans up resources properly.

---

### **Example Output**
When the server is running, it will display messages like:
```
Listening on ('127.0.0.1', 8080)
Accepted connection from ('127.0.0.1', 54321)
Echoing b'Hello, server!' to ('127.0.0.1', 54321)
Closing connection to ('127.0.0.1', 54321)
```

---

### **Limitations**
- The server currently echoes received data back to the client. Additional logic can be added to process the data further.
- The server does not implement SSL/TLS for secure communication.

---

### **Conclusion**
This script demonstrates how to build a scalable, non-blocking TCP server using Python's `selectors` module. It is a great starting point for developing more complex networking applications.