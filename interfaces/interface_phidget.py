from datastruct.datastruct_timeseries import *
from Phidget22.Devices.VoltageRatioInput import *
from pathlib import Path
import time


class PhidgetInterface:
    # Phidget API
    __voltage_ratio_input_0 = VoltageRatioInput()
    __voltage_ratio_input_1 = VoltageRatioInput()
    __connected = False

    __voltages = [0, 0]

    def connect(self):
        self.__voltage_ratio_input_0.setDeviceSerialNumber(716774)
        self.__voltage_ratio_input_0.setDeviceSerialNumber(716774)
        self.__voltage_ratio_input_0.setChannel(0)
        self.__voltage_ratio_input_0.setChannel(1)
        self.__voltage_ratio_input_0.setOnVoltageRatioChangeHandler(self.__update)
        self.__voltage_ratio_input_1.setOnVoltageRatioChangeHandler(self.__update)
        self.__voltage_ratio_input_0.openWaitForAttachment(1000)
        self.__voltage_ratio_input_1.openWaitForAttachment(1000)
        self.__connected = True

    def disconnect(self):
        self.__voltage_ratio_input_0.close()
        self.__voltage_ratio_input_1.close()
        self.__connected = False

    def get_connected(self):
        return self.__connected

    def __update(self, phidget_vri, voltage_ratio):
        self.__voltages[phidget_vri.getChannel()] = voltage_ratio

    def get_voltages(self):
        return self.__voltages

