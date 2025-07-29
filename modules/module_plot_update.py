from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from Backend.Interfaces.interface_ui import UIInterface
from Backend.DataLogger.module_data_logger import DataLoggerModule


class PlotUpdateModule(QObject):
    finished = pyqtSignal()
    interval = 300

    def __init__(self, data_logger_module: DataLoggerModule, ui_interface: UIInterface):
        super().__init__()
        self.data_logger_module = data_logger_module
        self.ui_interface = ui_interface
        self.loop_timer = QTimer()
        self.loop_timer.timeout.connect(self.run)
        self.loop_timer.start(self.interval)

    def run(self):

        self.ui_interface.update_plot(self.data_logger_module.target_data[0], self.data_logger_module.feedback_data[0],
                                      self.data_logger_module.target_data[1], self.data_logger_module.feedback_data[1])
        self.ui_interface.update_y_limits(self.data_logger_module.lb, self.data_logger_module.ub)
        if self.data_logger_module.target_data[0].data.__len__() > 0:
            self.ui_interface.update_positions(self.data_logger_module.output_data[0].data[-1], self.data_logger_module.output_data[1].data[-1])

    def change_interval(self, interval):
        self.interval = interval
        self.loop_timer.setInterval(interval)

