"""test pongwall_serial_protocol module"""
import os
# pylint: disable=W0212,W0613,W9015,W9016,W9011,W9012,W0401,W0614
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pytest
from pongwall_server.pongwall_serial_protocol import *

TESTS_PATH = Path(os.path.dirname(os.path.realpath(__file__)))


@contextmanager
def does_not_raise():
    """Used in 'raises' arguments for test functions.

    See:
        https://docs.pytest.org/en/latest/example/parametrize.html#parametrizing-conditional-raising

    Yields:
        None: Not sure how this works.
    """
    yield


@pytest.mark.parametrize(
    "args,expected,raises",
    [
        (b"", b"\x10\x01\x10\x02", does_not_raise()),
        (b"a", b"\x10\x01a\x10\x02", does_not_raise()),
        (b"A", b"\x10\x01A\x10\x02", does_not_raise()),
        (b"z", b"\x10\x01z\x10\x02", does_not_raise()),
        (b"Z", b"\x10\x01Z\x10\x02", does_not_raise()),
        (b"aoeu", b"\x10\x01aoeu\x10\x02", does_not_raise()),
        (b"\xDE\xAD\xBE\xEF", b"\x10\x01\xDE\xAD\xBE\xEF\x10\x02", does_not_raise()),
        (b"\x10", b"\x10\x01\x10\x10\x10\x02", does_not_raise()),
        ("", None, pytest.raises(TypeError)),
        (b"", b"\x10\x01\x10\x02", does_not_raise()),
        (b"Hello\x10World!", b"\x10\x01Hello\x10\x10World!\x10\x02", does_not_raise()),
        (
            bytearray("Hello World!", "ascii"),
            b"\x10\x01Hello World!\x10\x02",
            does_not_raise(),
        ),
        (
            bytearray("Hello\x10World!", "ascii"),
            b"\x10\x01Hello\x10\x10World!\x10\x02",
            does_not_raise(),
        ),
        (
            bytes("Hello World!", "ascii"),
            b"\x10\x01Hello World!\x10\x02",
            does_not_raise(),
        ),
        (
            bytes("Hello\x10World!", "ascii"),
            b"\x10\x01Hello\x10\x10World!\x10\x02",
            does_not_raise(),
        ),
        (np.zeros(1, dtype=np.uint8), b"\x10\x01\x00\x10\x02", does_not_raise()),
        (
            np.zeros(50000, dtype=np.uint8),
            b"\x10\x01" + b"\x00" * 50000 + b"\x10\x02",
            does_not_raise(),
        ),
        (
            np.full((50000, 1), np.uint8(0x10), dtype=np.uint8),
            b"\x10\x01" + b"\x10" * 100000 + b"\x10\x02",
            does_not_raise(),
        ),
    ],
)
def test_create_packet(args, expected, raises):
    """Tests _verify_suffix function"""
    with raises:
        assert create_packet(args) == expected
