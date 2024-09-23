from warnings import catch_warnings

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QPushButton, QMessageBox, QStyle, QStyleOptionButton

from controllers.pid_controller import PIDController
from interfaces.interface_jrk import JRKInterface, get_ports
from interfaces.interface_phidget import PhidgetInterface
from interfaces.interface_ui import UIInterface
from modules.module_connect import ConnectModule
from modules.module_device_update import DeviceUpdateModule
from modules.module_vertical_actuators_controller import VerticalActuatorsController
from modules.module_plot_update import PlotUpdateModule
from modules.module_data_logger import DataLoggerModule


class MainService(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Laminator UI')
        # Initialize interfaces
        self.ui_interface = UIInterface()
        self.phidget_interface = PhidgetInterface()
        self.jrk_interface = JRKInterface()

        # Initialize PID controllers
        self.linear_actuator_pid_module = VerticalActuatorsController(self.phidget_interface, self.jrk_interface)

        # Initialize data logger
        self.data_logger_module = DataLoggerModule(self.phidget_interface, self.linear_actuator_pid_module)

        self.setCentralWidget(self.ui_interface)
        self.resize(500, 750)
        self.setMinimumSize(500, 750)

        # Binding UI handlers
        self.ui_interface.set_connect_button_clicked_handler(self.__connect_button_clicked_handler)
        self.ui_interface.set_interval_textfield_change_handler(self.__interval_textfield_handler)
        self.ui_interface.set_save_button_clicked_handler(self.__save_button_clicked_handler)
        self.ui_interface.set_clear_button_clicked_handler(self.__clear_button_clicked_handler)

        self.ui_interface.get_control_layouts(0).set_params_button_clicked_handler(self.__pid_params_set_button_0_clicked_handler)
        self.ui_interface.get_control_layouts(1).set_params_button_clicked_handler(self.__pid_params_set_button_1_clicked_handler)
        self.ui_interface.get_control_layouts(0).set_target_force_button_clicked_handler(self.__target_set_torque_button_clicked_handler)
        self.ui_interface.get_control_layouts(1).set_target_force_button_clicked_handler(self.__target_set_torque_button_clicked_handler)

        self.ui_interface.get_control_layouts(0).set_up_button_clicked_handler(self.__jog_up_0_button_clicked_handler)
        self.ui_interface.get_control_layouts(0).set_down_button_clicked_handler(self.__jog_down_0_button_clicked_handler)
        self.ui_interface.get_control_layouts(0).set_all_up_button_clicked_handler(self.__jog_all_up_0_button_clicked_handler)
        self.ui_interface.get_control_layouts(0).set_all_down_button_clicked_handler(self.__jog_all_down_0_button_clicked_handler)

        self.ui_interface.get_control_layouts(1).set_up_button_clicked_handler(self.__jog_up_1_button_clicked_handler)
        self.ui_interface.get_control_layouts(1).set_down_button_clicked_handler(self.__jog_down_1_button_clicked_handler)
        self.ui_interface.get_control_layouts(1).set_all_up_button_clicked_handler(self.__jog_all_up_1_button_clicked_handler)
        self.ui_interface.get_control_layouts(1).set_all_down_button_clicked_handler(self.__jog_all_down_1_button_clicked_handler)

        self.ui_interface.set_start_force_control_button_clicked_handler(self.__start_force_control_button_clicked_handler)
        self.ui_interface.set_tare_button_clicked_handler(self.__tare_button_clicked_handler)
        self.ui_interface.set_horizontal_stage_speed_set_button_clicked_handler(self.__horizontal_stage_speed_set_button_clicked_handler)
        # Start threads
        self.__start_data_logger_thread()
        self.__start_serial_device_update_thread()
        self.__start_linear_actuator_pid_controller_thread()
        self.__start_update_plot_thread()

        # Show UI
        self.ui_interface.show()

    def __start_data_logger_thread(self):
        self.data_logger_thread = QThread(self)
        self.data_logger_module.moveToThread(self.data_logger_thread)
        self.data_logger_thread.started.connect(self.data_logger_thread.run)
        self.data_logger_thread.finished.connect(self.data_logger_thread.deleteLater)
        self.data_logger_thread.start()

    def __start_update_plot_thread(self):
        self.plot_update_thread = QThread()
        self.plot_update_module = PlotUpdateModule(self.data_logger_module, self.ui_interface)
        self.plot_update_module.moveToThread(self.plot_update_thread)
        self.plot_update_thread.started.connect(self.plot_update_module.run)
        self.plot_update_module.finished.connect(self.plot_update_thread.quit)
        self.plot_update_module.finished.connect(self.plot_update_module.deleteLater)
        self.plot_update_thread.finished.connect(self.plot_update_thread.deleteLater)
        self.plot_update_thread.start()

    def __start_serial_device_update_thread(self):
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

        self.linear_actuator_pid_module.moveToThread(self.linear_actuator_pid_thread)

        self.linear_actuator_pid_thread.started.connect(self.linear_actuator_pid_module.run)
        self.linear_actuator_pid_thread.finished.connect(self.linear_actuator_pid_thread.deleteLater)

        self.linear_actuator_pid_thread.start()

    def __interval_textfield_handler(self, textfield: QLineEdit):
        if textfield.text().isnumeric():
            self.plot_update_module.change_interval(int(textfield.text()))

    def __filename_textfield_handler(self, textfield: QLineEdit):
        self.data_logger_module.set_file_name(textfield.text())

    def __save_button_clicked_handler(self, button: QPushButton, textfield: QLineEdit):
        button.setEnabled(False)
        self.data_logger_module.set_file_name(textfield.text())
        save_worker = self.data_logger_module.save_data()
        save_worker.finished.connect(lambda: button.setEnabled(True))

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
        self.data_logger_module.clear_data()

    def __pid_params_set_button_0_clicked_handler(self, kp_str: str, ki_str: str, kd_str: str, i_lim_str: str):
        if is_number(kp_str) and is_number(ki_str) and is_number(kd_str) and is_number(i_lim_str):
            kp = float(kp_str)
            ki = float(ki_str)
            kd = float(kd_str)
            i_lim = float(i_lim_str)
            self.linear_actuator_pid_module.set_pid_params(0, kp, ki, kd, i_lim)
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if parameters in axis 0 contain non-numeric characters')

    def __pid_params_set_button_1_clicked_handler(self, kp_str: str, ki_str: str, kd_str: str, i_lim_str: str):
        if is_number(kp_str) and is_number(ki_str) and is_number(kd_str) and is_number(i_lim_str):
            kp = float(kp_str)
            ki = float(ki_str)
            kd = float(kd_str)
            i_lim = float(i_lim_str)
            self.linear_actuator_pid_module.set_pid_params(1, kp, ki, kd, i_lim)
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if parameters in axis 1 contain non-numeric characters')

    def __target_set_torque_button_clicked_handler(self, sink: str):
        targets = self.ui_interface.get_target_positions_str()
        if is_number(targets[0]) and is_number(targets[1]):
            target0 = float(targets[0])
            target1 = float(targets[1])

            if target0 * target1 <= 0:
                QMessageBox.warning(QMessageBox(),
                                    'Warning',
                                    'Invalid target, will result in unstable case')
            else:
                self.linear_actuator_pid_module.set_targets_forces(target0, target1)
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if targets force contain non-numeric characters')

    def __jog_up_0_button_clicked_handler(self, step: str):
        if is_number(step):
            current_positions = self.linear_actuator_pid_module.get_positions()
            target_positions = current_positions
            target_positions[0] = target_positions[0] + float(step)
            self.linear_actuator_pid_module.set_positions(target_positions[0],
                                                          target_positions[1])
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if step 0 textfield contain non-numeric characters')

    def __jog_up_1_button_clicked_handler(self, step: str):
        if is_number(step):
            current_positions = self.linear_actuator_pid_module.get_positions()
            target_positions = current_positions
            target_positions[1] = target_positions[1] + float(step)
            self.linear_actuator_pid_module.set_positions(target_positions[0],
                                                          target_positions[1])
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if step 1 textfield contain non-numeric characters')

    def __jog_all_up_0_button_clicked_handler(self, step: str):
        if is_number(step):
            current_positions = self.linear_actuator_pid_module.get_positions()
            target_positions = current_positions
            target_positions[0] = target_positions[0] + float(step)
            target_positions[1] = target_positions[1] + float(step)
            self.linear_actuator_pid_module.set_positions(target_positions[0],
                                                          target_positions[1])
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if step 0 textfield contain non-numeric characters')

    def __jog_all_up_1_button_clicked_handler(self, step: str):
        if is_number(step):
            current_positions = self.linear_actuator_pid_module.get_positions()
            target_positions = current_positions
            target_positions[1] = target_positions[1] + float(step)
            target_positions[0] = target_positions[0] + float(step)
            self.linear_actuator_pid_module.set_positions(target_positions[0],
                                                          target_positions[1])
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if step 1 textfield contain non-numeric characters')

    def __jog_down_0_button_clicked_handler(self, step: str):
        if is_number(step):
            current_positions = self.linear_actuator_pid_module.get_positions()
            target_positions = current_positions
            target_positions[0] = target_positions[0] - float(step)
            self.linear_actuator_pid_module.set_positions(target_positions[0],
                                                          target_positions[1])
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if step 0 textfield contain non-numeric characters')

    def __jog_down_1_button_clicked_handler(self, step: str):
        if is_number(step):
            current_positions = self.linear_actuator_pid_module.get_positions()
            target_positions = current_positions
            target_positions[1] = target_positions[1] - float(step)
            self.linear_actuator_pid_module.set_positions(target_positions[0],
                                                          target_positions[1])
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if step 1 textfield contain non-numeric characters')

    def __jog_all_down_0_button_clicked_handler(self, step: str):
        if is_number(step):
            current_positions = self.linear_actuator_pid_module.get_positions()
            target_positions = current_positions
            target_positions[0] = target_positions[0] - float(step)
            target_positions[1] = target_positions[1] - float(step)
            self.linear_actuator_pid_module.set_positions(target_positions[0],
                                                          target_positions[1])
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if step 0 textfield contain non-numeric characters')

    def __jog_all_down_1_button_clicked_handler(self, step: str):
        if is_number(step):
            current_positions = self.linear_actuator_pid_module.get_positions()
            target_positions = current_positions
            target_positions[1] = target_positions[1] - float(step)
            target_positions[0] = target_positions[0] - float(step)
            self.linear_actuator_pid_module.set_positions(target_positions[0],
                                                          target_positions[1])
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if step 1 textfield contain non-numeric characters')

    def __start_force_control_button_clicked_handler(self, button: QPushButton):
        match self.linear_actuator_pid_module.controller_mode:
            case VerticalActuatorsController.ControllerMode.TORQUE:
                self.linear_actuator_pid_module.controller_mode = VerticalActuatorsController.ControllerMode.POSITION
                button.setText('Start Force Control')
                button.setStyleSheet("background-color: green")
            case VerticalActuatorsController.ControllerMode.POSITION:
                self.linear_actuator_pid_module.controller_mode = VerticalActuatorsController.ControllerMode.TORQUE
                button.setText('Stop Force Control')
                button.setStyleSheet("background-color: red")

    def __tare_button_clicked_handler(self, button: QPushButton):
        self.phidget_interface.zero()

    def __horizontal_stage_speed_set_button_clicked_handler(self, button: QPushButton, textfield: QLineEdit):
        if is_number(textfield.text()):
            self.linear_actuator_pid_module.set_horizontal_target_speed(int(textfield.text()))
        else:
            QMessageBox.warning(QMessageBox(),
                                'Warning',
                                'Please check if linear stage speed textfield contain non-numeric characters')

def is_number(number_str: str) -> bool:
    try:
        float(number_str)
        return True
    except ValueError:
        return False