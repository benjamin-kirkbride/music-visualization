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

        self._gradient_array = gradient.from_config(gradient_str, height)

    @abc.abstractmethod
    def __call__(
        self,
        left_channel: NDArray[np.float64],
        right_channel: NDArray[np.float64],
    ):
        pass


class CenteredTwoChannel(Style):
    def __call__(
        self,
        left_channel: NDArray[np.float64],
        right_channel: NDArray[np.float64],
    ) -> NDArray[np.uint8]:
        # odd
        if self._width % 2:
            each_channel_width = int(self._width / 2) + 1
        # even
        else:
            each_channel_width = int(self._width / 2)

        left_graph = utils.one_channel(
            int(each_channel_width),
            self._height,
            left_channel,
            self._gradient_array,
        )
        right_graph = utils.one_channel(
            int(each_channel_width),
            self._height,
            right_channel,
            self._gradient_array,
        )

        left_graph = np.fliplr(left_graph)
        frame = np.concatenate((left_graph, right_graph), axis=1)

        frame = np.flipud(frame).copy()

        return frame


class CenterOut(Style):
    def __init__(
        self,
        width: int,
        height: int,
        gradient_str: str,
    ):
        self._width = width
        self._height = height
        self._half_height = math.ceil(self._height / 2)

        self._gradient_array = self._gradient_array = gradient.from_config(
            gradient_str, self._half_height
        )

    def __call__(
        self,
        left_channel: NDArray[np.float64],
        right_channel: NDArray[np.float64],
    ) -> NDArray[np.uint8]:

        # odd
        if self._width % 2:
            each_channel_width = int(self._width / 2) + 1
        # even
        else:
            each_channel_width = int(self._width / 2)

        left_graph = utils.one_channel(
            int(each_channel_width),
            self._half_height,
            left_channel,
            self._gradient_array,
        )
        right_graph = utils.one_channel(
            int(each_channel_width),
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
    def __init__(
        self,
        width: int,
        height: int,
        gradient_str: str,
    ):
        self._width = width
        self._height = height
        self._half_height = math.ceil(self._height / 2)

        self._gradient_array = self._gradient_array = gradient.from_config(
            gradient_str, self._half_height
        )

    def __call__(
        self,
        left_channel: NDArray[np.float64],
        right_channel: NDArray[np.float64],
    ) -> NDArray[np.uint8]:
        # odd
        if self._width % 2:
            each_channel_width = int(self._width / 2) + 1
        # even
        else:
            each_channel_width = int(self._width / 2)

        left_graph = utils.one_channel(
            int(each_channel_width),
            self._half_height,
            left_channel,
            self._gradient_array,
        )
        right_graph = utils.one_channel(
            int(each_channel_width),
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
    "centered_two_channel": CenteredTwoChannel,
    "center_out": CenterOut,
    "mouth": Mouth,
}
