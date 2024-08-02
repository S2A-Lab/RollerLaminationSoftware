from PyQt5.QtCore import QObject, QTimer

from interfaces.interface_phidget import PhidgetInterface
from interfaces.interface_jrk import JRKInterface
from controllers.pid_controller import PIDController


class PIDControllersModule(QObject):
    sampling_time = 100
    output_0 = 0
    output_1 = 0
    targets = [0, 0]

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
        self.prev_output_0 = 0
        self.prev_output_1 = 0
        self.output_0 = 0
        self.output_1 = 0
        self.watchdog_threshold = 400

    def run(self):
        if self.phidget_interface.get_connected() and self.jrk_interface.get_connected():
            voltages = self.phidget_interface.get_voltages()
            self.output_0 = self.pid_controllers[0].update(voltages[0], self.targets[0])
            self.output_1 = self.pid_controllers[1].update(voltages[1], self.targets[1])

            # target watchdog
            if (self.output_0 - self.output_1) > self.watchdog_threshold:
                if self.prev_output_0 - self.output_0 > 0:
                    self.output_0 = self.output_1 + self.watchdog_threshold
                elif self.prev_output_0 - self.output_0 <= 0:
                    self.output_1 = self.output_0 - self.watchdog_threshold
            elif (self.output_1 - self.output_0) > self.watchdog_threshold:
                if self.prev_output_1 - self.output_1 > 0:
                    self.output_1 = self.output_0 + self.watchdog_threshold
                elif self.prev_output_1 - self.output_1 <= 0:
                    self.output_0 = self.output_1 - self.watchdog_threshold

            self.jrk_interface.send_target(int(self.output_0), int(self.output_1))
            self.prev_output_0 = self.output_0
            self.prev_output_1 = self.output_1

    def set_targets(self, target1, target2):
        self.targets[0] = target1
        self.targets[1] = target2

    def set_pid_params(self, controller_id: int, kp: float, ki: float, kd: float, i_limit: float):
        self.pid_controllers[controller_id].set_pid_params(kp, ki, kd, i_limit)