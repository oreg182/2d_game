from config import get_confi
import socket
import logging as log
import datetime
from sys import path

PATH = path[0]
LOGPATH = PATH + '/logs'
timestr = datetime.datetime.now().strftime('%d-%m-%y_%H-%M-%S')

log.basicConfig(filename=LOGPATH + '/' + timestr + '.log')


def connect(msg: str) -> str:
    s1 = socket.socket()
    for _ in range(10):
        try:
            s1.connect(((get_confi("SERVER_IP")), get_confi("SERVERPORT")))
            break
        except ConnectionRefusedError:
            log.info("Connection_Refused from server")
    s1.send(msg.encode('utf-8'))
    s1.close()
    s2 = socket.socket()
    s2.bind(((get_confi("SERVER_IP")), get_confi("RESPONSEPORT")))
    s2.listen(1)
    conn, _ = s2.accept()
    return conn.recv(8192).decode('utf-8')

