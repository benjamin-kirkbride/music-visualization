""" test the serial functionality of LEDWall"""

from contextlib import ExitStack as does_not_raise

import numpy as np
import pytest
from nptyping import NDArray

import led_wall_driver_software


class MockSerial:
    def __init__(self):
        self.written = None
        self.has_readline = False

    def write(self, input_):
        self.written = input_

    def readline(self):
        self.has_readline = True


TEST_DATA = [
    (
        1,
        1,
        False,
        np.arange(1 * 1 * 3).reshape(1, 1, 3).astype(np.uint8),
        b"\x00\x01\x02",
        does_not_raise(),
    ),
    (
        1,
        1,
        False,
        np.arange(1 * 2 * 3).reshape(1, 2, 3).astype(np.uint8),
        None,
        pytest.raises(RuntimeError),
    ),
    (
        1,
        1,
        False,
        np.arange(1 * 2 * 3).reshape(1, 2, 3).astype(np.uint16),
        None,
        pytest.raises(RuntimeError),
    ),
    (
        2,
        2,
        True,
        np.arange(2 * 2 * 3).reshape(2, 2, 3).astype(np.uint8),
        b"\x00\x01\x02\x03\x04\x05\x09\x0a\x0b\x06\x07\x08",
        does_not_raise(),
    ),
]


@pytest.mark.parametrize(
    "width,height,serpentinize,input_data,expected,raises", TEST_DATA
)
def test_serpentinize(width, height, serpentinize, input_data, expected, raises):
    with raises:
        mock_serial = MockSerial()
        led_wall = led_wall_driver_software.LEDWall(
            led_wall_port=mock_serial,
            width=width,
            height=height,
            serpentine=serpentinize,
        )

        led_wall(input_data)

        assert mock_serial.written == expected
        assert mock_serial.has_readline
