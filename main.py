import socket
import platform
import ipaddress
import threading
import sys
import time
import queue
from tkinter import *

class Client:
    def __init__(self, IPaddr="", nick="user"):
        self.nickname = nick
        self.IP = IPaddr

class Chat:
    def __init__(self):
        self.loginWindow = Tk()
        self.loginWindow.title("PyChat")
        self.loginWindow.bind('<Return>', self.checkIn)
        checkInFrame = LabelFrame(self.loginWindow, \
                                  text="Enter your nickname", padx=5, pady=5)
        checkInFrame.pack(padx=10, pady=10)
        self.nickname = Entry(checkInFrame)
        self.nickname.grid(row=0, sticky=E+W)
        self.nickname.focus_set()
        self.host = socket.gethostbyname(socket.gethostname())
        myip = Label(checkInFrame, text='My IP: ' + str(self.host))
        myip.grid(row=1, sticky=E+W)
        
    def checkIn(self, event):
        global q
        self.name = self.nickname.get()
        print ('nickname selected: ' + self.name)
        self.loginWindow.focus()
        self.loginWindow.destroy()
        self.port = 9999
        self.clients = []
        tServer = threading.Thread(target=self.setServer, args=(q, ), daemon=True)
        tServer.start()
        ipv4 = self.findIPandMask()
        self.findClients(ipv4)
        self.createWindow()

    def setServer(self, q):
        self.chatHistory = None
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind((self.host, self.port))
        serverSocket.listen(5)
        print ('server socket listening')

        while True:
            clientSocket, addr = serverSocket.accept()
            print ("Got a connection from %s" % str(addr))
            clientSocket.send(self.name.encode('ascii'))
            try:
                
                msg = clientSocket.recv(1024).decode('ascii')
                #if msg:
                
                if self.chatHistory is not None:
                    print ('mesg received on Server:' + msg)
                    try:
                        #self.chatHistory.insert(END, msg)
                        q.put(msg)
                        #time.sleep(0.01)
                    except Exception as e:
                        print ('something wrong: ', str(e))
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

                s.settimeout(0.02)
                s.connect((str(host), port))
                print('find active host:', str(host), '!!!!!!!!!!!!!!!!!!')
                
                tm = s.recv(1000) # Receive no more than 1024 bytes # why receive nothing here?
                print ('trying receiving tm')
                nick = tm.decode('ascii')
                print("The mesg got from the server is %s" % tm.decode('ascii'))
                if str(host) not in [c.IP for c in self.clients]:
                    self.clients.append(Client(str(host), nick))
                s.close()
            except:
                continue

        print ('clients found: ', [c.IP for c in self.clients])

    def sendMessageToServer(self, msg, dest, port=9999):
        if dest is None or dest == []:
            print('must select a contact')
            return
        for d in dest:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((d, port))
                s.send(msg.encode('ascii'))
                s.close()
            except:
                continue
            
    def sendMessage(self, event):
        global q
        if self.textBox.get() == "":
            return
        msg = self.name + ": " + self.textBox.get() + "\n"
        receipts = [self.chatClients.get(idx) for idx in self.chatClients.curselection()]
        if receipts == []:
            print ('none selected')
            self.chatClients.select_set(0, END)
        print (self.chatClients.curselection())
        receipts = [(self.clients)[int(idx)] for idx in self.chatClients.curselection()]
        receipts = [r.IP for r in receipts]
        print ('sending mesg to: ', receipts)
        self.sendMessageToServer(msg, receipts)
        self.textBox.delete(0, 'end')
        self.chatHistory.configure(state='normal')
        self.chatHistory.insert(END, msg) 
        self.chatHistory.see(END)
        self.chatHistory.configure(state='disabled')
        #print ('queue: ', q)        

    def clearMessage(self):
        self.textBox.delete(0, 'end')

    def refreshClients(self):
        print ('clients refreshed')
        self.chatClients.delete(0, END)
        ipv4 = self.findIPandMask()
        self.clients = []
        self.findClients(ipv4)
        for i in range(len(self.clients)):
            self.chatClients.insert(i, self.clients[i].nickname + ' @ ' + self.clients[i].IP)
        self.chatClients.select_set(0)

    def readMessage(self):
        global q
        while True:
            try:
                msg = q.get_nowait()
                self.chatHistory.configure(state='normal')
                self.chatHistory.insert(END, msg)
                self.chatHistory.see(END)
                self.chatHistory.configure(state='disabled')
            except Exception as e:
                break
        self.root.after(1, self.readMessage)

    def createWindow(self):
        self.root = Tk()
        self.root.title("PyChat - " + self.name + " @ " + self.host)
        self.root.bind('<Return>', self.sendMessage)
        self.root.bind('<Escape>', self.clearMessage)
        
        chatFrame = LabelFrame(self.root, text="Chat", width=40, padx=5, pady=5)
        chatFrame.pack(padx=10, pady=10, side=LEFT)
        #chatFrame
        self.chatHistory = Text(chatFrame, bg='grey', height=10, width=40, state=DISABLED)
        self.chatHistory.grid(row=0, column=0, sticky=W+N+S)

        self.textBox = Entry(chatFrame)
        self.textBox.grid(row=1, sticky=E+W)
        self.textBox.focus_force()

        clientFrame = LabelFrame(self.root, text="Choose your contacts", width=20, padx=5, pady=5)
        clientFrame.pack(padx=10, pady=10, side=LEFT)

        scrollBar = Scrollbar(clientFrame, orient=VERTICAL)
        self.chatClients = Listbox(clientFrame, selectmode=EXTENDED, yscrollcommand=scrollBar.set)
        scrollBar.config(command=self.chatClients.yview)
        scrollBar.grid(row=0, column=1, sticky=N+S)
        self.chatClients.grid(row=0, column=0, sticky=E+W)
        for i in range(len(self.clients)):
            self.chatClients.insert(i, self.clients[i].nickname + ' @ ' + self.clients[i].IP)
        self.chatClients.select_set(0)
        Button(clientFrame, text='Refresh', command=self.refreshClients).grid(row=1, column=0, sticky=W)
        self.root.after(1, self.readMessage)

q = queue.Queue()
c = Chat()
mainloop()
