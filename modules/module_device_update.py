import time

from PyQt5.QtCore import QObject, pyqtSignal

from Backend.Interfaces.interface_jrk import get_ports
from Backend.Interfaces.interface_ui import UIInterface


class DeviceUpdateModule(QObject):
    finished = pyqtSignal()

    def __init__(self, ui_interface: UIInterface):
        super().__init__()
        self.ui_interface = ui_interface

    def run(self):
        prev_device = []
        while True:
            current_ports = get_ports()
            if prev_device != current_ports:
                self.ui_interface.device_combobox.clear()
                for port in get_ports():
                    self.ui_interface.device_combobox.addItem(port.description)
            prev_device = current_ports
            time.sleep(0.1)
