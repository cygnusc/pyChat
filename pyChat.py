#!/usr/bin/env python3
### -*- coding: utf-8 -*-

from tkinter import *
from pyChatService import chatService
import socket

clients = []
'''
            '10.125.20.24', '10.125.20.33', '10.125.20.129',
           '10.125.20.24', '10.125.20.33', '10.125.20.129',
           '10.125.20.24', '10.125.20.33', '10.125.20.129',
           '10.125.20.24', '10.125.20.33', '10.125.20.129',
           '10.125.20.24', '10.125.20.33', '10.125.20.129',
           '10.125.20.24', '10.125.20.33', '10.125.20.129']
'''
name = ""
IP = ""

class LoginWindow:
    def __init__(self):
        global IP
        self.root = Tk()
        self.root.title("PyChat")
        #self.root.geometry("300x100")
        self.root.bind('<Return>', self.checkIn)
        checkInFrame = LabelFrame(self.root, text="Enter your nickname", padx=5, pady=5)
        checkInFrame.pack(padx=10, pady=10)
        self.nickname = Entry(checkInFrame)
        self.nickname.grid(row=0, sticky=E+W)
        self.nickname.focus_set()
        IP = socket.gethostbyname(socket.gethostname())
        myip = Label(checkInFrame, text='My IP: ' + str(IP))
        myip.grid(row=1, sticky=E+W)

    def checkIn(self, event):
        global name
        name = self.nickname.get()
        print (name)
        self.root.focus()
        self.root.destroy()
        c = ChatWindow()

class ChatWindow:
    def clearMessage(self, event):
        self.textBox.delete(0, 'end')
    
    def sendMessage(self, event):
        if self.textBox.get() == "":
            return
        global clients
        msg = name + ": " + self.textBox.get() + "\n"
        #self.service.sendMessage(msg, clients)
        receipts = [self.chatClients.get(idx) for idx in self.chatClients.curselection()]
        if receipts == []:
            print ('none selected')
            self.chatClients.select_set(0, END)
        receipts = [clients[idx] for idx in self.chatClients.curselection()]
        receipts = [r.IP for r in receipts]
        print ('sending mesg to: ', receipts)
        self.service.sendMessage(msg, receipts)
        self.textBox.delete(0, 'end')
        self.chatHistory.configure(state='normal')
        self.chatHistory.insert(END, msg) 
        self.chatHistory.see(END)
        self.chatHistory.configure(state='disabled')

    def refreshClients(self):
        print ('clients refreshed')
        self.chatClients.delete(0, END)
        self.service.findClients(self.service.findIPandMask())
        clients = self.service.clients
        clients = list(set(clients))
        for i in range(len(clients)):
            self.chatClients.insert(i, clients[i].nickname + ' @ ' + clients[i].IP)
        self.chatClients.select_set(0)

    def selectAll(self):
        print ('all selected')
        if self.broadcast == False:
            self.chatClients.select_set(0, END)
            self.broadcast = True
        else:
            self.chatClients.select_clear(0, END)
            self.broadcast = False            

    def __init__(self):
        global clients
        global name
        self.service = chatService(name)
        clients = self.service.clients
        print('got clients: ', clients)
        root = Tk()
        root.title("PyChat - " + name + " @ " + IP)
        root.bind('<Return>', self.sendMessage)
        root.bind('<Escape>', self.clearMessage)
        #root.geometry("800x600")

        chatFrame = LabelFrame(root, text="Chat", width=40, padx=5, pady=5)
        chatFrame.pack(padx=10, pady=10, side=LEFT)
        #chatFrame
        self.chatHistory = Text(chatFrame, bg='grey', height=10, width=40, state=DISABLED)
        self.chatHistory.grid(row=0, column=0, sticky=W+N+S)

        self.textBox = Entry(chatFrame)
        self.textBox.grid(row=1, sticky=E+W)
        self.textBox.focus_force()

        clientFrame = LabelFrame(root, text="Choose your contacts", width=20, padx=5, pady=5)
        clientFrame.pack(padx=10, pady=10, side=LEFT)

        scrollBar = Scrollbar(clientFrame, orient=VERTICAL)
        self.chatClients = Listbox(clientFrame, selectmode=EXTENDED, yscrollcommand=scrollBar.set)
        scrollBar.config(command=self.chatClients.yview)
        scrollBar.grid(row=0, column=1, sticky=N+S)
        self.chatClients.grid(row=0, column=0, sticky=E+W)
        for i in range(len(clients)):
            self.chatClients.insert(i, clients[i].nickname + ' @ ' + clients[i].IP)
        self.chatClients.select_set(0)
            
        self.broadcast = False
        #Checkbutton(clientFrame, text="broadcast", variable=self.broadcast, command=self.selectAll).grid(row=1, column=0, sticky=W)
        Button(clientFrame, text='Refresh', command=self.refreshClients).grid(row=1, column=0, sticky=E)

class System:
    def __init__(self):    
        l = LoginWindow()
        mainloop()

my = System()
