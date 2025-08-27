import time, os
from itertools import chain
from PyQt6.QtCore import QTimer, QThread

from Backend.Interfaces.interface_horizontal_stage import HorizontalStageInterface
from Backend.Interfaces.interface_jrk import JRKInterface
from Backend.Schedulers.DataLogger.datastruct_timeseries import Timeseries
from Backend.Interfaces.interface_phidget import PhidgetInterface
from Backend.Interfaces.vertical_axis_base import VerticalAxis
from Backend.Schedulers.ActionExecute.scheduler_action_execute import ActionExecuteScheduler
from typing import Callable

class DataLoggerScheduler:
    __file_name: str = ""

    feedback_position   = [Timeseries(""),
                           Timeseries("")]
    target_position   = [Timeseries(""),
                         Timeseries("")]
    feedback_force          = [Timeseries(""),
                               Timeseries("")]
    target_force          = [Timeseries(""),
                             Timeseries("")]
    duty_cycle            = [Timeseries(""),
                             Timeseries("")]
    p_data                 = [Timeseries(""),
                              Timeseries("")]
    i_data                 = [Timeseries(""),
                              Timeseries("")]
    d_data                 = [Timeseries(""),
                              Timeseries("")]
    ilim_data              = [Timeseries(""),
                              Timeseries("")]
    olim_data              = [Timeseries(""),
                              Timeseries("")]
    controller_modes       = [Timeseries(""),
                              Timeseries("")]
    horizontal_position    =  Timeseries("")

    auto_start_end_recording = False
    sampling_time = 10  # [ms]

    __prev_executing = False
    __executing = True

    __start_time  = 0
    __start_time_set = False
    __is_saving = False
    __recording = False

    __data_save_worker = None
    __data_save_thread = QThread()
    __loop_timer : QTimer = QTimer()

    __data_save_end_operations : list[Callable[[], None]] = []

    lb = 0
    ub = 1

    @staticmethod
    def init():
        DataLoggerScheduler.__loop_timer.timeout.connect(DataLoggerScheduler.update_data)
        DataLoggerScheduler.__loop_timer.start(DataLoggerScheduler.sampling_time)
        DataLoggerScheduler.__data_save_thread.run = DataLoggerScheduler.__write_data

    @staticmethod
    def save_data():
        DataLoggerScheduler.__data_save_thread.start()

    @staticmethod
    def clear_data():
        fields_with_indices = [
            "feedback_position",
            "target_position",
            "feedback_force",
            "target_force",
            "duty_cycle",
            "p_data",
            "i_data",
            "d_data",
            "ilim_data",
            "olim_data",
            "controller_modes",
        ]

        for field in fields_with_indices:
            for i in range(2):
                getattr(DataLoggerScheduler, field)[i].reset()
        DataLoggerScheduler.horizontal_position.reset()
        DataLoggerScheduler.lb = 0
        DataLoggerScheduler.ub = 1

    @staticmethod
    def start_recording():
        DataLoggerScheduler.__recording = True
        if PhidgetInterface.get_connected():
            DataLoggerScheduler.__start_time_set = False

    @staticmethod
    def stop_recording():
        DataLoggerScheduler.__recording = False

    @staticmethod
    def set_file_name(file_name: str):
        DataLoggerScheduler.__file_name = file_name

        pairs = [
            ("target_position", "/target_position_{}"),
            ("feedback_position", "/feedback_position_{}"),
            ("target_force", "/target_force_{}"),
            ("feedback_force", "/feedback_force_{}"),
            ("duty_cycle","/duty_cycle_{}"),
            ("p_data", "/p_gain_{}"),
            ("i_data", "/i_gain_{}"),
            ("d_data", "/d_gain_{}"),
            ("ilim_data", "/i_limit_{}"),
            ("olim_data", "/out_limit_{}"),
            ("controller_modes", "/controller_mode_{}")
        ]
        os.mkdir(DataLoggerScheduler.__file_name)
        for field, suffix_format in pairs:
            for i in range(2):
                getattr(DataLoggerScheduler, field)[i].set_filename(
                    f"{DataLoggerScheduler.__file_name}{suffix_format.format(i)}"
                )

        DataLoggerScheduler.horizontal_position.set_filename(
            DataLoggerScheduler.__file_name + "/horizontal_position"
        )

    @staticmethod
    def update_data():
        try:
            DataLoggerScheduler.__executing = ActionExecuteScheduler.get_sequence_executing()
            if DataLoggerScheduler.auto_start_end_recording:
                if DataLoggerScheduler.__executing and not DataLoggerScheduler.__prev_executing:
                    DataLoggerScheduler.start_recording()
                elif not DataLoggerScheduler.__executing and DataLoggerScheduler.__prev_executing:
                    DataLoggerScheduler.stop_recording()
            DataLoggerScheduler.__prev_executing = DataLoggerScheduler.__executing

            if PhidgetInterface.get_connected() and HorizontalStageInterface.get_connected() and DataLoggerScheduler.__recording:
                if not DataLoggerScheduler.__start_time_set:
                    DataLoggerScheduler.__start_time = int(round(time.time() * 1000))
                    DataLoggerScheduler.__start_time_set = True

                current_time = int(round(time.time() * 1000))

                timestamp = current_time - DataLoggerScheduler.__start_time

                # Fetch target and feedback data
                target_forces = ActionExecuteScheduler.get_vertical_target_force()
                feedback_forces = [
                    PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_0),
                    PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_1)
                ]
                target_positions = ActionExecuteScheduler.get_vertical_target_position()
                feedback_positions = [
                    JRKInterface.get_position(VerticalAxis.AXIS_0),
                    JRKInterface.get_position(VerticalAxis.AXIS_1)
                ]
                duty_cycles = ActionExecuteScheduler.get_vertical_duty_cycles()

                # Update bounds
                DataLoggerScheduler.lb = min(*feedback_forces, *target_positions)
                DataLoggerScheduler.ub = max(*feedback_forces, *target_positions)
                # Fetch control parameters
                pid_params = ActionExecuteScheduler.get_pid_parameters()  # [pid_param0, pid_param1]
                controller_modes = ActionExecuteScheduler.get_vertical_modes()  # [controller_mode0, controller_mode1]

                # Log scalar data
                for i in range(2):
                    DataLoggerScheduler.target_force[i].update_data(timestamp, target_forces[i])
                    DataLoggerScheduler.feedback_force[i].update_data(timestamp, feedback_forces[i])
                    DataLoggerScheduler.target_position[i].update_data(timestamp, target_positions[i])
                    DataLoggerScheduler.feedback_position[i].update_data(timestamp, feedback_positions[i])
                    DataLoggerScheduler.duty_cycle[i].update_data(timestamp, duty_cycles[i])

                # Log PID data
                for i, pid in enumerate(pid_params):
                    DataLoggerScheduler.p_data[i].update_data(timestamp, pid[0])
                    DataLoggerScheduler.i_data[i].update_data(timestamp, pid[1])
                    DataLoggerScheduler.d_data[i].update_data(timestamp, pid[2])
                    DataLoggerScheduler.ilim_data[i].update_data(timestamp, pid[3])
                    DataLoggerScheduler.olim_data[i].update_data(timestamp, pid[4])

                # Log controller modes
                for i, mode in enumerate(controller_modes):
                    DataLoggerScheduler.controller_modes[i].update_data(timestamp, mode.value)

                # Log horizontal position
                DataLoggerScheduler.horizontal_position.update_data(timestamp, HorizontalStageInterface.get_position())
        except Exception as e:
            print(e)

    @staticmethod
    def get_is_saving():
        return DataLoggerScheduler.__is_saving

    @staticmethod
    def __write_data():
        DataLoggerScheduler.__is_saving = True
        fields = [
            "feedback_position",
            "target_position",
            "feedback_force",
            "target_force",
            "duty_cycle",
            "p_data",
            "i_data",
            "d_data",
            "ilim_data",
            "olim_data",
            "controller_modes",
        ]

        data_streams = list(chain.from_iterable(getattr(DataLoggerScheduler, field) for field in fields))
        data_streams.append(DataLoggerScheduler.horizontal_position)

        for timeseries in data_streams:
            timeseries.save_data()

        DataLoggerScheduler.__is_saving = False
        for func in DataLoggerScheduler.__data_save_end_operations:
            func()

    @staticmethod
    def add_save_end_callback(callback: Callable[[], None]):
        DataLoggerScheduler.__data_save_end_operations.append(callback)