from enum import Enum

from PyQt5.QtCore import QObject, QTimer

from Backend.Interfaces.interface_horizontal_stage import HorizontalStageInterface
from Backend.Interfaces.interface_phidget import PhidgetInterface
from Backend.Interfaces.interface_jrk import JRKInterface
from controllers.pid_controller import PIDController

class ActuatorsController(QObject):
    sampling_time = 10
    target_forces = [0.0, 0.0]
    prev_output = [0, 0]
    output = [0, 0]
    target_positions = [0, 0]


    class ControllerMode(Enum):
        POSITION = 0
        TORQUE = 1

    controller_mode = ControllerMode.POSITION

    def __init__(self):
        super().__init__()
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
        if PhidgetInterface.get_connected() and HorizontalStageInterface.get_connected():
            if not self.initialized:
                self.target_positions = JRKInterface.get_position()
                if self.target_positions[0] > 30 and self.target_positions[1] > 30:
                    self.initialized = True
                return
            match self.controller_mode:
                case ActuatorsController.ControllerMode.TORQUE:
                    voltages = PhidgetInterface.get_calibrated_forces()
                    self.output = [ self.pid_controllers[0].update(voltages[0], self.target_forces[0]),
                                    self.pid_controllers[1].update(voltages[1], self.target_forces[1])]

                    JRKInterface.set_duty_cycle((-self.output[0],-self.output [1]))

                    self.prev_output[0] = self.output[0]
                    self.prev_output[1] = self.output[1]


                case ActuatorsController.ControllerMode.POSITION:
                    self.output = [int(self.target_positions[0]),
                                   int(self.target_positions[1])]
                    self.prev_output[0] = self.output[0]
                    self.prev_output[1] = self.output[1]
                    JRKInterface.set_target_position(*self.output)

    def set_mode(self, mode: ControllerMode):
        self.controller_mode = mode
        self.pid_controllers[0].clear_errors()
        self.pid_controllers[1].clear_errors()

    def set_horizontal_maximum_speed(self, speed):
        if HorizontalStageInterface.get_connected():
            HorizontalStageInterface.send_speed_limit(speed*0.78125)
            self.linear_stage_velocity = speed*0.78125

    def set_horizontal_maximum_acceleration(self, accel):
        if HorizontalStageInterface.get_connected():
            HorizontalStageInterface.send_speed_limit(accel*0.78125)
            self.linear_stage_velocity = accel*0.78125

    def set_horizontal_target_position(self, position):
        if HorizontalStageInterface.get_connected():
            HorizontalStageInterface.send_target_position(position)

    def set_pid_params(self, controller_id: int, kp: float, ki: float, kd: float, i_limit: float, out_limit: float):
        self.pid_controllers[controller_id].set_pid_params(kp, ki, kd, i_limit, out_limit)

    def set_positions(self, controller_id: int, target):
        self.target_positions[controller_id] = target

    def set_targets_forces(self, controller_id: int, target):
        self.target_forces[controller_id] = target

    def get_positions(self):
        return self.target_positions

