import socket as so
import logging as log
import datetime
import sys
from threading import Thread, main_thread

PATH = sys.path[0]
LOGPATH = PATH + '/serverlogs'

timestr = datetime.datetime.now().strftime('%d-%m-%y_%H-%M-%S')
f = open(LOGPATH + '/' + timestr + '.log', 'w')
f.close()
log.basicConfig(filename=LOGPATH + '/' + timestr + '.log', level=log.DEBUG)


class RecvConnection(Thread):
    def __init__(self):
        super().__init__()

    def start(self):
        sock1 = so.socket()
        sock1.bind(('', 1337))
        while main_thread().is_alive():
            sock1.listen()
            conn, addr = sock1.accept()
            HandleConnection(conn, addr)


def send_back_to_client(addr, msg: str):
    sock = so.socket(so.AF_INET, so.SOCK_STREAM)
    for _ in range(100):
        try:
            sock.connect(addr)
        except ConnectionRefusedError:
            log.info("Connection_Refused from " + str(addr))
    sock.send(msg.encode('utf-8'))


class HandleConnection(Thread):
    def __init__(self, conn: so.socket(), addr):
        super(HandleConnection, self).__init__()
        self.ipaddr = addr[0]
        self.conn = conn
        print(self.conn)

    def start(self):
        msg = self.conn.recv(8192).decode('utf-8')
        print(msg)
        if msg == '':
            send_back_to_client(self.ipaddr, 'test')


if __name__ == '__main__':
    t = RecvConnection()
    t.start()
