import time

import serial
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from serial.tools import list_ports


def get_ports():
    return list_ports.comports()


class JRKInterface(QObject):
    serial_port = serial.Serial()
    __connected = False

    def __init__(self) -> object:
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

    def send_target(self, target1, target2):
        self.serial_port.writelines([(str(target1) + "," + str(target2)).encode()])
