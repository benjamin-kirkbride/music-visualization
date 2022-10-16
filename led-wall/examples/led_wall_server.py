""" Strobe the LED Wall.

Args:
    1: LED Wall port
    2: server port
    3: width
    4: height

"""

import pickle
import socket
import struct
import sys
import time

import numpy as np
import serial

import led_wall_driver_software as driver


class ConnectionClosed(Exception):
    pass


class MatrixServer:
    def __init__(
        self,
        led_wall_port: str,
        server_port: int,
        width: int,
        height: int,
    ):
        self._width = width
        self._height = height
        self._server_port = server_port

        self._led_matrix = driver.LEDWall(
            led_wall_port=serial.Serial(led_wall_port),
            width=width,
            height=height,
        )
        self.clear_display()

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )
        self._server_socket.bind(("", server_port))

        # only allow one connection at a time
        self._server_socket.listen(1)

        self._client = None
        self._client_address = None

    def clear_display(self):
        black_frame = np.zeros((self._width, self._height, 3), dtype=np.uint8)
        self._led_matrix(black_frame)

    def _await_client(self):
        self.clear_display()
        print(f"Waiting for connection on port {self._server_port}")
        # disable timeout while we wait for a client
        self._client, self._client_address = self._server_socket.accept()
        print(f"Client connected: {self._client_address}")

    def run(self):
        while True:
            if self._client is None:
                assert self._client_address is None
                self._await_client()

            # https://stackoverflow.com/a/60067126/1342874
            try:
                header = self._receive_exactly(self._client, 8)
            except ConnectionClosed:
                continue
            packet_size = struct.unpack("!Q", header)[0]
            try:
                pickled_frame = self._receive_exactly(
                    self._client, packet_size
                )
            except ConnectionClosed:
                continue

            frame = pickle.loads(pickled_frame)
            assert frame.shape == (
                27,
                48,
                3,
            ), f"frame had incorrect shape: {frame.shape}"
            self._led_matrix(frame)

    def _receive_exactly(self, sock: socket.socket, n) -> bytes:
        data = b""
        while n > 0:
            chunk = sock.recv(n)

            # https://stackoverflow.com/questions/16745409/what-does-pythons-socket-recv-return-for-non-blocking-sockets-if-no-data-is-r#comment115084279_16745409
            if len(chunk) == 0:
                print("Client Disconnected")
                self._client = None
                self._client_address = None
                raise ConnectionClosed
            n -= len(chunk)
            data += chunk

        return data


def main(
    led_wall_port: str,
    server_port: int,
    width: int,
    height: int,
) -> None:
    """Main function of strobe script

    Args:
        led_wall_port: path of LED Wall port
        server_port: server IP address
        auth_key: auth key for server
        width: LED Wall width in pixels
        height: LED Wall height in pixels
    """
    matrix_server = MatrixServer(
        led_wall_port=led_wall_port,
        server_port=server_port,
        width=width,
        height=height,
    )
    matrix_server.run()


if __name__ == "__main__":
    main(
        led_wall_port=sys.argv[1],
        server_port=int(sys.argv[2]),
        width=int(sys.argv[3]),
        height=int(sys.argv[4]),
    )
