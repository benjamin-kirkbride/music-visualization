from typing import List, NamedTuple, Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from PIL import ImageColor

from .. import config


class RGBA(NamedTuple):
    r: int
    g: int
    b: int
    a: int = 255


def _hex_to_rgba(hex_color: str) -> RGBA:
    if hex_color[0] != "#":
        # ImageColor requires a hash as the first character
        hex_color = "#" + hex_color

    rgba_color = RGBA(*ImageColor.getrgb(hex_color))
    return rgba_color


def gen_gradient(
    height: int, stops: List[Tuple[float, RGBA | str]]
) -> NDArray[np.uint8]:
    """Create a gradient of multiple stops.

    Terminology (and hopefully output) is stolen from the SVG standard.

    Args:
        height: the height of the gradient
        stops: a list of stops. A stop is a tuple. The first value of the stop is
            the offset, as float which represents a percentage (between 0 and 1),
            and a RGB tuple where each integer is between 0 and 255.

    Returns:
        ndarray: the gradient with a shape of (1, height, 4)
    """
    stops.sort()

    gradient_array = np.zeros((height, 4))
    remaining_points = height
    previous_end_point = 0
    previous_color: RGBA | None = None
    for stop in stops:
        offset = stop[0]
        assert 0 <= offset <= 1
        color = stop[1]
        if isinstance(color, str):
            color = _hex_to_rgba(color)
        assert isinstance(color, RGBA)

        end_point = int(remaining_points * offset)
        size = end_point - previous_end_point
        coefficient = np.linspace(1, 0, size)[:, None]

        if previous_color is None:
            # first stop
            previous_color = color

        bottom_color_array = np.full((size, 4), previous_color)
        top_color_array = np.full((size, 4), color)
        gradient_array[previous_end_point:end_point] = (
            top_color_array
            + (bottom_color_array - top_color_array) * coefficient
        )

        previous_end_point = end_point
        previous_color = color

    if offset != 1:
        size = height - end_point
        color_array = np.full((size, 4), previous_color)
        gradient_array[end_point:height] = color_array

    return gradient_array.astype(np.uint8)


def from_config(gradient_str: str, height: int) -> NDArray[np.uint8]:
    config_spec = config["gradients"][gradient_str]
    return gen_gradient(height, config_spec)
