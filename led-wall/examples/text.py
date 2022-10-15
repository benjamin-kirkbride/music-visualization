""" Strobe the LED Wall.

Args:
    1: LED Wall port
    2: width
    3: height
    4: Strobe Hz

"""

import json
import pathlib
import sys
import time

import numpy as np
import serial
from PIL import Image

import led_wall_driver_software as driver


def main(led_wall_port, width, height):
    led_wall = driver.LEDWall(
        led_wall_port=serial.Serial(led_wall_port), width=width, height=height,
    )

    path = str(pathlib.Path(__file__).parent.absolute()) + "/fonts/font.json"
    with open(path, "r") as read_file:
        decoded = json.load(read_file)

    for key in decoded:
        array = np.asarray(decoded[key])
        img = Image.fromarray(array)
        decoded[key] = img

    out_img = Image.new("RGB", (48, 27), (0, 0, 0))
    out_img.paste(decoded["A"], (0, 0))
    frame = np.array(out_img)
    # frame = np.invert(frame)

    black_frame = np.zeros((width, height, 3), dtype=np.uint8)
    # white_frame = np.full((width, height, 3), fill_value=np.uint8(255), dtype=np.uint8)

    led_wall(black_frame)
    # led_wall(white_frame)
    # led_wall(frame)


if __name__ == "__main__":
    main(led_wall_port=sys.argv[1], width=int(sys.argv[2]), height=int(sys.argv[3]))
