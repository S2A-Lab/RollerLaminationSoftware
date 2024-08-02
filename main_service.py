import time

from PyQt5.QtCore import QTimer, QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QPushButton

from interfaces.jrk_interface import JRKInterface, get_ports
from interfaces.phidget_interface import PhidgetInterface
from interfaces.ui_interface import UIInterface


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


class PlotUpdateWorker(QObject):
    finished = pyqtSignal()
    refresh_rate = 0.3

    def __init__(self, phidget_interface: PhidgetInterface, ui_interface: UIInterface):
        super().__init__()
        self.phidget_interface = phidget_interface
        self.ui_interface = ui_interface

    def run(self):
        while True:
            if self.phidget_interface.get_connected():
                self.ui_interface.update_plot(self.phidget_interface.data[0], self.phidget_interface.data[1],
                                              self.phidget_interface.data[1], self.phidget_interface.data[1])
            time.sleep(self.refresh_rate)


class DeviceUpdateWorker(QObject):
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


class MainService(QMainWindow):
    def __init__(self):
        super().__init__()
        self.plot_update_thread = None
        self.plot_update_worker = None
        self.setWindowTitle('Laminator UI')
        self.ui_interface = UIInterface()
        self.setCentralWidget(self.ui_interface)

        self.phidget_interface = PhidgetInterface()
        self.jrk_interface = JRKInterface()

        self.resize(500, 750)

        self.ui_interface.set_callback_connect_button_clicked(self.__connect_button_clicked_handler)
        self.ui_interface.set_callback_interval_textfield_change(self.__interval_button_handler)
        self.ui_interface.set_callback_save_button_clicked(self.__save_button_clicked_handler)
        self.ui_interface.set_callback_clear_button_clicked(self.__clear_button_clicked_handler)

        self.ui_interface.show()
        self.timer = QTimer()
        self.__start_update_plot_thread()
        self.__start_device_update_thread()

    def __start_update_plot_thread(self):

        self.plot_update_thread = QThread()
        self.plot_update_worker = PlotUpdateWorker(self.phidget_interface, self.ui_interface)
        self.plot_update_worker.moveToThread(self.plot_update_thread)
        self.plot_update_thread.started.connect(self.plot_update_worker.run)
        self.plot_update_worker.finished.connect(self.plot_update_thread.quit)
        self.plot_update_worker.finished.connect(self.plot_update_worker.deleteLater)
        self.plot_update_thread.finished.connect(self.plot_update_thread.deleteLater)
        self.plot_update_thread.start()

    def __start_device_update_thread(self):
        # Start device update thread
        self.device_update_thread = QThread()

        self.device_update_worker = DeviceUpdateWorker(self.ui_interface)
        self.device_update_worker.moveToThread(self.device_update_thread)
        self.device_update_thread.started.connect(self.device_update_worker.run)
        self.device_update_worker.finished.connect(self.device_update_thread.quit)
        self.device_update_worker.finished.connect(self.device_update_worker.deleteLater)
        self.device_update_thread.finished.connect(self.device_update_thread.deleteLater)

        self.device_update_thread.start()

    def __interval_button_handler(self, textfield: QLineEdit):
        if textfield.text().isnumeric():
            self.plot_update_worker.refresh_rate = int(textfield.text()) / 1000

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
        self.connect_worker = ConnectWorker(self.phidget_interface,
                                            self.jrk_interface,
                                            get_ports()[self.ui_interface.device_combobox.currentIndex()].device)
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

    def __clear_button_clicked_handler(self, button: QPushButton):
        self.phidget_interface.clear_data()

    def __clear_button_handler(self):
        self.phidget_interface.clear_data()
