# pyChat
a Local Area Network chat tool written in Python

\# -*- coding: utf-8 -*-这一行保证了代码使用UTF－8编码，这样unicode字符，包括中文就可以用来聊天了。不知道为什么Mac下面无法使用中文输入法，但这应该是Tk/Tcl的问题。在发送信息前要用encode(‘utf-8’)编码，而拿到消息之后则用decode(‘utf-8’)解码。如果直接发送原字符串，会出现收不到消息的问题。

为了方便用户，这个软件被设计成peer2peer的，每个计算机都是一个server，上面运行着两个线程，一个监听9999端口，一个监听9998端口。如果有人连接到9999，则发送用户昵称；而9998端口则只负责接收别人发过来的聊天消息，不发送任何数据。这两个线程分别在setNameServer和setMsgServer中设置。

为什么要分开两个端口，而不用一个端口同时负责发送昵称和接收消息？其实一开始的设置就只有一个端口，却发现Windows下无法两者兼顾，才搞了两个。

软件开始运行时会弹出一个loginWindow，记录用户的昵称，用户的昵称和他的IP会被绑定到一个Client类的实例中。这个longinWindow的Enter键被绑定到checkIn这个函数上，在这个checkIn函数中启动之前提到的服务器线程。

checkIn函数还会启动两个函数findIPandMask()和findClients()。第一个函数用来拿到当前主机到IP：

self.host = socket.gethostbyname(socket.gethostname())

以及子网掩码Mask。第二个函数findClient()则利用前一个函数的结果调用net4.network.hosts()得到当前子网的所有主机，然后扫描它们的9999号端口，拿到那些正在监听的主机IP和他们返回的昵称，然后把结果保存在self.clients当中。在connect的时候设置timeout为0.1秒，如果超时，说明扫描的主机没有，则按照exception处理（pass无视之）。

这里使用了多线程，因为如果单线程的一个一个扫描可能总共要花几十秒钟，用户等不起。扫描结果被保存在qClients这个队列中，而qClients是个全局变量，它的值之后会被updateClients这个Housekeeper函数处理。

这个project最大的挑战就是如何在子线程（比如setMsgServer）中更新tkinter的窗口变量，比如self.clients和self.chatHistory，因为总是会遇上main thread is not in main loop这样的错误。一开始走了很多弯路，后来看了这个帖子 http://stackoverflow.com/questions/25351488/intermittent-python-thread-error-main-thread-is-not-in-main-loop 的指点，
定义了全局变量qMsg，在子线程中往qMsg中添加元素，然后在主线程中反复调用readMessage这个函数，把qMsg中新添加的元素处理掉。其中self.root.after(1, …)确保隔一毫秒就做一次调用。总而言之，解决这个问题的关键在于线程不可能是全局的，变量却可以是全局的，qMsg（以及后来的qClients）很好的起到了中间人的作用。

代码中还用了其他的一些小技巧比如self.chatHistory.see(END)可以保证聊天记录自动滚动，保证最新的消息在输入框的上方，这里就不赘述了。

这个project还遇到的另一个尚未解决的问题。本来是想写两个不同的类，chatWindow和chatService，一个提供窗体，一个提供消息服务。结果却弄巧成拙的互相交流信息（比如msg和client）极为不便，因为互相不能调用对方的子函数。还想写一个Singleton类，也没能解决这个问题。这里就说明自己design pattern上面的欠缺了。最后把所有子函数写到同一个类Chat了事。

<EOF>
