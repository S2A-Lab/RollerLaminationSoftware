import time

from PyQt5.QtCore import QTimer, QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QPushButton

from phidget_interface import PhidgetInterface
from ui_interface import UIInterface


class SaveWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, phidget_interface: PhidgetInterface):
        super().__init__()
        self.phidget_interface = phidget_interface

    def run(self):
        self.phidget_interface.save_data()
        self.finished.emit()


class ConnectWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, phidget_interface: PhidgetInterface):
        super().__init__()
        self.phidget_interface = phidget_interface

    def connect(self):
        self.phidget_interface.connect()
        self.finished.emit()

    def disconnect(self):
        self.phidget_interface.disconnect()
        self.finished.emit()


class UIService(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui_interface = UIInterface()
        self.setCentralWidget(self.ui_interface)
        self.phidget_interface = PhidgetInterface()
        self.resize(500, 750)

        self.ui_interface.set_callback_connect_button_clicked(self.__connect_button_clicked_handler)
        self.ui_interface.set_callback_interval_textfield_change(self.__interval_button_handler)

        self.ui_interface.show()

        self.ui_interface.set_callback_save_button_clicked(self.__save_button_clicked_handler)

        self.timer = QTimer()
        self.timer.timeout.connect(self.run_tasks)
        self.timer.start(300)

    def run_tasks(self):
        if self.phidget_interface.get_connected():
            self.ui_interface.update_plot(self.phidget_interface.data[0], self.phidget_interface.data[1],
                                          self.phidget_interface.data[0], self.phidget_interface.data[1])

    def __interval_button_handler(self, textfield: QLineEdit):
        if textfield.text().isnumeric():
            self.timer.setInterval(int(textfield.text()))

    def __filename_textfield_handler(self, textfield: QLineEdit):
        self.phidget_interface.set_file_name(textfield.text())

    def __save_button_clicked_handler(self, button: QPushButton, textfield: QLineEdit):
        self.phidget_interface.set_file_name(textfield.text())
        self.save_thread = QThread()
        self.save_worker = SaveWorker(self.phidget_interface)
        self.save_worker.moveToThread(self.save_thread)
        self.save_thread.started.connect(self.save_worker.run)
        self.save_worker.finished.connect(self.save_thread.quit)
        self.save_worker.finished.connect(self.save_worker.deleteLater)
        self.save_thread.finished.connect(self.save_thread.deleteLater)

        self.save_thread.start()
        button.setEnabled(False)
        self.save_thread.finished.connect(lambda: button.setEnabled(True))

    def __connect_button_clicked_handler(self, button: QPushButton):
        self.connect_thread = QThread(self)
        self.connect_worker = ConnectWorker(self.phidget_interface)
        self.connect_worker.moveToThread(self.connect_thread)
        if not self.phidget_interface.get_connected():
            self.connect_thread.started.connect(self.connect_worker.connect)
            button.setText('Disconnect')
        else:
            self.connect_thread.started.connect(self.connect_worker.disconnect)
            button.setText('Connect')
        self.connect_worker.finished.connect(self.connect_thread.quit)
        self.connect_worker.finished.connect(self.connect_worker.deleteLater)
        self.connect_thread.finished.connect(self.connect_thread.deleteLater)
        self.connect_thread.start()

        button.setEnabled(False)

        self.connect_thread.finished.connect(lambda: button.setEnabled(True))

    def __clear_button_handler(self):
        self.phidget_interface.clear_data()
