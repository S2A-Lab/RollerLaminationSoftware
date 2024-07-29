import numpy as np
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, QTimer


class PhidgetInterface:
    voltage_ratio_input_0 = VoltageRatioInput()
    voltage_ratio_input_1 = VoltageRatioInput()
    connected = False
    sampling_time = 1000  # ms
    input_0_data = []
    input_1_data = []

    def connect(self):
        self.voltage_ratio_input_0.setDeviceSerialNumber(716773)
        self.voltage_ratio_input_0.setDeviceSerialNumber(716773)
        self.voltage_ratio_input_0.setChannel(0)
        self.voltage_ratio_input_0.setChannel(1)
        self.connected = True
        update_delegate = QTimer()
        update_delegate.timeout.connect(self.update_voltage)
        update_delegate.start(1000)  # Update every 1000 milliseconds (1 Hz)

    def disconnect(self):
        self.voltage_ratio_input_0.close()
        self.voltage_ratio_input_1.close()
        self.connected = False

    def update_voltage(self):
        self.voltage_ratio_input_0.getVoltageRatio()
        self.voltage_ratio_input_1.getVoltageRatio()
        self.input_0_data.append(self.voltage_ratio_input_0.getVoltageRatio())
        self.input_1_data.append(self.voltage_ratio_input_1.getVoltageRatio())

    def connect_button_handler(self):
        if self.connected:
            print("Disconnect")
            self.disconnect()
        else:
            print("Connect")
            self.connect()
