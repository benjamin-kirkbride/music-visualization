""" Strobe the LED Wall.

Args:
    1: LED Wall port
    2: width
    3: height
    4: Strobe Hz

"""

import sys
import time

import numpy as np  # type:ignore
import serial  # type:ignore

import led_wall_driver_software as driver


def main(led_wall_port: str, width: int, height: int, strobe_hz: int) -> None:
    """ Main function of strobe script

    Args:
        led_wall_port: path of LED Wall port
        width: LED Wall width in pixels
        height: LED Wall height in pixels
        strobe_hz: frequency of strobe
    """

    led_wall = driver.LEDWall(
        led_wall_port=serial.Serial(led_wall_port), width=width, height=height,
    )

    black_frame = np.zeros((width, height, 3), dtype=np.uint8)
    white_frame = np.full((width, height, 3), fill_value=np.uint8(255), dtype=np.uint8)

    while True:
        led_wall(black_frame)
        time.sleep(1 / strobe_hz)
        led_wall(white_frame)
        time.sleep(1 / strobe_hz)


if __name__ == "__main__":
    main(
        led_wall_port=sys.argv[1],
        width=int(sys.argv[2]),
        height=int(sys.argv[3]),
        strobe_hz=int(sys.argv[4]),
    )
