import math
import multiprocessing as mp
from typing import List, Optional, Tuple

import numpy as np

from . import teensy_reciever


def _reshape_bin_rms_array(
    bin_rms_array: np.ndarray, width: int
) -> np.ndarray:
    common_multiple_bin_rms_array = np.repeat(
        bin_rms_array, repeats=width
    ).reshape((width, len(bin_rms_array)))
    reshaped_bin_rms_array = np.mean(common_multiple_bin_rms_array, axis=1)
    return reshaped_bin_rms_array


def _gen_gradient(
    height: int, stops: List[Tuple[float, Tuple[int, int, int, int]]]
) -> np.ndarray:
    """Create a gradient of multiple stops.

    Terminology (and hopefully output) is stolen from the SVG standard.

    Args:
        height: the height of the gradient
        stops: a list of stops. A stop is a tuple. The first value of the stop is
            the offset, as float which represents a percentage (between 0 and 1),
            and a RGB tuple where each integer is between 0 and 255.

    Returns:
        ndarray: the gradient with a shape of (1, height, 3)
    """
    stops.sort()

    gradient = np.zeros((height, 4))
    remaining_points = height
    previous_end_point = 0
    previous_color: Optional[Tuple[int, int, int, int]] = None
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
        gradient[previous_end_point:end_point] = (
            top_color_array
            + (bottom_color_array - top_color_array) * coefficient
        )

        previous_end_point = end_point
        previous_color = color

    if offset != 1:
        size = height - end_point
        color_array = np.full((size, 4), previous_color)
        gradient[end_point:height] = color_array

    return gradient.astype(np.uint8)


def _normal_bar(height: int) -> np.ndarray:
    return _gen_gradient(
        height, [(0.5, (255, 255, 255, 255)), (0.5, (255, 0, 0, 255))]
    )


def _st_practice_bar(height: int) -> np.ndarray:
    return _gen_gradient(
        height,
        [
            (0.3, (60, 210, 60, 255)),
            (0.75, (255, 215, 0, 255)),
            (0.95, (255, 0, 0, 255)),
        ],
    )


def _rainbow_bar(height: int) -> np.ndarray:
    return _gen_gradient(
        height,
        [
            (0.0, (148, 0, 211, 255)),
            (0.2, (0, 0, 255, 255)),
            (0.4, (0, 255, 0, 255)),
            (0.6, (255, 255, 0, 255)),
            (0.8, (255, 127, 0, 255)),
            (1.0, (255, 0, 0, 255)),
        ],
    )


def one_channel(
    width: int, height: int, bin_rms_array: np.ndarray
) -> np.ndarray:
    """Turn each bin of a bin_rms_array into a bar graph

    Args:
        width: width of LED Wall in pixels
        height: height of LED Wall in pixels
        bin_rms_array: array of bin energies

    Returns:
        np.ndarray: uint8 ndarray with dimensions (width, height, 3)

    Raises:
        NotImplementedError: when the width and length of the bin_rms_array don't match
    """
    if not width == len(bin_rms_array):
        bin_rms_array = _reshape_bin_rms_array(bin_rms_array, width)

    bar_graph = np.zeros((height, width, 4), dtype=np.uint8)

    full_bar = _rainbow_bar(height)
    for i, energy in enumerate(bin_rms_array):
        if not energy:
            bar_height = 0
        else:
            bar_height = int(energy * height)

        bar_graph[0:bar_height, i, :] = full_bar[0:bar_height, :]

    return np.flipud(bar_graph)


def centered_two_channel(
    width: int,
    height: int,
    left_channel: np.ndarray,
    right_channel: np.ndarray,
) -> np.ndarray:
    # odd
    if width % 2:
        each_channel_width = int(width / 2) + 1
    # even
    else:
        each_channel_width = int(width / 2)

    left_graph = one_channel(int(each_channel_width), height, left_channel)
    right_graph = one_channel(int(each_channel_width), height, right_channel)

    left_graph = np.fliplr(left_graph)
    frame = np.concatenate((left_graph, right_graph), axis=1)

    frame = np.flipud(frame).copy()

    return frame


def center_out(
    width: int,
    height: int,
    left_channel: np.ndarray,
    right_channel: np.ndarray,
) -> np.ndarray:
    half_height = math.ceil(height / 2)

    # odd
    if width % 2:
        each_channel_width = int(width / 2) + 1
    # even
    else:
        each_channel_width = int(width / 2)

    left_graph = one_channel(
        int(each_channel_width), half_height, left_channel
    )
    right_graph = one_channel(
        int(each_channel_width), half_height, right_channel
    )

    left_graph = np.fliplr(left_graph)
    bottom_half = np.concatenate((left_graph, right_graph), axis=1)
    top_half = np.flipud(bottom_half.copy())
    frame = np.vstack((bottom_half, top_half))

    if height % 2:  # odd
        frame = np.delete(frame, int(half_height), axis=0)
    return frame


def teeth(
    width: int,
    height: int,
    left_channel: np.ndarray,
    right_channel: np.ndarray,
) -> np.ndarray:
    half_height = math.ceil(height / 2)

    # odd
    if width % 2:
        each_channel_width = int(width / 2) + 1
    # even
    else:
        each_channel_width = int(width / 2)

    left_graph = one_channel(
        int(each_channel_width), half_height, left_channel
    )
    right_graph = one_channel(
        int(each_channel_width), half_height, right_channel
    )

    left_graph = np.fliplr(left_graph)
    bottom_half = np.concatenate((left_graph, right_graph), axis=1)
    top_half = np.flipud(bottom_half.copy())
    frame = np.vstack((top_half, bottom_half))

    if height % 2:  # odd
        frame = np.delete(frame, int(half_height), axis=0)
    return frame


def generate_frame(
    graphic_function, width, height, left_channel_bins, right_channel_bins
):
    return graphic_function(
        width,
        height,
        left_channel_bins,
        right_channel_bins,
    )


def process_function(
    frame_queues: List[mp.Queue], teensy_port: str, width: int, height: int
) -> None:
    with open(teensy_port, "r") as teensy_port_stream:
        left_channel_bins = None
        right_channel_bins = None
        while True:
            channel, bins = teensy_reciever.get_bins(teensy_port_stream)
            if channel == "l":
                assert left_channel_bins is None
                left_channel_bins = bins

            if channel == "r":
                assert right_channel_bins is None
                right_channel_bins = bins

            if (
                left_channel_bins is not None
                and right_channel_bins is not None
            ):
                frame = generate_frame(
                    center_out,
                    width,
                    height,
                    left_channel_bins,
                    right_channel_bins,
                )
                for frame_queue in frame_queues:
                    frame_queue.put(frame)
                left_channel_bins = None
                right_channel_bins = None
