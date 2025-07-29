import serial
from serial.tools import list_ports

def get_ports():
    return list_ports.comports()

class HorizontalStageInterface:

    serial_port = serial.Serial()
    __connected = False
    @staticmethod
    def __init__(parent=None):
        super().__init__()
        HorizontalStageInterface.serial_port = serial.Serial()

    @staticmethod
    def connect(port_name, baudrate: int):
        HorizontalStageInterface.serial_port = serial.Serial(port_name, baudrate)
        HorizontalStageInterface.__connected = True

    @staticmethod
    def disconnect():
        HorizontalStageInterface.serial_port.close()
        HorizontalStageInterface.__connected = False

    @staticmethod
    def get_connected():
        return HorizontalStageInterface.__connected

    @staticmethod
    def send_target_position(target):
        HorizontalStageInterface.serial_port.write(("tp" + str(target) + '\n').encode())

    @staticmethod
    def send_speed_limit(speed):
        HorizontalStageInterface.serial_port.write(("sp" + str(speed) + '\n').encode())

    @staticmethod
    def send_accel_limit(acceleration):
        HorizontalStageInterface.serial_port.write(("ac" + str(acceleration) + '\n').encode())

    @staticmethod
    def get_position():
        HorizontalStageInterface.serial_port.write("fb \r\n".encode())
        return int(HorizontalStageInterface.serial_port.readline())