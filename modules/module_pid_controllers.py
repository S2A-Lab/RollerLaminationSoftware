import time

from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from interfaces.interface_phidget import PhidgetInterface
from interfaces.interface_jrk import JRKInterface
from controllers.pid_controller import PIDController


class PIDControllersModule(QObject):
    sampling_time = 100

    def __init__(self, phidget_interface: PhidgetInterface, jrk_interface: JRKInterface):
        super().__init__()
        self.phidget_interface = phidget_interface
        self.jrk_interface = jrk_interface
        self.pid_controllers = [PIDController(0, 0, 0, 0, 0.1),
                                PIDController(0, 0, 0, 0, 0.1)]
        self.targets = [0, 0]
        self.loop_timer = QTimer()
        self.loop_timer.timeout.connect(self.run)
        self.loop_timer.start(self.sampling_time)
        self.prev_output_1 = 0
        self.prev_output_2 = 0
        self.watchdog_threshold = 400

    def run(self):
        if self.phidget_interface.get_connected() and self.jrk_interface.get_connected():
            if len(self.phidget_interface.data[0].data) > 0 and len(self.phidget_interface.data[1].data) > 0:
                output_axis_1 = self.pid_controllers[0].update(self.phidget_interface.data[0].data[
                                                                   len(self.phidget_interface.data[0].data) - 1],
                                                               self.targets[0])
                output_axis_2 = self.pid_controllers[1].update(self.phidget_interface.data[1].data[
                                                                   len(self.phidget_interface.data[1].data) - 1],
                                                               self.targets[1])

                # target watchdog
                if (output_axis_1 - output_axis_2) > self.watchdog_threshold:
                    if self.prev_output_1 - output_axis_1 > 0:
                        output_axis_1 = output_axis_2 + self.watchdog_threshold
                    elif self.prev_output_1 - output_axis_1 <= 0:
                        output_axis_2 = output_axis_1 - self.watchdog_threshold
                elif (output_axis_2 - output_axis_1) > self.watchdog_threshold:
                    if self.prev_output_2 - output_axis_2 > 0:
                        output_axis_2 = output_axis_1 + self.watchdog_threshold
                    elif self.prev_output_2 - output_axis_2 <= 0:
                        output_axis_1 = output_axis_2 - self.watchdog_threshold

                self.jrk_interface.send_target(output_axis_1, output_axis_2)

    def set_targets(self, target1, target2):
        self.targets[0] = target1
        self.targets[1] = target2

    def set_pid_params(self, controller_id: int, kp: float, ki: float, kd: float, i_limit: float):
        self.pid_controllers[controller_id].set_pid_params(kp, ki, kd, i_limit)
