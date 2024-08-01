from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QLineEdit

from phidget_interface import PhidgetInterface
from qt_plotter import QtPlotterUI


class UIService(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui_interface = QtPlotterUI()
        self.setCentralWidget(self.ui_interface)
        self.phidget_interface = PhidgetInterface()
        self.resize(500, 750)

        self.ui_interface.set_connect_button_function(self.phidget_interface.connect_button_handler)
        self.ui_interface.set_interval_input_function(self.__set_interval_handler)

        self.ui_interface.show()

        self.timer = QTimer()
        self.timer.timeout.connect(self.run_tasks)
        self.timer.start(300)

    def run_tasks(self):
        if self.phidget_interface.get_connected():
            self.ui_interface.update_plot(self.phidget_interface.data[0], self.phidget_interface.data[1],
                                          self.phidget_interface.data[0], self.phidget_interface.data[1])

    def __set_interval_handler(self, textfield: QLineEdit):
        if textfield.text().isnumeric():
            self.timer.setInterval(int(textfield.text()))
