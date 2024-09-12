import serial
from PyQt5.QtCore import QObject
from serial.tools import list_ports
import re
from datastruct.datastruct_timeseries import Timeseries


def get_ports():
    return list_ports.comports()


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

    def send_target(self, target0, target1):
        self.serial_port.writelines([(str(target0) + "," + str(target1)).encode()])

    def get_position(self)->[int, int]:
        match = False
        while not match:
            feedback_str = self.serial_port.readline().decode()
            match = re.search(r"x:(\d+), y:(\d+)", feedback_str)
            if match:
                x = int(match.group(1))
                y = int(match.group(2))
                return [x, y]