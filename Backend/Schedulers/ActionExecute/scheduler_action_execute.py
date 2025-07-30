from PyQt6.QtCore import QObject, QTimer, QDateTime
from typing import cast
from Backend.Interfaces.interface_phidget import PhidgetInterface
from Backend.Interfaces.interface_jrk import JRKInterface
from Backend.Interfaces.interface_horizontal_stage import HorizontalStageInterface
from controllers.pid_controller import PIDController
from Backend.Schedulers.ActionExecute.macro_step import *
from Backend.Interfaces.vertical_axis_base import VerticalAxis

class ActuatorsControllerState(Enum):
    START = 0
    EXECUTING = 1
    END = 2

class ActionExecuteScheduler:
    __sampling_time = 10 # [ms]

    __vertical_target_forces = [0.0, 0.0]
    __vertical_target_positions = [0.0, 0.0]
    __vertical_controller_modes = [MacroStep.ActionMoveVertical.Mode.POSITION, MacroStep.ActionMoveVertical.Mode.POSITION]
    __vertical_controller_duty_cycles = [0.0,0.0]

    __horizontal_target_position = 0.0

    __step_loaded: MacroStep = None
    __step_sequence: list[MacroStep] = []
    __sequence_index: int = 0
    __step_start_time: float = 0

    __step_execute_state: ActuatorsControllerState = ActuatorsControllerState.END
    __sequence_execution_end: bool = True
    __pid_controllers: list[PIDController] = [PIDController(0, 0, 0, 0, 200, 10),
                                              PIDController(0, 0, 0, 0, 200, 10)]
    __linear_stage_velocity = 0

    __loop_timer : QTimer = QTimer()

    @staticmethod
    def init():
        ActionExecuteScheduler.__loop_timer.timeout.connect(ActionExecuteScheduler.run)
        ActionExecuteScheduler.__loop_timer.start(ActionExecuteScheduler.__sampling_time)
        ActionExecuteScheduler.initialized = False
        ActionExecuteScheduler.horizontal_target_speed = 0
        print("P1")

    @staticmethod
    def run():
        if PhidgetInterface.get_connected() and HorizontalStageInterface.get_connected():
            if not ActionExecuteScheduler.initialized:
                ActionExecuteScheduler.initialized = True
                return
            # Parse macro
            match ActionExecuteScheduler.__step_execute_state:
                # At start stage parse actions and load to the scheduler
                case ActuatorsControllerState.START:
                    print("Start Step")
                    for actions in ActionExecuteScheduler.__step_loaded.actions:
                        if isinstance(actions, MacroStep.ActionMoveHorizontal):
                            actions : MacroStep.ActionMoveHorizontal
                            HorizontalStageInterface.send_speed_limit(actions.max_vel)
                            HorizontalStageInterface.send_accel_limit(actions.max_accel)
                            HorizontalStageInterface.send_target_position(actions.target_position)
                        elif isinstance(actions, MacroStep.ActionMoveVertical):
                            actions : MacroStep.ActionMoveVertical
                            if actions.axis == MacroStep.ActionMoveVertical.Axis.ALL:
                                ActionExecuteScheduler.__vertical_controller_modes = [actions.mode, actions.mode]
                                if actions.mode == MacroStep.ActionMoveVertical.Mode.FORCE:
                                    ActionExecuteScheduler.__vertical_target_forces = [actions.target, actions.target]
                                    ActionExecuteScheduler.__pid_controllers[0].clear_errors()
                                    ActionExecuteScheduler.__pid_controllers[1].clear_errors()
                                elif actions.mode == MacroStep.ActionMoveVertical.Mode.POSITION:
                                    ActionExecuteScheduler.__vertical_target_positions = [actions.target, actions.target]
                            else:
                                ActionExecuteScheduler.__vertical_controller_modes[cast(int, actions.axis.value)] = actions.mode
                                if actions.mode == MacroStep.ActionMoveVertical.Mode.FORCE:
                                    ActionExecuteScheduler.__vertical_target_forces[cast(int, actions.axis.value)] = actions.target
                                elif actions.mode == MacroStep.ActionMoveVertical.Mode.POSITION:
                                    ActionExecuteScheduler.__vertical_target_positions[cast(int, actions.axis.value)] = actions.target
                        elif isinstance(actions, MacroStep.ActionChangeVerticalPIDParams):
                            actions : MacroStep.ActionChangeVerticalPIDParams
                            if actions.axis == MacroStep.ActionChangeVerticalPIDParams.Axis.ALL:
                                ActionExecuteScheduler.__pid_controllers[0].set_pid_params(actions.kp, actions.ki, actions.kd,
                                                                         actions.i_limit, actions.out_limit)
                                ActionExecuteScheduler.__pid_controllers[1].set_pid_params(actions.kp, actions.ki, actions.kd,
                                                                         actions.i_limit, actions.out_limit)
                                ActionExecuteScheduler.__pid_controllers[0].clear_errors()
                                ActionExecuteScheduler.__pid_controllers[1].clear_errors()
                            else:
                                
                                ActionExecuteScheduler.__pid_controllers[cast(int, actions.axis.value)].set_pid_params(actions.kp, actions.ki, actions.kd,
                                                                                                     actions.i_limit, actions.out_limit)
                                ActionExecuteScheduler.__pid_controllers[cast(int, actions.axis.value)].clear_errors()
                        elif isinstance(actions, MacroStep.ActionStopPrevious):
                            actions : MacroStep.ActionStopPrevious
                            if actions.axis == MacroStep.ActionStopPrevious.Axis.ALL:
                                ActionExecuteScheduler.__vertical_target_forces = [0, 0]
                                ActionExecuteScheduler.__vertical_target_positions = [JRKInterface.get_position(VerticalAxis.AXIS_0), JRKInterface.get_position(VerticalAxis.AXIS_1)]
                                HorizontalStageInterface.send_target_position(HorizontalStageInterface.get_position())
                            elif actions.axis == MacroStep.ActionStopPrevious.Axis.Y:
                                HorizontalStageInterface.send_target_position(HorizontalStageInterface.get_position())
                            else:
                                ActionExecuteScheduler.__vertical_target_forces[cast(int, actions.axis.value)] = 0
                                ActionExecuteScheduler.__vertical_target_positions[cast(int, actions.axis.value)] = JRKInterface.get_position(VerticalAxis(cast(int, actions.axis.value)))
                            pass
                    ActionExecuteScheduler.__step_start_time = QDateTime.currentMSecsSinceEpoch()
                    ActionExecuteScheduler.__step_execute_state = ActuatorsControllerState.EXECUTING
                # At running stage parse and judge the end condition until end
                case ActuatorsControllerState.EXECUTING:
                    step_end_validation = True
                    for condition in ActionExecuteScheduler.__step_loaded.end_conditions:
                        condition_validation = False
                        if isinstance(condition, MacroStep.EndConditionForce):
                            condition: MacroStep.EndConditionForce
                            match condition.axis:
                                case MacroStep.EndConditionForce.Axis.X0:
                                    condition_validation = (
                                            abs(PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_0)- condition.target) < condition.threshold)
                                case MacroStep.EndConditionForce.Axis.X1:
                                    condition_validation = (
                                            abs(PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_1)- condition.target) < condition.threshold)
                                case MacroStep.EndConditionForce.Axis.ALL:
                                    condition_validation = (
                                            abs(PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_0) - condition.target) < condition.threshold and
                                            abs(PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_1) - condition.target) < condition.threshold)
                        elif isinstance(condition, MacroStep.EndConditionTime):
                            condition: MacroStep.EndConditionTime
                            condition_validation = QDateTime.currentMSecsSinceEpoch() - ActionExecuteScheduler.__step_start_time >= condition.wait_time
                        elif isinstance(condition, MacroStep.EndConditionPosition):
                            condition: MacroStep.EndConditionPosition
                            match condition.axis:
                                case MacroStep.EndConditionPosition.Axis.X0:
                                    condition_validation = abs(
                                        JRKInterface.get_position(VerticalAxis.AXIS_0) - condition.target) < condition.threshold
                                case MacroStep.EndConditionPosition.Axis.X1:
                                    condition_validation = abs(
                                        JRKInterface.get_position(VerticalAxis.AXIS_1) - condition.target) < condition.threshold
                                case MacroStep.EndConditionPosition.Axis.Y:
                                    condition_validation = abs(
                                        HorizontalStageInterface.get_position() - condition.target) < condition.threshold
                        step_end_validation &= condition_validation
                        if not condition_validation: break
                    if step_end_validation:
                        ActionExecuteScheduler.__step_execute_state = ActuatorsControllerState.END
                case ActuatorsControllerState.END:
                    if ActionExecuteScheduler.__sequence_index + 1 < len(ActionExecuteScheduler.__step_sequence):
                        ActionExecuteScheduler.__sequence_index += 1
                        print("End Step")
                        ActionExecuteScheduler.__step_loaded = ActionExecuteScheduler.__step_sequence[ActionExecuteScheduler.__sequence_index]
                        ActionExecuteScheduler.__step_execute_state = ActuatorsControllerState.START
                    else:
                        if not ActionExecuteScheduler.__sequence_execution_end:
                            ActionExecuteScheduler.__sequence_execution_end = True
                            print("Execution End")

            # Execute
            for i in range(VerticalAxis.AXIS_COUNT.value):
                match ActionExecuteScheduler.__vertical_controller_modes[i]:
                    case MacroStep.ActionMoveVertical.Mode.FORCE:
                        ActionExecuteScheduler.__vertical_controller_duty_cycles[i] = -ActionExecuteScheduler.__pid_controllers[i].update(
                            PhidgetInterface.get_calibrated_forces(VerticalAxis(i)),
                            ActionExecuteScheduler.__vertical_target_forces[i])
                        JRKInterface.set_duty_cycle(int(ActionExecuteScheduler.__vertical_controller_duty_cycles[i]), VerticalAxis(i))

                    case MacroStep.ActionMoveVertical.Mode.POSITION:
                        JRKInterface.set_target_position(int(ActionExecuteScheduler.__vertical_target_positions[i]), VerticalAxis(i))

    @staticmethod
    def run_step_sequence(macro_steps: list[MacroStep]):
        if len(macro_steps) > 0:
            ActionExecuteScheduler.__step_sequence            = macro_steps
            ActionExecuteScheduler.__step_loaded              = macro_steps[0]
            ActionExecuteScheduler.__sequence_index           = 0
            ActionExecuteScheduler.__step_execute_state       = ActuatorsControllerState.START
            ActionExecuteScheduler.__sequence_execution_end   = False

    @staticmethod
    def stop():
        ActionExecuteScheduler.__step_execute_state = ActuatorsControllerState.END
        ActionExecuteScheduler.__vertical_controller_modes = [MacroStep.ActionMoveVertical.Mode.POSITION, MacroStep.ActionMoveVertical.Mode.POSITION]
        ActionExecuteScheduler.__vertical_target_forces = [0, 0]
        ActionExecuteScheduler.__pid_controllers[0].clear_errors()
        ActionExecuteScheduler.__pid_controllers[1].clear_errors()
        ActionExecuteScheduler.__vertical_target_positions = [JRKInterface.get_position(VerticalAxis.AXIS_0),
                                            JRKInterface.get_position(VerticalAxis.AXIS_1)]
        HorizontalStageInterface.send_target_position(HorizontalStageInterface.get_position())

    @staticmethod
    def get_execute_state():
        return ActionExecuteScheduler.__step_execute_state

    @staticmethod
    def get_sequence_execution_index():
        return ActionExecuteScheduler.__sequence_index

    @staticmethod
    def get_sequence_execution_end():
        return ActionExecuteScheduler.__sequence_execution_end

    @staticmethod
    def get_pid_parameters():
        return [ActionExecuteScheduler.__pid_controllers[0].get_pid_params(), ActionExecuteScheduler.__pid_controllers[1].get_pid_params()]

    @staticmethod
    def get_vertical_target_position():
        return ActionExecuteScheduler.__vertical_target_positions

    @staticmethod
    def get_vertical_target_force():
        return ActionExecuteScheduler.__vertical_target_forces

    @staticmethod
    def get_vertical_modes():
        return ActionExecuteScheduler.__vertical_controller_modes

    @staticmethod
    def get_vertical_duty_cycles():
        return ActionExecuteScheduler.__vertical_controller_duty_cycles

    @staticmethod
    def get_horizontal_target_position():
        return ActionExecuteScheduler.__horizontal_target_position
