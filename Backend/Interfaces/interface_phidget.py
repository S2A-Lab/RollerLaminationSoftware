from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput
from Backend.Interfaces.vertical_axis_base import VerticalAxis


class PhidgetInterface:
    serial_number = 716774

    channels = [0, 1]

    _inputs = []
    _voltages = [0.0 for _ in channels]
    _coefficients = [1.614167101957641e+05, 3.202322168529868e+05]
    _zero_offsets = [0.0 for _ in channels]
    _sampling_interval = 8
    _connected = False

    @staticmethod
    def connect():
        for i, ch in enumerate(PhidgetInterface.channels):
            input_device = VoltageRatioInput()
            input_device.setDeviceSerialNumber(PhidgetInterface.serial_number)
            input_device.setChannel(ch)
            input_device.openWaitForAttachment(1000)
            input_device.setDataInterval(PhidgetInterface._sampling_interval)
            input_device.setOnVoltageRatioChangeHandler(PhidgetInterface._make_update_handler(i))
            PhidgetInterface._inputs.append(input_device)

        PhidgetInterface._connected = True

    @staticmethod
    def disconnect():
        for input_device in PhidgetInterface._inputs:
            input_device.close()
        PhidgetInterface._inputs.clear()
        PhidgetInterface._connected = False

    @staticmethod
    def get_connected():
        return PhidgetInterface._connected

    @staticmethod
    def _make_update_handler(index):
        def handler(device, voltage_ratio):
            PhidgetInterface._voltages[index] = voltage_ratio
        return handler

    @staticmethod
    def set_coefficients(coeff: float, vertical_axis: VerticalAxis):
        """Set per-channel scaling coefficients"""
        PhidgetInterface._coefficients[vertical_axis.value] = coeff

    @staticmethod
    def zero():
        """Tare each channel by setting current value as zero reference"""
        PhidgetInterface._zero_offsets = [
            PhidgetInterface._voltages[i] * PhidgetInterface._coefficients[i]
            for i in range(len(PhidgetInterface.channels))
        ]
    @staticmethod
    def get_raw_voltages(vertical_axis: VerticalAxis):
        return PhidgetInterface._voltages[vertical_axis.value]

    @staticmethod
    def get_forces(vertical_axis: VerticalAxis):
        """Returns un-tared force (raw voltage × coefficient)"""
        return PhidgetInterface._voltages[vertical_axis.value] * PhidgetInterface._coefficients[vertical_axis.value]

    @staticmethod
    def get_calibrated_forces(vertical_axis: VerticalAxis):
        """Returns tared force (raw voltage × coefficient − zero offset)"""
        return PhidgetInterface._voltages[vertical_axis.value] * PhidgetInterface._coefficients[vertical_axis.value] - PhidgetInterface._zero_offsets[vertical_axis.value]
