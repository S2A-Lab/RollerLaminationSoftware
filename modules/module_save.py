from PyQt5.QtCore import QObject, pyqtSignal

from interfaces.interface_phidget import PhidgetInterface


class SaveModule(QObject):
    finished = pyqtSignal()

    def __init__(self, phidget_interface: PhidgetInterface):
        super().__init__()
        self.phidget_interface = phidget_interface

    def run(self):
        self.phidget_interface.save_data()
        self.finished.emit()
