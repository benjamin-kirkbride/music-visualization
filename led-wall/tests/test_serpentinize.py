""" test the _serpentinize method of LEDWall"""

from contextlib import ExitStack as does_not_raise

import numpy as np
import pytest

import led_wall_driver_software

RAW_FRAMES = [
    (
        np.arange(3 * 2).reshape(3, 2),
        np.array([(0, 1), (3, 2), (4, 5)]),
        does_not_raise(),
    ),
    (
        np.arange(3 * 3).reshape(3, 3),
        np.array([(0, 1, 2), (5, 4, 3), (6, 7, 8)]),
        does_not_raise(),
    ),
]


@pytest.mark.parametrize("input_array,expected,raises", RAW_FRAMES)
def test_serpentinize(input_array: np.ndarray, expected: np.ndarray, raises):
    with raises:
        serpentinized = led_wall_driver_software.LEDWall._serpentinize(input_array)
        # https://stackoverflow.com/a/10580782
        assert np.array_equal(serpentinized, expected)
