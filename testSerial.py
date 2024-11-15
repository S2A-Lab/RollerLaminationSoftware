import serial
from serial.tools import list_ports
import numpy as np

serial_port = serial.Serial("COM12",115200)
print(list_ports.comports()[4].device)

targetz = value = np.int16(2000)
first_chunk = targetz & 0x7F  # Extracts the lower 7 bits (0x7F is 0b01111111)
second_chunk = (targetz >> 7) & 0x7F  # Extracts the next 7 bits
remaining_bits = (targetz >> 14) & 0x03  # Extracts the remaining 2 bits

serial_port.write(bytearray([0, 0, 0, 0, 0, 0,
                                  first_chunk, second_chunk, remaining_bits,
                                  255]))
serial_port.write(bytearray([0, 0, 0, 0, 0, 0,
                                  first_chunk, second_chunk, remaining_bits,
                                  255]))
serial_port.write(bytearray([0, 0, 0, 0, 0, 0,
                                  first_chunk, second_chunk, remaining_bits,
                                  255]))
serial_port.write(bytearray([0, 0, 0, 0, 0, 0,
                                  first_chunk, second_chunk, remaining_bits,
                                  255]))


serial_port.close()
