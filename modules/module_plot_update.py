from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from interfaces.interface_phidget import PhidgetInterface
from interfaces.interface_ui import UIInterface


class PlotUpdateModule(QObject):
    finished = pyqtSignal()
    interval = 300

    def __init__(self, phidget_interface: PhidgetInterface, ui_interface: UIInterface):
        super().__init__()
        self.phidget_interface = phidget_interface
        self.ui_interface = ui_interface
        self.loop_timer = QTimer()
        self.loop_timer.timeout.connect(self.run)
        self.loop_timer.start(self.interval)

    def run(self):
        if self.phidget_interface.get_connected():
            self.ui_interface.update_plot(self.phidget_interface.data[0], self.phidget_interface.data[1],
                                          self.phidget_interface.data[1], self.phidget_interface.data[1])

    def change_interval(self, interval):
        self.interval = interval
        self.loop_timer.setInterval(interval)

