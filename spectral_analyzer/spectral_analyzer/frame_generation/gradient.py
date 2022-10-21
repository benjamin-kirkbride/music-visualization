import colorsys
import xml.etree.ElementTree as ET
from typing import List, NamedTuple, Tuple

import numpy as np
from numpy.typing import NDArray
from PIL import ImageColor

from .. import PROJECT_ROOT

GRADIENTS = PROJECT_ROOT / "frame_generation" / "gradients"


def _rgb_to_hsv(rgb):
    # https://stackoverflow.com/a/7274986/1342874
    # Translated from source of colorsys.rgb_to_hsv
    # r,g,b should be a numpy arrays with values between 0 and 255
    # rgb_to_hsv returns an array of floats between 0.0 and 1.0.
    rgb = rgb.astype("float")
    hsv = np.zeros_like(rgb)
    # in case an RGBA array was passed, just copy the A channel
    hsv[..., 3:] = rgb[..., 3:]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.max(rgb[..., :3], axis=-1)
    minc = np.min(rgb[..., :3], axis=-1)
    hsv[..., 2] = maxc
    mask = maxc != minc
    hsv[mask, 1] = (maxc - minc)[mask] / maxc[mask]
    rc = np.zeros_like(r)
    gc = np.zeros_like(g)
    bc = np.zeros_like(b)
    rc[mask] = (maxc - r)[mask] / (maxc - minc)[mask]
    gc[mask] = (maxc - g)[mask] / (maxc - minc)[mask]
    bc[mask] = (maxc - b)[mask] / (maxc - minc)[mask]
    hsv[..., 0] = np.select(
        [r == maxc, g == maxc], [bc - gc, 2.0 + rc - bc], default=4.0 + gc - rc
    )
    hsv[..., 0] = (hsv[..., 0] / 6.0) % 1.0
    return hsv


def _hsv_to_rgb(hsv):
    # https://stackoverflow.com/a/7274986/1342874
    # Translated from source of colorsys.hsv_to_rgb
    # h,s should be a numpy arrays with values between 0.0 and 1.0
    # v should be a numpy array with values between 0.0 and 255.0
    # hsv_to_rgb returns an array of uints between 0 and 255.
    rgb = np.empty_like(hsv)
    rgb[..., 3:] = hsv[..., 3:]
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = (h * 6.0).astype("uint8")
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    conditions = [s == 0.0, i == 1, i == 2, i == 3, i == 4, i == 5]
    rgb[..., 0] = np.select(conditions, [v, q, p, p, t, v], default=v)
    rgb[..., 1] = np.select(conditions, [v, v, v, q, p, p], default=t)
    rgb[..., 2] = np.select(conditions, [v, p, t, v, v, q], default=p)
    return rgb.astype("uint8")


class RGBA(NamedTuple):
    red: int
    green: int
    blue: int
    alpha: int = 255


def shift_hue(rgba: RGBA, hue_shift):
    rgb_array = np.array(rgba[:-1], dtype=np.uint8)
    hsv = _rgb_to_hsv(rgb_array)
    hsv[..., 0] = hsv[..., 0] + hue_shift
    rgb_array = _hsv_to_rgb(hsv)

    return RGBA(rgb_array[0], rgb_array[1], rgb_array[2], rgba[-1])


def _hex_to_rgba(hex_color: str) -> RGBA:
    if hex_color[0] != "#":
        # ImageColor requires a hash as the first character
        hex_color = "#" + hex_color

    rgba_color = RGBA(*ImageColor.getrgb(hex_color))
    return rgba_color


def gen_gradient(
    height: int, stops: List[Tuple[float, RGBA]]
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


def svg_to_gradient(svg_name) -> List[Tuple[float, RGBA]]:
    tree = ET.parse((GRADIENTS / svg_name).with_suffix(".svg"))
    # https://stackoverflow.com/a/55049369/1342874
    # we only support one gradient per svg, so only grab the first one
    linear_gradient_element = tree.getroot().find(".//linearGradient")
    assert isinstance(linear_gradient_element, ET.Element)

    stops: List[Tuple[float, RGBA]] = []
    for stop in linear_gradient_element.iter("stop"):
        raw_offset = stop.attrib["offset"]
        assert isinstance(raw_offset, str)
        offset = float(raw_offset[0:-1]) / 100

        rgba = _hex_to_rgba(stop.attrib["stop-color"])

        stops.append((offset, rgba))
    return stops


def from_config(gradient_str: str, height: int) -> NDArray[np.uint8]:
    stops = svg_to_gradient(gradient_str)
    return gen_gradient(height, stops)
