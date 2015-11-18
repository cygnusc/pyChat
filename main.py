#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        global qClients
        self.name = self.nickname.get()
        print ('nickname selected: ' + self.name)
        self.loginWindow.focus()
        self.loginWindow.destroy()
        self.port = 9999
        self.clients = []
        self.chatClients = None
        #tServer = threading.Thread(target=self.setNameServer, args=(q, ), daemon=True)
        nameServer = threading.Thread(target=self.setNameServer, daemon=True)
        nameServer.start()
        msgServer = threading.Thread(target=self.setMsgServer, args=(q, qClients,), daemon=True)
        msgServer.start()
        ipv4 = self.findIPandMask()
        self.findClients(ipv4)
        self.createWindow()

    def setNameServer(self):
        self.chatHistory = None        
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind((self.host, self.port))
        serverSocket.listen(5)
        print ('server socket listening')
        while True:
            time.sleep(0.01)
            clientSocket, addr = serverSocket.accept()
            print ("Got a connection from %s" % str(addr))
            clientSocket.send(self.name.encode('utf-8'))            
            clientSocket.close()
            #self.refreshClients()

    def setMsgServer(self, q, qClients, port = 9998):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind((self.host, port))
        serverSocket.listen(5)
        while True:
            time.sleep(0.01)
            clientSocket, addr = serverSocket.accept()
            try:            
                msg = clientSocket.recv(1024).decode('utf-8')            
                if self.chatHistory is not None:
                    print ('mesg received on Server:' + msg)
                    try:
                        #self.chatHistory.insert(END, msg)
                        q.put(msg)
                        print('addr: ', addr)
                        qClients.put(Client(addr[0], msg.split(':')[0]))
                        #time.sleep(0.01)
                    except Exception as e:
                        print ('something wrong: ', str(e))
                #clientSocket.send(self.nickname.encode('utf-8'))
            except:
                pass

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
        net4 = ipaddress.ip_interface(ipv4.split()[0])
        port = 9999
        for host in net4.network.hosts():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

                s.settimeout(0.01)
                s.connect((str(host), port))
                print('find active host:', str(host), '!!!!!!!!!!!!!!!!!!')
                
                tm = s.recv(1000) # Receive no more than 1024 bytes # why receive nothing here?
                print ('trying receiving tm')
                nick = tm.decode('utf-8')
                print("The mesg got from the server is %s" % tm.decode('utf-8'))
                if str(host) not in [c.IP for c in self.clients]:
                    self.clients.append(Client(str(host), nick))
                s.close()
            except:
                continue

        print ('clients found: ', [c.IP for c in self.clients])

    def sendMessageToServer(self, msg, dest, port=9998):
        if dest is None or dest == []:
            print('must select a contact')
            return
        for d in dest:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.1)
                s.connect((d, port))
                s.send(msg.encode('utf-8'))
                s.close()
            except Exception as e:
                print ('error sending mesg: ', e)
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
        if self.chatClients is not None:
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
                time.sleep(0.01)
                msg = q.get_nowait()
                self.chatHistory.configure(state='normal')
                self.chatHistory.insert(END, msg)
                self.chatHistory.see(END)
                self.chatHistory.configure(state='disabled')
            except Exception as e:
                break
        self.root.after(1, self.readMessage)

    def updateClients(self):
        global qClients
        while True:
            try:
                time.sleep(0.01)
                client = qClients.get_nowait()
                print ('client.nickname = ', client.nickname)
            
                print ('client.ip = ', client.IP)
                print ('current clients = ', [c.IP for c in self.clients])
                if client.IP not in [c.IP for c in self.clients]:
                    self.clients.append(client)
                    self.chatClients.delete(0, END)
                    for i in range(len(self.clients)):
                        self.chatClients.insert(i, self.clients[i].nickname + ' @ ' + self.clients[i].IP)
                    self.chatClients.select_set(0)
            except Exception as e:
                #print ('something happened in updateClients()', str(e))
                break
        self.root.after(500, self.updateClients)

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
        self.root.after(500, self.updateClients)

qClients = queue.Queue()
q = queue.Queue()
c = Chat()
mainloop()
