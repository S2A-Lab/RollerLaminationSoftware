import time

from PyQt6.QtCore import QObject, QTimer, QThread

from Backend.DataLogger.datastruct_timeseries import Timeseries
from Backend.Interfaces.interface_phidget import PhidgetInterface
from Backend.Interfaces.vertical_axis_base import VerticalAxis
from Utilities.move_worker_to_thread import Worker, move_worker_to_thread
from modules.module_actuators_controller import ActuatorsController


class DataSaveWorker(Worker):
    def stop(self):
        pass

    def __init__(self, datasets):
        super().__init__()
        self.datasets = datasets

    def run(self):
        for dataset in self.datasets:
            dataset.save_data()


class DataLoggerModule(QObject):
    __file_name: str = 'PhidgetData'

    target_data   = [Timeseries(""),
                     Timeseries("")]
    feedback_data = [Timeseries(""),
                     Timeseries("")]
    output_data   = [Timeseries(""),
                     Timeseries("")]
    p_data        = [Timeseries(""),
                     Timeseries("")]
    i_data        = [Timeseries(""),
                     Timeseries("")]
    d_data        = [Timeseries(""),
                     Timeseries("")]
    ilim_data     = [Timeseries(""),
                     Timeseries("")]
    horizontal_position    = Timeseries("")
    __start_time  = 0
    __start_time_set = False
    sampling_time = 20  # [ms]
    lb = 0
    ub = 1

    def __init__(self, pid_controller_module: ActuatorsController):
        super().__init__()
        self.data_save_worker = None
        self.data_save_thread = None
        self.pid_module = pid_controller_module
        self.loop_timer = QTimer()
        self.loop_timer.timeout.connect(self.update_data)
        self.loop_timer.start(self.sampling_time)

    def save_data(self):
        self.data_save_thread = QThread()
        self.data_save_worker = DataSaveWorker(self.target_data + self.feedback_data + self.output_data + self.p_data + self.i_data + self.d_data + self.ilim_data + [self.horizontal_position])
        move_worker_to_thread(self.data_save_worker, self.data_save_thread)

        self.data_save_thread.start()
        return self.data_save_worker

    def clear_data(self):
        self.target_data[0].reset()
        self.target_data[1].reset()
        self.feedback_data[0].reset()
        self.feedback_data[1].reset()
        self.output_data[0].reset()
        self.output_data[1].reset()
        self.lb = 0
        self.ub = 1
        if PhidgetInterface.get_connected():
            self.__start_time_set = True
            self.__start_time = int(round(time.time() * 1000))
        else:
            self.__start_time_set = False

    def set_file_name(self, file_name: str):
        self.__file_name = file_name

        self.target_data[0].set_filename(     self.__file_name + "_target_0"  )
        self.target_data[1].set_filename(     self.__file_name + "_target_1"  )
        self.feedback_data[0].set_filename(   self.__file_name + "_feedback_0")
        self.feedback_data[1].set_filename(   self.__file_name + "_feedback_0")
        self.output_data[0].set_filename(     self.__file_name + "_output_0"  )
        self.output_data[1].set_filename(     self.__file_name + "_output_0"  )
        self.p_data[0].set_filename(          self.__file_name + "_p_gain_0"  )
        self.p_data[0].set_filename(          self.__file_name + "_p_gain_1"  )
        self.i_data[0].set_filename(          self.__file_name + "_i_gain_0"  )
        self.i_data[0].set_filename(          self.__file_name + "_i_gain_1"  )
        self.d_data[0].set_filename(          self.__file_name + "_d_gain_0"  )
        self.d_data[0].set_filename(          self.__file_name + "_d_gain_1"  )
        self.ilim_data[0].set_filename(       self.__file_name + "_i_limit_0" )
        self.ilim_data[1].set_filename(       self.__file_name + "_i_limit_1" )
        self.horizontal_position.set_filename(self.__file_name + "_position"  )

    def update_data(self):
        if PhidgetInterface.get_connected():
            if not self.__start_time_set:
                self.__start_time = int(round(time.time() * 1000))
                self.__start_time_set = True

            current_time = int(round(time.time() * 1000))

            voltages = [PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_0),
                        PhidgetInterface.get_calibrated_forces(VerticalAxis.AXIS_0)]
            target = self.pid_module.target_forces
            output = self.pid_module.output

            self.feedback_data[0].update_data(current_time - self.__start_time, voltages[0])
            self.feedback_data[1].update_data(current_time - self.__start_time, voltages[1])
            self.target_data[0].update_data(current_time - self.__start_time, target[0])
            self.target_data[1].update_data(current_time - self.__start_time, target[1])
            self.output_data[0].update_data(current_time - self.__start_time, output[0])
            self.output_data[1].update_data(current_time - self.__start_time, output[1])

            self.lb = min(voltages[0], voltages[1], target[0], target[1])
            self.ub = max(voltages[0], voltages[1], target[0], target[1])

            pid_param0 = self.pid_module.pid_controllers[0].get_pid_params()
            pid_param1 = self.pid_module.pid_controllers[1].get_pid_params()

            self.p_data[0].update_data(current_time - self.__start_time,pid_param0[0])
            self.i_data[0].update_data(current_time - self.__start_time,pid_param0[1])
            self.d_data[0].update_data(current_time - self.__start_time,pid_param0[2])
            self.ilim_data[0].update_data(current_time - self.__start_time, pid_param0[3])
            self.p_data[1].update_data(current_time - self.__start_time, pid_param1[0])
            self.i_data[1].update_data(current_time - self.__start_time, pid_param1[1])
            self.d_data[1].update_data(current_time - self.__start_time, pid_param1[2])
            self.ilim_data[1].update_data(current_time - self.__start_time, pid_param1[3])
            self.horizontal_position.update_data(current_time - self.__start_time, self.pid_module.horizontal_target_speed)

