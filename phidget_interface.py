import numpy as np
from Phidget22.Devices.VoltageRatioInput import *
import time

from PyQt5.QtWidgets import QPushButton


class PhidgetData:
    def __init__(self, filename):
        self.data = []
        self.timestamp = []
        self.__filename = filename

    def update_data(self, timestamp, data):
        self.data.append(data)
        self.timestamp.append(timestamp)

    def reset(self):
        self.__filename = ""
        self.timestamp = []
        self.data = []

    def set_filename(self, filename):
        self.__filename = filename

    def save_data(self):
        f = open(self.__filename + ".csv", "wb")
        f.write('time[ms], data\n'.encode())
        np.savetxt(f, np.array([self.timestamp, self.data]), delimiter=",")


class PhidgetInterface:
    # Phidget API
    __voltage_ratio_input_0 = VoltageRatioInput()
    __voltage_ratio_input_1 = VoltageRatioInput()
    __connected = False

    # Data Management
    __file_name = "PhidgetData"
    data = [PhidgetData(__file_name + "_channel_0"), PhidgetData(__file_name + "_channel_1")]
    __start_time = 0
    __start_time_set = False

    def connect(self):
        self.__voltage_ratio_input_0.setDeviceSerialNumber(716773)
        self.__voltage_ratio_input_0.setDeviceSerialNumber(716773)
        self.__voltage_ratio_input_0.setChannel(0)
        self.__voltage_ratio_input_0.setChannel(1)
        self.__voltage_ratio_input_0.setOnVoltageRatioChangeHandler(self.__on_voltage_change)
        self.__voltage_ratio_input_1.setOnVoltageRatioChangeHandler(self.__on_voltage_change)
        self.__voltage_ratio_input_0.openWaitForAttachment(1000)
        self.__voltage_ratio_input_1.openWaitForAttachment(1000)
        self.data[0].set_filename(self.__file_name + "_channel_0")
        self.data[1].set_filename(self.__file_name + "_channel_1")
        self.__connected = True
        if not self.__start_time_set:
            self.__start_time = int(round(time.time() * 1000))
            self.__start_time_set = True

    def disconnect(self):
        self.__voltage_ratio_input_0.close()
        self.__voltage_ratio_input_1.close()
        self.__connected = False

    def get_connected(self):
        return self.__connected

    def save_data(self):
        self.data[0].save_data()
        self.data[1].save_data()

    def clear_data(self):
        self.data[0].reset()
        self.data[1].reset()
        self.__start_time_set = False

    def __on_voltage_change(self, phidget_vri, voltage_ratio):
        self.data[phidget_vri.getChannel()].update_data(int(round(time.time() * 1000)), voltage_ratio)

    def connect_button_handler(self, button_instance: QPushButton):
        if self.__connected:
            button_instance.setText("Connected")
            self.disconnect()
        else:
            button_instance.setText("Disconnected")
            self.connect()

    def set_file_name(self, file_name: str):
        self.__file_name = file_name
