from array import array
from pathlib import Path
from typing import Optional

import arcade
import arcade.gl as gl
import numpy as np

from . import PROJECT_ROOT


class NumpySprite:
    def __init__(
        self,
        ctx: arcade.ArcadeContext,
        center_x: float,
        center_y: float,
        texture_width: int,
        texture_height: int,
        width: int = 0,
        height: int = 0,
        data: Optional[np.ndarray] = None,
        filter: int = gl.NEAREST,
    ):
        self.ctx = ctx

        self._position: arcade.Point = (center_x, center_y)
        self._texture_width = texture_width
        self._texture_height = texture_height

        if width == 0:
            width = self._texture_width

        if height == 0:
            height = self._texture_height

        self._width = width
        self._height = height

        self._position_changed = False
        self._size_changed = False

        self._program = self.ctx.load_program(
            vertex_shader=f"{PROJECT_ROOT}/shaders/vert.glsl",
            fragment_shader=f"{PROJECT_ROOT}/shaders/frag.glsl",
            geometry_shader=f"{PROJECT_ROOT}/shaders/geo.glsl",
        )
        self._program["sprite_texture"] = 0

        self._texture = gl.Texture(
            self.ctx,
            (self._texture_width, self._texture_height),
            filter=(filter, filter),
        )

        if data is None:
            data = np.zeros(
                (self._texture_width, self._texture_height, 4), dtype=np.uint8
            )

        self._texture.write(data)  # type: ignore

        self._vertex_buffer = self.ctx.buffer(
            data=array(
                "f",
                (
                    self._position[0],
                    self._position[1],
                    self._width,
                    self._height,
                ),
            )
        )

        self._geometry = self.ctx.geometry(
            content=[
                gl.BufferDescription(
                    self._vertex_buffer, "2f 2f", ["in_position", "in_size"]
                )
            ]
        )

    @property
    def position(self) -> arcade.Point:
        return self._position

    @position.setter
    def position(self, new_value: arcade.Point):
        if (
            new_value[0] != self._position[0]
            or new_value[1] != self._position[1]
        ):
            self._position = new_value
            self._position_changed = True

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, new_value: int):
        if new_value != self._width:
            self._width = new_value
            self._size_changed = True

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, new_value: int):
        if new_value != self._height:
            self._height = new_value
            self._size_changed = True

    def _write_buffers_to_gpu(self):
        if self._size_changed or self._position_changed:
            self._vertex_buffer.write(
                data=array(
                    "f",
                    (
                        self._position[0],
                        self._position[1],
                        self._width,
                        self._height,
                    ),
                )
            )
            self._size_changed = False
            self._position_changed = False

    def draw(self):

        self._write_buffers_to_gpu()

        self._texture.use(unit=0)
        self._geometry.render(self._program)

    def write(self, data: np.ndarray):
        self._texture.write(data)  # type: ignore
