""" Drive a WS2811 Matrix using Arduino"""

import sys
from pathlib import Path
import time
import re

import serial
from PIL import Image
import numpy as np

from pongwall_server import frame

# Constants
CONTROLLER = serial.Serial(sys.argv[1], 9600)

MATRIX_WIDTH = 48
MATRIX_HEIGHT = 27
NUM_LEDS = MATRIX_WIDTH * MATRIX_HEIGHT
BYTES_PER_LED = 3
BYTES_PER_FRAME = NUM_LEDS * BYTES_PER_LED


def send_frame(frame_: bytes) -> None:
    start_time = time.monotonic()
    CONTROLLER.write(frame_)
    # time.sleep(.3)
    print("send frame: ", (time.monotonic() - start_time) * 1000)


if __name__ == "__main__":
    START_TIME = time.monotonic()
    IMAGE = np.asarray(Image.open(Path(sys.argv[2])))

    FRAME_COUNT = len(IMAGE) / 27
    print("image parse: ", (time.monotonic() - START_TIME) * 1000)
    while True:
        CURRENT_BPM = float(input())
        TIME_TO_NEXT_BEAT = time.monotonic() + (60 / CURRENT_BPM)
        TIME_PER_FRAME = (TIME_TO_NEXT_BEAT - time.monotonic()) / FRAME_COUNT
        for FRAME_NUMBER, NOT_SERPENTINIZED_FRAME in enumerate(
            np.split(IMAGE, FRAME_COUNT)
        ):
            FRAME_TIME = time.monotonic()
            RAW_FRAME = frame.serpentinize(
                NOT_SERPENTINIZED_FRAME, MATRIX_WIDTH, MATRIX_HEIGHT
            )

            FRAME = frame.make_data(RAW_FRAME)

            CONTROLLER.readline()
            send_frame(FRAME)
            while time.monotonic() - FRAME_TIME < TIME_PER_FRAME:
                pass

            print(f"frame {FRAME_NUMBER}: ", (time.monotonic() - START_TIME) * 1000)

    print("whole enchilada: ", (time.monotonic() - START_TIME) * 1000)
    print("done")
