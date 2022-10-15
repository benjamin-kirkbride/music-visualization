""" Drive a WS2811 Matrix using Arduino"""

import sys
from pathlib import Path
import time

import serial
from PIL import Image
import numpy as np

from pongwall_server import frame

# Constants
CONTROLLER = serial.Serial(sys.argv[1], 921600)

MATRIX_WIDTH = 48
MATRIX_HEIGHT = 27
NUM_LEDS = MATRIX_WIDTH * MATRIX_HEIGHT
BYTES_PER_LED = 3
BYTES_PER_FRAME = NUM_LEDS * BYTES_PER_LED


def send_frame(frame_: bytes) -> None:
    start_time = time.monotonic()
    CONTROLLER.write(frame_)
    print("send frame: ", (time.monotonic() - start_time) * 1000)


if __name__ == "__main__":
    start_time = time.monotonic()
    IMAGE = np.asarray(Image.open(Path(sys.argv[2])))
    print("image parse: ", (time.monotonic() - start_time) * 1000)

    RAW_FRAME = frame.serpentinize(IMAGE, MATRIX_WIDTH, MATRIX_HEIGHT)

    FRAME = frame.make_data(RAW_FRAME)

    send_frame(FRAME)

    print("whole enchilada: ", (time.monotonic() - start_time) * 1000)
    print("done")
