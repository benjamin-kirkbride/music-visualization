import multiprocessing as mp
from typing import List

from .. import teensy_reciever
from .display_styles import STYLE


def process_function(
    frame_queues: List[mp.Queue],
    teensy_port: str,
    width: int,
    height: int,
    style: str,
    gradient_str: str,
) -> None:
    generate_frame = STYLE[style](
        width=width, height=height, gradient_str=gradient_str
    )

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
                    left_channel_bins,
                    right_channel_bins,
                )
                for frame_queue in frame_queues:
                    frame_queue.put(frame)
                left_channel_bins = None
                right_channel_bins = None
