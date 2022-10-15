import multiprocessing as mp

import arcade
import numpy as np

from .numpy_sprite import NumpySprite


def generate_grid(width, height, scale):
    grid_array = np.full(
        (height, width, 4),
        (0, 0, 0, 0),
        dtype=np.uint8,
    )

    # vertical grid lines
    grid_array[:, 0:-1:scale, :] = [0, 0, 0, 255]

    # horizontal grid lines
    grid_array[0:-1:scale, :, :] = [0, 0, 0, 255]

    return grid_array


class EmulatedLEDWall(arcade.Window):
    """
    Main application class.
    """

    def __init__(
        self,
        window_width: int,
        window_height: int,
        panel_width: int,
        panel_height: int,
        display_scale: int,
        frame_queue: mp.Queue,
        title: str,
    ):
        super().__init__(
            window_width, window_height, title, antialiasing=False
        )

        self._window_width = window_width
        self._window_height = window_height
        self._panel_width = panel_width
        self._panel_height = panel_height
        self._display_scale = display_scale
        self._frame_queue = frame_queue

        arcade.enable_timings()

        blank_frame = np.zeros(
            (self._panel_height, self._panel_height, 4), dtype=np.uint8
        )

        self.frame = NumpySprite(
            self.ctx,
            self._window_width / 2,
            self._window_height / 2,
            self._panel_width,
            self._panel_height,
            self._window_width,
            self._window_height,
            blank_frame,
        )

        grid_array = generate_grid(window_width, window_height, display_scale)

        self.grid = NumpySprite(
            self.ctx,
            (self._window_width / 2),
            (self._window_height / 2),
            self._window_width,
            self._window_height,
            self._window_width,
            self._window_height,
            grid_array,
        )

        self.left_channel_bins = np.full((self._panel_width), 0)
        self.right_channel_bins = np.full((self._panel_width), 0)

        arcade.set_background_color(arcade.color.BLACK)

    def on_update(self, delta_time: float):
        while self._frame_queue.empty():
            # wait till we have a frame
            pass

        while not self._frame_queue.empty():
            newest_frame = self._frame_queue.get()

        assert newest_frame.shape == (self._panel_height, self._panel_width, 4)
        self.frame.write(newest_frame)

        # print(arcade.get_fps())

    def on_draw(self):
        """
        Render the screen.
        """
        self.clear()

        self.frame.draw()
        self.grid.draw()


def process(**kwargs):
    EmulatedLEDWall(title="LED Panel Emulator", **kwargs)
    arcade.run()
