import abc
import math
from typing import Callable, Dict, NamedTuple, Type

import numpy as np
from numpy.typing import NDArray

from . import gradient, utils


class Style(abc.ABC):
    def __init__(
        self,
        width: int,
        height: int,
        gradient_str: str,
    ):
        self._width = width
        self._height = height
        self._half_height = math.ceil(self._height / 2)

        # odd
        if self._width % 2:
            self._each_channel_width = int(self._width / 2) + 1
        # even
        else:
            self._each_channel_width = int(self._width / 2)

        self._get_gradient(gradient_str)

    @abc.abstractmethod
    def __call__(
        self,
        left_channel: NDArray[np.float64],
        right_channel: NDArray[np.float64],
    ):
        pass

    def _get_gradient(self, gradient_str: str):
        self._gradient_array = self._gradient_array = gradient.from_config(
            gradient_str, self._height
        )

    def _reshape_bin_rms_array(
        self,
        bin_rms_array: NDArray[np.float64],
        width: int,
    ) -> NDArray[np.float64]:
        """Reshapes the bin array to be equal to the width.

        Maintains relative intensity.

        This should not be nessesary (idealy len(bin_rms_array) == width)
        """
        if not len(bin_rms_array) == width:
            # no need to reshape if the size is already correct (duh)
            return bin_rms_array

        # find the lowest common multiple bin
        common_multiple_bin_rms_array = np.repeat(
            bin_rms_array, repeats=width
        ).reshape((width, len(bin_rms_array)))
        # crunch it back down to `width` size
        reshaped_bin_rms_array = np.mean(common_multiple_bin_rms_array, axis=1)
        assert len(reshaped_bin_rms_array) == width
        return reshaped_bin_rms_array

    def _generate_bar_graph(
        self,
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
        """
        if not width == len(bin_rms_array):
            bin_rms_array = self._reshape_bin_rms_array(bin_rms_array, width)

        bar_graph = np.zeros((height, width, 4), dtype=np.uint8)

        for i, energy in enumerate(bin_rms_array):
            if not energy:
                bar_height = 0
            else:
                bar_height = int(energy * height)

            bar_graph[0:bar_height, i, :] = gradient_array[0:bar_height, :]

        return np.flipud(bar_graph)


class BottomUp(Style):
    def __call__(
        self,
        left_channel: NDArray[np.float64],
        right_channel: NDArray[np.float64],
    ) -> NDArray[np.uint8]:
        left_graph = self._generate_bar_graph(
            int(self._each_channel_width),
            self._height,
            left_channel,
            self._gradient_array,
        )
        right_graph = self._generate_bar_graph(
            int(self._each_channel_width),
            self._height,
            right_channel,
            self._gradient_array,
        )

        left_graph = np.fliplr(left_graph)
        frame = np.concatenate((left_graph, right_graph), axis=1)

        frame = np.flipud(frame).copy()

        return frame


class PerBinColor(Style):
    def __call__(
        self,
        left_channel: NDArray[np.float64],
        right_channel: NDArray[np.float64],
    ) -> NDArray[np.uint8]:
        left_graph = self._generate_bar_graph(
            int(self._each_channel_width),
            self._height,
            left_channel,
            self._gradient_array,
        )
        right_graph = self._generate_bar_graph(
            int(self._each_channel_width),
            self._height,
            right_channel,
            self._gradient_array,
        )

        left_graph = np.fliplr(left_graph)
        frame = np.concatenate((left_graph, right_graph), axis=1)

        frame = np.flipud(frame).copy()

        return frame

    def _generate_bar_graph(
        self,
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
        """
        if not width == len(bin_rms_array):
            bin_rms_array = self._reshape_bin_rms_array(bin_rms_array, width)

        bar_graph = np.zeros((height, width, 4), dtype=np.uint8)

        for i, energy in enumerate(bin_rms_array):
            if not energy:
                bar_height = 0
            else:
                bar_height = int(energy * height)

            bar_graph[0:bar_height, i, :] = gradient_array[bar_height - 1]

        return np.flipud(bar_graph)


class TopDown(Style):
    def __call__(
        self,
        left_channel: NDArray[np.float64],
        right_channel: NDArray[np.float64],
    ) -> NDArray[np.uint8]:
        left_graph = self._generate_bar_graph(
            int(self._each_channel_width),
            self._height,
            left_channel,
            self._gradient_array,
        )
        right_graph = self._generate_bar_graph(
            int(self._each_channel_width),
            self._height,
            right_channel,
            self._gradient_array,
        )

        left_graph = np.fliplr(left_graph)
        frame = np.concatenate((left_graph, right_graph), axis=1)

        return frame


class CenterOut(Style):
    def _get_gradient(self, gradient_str: str):
        self._gradient_array = self._gradient_array = gradient.from_config(
            gradient_str, self._half_height
        )

    def __call__(
        self,
        left_channel: NDArray[np.float64],
        right_channel: NDArray[np.float64],
    ) -> NDArray[np.uint8]:
        left_graph = self._generate_bar_graph(
            int(self._each_channel_width),
            self._half_height,
            left_channel,
            self._gradient_array,
        )
        right_graph = self._generate_bar_graph(
            int(self._each_channel_width),
            self._half_height,
            right_channel,
            self._gradient_array,
        )

        left_graph = np.fliplr(left_graph)
        bottom_half = np.concatenate((left_graph, right_graph), axis=1)
        top_half = np.flipud(bottom_half.copy())
        frame = np.vstack((bottom_half, top_half))

        if self._height % 2:  # odd
            frame = np.delete(frame, int(self._half_height), axis=0)
        return frame


class Mouth(Style):
    def _get_gradient(self, gradient_str: str):
        self._gradient_array = self._gradient_array = gradient.from_config(
            gradient_str, self._half_height
        )

    def __call__(
        self,
        left_channel: NDArray[np.float64],
        right_channel: NDArray[np.float64],
    ) -> NDArray[np.uint8]:
        left_graph = self._generate_bar_graph(
            int(self._each_channel_width),
            self._half_height,
            left_channel,
            self._gradient_array,
        )
        right_graph = self._generate_bar_graph(
            int(self._each_channel_width),
            self._half_height,
            right_channel,
            self._gradient_array,
        )

        left_graph = np.fliplr(left_graph)
        bottom_half = np.concatenate((left_graph, right_graph), axis=1)
        top_half = np.flipud(bottom_half.copy())
        frame = np.vstack((top_half, bottom_half))

        if self._height % 2:  # odd
            frame = np.delete(frame, int(self._half_height), axis=0)
        return frame


STYLE: Dict[str, Type[Style]] = {
    "bottom_up": BottomUp,
    "top_down": TopDown,
    "per_bin_color": PerBinColor,
    "center_out": CenterOut,
    "mouth": Mouth,
}
