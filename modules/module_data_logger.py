import time

from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread

from datastruct.datastruct_timeseries import Timeseries
from interfaces.interface_phidget import PhidgetInterface
from modules.module_vertical_actuators_controller import VerticalActuatorsController


class DataSaveWorker(QObject):
    finished = pyqtSignal()
    def __init__(self, datasets):
        super().__init__()
        self.datasets = datasets

    def run(self):
        for dataset in self.datasets:
            dataset.save_data()
        self.finished.emit()

class DataLoggerModule(QObject):
    __file_name: str = 'PhidgetData'

    target_data = [Timeseries("./data/" + __file_name + "_target_0"),
                   Timeseries("./data/" + __file_name + "_target_1")]
    feedback_data = [Timeseries("./data/" + __file_name + "_feedback_0"),
                     Timeseries("./data/" + __file_name + "_feedback_1")]
    output_data = [Timeseries("./data/" + __file_name + "_output_0"),
                   Timeseries("./data/" + __file_name + "_output_1")]
    p_data = [Timeseries("./data/" + __file_name + "_p_gain_0"),
              Timeseries("./data/" + __file_name + "_p_gain_1")]
    i_data = [Timeseries("./data/" + __file_name + "_i_gain_0"),
              Timeseries("./data/" + __file_name + "_i_gain_1")]
    d_data = [Timeseries("./data/" + __file_name + "_d_gain_0"),
              Timeseries("./data/" + __file_name + "_d_gain_1")]
    ilim_data = [Timeseries("./data/" + __file_name + "_i_limit_0"),
                 Timeseries("./data/" + __file_name + "_i_limit_1")]
    speed_data = Timeseries("./data/" + __file_name + "_speed")
    __start_time = 0
    __start_time_set = False
    sampling_time = 100  # [ms]

    def __init__(self, phidget_interface: PhidgetInterface, pid_controller_module: VerticalActuatorsController):
        super().__init__()
        self.data_save_worker = None
        self.data_save_thread = None
        self.phidget_interface = phidget_interface
        self.pid_module = pid_controller_module
        self.loop_timer = QTimer()
        self.loop_timer.timeout.connect(self.update_data)
        self.loop_timer.start(self.sampling_time)

    def save_data(self):
        self.data_save_thread = QThread()
        self.data_save_worker = DataSaveWorker(self.target_data + self.feedback_data + self.output_data + self.p_data + self.i_data + self.d_data + self.ilim_data + [self.speed_data])
        self.data_save_worker.moveToThread(self.data_save_thread)
        self.data_save_thread.started.connect(self.data_save_worker.run)
        self.data_save_worker.finished.connect(self.data_save_thread.quit)
        self.data_save_worker.finished.connect(self.data_save_worker.deleteLater)
        self.data_save_thread.finished.connect(self.data_save_thread.deleteLater)

        self.data_save_thread.start()
        return self.data_save_worker

    def clear_data(self):
        self.target_data[0].reset()
        self.target_data[1].reset()
        self.feedback_data[0].reset()
        self.feedback_data[1].reset()
        self.output_data[0].reset()
        self.output_data[1].reset()
        if self.phidget_interface.get_connected():
            self.__start_time_set = True
            self.__start_time = int(round(time.time() * 1000))
        else:
            self.__start_time_set = False

    def set_file_name(self, file_name: str):
        self.__file_name = file_name

        self.target_data[0].set_filename("./data/" + self.__file_name + "_target_0")
        self.target_data[1].set_filename("./data/" + self.__file_name + "_target_1")
        self.feedback_data[0].set_filename("./data/" + self.__file_name + "_feedback_0")
        self.feedback_data[1].set_filename("./data/" + self.__file_name + "_feedback_0")
        self.output_data[0].set_filename("./data/" + self.__file_name + "_output_0")
        self.output_data[1].set_filename("./data/" + self.__file_name + "_output_0")
        self.p_data[0].set_filename("./data/" + self.__file_name + "_p_gain_0")
        self.p_data[0].set_filename("./data/" + self.__file_name + "_p_gain_1")
        self.i_data[0].set_filename("./data/" + self.__file_name + "_i_gain_0")
        self.i_data[0].set_filename("./data/" + self.__file_name + "_i_gain_1")
        self.d_data[0].set_filename("./data/" + self.__file_name + "_d_gain_0")
        self.d_data[0].set_filename("./data/" + self.__file_name + "_d_gain_1")
        self.ilim_data[0].set_filename("./data/" + self.__file_name + "_i_limit_0")
        self.ilim_data[1].set_filename("./data/" + self.__file_name + "_i_limit_1")
        self.speed_data.set_filename("./data/" + self.__file_name + "_speed")

    def update_data(self):
        if self.phidget_interface.get_connected():
            if not self.__start_time_set:
                self.__start_time = int(round(time.time() * 1000))
                self.__start_time_set = True

            current_time = int(round(time.time() * 1000))

            voltages = self.phidget_interface.get_voltages()
            target = self.pid_module.target_forces
            output = self.pid_module.output

            self.feedback_data[0].update_data(current_time - self.__start_time, voltages[0])
            self.feedback_data[1].update_data(current_time - self.__start_time, voltages[1])
            self.target_data[0].update_data(current_time - self.__start_time, target[0])
            self.target_data[1].update_data(current_time - self.__start_time, target[1])
            self.output_data[0].update_data(current_time - self.__start_time, output[0])
            self.output_data[1].update_data(current_time - self.__start_time, output[1])

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
            self.speed_data.update_data(current_time - self.__start_time, self.pid_module.horizontal_target_speed)

