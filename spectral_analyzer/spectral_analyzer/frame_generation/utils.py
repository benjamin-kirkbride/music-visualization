from typing import Callable, List, NamedTuple, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from . import gradient


def _reshape_bin_rms_array(
    bin_rms_array: NDArray[np.float64], width: int
) -> NDArray[np.float64]:
    common_multiple_bin_rms_array = np.repeat(
        bin_rms_array, repeats=width
    ).reshape((width, len(bin_rms_array)))
    reshaped_bin_rms_array = np.mean(common_multiple_bin_rms_array, axis=1)
    return reshaped_bin_rms_array


def one_channel(
    width: int,
    height: int,
    bin_rms_array: NDArray[np.float64],
    gradient_array: NDArray[np.uint8],
) -> NDArray[np.uint8]:
    """Turn each bin of a bin_rms_array into a bar graph

    One audio channel at a time

    Args:
        width: width of LED Wall in pixels
        height: height of LED Wall in pixels
        bin_rms_array: array of bin energies

    Returns:
        NDArray[np.uint8]: uint8 ndarray with dimensions (width, height, 3)

    Raises:
        NotImplementedError: when the width and length of the bin_rms_array don't match
    """
    if not width == len(bin_rms_array):
        bin_rms_array = _reshape_bin_rms_array(bin_rms_array, width)

    bar_graph = np.zeros((height, width, 4), dtype=np.uint8)

    for i, energy in enumerate(bin_rms_array):
        if not energy:
            bar_height = 0
        else:
            bar_height = int(energy * height)

        bar_graph[0:bar_height, i, :] = gradient_array[0:bar_height, :]

    return np.flipud(bar_graph)
