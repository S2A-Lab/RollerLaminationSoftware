import serial
from PyQt5.QtCore import QObject
from serial.tools import list_ports
import re
import numpy as np
from datastruct.datastruct_timeseries import Timeseries

import subprocess
import yaml

def jrk2cmd(*args):
    return subprocess.check_output(['jrk2cmd'] + list(args))

def get_ports():
    return list_ports.comports()


def split_16bit_to_7bit_chunks(value: int):
    # Ensure the value is within 16-bit range
    value = np.int16(value)
    if value < -0x8000 or value > 0x7FFF:
        raise ValueError("Value exceeds 16-bit integer range.")

    # Extract the two 7-bit chunks and the remaining 2 bits
    first_chunk = value & 0x7F  # Extracts the lower 7 bits (0x7F is 0b01111111)
    second_chunk = (value >> 7) & 0x7F  # Extracts the next 7 bits
    remaining_bits = (value >> 14) & 0x03  # Extracts the remaining 2 bits

    # Store them in byte arrays
    byte_array = [first_chunk, second_chunk, remaining_bits]

    return byte_array

def reconstruct_16bit_value(chunk1, chunk2, remaining_bits):
    # Reconstruct the 16-bit value from the 2-bit remaining and two 7-bit chunks
    return (remaining_bits << 14) | (chunk2 << 7) | chunk1

class JRKInterface(QObject):
    serial_port = serial.Serial()
    __connected = False

    def __init__(self):
        super().__init__()
        self.serial_port = serial.Serial()

    def connect(self, port_name, baudrate: int):
        self.serial_port = serial.Serial(port_name, baudrate)
        self.__connected = True

    def disconnect(self):
        self.serial_port.close()
        self.__connected = False

    def get_connected(self):
        return self.__connected

    def send_target(self, target0 : int, target1 : int, target2 : int):
        jrk2cmd('-d', '00425280', '--target', str(int(target0)))
        jrk2cmd('-d', '00425253', '--target', str(int(target1)))

        self.serial_port.write(bytearray([*split_16bit_to_7bit_chunks(target0),
                                          *split_16bit_to_7bit_chunks(target1),
                                          *split_16bit_to_7bit_chunks(target2),
                                          255]))
        self.serial_port.writelines([(str(target0) + "," + str(target1) +","+ str(target2) + "\r\n").encode()])

    def get_position(self) -> [int, int, int]:
        while self.serial_port.read(1) != b'\xff':
           pass

        received_data = self.serial_port.read(10)
        if received_data[9] == 255:
            # Reconstruct each 16-bit target value
            # x = reconstruct_16bit_value(received_data[0], received_data[1], received_data[2])
            # y = reconstruct_16bit_value(received_data[3], received_data[4], received_data[5])
            status_x = yaml.safe_load(jrk2cmd('-d', '00425280', '-s', '--full'))
            x = status_x['Scaled Feedback']
            status_y = yaml.safe_load(jrk2cmd('-d', '00425253', '-s', '--full'))
            y = status_y['Scaled Feedback']
            z = reconstruct_16bit_value(received_data[6], received_data[7], received_data[8])
            return [x, y, z]
