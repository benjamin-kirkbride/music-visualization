""" Drive a Matrix of LED's using a microcontroller.

This relies on a microcontroller that is flashed with specific firmware."""
import time
from pathlib import Path
from typing import Any

import numpy as np
import serial


class LEDWall:
    def __init__(
        self,
        led_wall_port: serial.Serial,
        width: int,
        height: int,
        serpentine: bool = True,
    ):
        self.led_wall_port = led_wall_port

        self.width = width
        self.height = height

        self.serpentine = serpentine

    def __call__(self, frame: np.ndarray) -> None:
        if self.serpentine:
            frame = self._serpentinize(frame)

        self.led_wall_port.write(frame.tobytes())

        # wait for the LED wall to respond
        self.led_wall_port.readline()

    @staticmethod
    def _serpentinize(input_array: np.ndarray) -> np.ndarray:  # type: ignore
        """ Serpentinize input array

        See also: boustrophedon

        Args:
            input_array: array to serpentinize

        Returns:
            NDArray[(Any, Any, 3), UInt8]
        """

        input_array[1::2] = input_array[1::2, ::-1]
        return input_array
