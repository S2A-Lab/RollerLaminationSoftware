import time

import serial
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from serial.tools import list_ports


def get_ports():
    return list_ports.comports()


class JRKInterface(QObject):

    def __init__(self):
        super().__init__()
        self.serial_port = serial.Serial()

    def connect(self, port_name, baudrate: int):
        self.serial_port = serial.Serial(port_name, baudrate)

    def disconnect(self):
        self.serial_port.close()

    def send_target(self, target1, target2):
        self.serial_port.writelines(target1 + "," + target2)

