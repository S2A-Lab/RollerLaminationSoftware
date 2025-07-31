import subprocess
import yaml

from Backend.Interfaces.vertical_axis_base import VerticalAxis

def jrk2cmd(*args):
    return subprocess.check_output(['jrk2cmd'] + list(args))

class JRKInterface:
    channels = ["00425280", "00425253"]

    __connected = False
    @staticmethod
    def connect():
        for idx, channel in enumerate(JRKInterface.channels):
            if not channel in JRKInterface.get_devices_list():
                print("Device not found.")
                return
        JRKInterface.__connected = True

    @staticmethod
    def disconnect():
        JRKInterface.__connected = False

    @staticmethod
    def get_devices_list():
        devices = yaml.safe_load(jrk2cmd('--list'))
        return list(devices.keys()) if devices else []

    @staticmethod
    def set_target_position(target: int, vertical_axis: VerticalAxis):
        jrk2cmd('-d', JRKInterface.channels[vertical_axis.value], '--target', str(int(target)))

    @staticmethod
    def set_duty_cycle(target: int, vertical_axis: VerticalAxis):
        jrk2cmd('-d', JRKInterface.channels[vertical_axis.value], '--force-duty-cycle-target', str(int(target)))

    @staticmethod
    def get_position(vertical_axis: VerticalAxis) -> int:
        status_x = yaml.safe_load(jrk2cmd('-d', JRKInterface.channels[vertical_axis.value], '-s', '--full'))
        x = status_x['Scaled feedback']
        return int(x)

    @staticmethod
    def is_connected():
        return JRKInterface.__connected