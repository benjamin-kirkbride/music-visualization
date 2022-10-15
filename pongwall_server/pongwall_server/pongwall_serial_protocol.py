"""Pongwall Serial Protocol

Args:
    1: Device location of Controller. Ex: /dev/ttyACM0

Globals:
    CONTROLLER: Serial connection to controller
    CONTROL_BYTE: Control byte as per PongWall Protocol Specification
    LITERAL_CONTROL_BYTE_MODIFIER: Byte to send a literal control byte in the data
        portion of the packet as per PongWall Protocol Specification
    START_CODE: Control Code for starting a packet as per PongWall Protocol
        Specification
    END_CODE: Control Code for ending a packet as per PongWall Protocol
        Specification
"""

import re

CONTROL_BYTE = 0x10
LITERAL_CONTROL_BYTE_MODIFIER = CONTROL_BYTE

START_CODE = [CONTROL_BYTE, 0x01]
END_CODE = [CONTROL_BYTE, 0x02]


def create_packet(data: bytes) -> bytes:
    """ Create a packet based on the PongWall Protocol Specification

    Args:
        data: data to be encapsulated

    Returns:
        bytes: the packet
    """
    encoded_control_byte = chr(CONTROL_BYTE).encode()
    escaped_data = re.sub(encoded_control_byte, encoded_control_byte * 2, data)
    packet = bytes(START_CODE) + escaped_data + bytes(END_CODE)
    return packet
