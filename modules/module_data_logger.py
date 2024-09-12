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

    target_data = [Timeseries("./data/" + __file_name + "_target_channel_0"),
                   Timeseries("./data/" + __file_name + "_target_channel_1")]
    feedback_data = [Timeseries("./data/" + __file_name + "_feedback_channel_0"),
                     Timeseries("./data/" + __file_name + "_feedback_channel_1")]
    output_data = [Timeseries("./data/" + __file_name + "_output_channel_0"),
                   Timeseries("./data/" + __file_name + "_output_channel_1")]

    __start_time = 0
    __start_time_set = False
    sampling_time = 100  # [ms]

    coeff_channel_0 = 1.614167101957641e+05
    coeff_channel_1 = 3.202322168529868e+05

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
        self.data_save_worker = DataSaveWorker(self.target_data + self.feedback_data + self.output_data)
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

        self.target_data[0].set_filename("./data/" + self.__file_name + "_target_channel_0")
        self.target_data[1].set_filename("./data/" + self.__file_name + "_target_channel_1")
        self.feedback_data[0].set_filename("./data/" + self.__file_name + "_feedback_channel_0")
        self.feedback_data[1].set_filename("./data/" + self.__file_name + "_feedback_channel_1")
        self.output_data[0].set_filename("./data/" + self.__file_name + "_output_channel_0")
        self.output_data[1].set_filename("./data/" + self.__file_name + "_output_channel_1")

    def update_data(self):
        if self.phidget_interface.get_connected():
            if not self.__start_time_set:
                self.__start_time = int(round(time.time() * 1000))
                self.__start_time_set = True

            current_time = int(round(time.time() * 1000))

            voltages = self.phidget_interface.get_voltages()
            target = self.pid_module.target_forces
            output = [self.pid_module.output_0, self.pid_module.output_1]
            self.feedback_data[0].update_data(current_time - self.__start_time, voltages[0])
            self.feedback_data[1].update_data(current_time - self.__start_time, voltages[1])
            self.target_data[0].update_data(current_time - self.__start_time, target[0])
            self.target_data[1].update_data(current_time - self.__start_time, target[1])
            self.output_data[0].update_data(current_time - self.__start_time, output[0])
            self.output_data[1].update_data(current_time - self.__start_time, output[1])

