import subprocess
import yaml
import re

from PyQt5.QtCore import QTimer, QThread

from Backend.Interfaces.vertical_axis_base import VerticalAxis

def jrk2cmd(*args):
    return subprocess.check_output(['jrk2cmd'] + list(args))

class JRKInterface:
    channels = ["00425280", "00425253"]

    __connected = False

    __thread = QThread()

    __target_position = [0, 0]
    __pending_send_target_position = [False, False]
    __duty_cycle = [0, 0]
    __pending_send_duty_cycle = [False, False]
    __feedback_position = [0,0]
    __devices = []

    @staticmethod
    def init():
        JRKInterface.__thread.run = JRKInterface.__run
        JRKInterface.__thread.start()

    @staticmethod
    def connect():
        for idx, channel in enumerate(JRKInterface.channels):
            if not channel in JRKInterface.get_devices_list():
                print("Device not found.")
                return
        JRKInterface.__connected = True

    @staticmethod
    def __run():
        count = 0
        while True:
            count += 1
            if count > 20:
                devices = str(yaml.safe_load(jrk2cmd('--list')))
                JRKInterface.__devices = re.findall(r"\b\d{8}\b", devices)
                count = 0

            if JRKInterface.is_connected():
                for i in range(2):
                    status_x = yaml.safe_load(jrk2cmd('-d', JRKInterface.channels[i], '-s', '--full'))
                    x = status_x['Scaled feedback']
                    JRKInterface.__feedback_position[i] = x

                    if JRKInterface.__pending_send_target_position[i]:
                        jrk2cmd('-d', JRKInterface.channels[i], '--target',
                                str(int(JRKInterface.__target_position[i])))
                        JRKInterface.__pending_send_target_position[i] = False
                    if JRKInterface.__pending_send_duty_cycle[i]:
                        jrk2cmd('-d', JRKInterface.channels[i], '--force-duty-cycle-target',
                                str(int(JRKInterface.__duty_cycle[i])))
                        JRKInterface.__pending_send_duty_cycle[i] = False
            QThread.msleep(1)


    @staticmethod
    def disconnect():
        JRKInterface.__connected = False

    @staticmethod
    def get_devices_list():
        devices = str(yaml.safe_load(jrk2cmd('--list')))
        return re.findall(r"\b\d{8}\b", devices)

    @staticmethod
    def set_target_position(target: int, vertical_axis: VerticalAxis):
        JRKInterface.__target_position[vertical_axis.value] = target
        JRKInterface.__pending_send_target_position[vertical_axis.value] = True

    @staticmethod
    def set_duty_cycle(target: int, vertical_axis: VerticalAxis):
        JRKInterface.__duty_cycle[vertical_axis.value] = target
        JRKInterface.__pending_send_duty_cycle[vertical_axis.value] = True

    @staticmethod
    def get_position(vertical_axis: VerticalAxis) -> int:
        return JRKInterface.__feedback_position[vertical_axis.value]

    @staticmethod
    def is_connected():
        return JRKInterface.__connected