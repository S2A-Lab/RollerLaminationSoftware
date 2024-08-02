import time

from PyQt5.QtCore import QTimer, QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QPushButton, QMessageBox

from interfaces.interface_jrk import JRKInterface, get_ports
from interfaces.interface_phidget import PhidgetInterface
from interfaces.interface_ui import UIInterface
from modules.module_connect import ConnectModule
from modules.module_device_update import DeviceUpdateModule
from modules.module_pid_controllers import PIDControllersModule
from modules.module_plot_update import PlotUpdateModule
from modules.module_save import SaveModule


class MainService(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Laminator UI')
        self.ui_interface = UIInterface()
        self.phidget_interface = PhidgetInterface()
        self.jrk_interface = JRKInterface()

        self.plot_update_module = PlotUpdateModule(self.phidget_interface, self.ui_interface)

        self.setCentralWidget(self.ui_interface)
        self.resize(500, 750)

        self.ui_interface.set_callback_connect_button_clicked(self.__connect_button_clicked_handler)
        self.ui_interface.set_callback_interval_textfield_change(self.__interval_textfield_handler)
        self.ui_interface.set_callback_save_button_clicked(self.__save_button_clicked_handler)
        self.ui_interface.set_callback_clear_button_clicked(self.__clear_button_clicked_handler)

        self.ui_interface.show()
        self.timer = QTimer()
        self.__start_update_plot_thread()
        self.__start_device_update_thread()
        self.__start_linear_actuator_pid_controller_thread()
        self.ui_interface.get_control_layouts(0).set_button_handler(self.__pid_set_button_0_clicked_handler)
        self.ui_interface.get_control_layouts(1).set_button_handler(self.__pid_set_button_1_clicked_handler)

        self.ui_interface.get_control_layouts(0).set_target_handler(self.__target_set_button_clicked_handler)
        self.ui_interface.get_control_layouts(1).set_target_handler(self.__target_set_button_clicked_handler)

    def __start_update_plot_thread(self):

        self.plot_update_thread = QThread()
        self.plot_update_module = PlotUpdateModule(self.phidget_interface, self.ui_interface)
        self.plot_update_module.moveToThread(self.plot_update_thread)
        self.plot_update_thread.started.connect(self.plot_update_module.run)
        self.plot_update_module.finished.connect(self.plot_update_thread.quit)
        self.plot_update_module.finished.connect(self.plot_update_module.deleteLater)
        self.plot_update_thread.finished.connect(self.plot_update_thread.deleteLater)
        self.plot_update_thread.start()

    def __start_device_update_thread(self):
        # Start device update thread
        self.device_update_thread = QThread()

        self.device_update_module = DeviceUpdateModule(self.ui_interface)
        self.device_update_module.moveToThread(self.device_update_thread)
        self.device_update_thread.started.connect(self.device_update_module.run)
        self.device_update_module.finished.connect(self.device_update_thread.quit)
        self.device_update_module.finished.connect(self.device_update_module.deleteLater)
        self.device_update_thread.finished.connect(self.device_update_thread.deleteLater)

        self.device_update_thread.start()

    def __start_linear_actuator_pid_controller_thread(self):
        self.linear_actuator_pid_thread = QThread()
        self.linear_actuator_pid_module = PIDControllersModule(self.phidget_interface, self.jrk_interface)
        self.linear_actuator_pid_module.moveToThread(self.linear_actuator_pid_thread)

        self.linear_actuator_pid_thread.started.connect(self.linear_actuator_pid_module.run)
        self.linear_actuator_pid_thread.finished.connect(self.linear_actuator_pid_thread.deleteLater)

        self.linear_actuator_pid_thread.start()

    def __interval_textfield_handler(self, textfield: QLineEdit):
        if textfield.text().isnumeric():
            self.plot_update_module.change_interval(int(textfield.text()))

    def __filename_textfield_handler(self, textfield: QLineEdit):
        self.phidget_interface.set_file_name(textfield.text())

    def __save_button_clicked_handler(self, button: QPushButton, textfield: QLineEdit):
        self.phidget_interface.set_file_name(textfield.text())
        self.save_thread = QThread()
        self.save_module = SaveModule(self.phidget_interface)
        self.save_module.moveToThread(self.save_thread)
        self.save_thread.started.connect(self.save_module.run)
        self.save_module.finished.connect(self.save_thread.quit)
        self.save_module.finished.connect(self.save_module.deleteLater)
        self.save_thread.finished.connect(self.save_thread.deleteLater)

        self.save_thread.start()
        button.setEnabled(False)
        self.save_thread.finished.connect(lambda: button.setEnabled(True))

    def __connect_button_clicked_handler(self, button: QPushButton):
        self.connect_thread = QThread(self)
        self.connect_module = ConnectModule(self.phidget_interface,
                                            self.jrk_interface,
                                            get_ports()[self.ui_interface.device_combobox.currentIndex()].device)
        self.connect_module.moveToThread(self.connect_thread)
        if not self.phidget_interface.get_connected():
            self.connect_thread.started.connect(self.connect_module.connect)
            button.setText('Disconnect')
        else:
            self.connect_thread.started.connect(self.connect_module.disconnect)
            button.setText('Connect')
        self.connect_module.finished.connect(self.connect_thread.quit)
        self.connect_module.finished.connect(self.connect_module.deleteLater)
        self.connect_thread.finished.connect(self.connect_thread.deleteLater)
        self.connect_thread.start()

        button.setEnabled(False)

        self.connect_thread.finished.connect(lambda: button.setEnabled(True))

    def __clear_button_clicked_handler(self, button: QPushButton):
        self.phidget_interface.clear_data()

    def __clear_button_handler(self):
        self.phidget_interface.clear_data()

    def __pid_set_button_0_clicked_handler(self, kp_str: str, ki_str: str, kd_str: str, i_lim_str: str):
        if kp_str.isnumeric() and ki_str.isnumeric() and kd_str.isnumeric() and i_lim_str.isnumeric():
            kp = float(kp_str)
            ki = float(ki_str)
            kd = float(kd_str)
            i_lim = float(i_lim_str)
            self.linear_actuator_pid_module.set_pid_params(0, kp, ki, kd, i_lim)
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if parameters in axis 0 contains non-numeric characters')

    def __pid_set_button_1_clicked_handler(self, kp_str: str, ki_str: str, kd_str: str, i_lim_str: str):
        if kp_str.isnumeric() and ki_str.isnumeric() and kd_str.isnumeric() and i_lim_str.isnumeric():
            kp = float(kp_str)
            ki = float(ki_str)
            kd = float(kd_str)
            i_lim = float(i_lim_str)
            self.linear_actuator_pid_module.set_pid_params(1, kp, ki, kd, i_lim)
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if parameters in axis 1 contains non-numeric characters')

    def __target_set_button_clicked_handler(self, sink: str):
        targets = self.ui_interface.get_targets()
        if targets[0].isnumeric() and targets[1].isnumeric():
            target0 = float(targets[0])
            target1 = float(targets[1])

            if target0 * target1 <= 0:
                QMessageBox.warning(QMessageBox(),
                                    'Warning',
                                    'Invalid target, will result in unstable case')
            else:
                self.linear_actuator_pid_module.set_targets(target0, target1)
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if targets contains non-numeric characters')

