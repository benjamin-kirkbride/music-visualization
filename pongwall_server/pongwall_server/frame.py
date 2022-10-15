"""Python script to convert an image to the rgb values for fastled"""

import sys
from array import array
import time
from typing import cast

import imageio
import numpy as np


def serpentinize(raw_frame: imageio.core.util.Array, width, height):
    start_time = time.monotonic()
    even_rows = raw_frame[0::2, :]
    odd_rows = raw_frame[1::2, ::-1]
    # not all images have an alpha channel
    frame = np.empty((height, width, raw_frame.shape[2]), dtype=np.uint8)
    frame[0::2] = even_rows
    frame[1::2] = odd_rows
    print("serpentinize: ", (time.monotonic() - start_time) * 1000)
    return frame


def make_data(frame: np.ndarray) -> bytes:
    start_time = time.monotonic()

    if frame.shape[2] == 4:
        opacity = frame[:, :, 3:] / np.uint8(255)
        frame = frame[:, :, 0:3] * opacity

    frame_data: bytes
    frame_data = frame.astype(np.uint8).tobytes()
    print(f"bytes: {len(frame_data)}")
    print("make_data: ", (time.monotonic() - start_time) * 1000)
    return frame_data
