import socket
import platform
import ipaddress
import threading
import sys

class Client:
    def __init__(self, IPaddr="", nick="user"):
        self.nickname = nick
        self.IP = IPaddr

class chatService:
    def __init__(self, name="user"):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 9999
        self.nickname = name
        self.clients = []
        tServer = threading.Thread(target=self.setServer, daemon=True)
        tServer.start()
        ipv4 = self.findIPandMask()
        self.findClients(ipv4)
    
    def setServer(self):        
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind((self.host, self.port))
        serverSocket.listen(5)
        print ('server socket listening')

        while True:
            clientSocket, addr = serverSocket.accept()
            print ("Got a connection from %s" % str(addr))
            clientSocket.send(self.nickname.encode('ascii'))
            try:
                
                msg = clientSocket.recv(1024)
                #if msg:
                print ('mesg received on Server:' + msg.decode('ascii'))
                #clientSocket.send(self.nickname.encode('ascii'))
            except:
                pass
            clientSocket.close()

    def findIPandMask(self):
        os = platform.system()
        print ('current os = ' + os)
        host = socket.gethostname() # get local machine name
        localIP = socket.gethostbyname(socket.gethostname())
        print ('local IP = ' + localIP)

        import subprocess
        if os == 'Windows':
            output = subprocess.check_output("ipconfig | findstr Mask", shell=True).decode("utf-8")
            mask = output.split(':')[1].strip()
        elif os == 'Linux':
            output = subprocess.check_output("ifconfig | grep Mask | head -1", shell=True).decode("utf-8")
            mask = output.split(':')[-1].strip()
        elif os == 'Darwin':
            output = subprocess.check_output("ifconfig | grep netmask | grep broadcast", shell=True)
            netmask = output.decode("utf-8").split()[3]
            print ('netmask ', netmask)
            netmask = int(netmask, 0)
            print ('netmask ', netmask)
            mask = 32
            while netmask == netmask // 2 * 2:
                netmask = netmask // 2
                mask -= 1
            print (mask)
        ipv4 = localIP + '/' + str(mask);
        print (ipv4)
        return ipv4

    def findClients(self, ipv4):
        net4 = ipaddress.ip_interface(ipv4)
        port = 9999
        for host in net4.network.hosts():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

                #print ('testing', host) # connection to hostname on the port.
                s.settimeout(0.01)
                s.connect((str(host), port))                               
                #if host not in clients:
                print('find active host:', str(host), '!!!!!!!!!!!!!!!!!!')
                
                tm = s.recv(1000) # Receive no more than 1024 bytes # why receive nothing here?
                print ('trying receiving tm')
                nick = tm.decode('ascii')
                #self.clients.append(str(host))
                if str(host) not in [c.IP for c in self.clients]:
                    self.clients.append(Client(str(host), nick))
                '''
                if tm:
                    self.nickname = tm.decode('ascii')
                    print(nickname + '@' + str(host))
                    print('connection alive')
                else:
                    print('no nickname received!!')
                '''
                s.close()
            except:
                #print ('something in findClients happened')
                continue
            print("The mesg got from the server is %s" % tm.decode('ascii'))

    def sendMessage(self, msg, dest, port=9999):
        if dest is None or dest == []:
            print('must select a contact')
            return
        for d in dest:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #s.settimeout(0.1)
                s.connect((d, port))
                s.send(msg.encode('ascii'))
                s.close()
            except:
                continue
