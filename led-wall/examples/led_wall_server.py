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

import numpy as np
import serial

import led_wall_driver_software as driver


def _receive_exactly(sock, n) -> bytes:
    data = b""

    while n > 0:
        chunk = sock.recv(n)
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

    led_wall = driver.LEDWall(
        led_wall_port=serial.Serial(led_wall_port),
        width=width,
        height=height,
    )

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", server_port))

    # blank out LED Wall
    black_frame = np.zeros((width, height, 3), dtype=np.uint8)
    led_wall(black_frame)

    # only allow one connection at a time
    server_socket.listen(1)
    print(f"Listening on port {server_port}")

    print("Waiting on client connection")
    client, client_address = server_socket.accept()
    print(f"Client connected: {client_address}")

    while True:
        # https://stackoverflow.com/a/60067126/1342874
        header = _receive_exactly(client, 8)
        size = struct.unpack("!Q", header)[0]
        print(struct.unpack("!Q", header))
        pickled_frame = _receive_exactly(client, size)

        frame = pickle.loads(pickled_frame)
        assert frame.shape == (
            27,
            48,
            3,
        ), f"frame had incorrect shape: {frame.shape}"
        # decrease brightness
        # frame = np.multiply(frame, 0.2).astype(np.uint8)
        led_wall(frame)


if __name__ == "__main__":
    main(
        led_wall_port=sys.argv[1],
        server_port=int(sys.argv[2]),
        width=int(sys.argv[3]),
        height=int(sys.argv[4]),
    )
