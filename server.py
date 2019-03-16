import socket as so
import logging
import datetime
from threading import Thread
from config import get_confi
from tkinter import *

__version__ = 0.1

PATH = sys.path[0]
LOGPATH = PATH + '/serverlogs'

SERVERPORT = int(get_confi('SERVERPORT'))
RESPONSEPORT = int(get_confi("RESPONSEPORT"))

DEFAULT = 'DEFAULT'

timestr = datetime.datetime.now().strftime('%d-%m-%y_%H-%M-%S')
f = open(LOGPATH + '/server' + timestr + '.log', 'w')
f.close()
logging.basicConfig(filename=LOGPATH + '/server' + timestr + '.log', level=logging.DEBUG)


def _manipulate_chunk(xcoord, ycoord, new_text):
    with open('save.txt') as f:
        chunks = f.read().split(';')
        new_str = ''
        for c in chunks:
            if c.split('*')[1] == xcoord and c.split('*')[2] == ycoord:
                new_str += new_text
            else:
                new_str += c + '*'
        new_str = new_str[:-1]
        f.write(new_str)


def manipulate_playground(_type, extra: str):
    if _type == 'BUILD:':
        print('in build')
        building = extra.split('=')[0]
        xcoord = extra.split('=')[1]
        ycoord = extra.split('=')[2]
        profile = extra.split('=')[3]
        with open('save.txt') as f:
            chunks = f.read()
        for c in chunks:
            new = ''
            if c.split('*')[1] == xcoord and c.split('*')[2] == ycoord:
                chunk = c.split('*')
                new += chunk[0] + '*' + chunk[1] + '*' + chunk[2] + '*' + chunk[3] + '*' + chunk[4] + '*' + building + '=' + profile + '*' + chunk[6]
                print(new)
                _manipulate_chunk(xcoord, ycoord, new)
                break

    elif _type == 'UNIT':
        pass


class Commands:
    @staticmethod
    def playground_send_complete(addr, master):
        with open('save.txt', 'r') as f:
            string = f.read()
        send_back_to_client(addr, string, master)

    @staticmethod
    def login(addr, master):
        send_back_to_client(addr, '0', master)

    @staticmethod
    def action(addr, master, extra):
        manipulate_playground('BUILD', extra)
        send_back_to_client(addr, 'DONE', master)


class RecvConnection(Thread):
    def __init__(self, master):
        super().__init__(daemon=True)
        self.stop_thread = False
        self.master = master

    def run(self):
        sock1 = so.socket()
        sock1.bind(('', SERVERPORT))
        self.master.log('binded listen socket at 1337')
        while True:
            self.master.log('sock is listening')
            sock1.listen(5)
            conn, addr = sock1.accept()
            thread = HandleConnection(conn, addr, self.master)
            thread.start()


def send_back_to_client(addr, msg: str, master):
    sock = so.socket(so.AF_INET, so.SOCK_STREAM)
    for _ in range(10):
        try:
            sock.connect((addr, RESPONSEPORT))
            break
        except ConnectionRefusedError:
            master.log("Connection_Refused from " + str(addr))
    sock.send(msg.encode('utf-8'))
    sock.close()


class HandleConnection(Thread):
    def __init__(self, conn: so.socket, addr, master):
        super(HandleConnection, self).__init__()
        self.ipaddr = addr[0]
        self.conn = conn
        self.master = master
        self.master.log(str(self.conn))

    def run(self):
        msg = self.conn.recv(8192).decode('utf-8')
        print(msg)
        header = msg.split('><')[0]
        if header == 'PLAYGROUND':
            Commands.playground_send_complete(self.ipaddr, self.master)
        elif header == 'LOGIN':
            Commands.login(self.ipaddr, self.master)
        elif header == 'ACTION':
            Commands.action(self.ipaddr, self.master, msg.split('><')[1])
        self.conn.close()


class Gui:
    def __init__(self):
        self.root = Tk()
        self.root.title('Server ver. ' + str(__version__))
        self.logframe = Frame(self.root)
        self.logframe.pack()
        self.logwidget = Text(self.logframe)
        self.logwidget.pack()
        self.recvthread = None
        Button(self.root, text='Start', command=self.start).pack()
        Button(self.root, text='Shutdown', command=self.shutdown).pack()
        self.root.mainloop()

    def log(self, msg: str):
        self.logwidget.insert(END, '\n' + msg)

    def start(self):
        self.recvthread = RecvConnection(self)
        self.recvthread.start()
        self.log('STARTING SERVER')

    def shutdown(self):
        self.root.destroy()


GUI = Gui()


def log(msg):
    logging.debug(msg)
    GUI.log(msg)
