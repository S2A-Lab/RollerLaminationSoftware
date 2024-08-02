from PyQt5.QtCore import QObject, pyqtSignal

from interfaces.interface_jrk import JRKInterface
from interfaces.interface_phidget import PhidgetInterface


class ConnectModule(QObject):
    finished = pyqtSignal()

    def __init__(self, phidget_interface: PhidgetInterface, jrk_interface: JRKInterface, serial_port: str):
        super().__init__()
        self.phidget_interface = phidget_interface
        self.jrk_interface = jrk_interface
        self.serial_port = serial_port

    def connect(self):
        self.phidget_interface.connect()
        self.jrk_interface.connect(self.serial_port, 115200)
        self.finished.emit()

    def disconnect(self):
        self.phidget_interface.disconnect()
        self.jrk_interface.disconnect()
        self.finished.emit()
