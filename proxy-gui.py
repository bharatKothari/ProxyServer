import sys
import socket
import threading
import time
import tkinter as tk


HOST = '0.0.0.0'  # all local IPs
PORT = 8888  # Port number
max_conn = 5  # Maximim connection queues
buffer_size = 1024  # Maximum Socket buffer size
sock_timeout = 0.5  # Timeout for socket actions
cache_entries = []  # List of cached pages
cache_max = 30  # Max size of cache list
# Connection established message to be sent to client
conn_est = (
    "HTTP/1.0 200 connection established\r\nProxy-Agent: Pyx\r\n\r\n".encode())

print('\nProxy configuration:\n\n')

print(f'HOSTNAME: {HOST}')
print(f'Port: {PORT}')
print(f'Maximum connections: {max_conn}')
print(f'Socket Buffer size: {buffer_size}')
print(f'Socket timeout: {sock_timeout}')
print(f'Maximum cache entries: {cache_max}')

class Proxy:
    """A threaded HTTP and HTTPS web proxy with
    HTTP caching and dynamic blocking/unblocking of websites."""
    terminal = sys.stdout  # Save old terminal
    blocked_sites = ["www.google.com"]  # Websites not to connect to
    exit = False  # Exit flag for all threads

    def start(self):
    
        print("Starting Proxy")
        console = tk.Tk()

        # Block a website
        def block():
            webserver = block_input.get()
            if webserver is not None:
                self.blocked_sites.append(webserver)
                print("blocked", webserver)

        # Unblock a website
        def unblock():
            webserver = unblock_input.get()
            if webserver is not None:
                if webserver in self.blocked_sites:
                    self.blocked_sites.remove(webserver)
                print("unblocked", webserver)

        # Terminate Proxy
        def close():
            self.exit = True
            sys.stdout = self.terminal
            console.destroy()

        # Input for blocking websites
        block_input = tk.Entry(console)
        block_input.grid(row=0, column=0)

        # Input for unblocking websites
        unblock_input = tk.Entry(console)
        unblock_input.grid(row=1, column=0)

        # Block button
        block_button = tk.Button(console, text="BLOCK", command=block)
        block_button.grid(row=0, column=1)

        # Unblock button
        unblock_button = tk.Button(console, text="UNBLOCK", command=unblock)
        unblock_button.grid(row=1, column=1)

        # Close window button
        console.protocol("WM_DELETE_WINDOW", close)

        # Redirect terminal to console
        text = tk.Text(console)
        text.grid(row=2, columnspan=2)
        sys.stdout = self.Std_redirector(text)

        # Start proxy thread
        thread = threading.Thread(target=self.proxy, args=())
        thread.start()

        tk.mainloop()

    def proxy(self):
        """Main proxy thread: listens for client requests,
        instantiates new threads to handle each request"""
        try:
            # Initiate Socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            sock.bind((HOST, PORT))  # Bind Socket for Listen
            sock.listen(max_conn)  # Start Listening for Incoming Conditions

        # Failed to initialize socket
        except Exception as e:
            print(e)
            print("Unable to Initialize Socket")
            sys.exit(2)

        print("Server started successfully")
        sock.settimeout(sock_timeout)

        while True:
            try:
                # User terminates proxy
                if self.exit:
                    sock.close()
                    print("\nServer shut down successfully")
                    sys.exit(1)

                # Get request from client
                conn, addr = sock.accept()  # Accept Conn from Client Browser
                conn.settimeout(sock_timeout)  # Set request timeout
                data = conn.recv(buffer_size)  # Receive Client Data
                thread = threading.Thread(target=self.conn_string,
                                          args=(conn, data, addr))
                thread.start()  # Start a thread
            except Exception:
                pass

        sock.close()
        sys.exit(2)

    def conn_string(self, conn, data, addr):
        """Gets webserver and port, checks if blocked,
        forwards to HTTP or HTTPS proxy function"""
        try:
            # Process client request
            url = data.decode().lower()
            url = url.split('host: ')[1]
            url = url.split('\r\n')[0]
            port_pos = url.find(":")

            # default (http)
            if port_pos == -1:
                port = 80
                webserver = url
            # find port (https)
            else:
                port = int(url[(port_pos + 1):])
                webserver = url[:port_pos]

            # Check if blocked
            if webserver in self.blocked_sites:
                print("BLOCKED")
                conn.close()
                return

            # Determine nature of request
            request = data.decode()
            request = request.split(' ')[0]
            if request == "CONNECT":
                self.https_proxy_server(webserver, port, conn, addr)
            else:
                self.http_proxy_server(webserver, port, conn, addr, data)
        except Exception:
            pass

    def http_proxy_server(self, webserver, port, conn, addr, data):
        """Checks if request is already in cache.
        if present, checks if server has modified since cache entry
        if not, forwards cached copy to client.
        otherwise gets response from server, forwards to client
        and caches response.

        Cache entry is now highest priority"""
        print(webserver)
        start = time.time()
        end = time.time()

        # Check cache
        url = data.decode()
        url = url.split(' ')[1]
        cached = None
        for entry in cache_entries:
            if entry[0] == url:
                cached = entry
                break

        try:
            # Initiate socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((webserver, port))  # Connect to server
            sock.settimeout(sock_timeout)
            conn.settimeout(sock_timeout)

            # Check if modified since put into cache and remove entry
            if cached:
                print("Cache Hit")
                cache_entries.remove(cached)
                request = data.decode()
                request = request.split("\r\n", 1)
                check_time = request[0] + "\r\n"
                check_time += "If-Modified-Since: " + cached[2] + "\r\n"
                check_time += request[1]
                sock.send(check_time.encode())  # Ask server for modified time

            # Remove least recently accessed cache entry
            else:
                print("Cache Miss")
                if len(cache_entries) >= cache_max:
                    cache_entries.pop()
                sock.send(data)  # Send request to server

            page = bytearray("", 'utf-8')  # Response to be cached
            date = ""  # Time of response
            server_bandwidth = 0
            cache_bandwidth = 0
            while True:
                try:
                    # User terminates proxy
                    if self.exit:
                        break

                    # Get reply from server
                    reply = sock.recv(buffer_size)
                    server_bandwidth += len(reply)

                    # Get code
                    code = str(reply)
                    code = code.split(' ')
                    if len(code) > 1:
                        code = code[1]
                    else:
                        code = -1

                    # If cache is up to date with website
                    if code == "304":
                        print("Not Modified")
                        page = cached[1]
                        date = cached[2]
                        conn.send(page)
                        end = time.time()
                        cache_bandwidth += len(page)
                        break

                    # If cache is not up to date with website
                    elif code == "200":
                        print("New Page")
                        date = str(reply)
                        date_pos = date.find('Date: ')
                        date = date[date_pos+6:date_pos+36]
                        page.extend(reply)
                        conn.send(reply)  # Send reply back to client
                        end = time.time()

                    # If more data is received
                    elif len(reply) > 0:
                        print("More data")
                        page.extend(reply)
                        conn.send(reply)
                        end = time.time()

                    # Break the connection if receiving data failed
                    else:
                        end = time.time()
                        break

                except socket.timeout:
                    break

            # Add to cache
            cache_entries.append((url, page, date))

            print("Time Taken: ", end - start)
            print("Server Bandwidth: ", server_bandwidth)
            print("Cache Bandwidth: ", cache_bandwidth)
            print("Done\n")

            sock.close()
            conn.close()
            sys.exit(1)
        except OSError:
            sock.close()
            conn.close()
            sys.exit(2)

    def https_proxy_server(self, webserver, port, conn, addr):
        """Gets request from client and forwards to server.
        Gets response from server and forwards to client."""
        print(webserver)
        try:
            # Initiate Socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((webserver, port))  # Connect to server
            sock.setblocking(0)
            conn.setblocking(0)

            # Send connection established message to client
            conn.send(conn_est)
            while True:
                # User terminates proxy
                if self.exit:
                    break

                try:
                    # Get request from client
                    request = conn.recv(buffer_size)
                    if len(request) > 0:
                        sock.send(request)  # Send request to server
                    else:
                        # Break the connection if receiving request failed
                        break
                except OSError:
                    pass

                try:
                    # Get reply from server
                    reply = sock.recv(buffer_size)
                    if len(reply) > 0:
                        conn.send(reply)  # Send reply back to client
                    else:
                        # Break the connection if receiving reply failed
                        break
                except OSError:
                    pass

            print("done")
            sock.close()
            conn.close()
            sys.exit(1)
        except OSError:
            sock.close()
            conn.close()
            sys.exit(2)

    class Std_redirector(object):
        """Redirector for terminal output."""

        def __init__(self, widget):
            self.widget = widget

        def write(self, string):
            self.widget.insert(tk.END, string)
            self.widget.see(tk.END)

        def flush(self):
            pass


Proxy().start()
print("Shutting down")
