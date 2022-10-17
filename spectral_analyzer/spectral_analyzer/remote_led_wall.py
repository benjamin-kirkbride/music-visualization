import multiprocessing as mp
import pickle
import socket
import struct
import sys

import numpy as np


class RemoteLEDWall:
    """Object for controlling and managing the LED Wall"""

    def __init__(
        self,
        matrix_width: int,
        matrix_height: int,
        led_wall_server: str,
        brightness: int,
    ):
        self._width = matrix_width
        self._height = matrix_height
        self._brightness = brightness / 100

        self._connect_to_remote_wall(led_wall_server=led_wall_server)

    def _connect_to_remote_wall(self, led_wall_server: str):
        # connect to LED Wall
        # TODO: this should retry
        server_address = led_wall_server.split(":")[0]
        try:
            server_port = int(led_wall_server.split(":")[1])
        except IndexError:
            sys.exit("must provide a port on the host")

        self.led_wall_connection = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.led_wall_connection.connect((server_address, server_port))

    def send_frame(self, frame) -> None:
        # apply brightness
        frame = np.multiply(frame, self._brightness).astype(np.uint8)
        # TODO: figure out why the channels are backwards
        frame = np.fliplr(frame)
        pickled_frame = pickle.dumps(frame)

        # https://stackoverflow.com/a/60067126/1342874
        header = struct.pack("!Q", len(pickled_frame))
        self.led_wall_connection.sendall(header)
        self.led_wall_connection.sendall(pickled_frame)


def process(frame_queue: mp.Queue, **kwargs):
    remote_led_wall = RemoteLEDWall(**kwargs)

    while not frame_queue.empty():
        frame_queue.get()

    while True:
        # block until another frame is ready
        frame = frame_queue.get(block=True, timeout=None)
        # remove alpha channel
        frame = frame[:, :, 0:3]
        remote_led_wall.send_frame(frame)
