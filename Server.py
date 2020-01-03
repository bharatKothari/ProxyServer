import socket;
import threading;

serverSocket = socket.socket()

if __name__ == "__main__":
    serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #using IPv4 addresses and TCP
    print('socket made')
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind(('192.168.43.192',9000))
    print('socket bind')
    serverSocket.listen(10)
    print('socket listening')

    conn,client_addr = serverSocket.accept()
    request = conn.recv(2048)
    print(request)
    first_line=request.split(b'\n')[0]
    url = first_line.split(b' ')[1]

    http_pos = url.find(b"://") # find pos of ://
    if (http_pos==-1):
        temp = url
    else:
        temp = url[(http_pos+3):] # get the rest of url

    port_pos = temp.find(b":") # find the port pos (if any)

    # find end of web server
    webserver_pos = temp.find(b"/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if (port_pos==-1 or webserver_pos < port_pos): 

        # default port 
        port = 80 
        webserver = temp[:webserver_pos] 

    else: # specific port 
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos] 

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((webserver, port))
    s.sendall(request)

    while 1:
        # receive data from web server
        data = s.recv(2048)

        if (len(data) > 0):
            conn.send(data) # send to browser/client
        else:
            break