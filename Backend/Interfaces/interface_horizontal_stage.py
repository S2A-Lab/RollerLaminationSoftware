from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt6.QtCore import pyqtSignal, QIODevice, QThread


def get_ports():
    return QSerialPortInfo.availablePorts()

class HorizontalStageInterface:

    __run_thread = QThread()
    __serial_port = QSerialPort()
    __connected = False
    __buffer = b''
    __waiting_for_feedback = False

    __target_position = 0.0
    __maximum_speed = 10.0
    __maximum_acceleration = 10.0

    __request_write_target_position = False
    __request_write_maximum_speed = False
    __request_write_maximum_acceleration = False

    __feedback_position = 0.0

    @staticmethod
    def init():
        HorizontalStageInterface.__run_thread.run = HorizontalStageInterface.__run
        HorizontalStageInterface.__run_thread.start()

    @staticmethod
    def connect(port_name: str, baudrate: int):
        HorizontalStageInterface.__serial_port.setPortName(port_name)
        HorizontalStageInterface.__serial_port.setBaudRate(baudrate)
        if HorizontalStageInterface.__serial_port.open(QIODevice.ReadWrite):
            HorizontalStageInterface.__connected = True
        else:
            print(f"Failed to open port {port_name}")

    @staticmethod
    def disconnect():
        if HorizontalStageInterface.__serial_port.isOpen():
            HorizontalStageInterface.__serial_port.close()
        HorizontalStageInterface.__connected = False

    @staticmethod
    def get_connected():
        return HorizontalStageInterface.__connected

    @staticmethod
    def send_target_position(target):
        HorizontalStageInterface.__target_position = target
        HorizontalStageInterface.__request_write_target_position = True

    @staticmethod
    def send_speed_limit(speed):
        HorizontalStageInterface.__maximum_speed = speed
        HorizontalStageInterface.__request_write_maximum_speed = True

    @staticmethod
    def send_accel_limit(acceleration):
        HorizontalStageInterface.__maximum_acceleration = acceleration
        HorizontalStageInterface.__request_write_maximum_acceleration = True

    @staticmethod
    def get_position():
        return HorizontalStageInterface.__feedback_position

    @staticmethod
    def __write(command: str):
        HorizontalStageInterface.__serial_port.write(command.encode())

    @staticmethod
    def __run():
        while True:
            if HorizontalStageInterface.__connected:
                # Handle sending requests
                if HorizontalStageInterface.__request_write_maximum_speed:
                    HorizontalStageInterface.__write(f"sp{HorizontalStageInterface.__maximum_speed}\n")
                    HorizontalStageInterface.__request_write_maximum_acceleration = False
                if HorizontalStageInterface.__request_write_target_position:
                    HorizontalStageInterface.__write(f"tp{HorizontalStageInterface.__target_position}\n")
                    HorizontalStageInterface.__request_write_target_position = False
                if HorizontalStageInterface.__request_write_maximum_acceleration:
                    HorizontalStageInterface.__write(f"ac{HorizontalStageInterface.__maximum_acceleration}\n")
                    HorizontalStageInterface.__request_write_maximum_acceleration = False

                HorizontalStageInterface.__write(f"fb\n")

                HorizontalStageInterface.__buffer += HorizontalStageInterface.__serial_port.readAll().data()
                if b'\n' in HorizontalStageInterface.__buffer:
                    line, _, HorizontalStageInterface.__buffer = HorizontalStageInterface.__buffer.partition(b'\n')
                    if HorizontalStageInterface.__waiting_for_feedback:
                        try:
                            HorizontalStageInterface.__feedback_position = int(line.decode().strip())
                        except ValueError:
                            print("Invalid feedback value")
                        HorizontalStageInterface.__waiting_for_feedback = False
            else:
                pass
            QThread.msleep(1)