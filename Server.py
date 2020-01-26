import socket
import threading
import json
import ssl

class Server:
    def __init__(self):
        self.serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #using IPv4 addresses and TCP
        self.serverSocket.bind(('127.0.0.1',7000))
        self.serverSocket.listen(10)
    
    def isHostAllowed(self,conn,addr):
        file = open("lists.json","r")
        lists = json.load(file)
        for client in lists["blocked_clients"]:
            if(client == addr[0]):
                return False
        return True

    def connectToClient(self):
        print("Waiting for clients")
        while True:
            conn,client_addr = self.serverSocket.accept()
            print(client_addr)
            if(not self.isHostAllowed(conn,client_addr)):
                conn.close()
                continue
            clientThread = threading.Thread(target=self.handleClient,args=(conn,client_addr))
            clientThread.start()

    def handleClient(self,conn,client_addr):
        request = conn.recv(2048)
        print(request)
        first_line=request.split(b'\n')[0]
        url = first_line.split(b' ')[1]
        (webserver,port) = self.getWebServerPort(url)
        context = ssl.create_default_context()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s = context.wrap_socket(s, server_hostname=webserver, server_side=False, do_handshake_on_connect=True, suppress_ragged_eofs=True, session=None)
        s.connect((webserver, port))
        s.sendall(request)
        while 1:# receive data from web server
            data = s.recv(2048)
            if (len(data) > 0):
                conn.send(data) # send to browser/client
            else:
                break
        s.close()
        conn.close()

    def getWebServerPort(self,url):
        http_pos = url.find(b"://") # find pos of ://
        if (http_pos==-1):
            temp = url
        else:
            temp = url[(http_pos+3):] # get the rest of url
        port_pos = temp.find(b":") # find the port pos (if any)
        webserver_pos = temp.find(b"/")
        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1
        if (port_pos==-1 or webserver_pos < port_pos): 
            port = 443 #default
            webserver = temp[:webserver_pos] 
        else: # specific port 
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos] 
        return webserver,port
        

if __name__ == "__main__":
    s = Server()
    s.connectToClient()
