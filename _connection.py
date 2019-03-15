from config import get_confi
import socket
import logging as log


def connect(header: str, msg: str) -> str:
    msg = header + '><' + msg
    log.debug('Connection to server with message: ' + msg)
    s1 = socket.socket()
    success = False
    for _ in range(100):
        try:
            s1.connect(((get_confi("SERVER_IP")), int(get_confi("SERVERPORT"))))
            s1.send(msg.encode('utf-8'))
            s1.close()
            success = True
            break
        except ConnectionRefusedError:
            log.info("Connection_Refused from server")
    if not success:
        log.error('Method connect failed -> To many trys to connect to server')
        return 'ConnectionRefusedError Server konnte nicht erreicht werden 0001'
    else:
        s2 = socket.socket()
        s2.bind(((get_confi("SERVER_IP")), int(get_confi("RESPONSEPORT"))))
        s2.listen(1)
        conn, _ = s2.accept()
        return conn.recv(8192).decode('utf-8')
