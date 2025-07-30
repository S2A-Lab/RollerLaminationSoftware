import time
from itertools import chain
from PyQt6.QtCore import QObject, QTimer, QThread

from Backend.Interfaces.interface_horizontal_stage import HorizontalStageInterface
from Backend.Schedulers.DataLogger.datastruct_timeseries import Timeseries
from Backend.Interfaces.interface_phidget import PhidgetInterface
from Backend.Interfaces.vertical_axis_base import VerticalAxis
from Backend.Schedulers.ActionExecute.scheduler_action_execute import ActionExecuteScheduler
from Utilities.move_worker_to_thread import Worker, move_worker_to_thread



class DataSaveWorker(Worker):
    def stop(self):
        pass

    def __init__(self, datasets):
        super().__init__()
        self.datasets = datasets

    def run(self):
        for dataset in self.datasets:
            dataset.save_data()


class DataLoggerScheduler:
    __file_name: str = ""

    target_position_data   = [Timeseries(""),
                              Timeseries("")]
    feedback_data          = [Timeseries(""),
                              Timeseries("")]
    output_data            = [Timeseries(""),
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
    __start_time  = 0
    __start_time_set = False
    sampling_time = 10  # [ms]
    __data_save_worker = None
    __data_save_thread = QThread()
    loop_timer : QTimer = QTimer()
    lb = 0
    ub = 1
    
    @staticmethod
    def init():
        DataLoggerScheduler.loop_timer.timeout.connect()
        DataLoggerScheduler.loop_timer.start(DataLoggerScheduler.sampling_time)

    @staticmethod
    def save_data():
        fields = [
            "target_position_data",
            "feedback_data",
            "output_data",
            "p_data",
            "i_data",
            "d_data",
            "ilim_data",
            "controller_modes",
            "olim_data"
        ]

        data_streams = list(chain.from_iterable(getattr(DataLoggerScheduler, field) for field in fields))
        data_streams.append(DataLoggerScheduler.horizontal_position)

        DataLoggerScheduler.__data_save_worker = DataSaveWorker(data_streams)

        move_worker_to_thread(DataLoggerScheduler.__data_save_worker, DataLoggerScheduler.__data_save_thread)

        DataLoggerScheduler.__data_save_thread.start()
        return DataLoggerScheduler.__data_save_worker

    @staticmethod
    def clear_data():
        fields_with_indices = [
            "target_position_data",
            "feedback_data",
            "output_data",
            "p_data",
            "i_data",
            "d_data",
            "ilim_data",
            "controller_modes"
            "olim_data"
        ]

        for field in fields_with_indices:
            for i in range(2):
                getattr(DataLoggerScheduler, field)[i].reset()

        DataLoggerScheduler.lb = 0
        DataLoggerScheduler.ub = 1
        if PhidgetInterface.get_connected():
            DataLoggerScheduler.__start_time_set = True
            DataLoggerScheduler.__start_time = int(round(time.time() * 1000))
        else:
            DataLoggerScheduler.__start_time_set = False

    @staticmethod
    def set_file_name(file_name: str):
        DataLoggerScheduler.__file_name = file_name

        pairs = [
            ("target_position_data", "_target_position_{}"),
            ("feedback_data", "_feedback_{}"),
            ("output_data", "_output_{}"),
            ("p_data", "_p_gain_{}"),
            ("i_data", "_i_gain_{}"),
            ("d_data", "_d_gain_{}"),
            ("ilim_data", "_i_limit_{}"),
            ("controller_modes", "_controller_mode_{}"),
            ("olim_data", "_out_limit_{}"),
        ]

        for field, suffix_format in pairs:
            for i in range(2):
                getattr(DataLoggerScheduler, field)[i].set_filename(
                    f"{DataLoggerScheduler.__file_name}{suffix_format.format(i)}"
                )

        DataLoggerScheduler.horizontal_position.set_filename(
            DataLoggerScheduler.__file_name + "_position"
        )

    @staticmethod
    def update_data():
        if PhidgetInterface.get_connected() and HorizontalStageInterface.get_connected():
            if not DataLoggerScheduler.__start_time_set:
                DataLoggerScheduler.__start_time = int(round(time.time() * 1000))
                DataLoggerScheduler.__start_time_set = True

            current_time = int(round(time.time() * 1000))

            voltages = [PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_0),
                        PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_0)]
            target = ActionExecuteScheduler.get_vertical_target_position()
            output = ActionExecuteScheduler.get_vertical_duty_cycles()

            DataLoggerScheduler.feedback_data[0].update_data(current_time - DataLoggerScheduler.__start_time, voltages[0])
            DataLoggerScheduler.feedback_data[1].update_data(current_time - DataLoggerScheduler.__start_time, voltages[1])
            DataLoggerScheduler.target_position_data[0].update_data(current_time - DataLoggerScheduler.__start_time, target[0])
            DataLoggerScheduler.target_position_data[1].update_data(current_time - DataLoggerScheduler.__start_time, target[1])
            DataLoggerScheduler.output_data[0].update_data(current_time - DataLoggerScheduler.__start_time, output[0])
            DataLoggerScheduler.output_data[1].update_data(current_time - DataLoggerScheduler.__start_time, output[1])

            DataLoggerScheduler.lb = min(voltages[0], voltages[1], target[0], target[1])
            DataLoggerScheduler.ub = max(voltages[0], voltages[1], target[0], target[1])

            [pid_param0,pid_param1] = ActionExecuteScheduler.get_pid_parameters()
            [controller_mode0, controller_mode1] = ActionExecuteScheduler.get_vertical_modes()

            DataLoggerScheduler.p_data[0].update_data(current_time - DataLoggerScheduler.__start_time,pid_param0[0])
            DataLoggerScheduler.i_data[0].update_data(current_time - DataLoggerScheduler.__start_time,pid_param0[1])
            DataLoggerScheduler.d_data[0].update_data(current_time - DataLoggerScheduler.__start_time,pid_param0[2])
            DataLoggerScheduler.ilim_data[0].update_data(current_time - DataLoggerScheduler.__start_time, pid_param0[3])
            DataLoggerScheduler.olim_data[0].update_data(current_time - DataLoggerScheduler.__start_time, pid_param0[4])

            DataLoggerScheduler.p_data[1].update_data(current_time - DataLoggerScheduler.__start_time, pid_param1[0])
            DataLoggerScheduler.i_data[1].update_data(current_time - DataLoggerScheduler.__start_time, pid_param1[1])
            DataLoggerScheduler.d_data[1].update_data(current_time - DataLoggerScheduler.__start_time, pid_param1[2])
            DataLoggerScheduler.ilim_data[1].update_data(current_time - DataLoggerScheduler.__start_time, pid_param1[3])
            DataLoggerScheduler.olim_data[1].update_data(current_time - DataLoggerScheduler.__start_time, pid_param1[4])

            DataLoggerScheduler.controller_modes[0].update_data(current_time - DataLoggerScheduler.__start_time, controller_mode0)
            DataLoggerScheduler.controller_modes[1].update_data(current_time - DataLoggerScheduler.__start_time, controller_mode1)

            DataLoggerScheduler.horizontal_position.update_data(current_time - DataLoggerScheduler.__start_time, ActionExecuteScheduler.get_horizontal_target_position())
