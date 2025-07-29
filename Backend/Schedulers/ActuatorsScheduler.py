import time
from datetime import time
from enum import Enum
from unittest import case

from PyQt5.QtCore import QObject, QTimer

from Backend.Interfaces.interface_phidget import PhidgetInterface
from Backend.Interfaces.interface_jrk import JRKInterface
from Backend.Interfaces.interface_horizontal_stage import HorizontalStageInterface
from controllers.pid_controller import PIDController
from MacroStep import *
from Backend.Interfaces.vertical_axis_base import VerticalAxis

class ActuatorsControllerState(Enum):
    START = 0
    EXECUTING = 1
    END = 2

class StepExecutionController(QObject):
    sampling_time = 10 # [ms]

    vertical_target_forces = [0.0, 0.0]
    vertical_target_positions = [0.0, 0.0]
    vertical_modes = []

    step_loaded: MacroStep = None
    step_start_time  = 0

    step_execute_state: ActuatorsControllerState = ActuatorsControllerState.END

    class VControllerMode(Enum):
        POSITION = 0
        FORCE    = 1

    def __init__(self):
        super().__init__()
        self.pid_controllers = [PIDController(0, 0, 0, 0, 0.2),
                                PIDController(0, 0, 0, 0, 0.2)]
        self.vertical_controller_mode = []
        self.vertical_target_forces = [0, 0]
        self.linear_stage_velocity = 0
        self.loop_timer = QTimer()
        self.loop_timer.timeout.connect(self.run)
        self.loop_timer.start(self.sampling_time)

        self.initialized = False

        self.horizontal_target_speed = 0

    def run(self):
        if PhidgetInterface.get_connected() and HorizontalStageInterface.get_connected():
            if not self.initialized:
                self.initialized = True
                return
            # Parse macro
            match self.step_execute_state:
                # At start stage parse actions and load to the scheduler
                case ActuatorsControllerState.START:
                    for actions in self.step_loaded.actions:
                        if actions is MacroStep.MoveHorizontalAction:
                            actions : MacroStep.MoveHorizontalAction
                            HorizontalStageInterface.send_speed_limit(actions.max_vel)
                            HorizontalStageInterface.send_accel_limit(actions.max_accel)
                            HorizontalStageInterface.send_target_position(actions.target_position)
                        elif actions is MacroStep.MoveVerticalAction:
                            actions : MacroStep.MoveVerticalAction
                            if actions.axis == MacroStep.MoveVerticalAction.Axis.ALL:
                                self.vertical_modes = [actions.mode, actions.mode]
                                if actions.mode == MacroStep.MoveVerticalAction.Mode.FORCE:
                                    self.vertical_target_forces = [actions.target, actions.target]
                                    self.pid_controllers[0].clear_errors()
                                    self.pid_controllers[1].clear_errors()
                                elif actions.mode == MacroStep.MoveVerticalAction.Mode.POSITION:
                                    self.vertical_target_positions = [actions.target, actions.target]
                            else:
                                self.vertical_modes[actions.axis.value] = actions.mode
                                if actions.mode == MacroStep.MoveVerticalAction.Mode.FORCE:
                                    self.vertical_target_forces[actions.axis.value] = actions.target
                                elif actions.mode == MacroStep.MoveVerticalAction.Mode.POSITION:
                                    self.vertical_target_positions[actions.axis.value] = actions.target
                        elif actions is MacroStep.ChangeVerticalPIDParamsAction:
                            actions : MacroStep.ChangeVerticalPIDParamsAction
                            if actions.axis == MacroStep.ChangeVerticalPIDParamsAction.Axis.ALL:
                                self.pid_controllers[0].set_pid_params(actions.kp, actions.ki, actions.kd,
                                                                       actions.i_limit, actions.out_limit)
                                self.pid_controllers[1].set_pid_params(actions.kp, actions.ki, actions.kd,
                                                                       actions.i_limit, actions.out_limit)
                                self.pid_controllers[0].clear_errors()
                                self.pid_controllers[1].clear_errors()
                            else:
                                self.pid_controllers[actions.axis.value].set_pid_params(actions.kp, actions.ki, actions.kd,
                                                                       actions.i_limit, actions.out_limit)
                                self.pid_controllers[actions.axis.value].clear_errors()
                        elif actions is MacroStep.StopPreviousActions:
                            actions : MacroStep.StopPreviousActions
                            if actions.axis == MacroStep.StopPreviousActions.Axis.ALL:
                                self.vertical_target_forces = [0, 0]
                                self.vertical_target_positions = [JRKInterface.get_position(VerticalAxis.AXIS_0),JRKInterface.get_position(VerticalAxis.AXIS_1)]
                                HorizontalStageInterface.send_target_position(HorizontalStageInterface.get_position())
                            elif actions.axis == MacroStep.StopPreviousActions.Axis.Y:
                                HorizontalStageInterface.send_target_position(HorizontalStageInterface.get_position())
                            else:
                                self.vertical_target_forces[actions.axis.value] = 0
                                self.vertical_target_positions[actions.axis.value] = JRKInterface.get_position(VerticalAxis(actions.axis.value))
                            pass

                    self.step_start_time = time.time() * 1000.0
                    self.step_execute_state = ActuatorsControllerState.EXECUTING
                # At running stage parse and judge the end condition until end
                case ActuatorsControllerState.EXECUTING:
                    # TODO: and / or condition
                    step_end_validation = True
                    for conditions in self.step_loaded.end_conditions:
                        condition_validation = False
                        if conditions is MacroStep.WaitForceEnd:
                            conditions: MacroStep.WaitForceEnd
                            match conditions.axis:
                                case MacroStep.WaitForceEnd.Axis.X0:
                                    condition_validation = (
                                            abs(PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_0)- conditions.target) < conditions.threshold)
                                case MacroStep.WaitForceEnd.Axis.X1:
                                    condition_validation = (
                                            abs(PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_1)- conditions.target) < conditions.threshold)
                                case MacroStep.WaitForceEnd.Axis.ALL:
                                    condition_validation = (
                                            abs(PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_0) - conditions.target) < conditions.threshold and
                                            abs(PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_1) - conditions.target) < conditions.threshold)
                        elif conditions is MacroStep.WaitTimeEnd:
                            conditions: MacroStep.WaitTimeEnd
                            condition_validation = time.time()*1000 - self.step_start_time >= conditions.wait_time
                        elif conditions is MacroStep.WaitPositionEnd:
                            conditions: MacroStep.WaitPositionEnd
                            match conditions.axis:
                                case MacroStep.WaitPositionEnd.Axis.X0:
                                    condition_validation = abs(
                                        JRKInterface.get_position(VerticalAxis.AXIS_0) - conditions.target) < conditions.threshold
                                case MacroStep.WaitPositionEnd.Axis.X1:
                                    condition_validation = abs(
                                        JRKInterface.get_position(VerticalAxis.AXIS_1) - conditions.target) < conditions.threshold
                                case MacroStep.WaitPositionEnd.Axis.Y:
                                    condition_validation = abs(
                                        HorizontalStageInterface.get_position() - conditions.target) < conditions.threshold
                        if not condition_validation: return

                    self.step_execute_state = ActuatorsControllerState.END
            for i in range(VerticalAxis.AXIS_COUNT.value):
                match self.vertical_modes[i]:
                    case self.VControllerMode.FORCE:
                        self.vertical_target_forces[i] = -self.pid_controllers[i].update(
                            PhidgetInterface.get_calibrated_forces(VerticalAxis(i)),
                            self.vertical_target_forces[i])
                        JRKInterface.set_duty_cycle(int(self.vertical_target_forces[i]), VerticalAxis(i))
                    case self.VControllerMode.POSITION:
                        JRKInterface.set_target_position(int(self.vertical_target_positions[i]), VerticalAxis(i))

    def run_step(self, macro_step: MacroStep):
        self.step_loaded = macro_step
        self.step_execute_state       = ActuatorsControllerState.START

    def stop(self):
        self.step_execute_state = ActuatorsControllerState.END
        self.vertical_modes = [StepExecutionController.VControllerMode.POSITION, StepExecutionController.VControllerMode.POSITION]
        self.vertical_target_forces = [0, 0]
        self.pid_controllers[0].clear_errors()
        self.pid_controllers[1].clear_errors()
        self.vertical_target_positions = [JRKInterface.get_position(VerticalAxis.AXIS_0),
                                          JRKInterface.get_position(VerticalAxis.AXIS_1)]
        HorizontalStageInterface.send_target_position(HorizontalStageInterface.get_position())