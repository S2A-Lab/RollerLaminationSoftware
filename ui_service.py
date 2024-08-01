import sys
import time
from multiprocessing import Process, Queue

from PyQt5.QtWidgets import QApplication

from phidget_interface import PhidgetInterface
from qt_plotter import QtPlotterUI


class UIService:

    def __init__(self):
        app = QApplication(sys.argv)

        self.ex = QtPlotterUI()
        self.ex.set_connect_button_function(PhidgetInterface.connect_button_handler)
        task = Process(target=self.__plotter_update_thread)
        task.start()
        task.join()
        self.ex.show()

        sys.exit(app.exec_())

    def __plotter_update_thread(self):
        while True:
            if PhidgetInterface.get_connected(PhidgetInterface):
                self.ex.update_plot(PhidgetInterface.data[0], PhidgetInterface.data[1])
            time.sleep(1)
