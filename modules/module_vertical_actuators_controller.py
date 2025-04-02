from enum import EnumType, Enum

from PyQt5.QtCore import QObject, QTimer

from interfaces.interface_phidget import PhidgetInterface
from interfaces.interface_jrk import JRKInterface
from controllers.pid_controller import PIDController


class VerticalActuatorsController(QObject):
    sampling_time = 200
    target_forces = [0, 0]
    prev_output = [0, 0]
    output = [0, 0]
    PID_zero_position = [0, 0]


    class ControllerMode(Enum):
        POSITION = 0
        TORQUE = 1

    controller_mode = ControllerMode.POSITION

    def __init__(self, phidget_interface: PhidgetInterface, jrk_interface: JRKInterface):
        super().__init__()
        self.phidget_interface = phidget_interface
        self.jrk_interface = jrk_interface
        self.pid_controllers = [PIDController(0, 0, 0, 0, 0.2),
                                PIDController(0, 0, 0, 0, 0.2)]
        self.target_forces = [0, 0]
        self.linear_stage_velocity = 0
        self.loop_timer = QTimer()
        self.loop_timer.timeout.connect(self.run)
        self.loop_timer.start(self.sampling_time)

        self.watchdog_threshold = 500
        self.initialized = False

        self.horizontal_target_speed = 0

    def run(self):
        if self.phidget_interface.get_connected() and self.jrk_interface.get_connected():
            if not self.initialized:
                self.PID_zero_position = self.jrk_interface.get_position()
                if self.PID_zero_position[0] > 30 and self.PID_zero_position[1] > 30:
                    self.initialized = True
                return
            match self.controller_mode:
                case VerticalActuatorsController.ControllerMode.TORQUE:
                    voltages = self.phidget_interface.get_voltages()
                    self.output = [ self.pid_controllers[0].update(voltages[0], self.target_forces[0]),
                                    self.pid_controllers[1].update(voltages[1], self.target_forces[1])]

                    self.jrk_interface.send_target(int(-self.output [0] + self.PID_zero_position[0]),
                                                   int(-self.output [1] + self.PID_zero_position[1]),
                                                        self.horizontal_target_speed)
                    self.prev_output[0] = self.output[0]
                    self.prev_output[1] = self.output[1]

                case VerticalActuatorsController.ControllerMode.POSITION:
                    self.output = [ int(self.PID_zero_position[0]),
                                    int(self.PID_zero_position[1])]
                    self.prev_output[0] = self.output[0]
                    self.prev_output[1] = self.output[1]
                    self.jrk_interface.send_target(*self.output, self.horizontal_target_speed)

    def set_mode(self, mode: ControllerMode):
        self.controller_mode = mode
        self.pid_controllers[0].clear_errors()
        self.pid_controllers[1].clear_errors()

    def set_targets_forces(self, target0, target1):
        self.target_forces[0] = target0
        self.target_forces[1] = target1

    def set_horizontal_target_speed(self, speed):
        if self.jrk_interface.get_connected():
            self.jrk_interface.send_horizontal(speed*0.78125)
            self.linear_stage_velocity = speed*0.78125
            print("Sent")

    def set_pid_params(self, controller_id: int, kp: float, ki: float, kd: float, i_limit: float):
        self.pid_controllers[controller_id].set_pid_params(kp, ki, kd, i_limit)

    def set_positions(self, target0, target1):
        self.PID_zero_position[0] = target0
        self.PID_zero_position[1] = target1

    def get_positions(self):
        return self.PID_zero_position
