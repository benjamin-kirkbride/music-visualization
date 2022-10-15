import socket
from _thread import *

import numpy as np

from .user import User

port = 5555

s = socket.socket()

try:
    s.bind(("", port))
except socket.error as e:
    print(str(e))

s.listen(5)
users = {}


def _receive_exactly(sock, n):
    data = b""

    while n > 0:
        chunk = sock.recv(n)
        n -= len(chunk)
        data += chunk

    return data


def threaded_client(conn, user):
    while True:
        try:
            header = _receive_exactly(conn, 8)
            size = struct.unpack("!Q", header)[0]
            pickled_frame = _receive_exactly(client, size)
            frame = pickle.loads(pickled_frame)
            if not data:
                break
        except:
            break


def listener():
    while True:
        conn, addr = s.accept()

        users[addr] = User()
        start_new_thread(threaded_client, (conn, addr))


def main():
    start_new_thread(listener, ())

    fill_frame = np.zeros((48, 27, 4), dtype=np.uint8)
    frames = {}

