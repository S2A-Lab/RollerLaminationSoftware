import subprocess
import yaml
import re
from PyQt6.QtCore import QThread
from Backend.Interfaces.vertical_axis_base import VerticalAxis


def jrk2cmd(*args):
    return subprocess.check_output(['jrk2cmd'] + list(args))


class JRKWorker(QThread):
    def __init__(self, channels, parent=None):
        super().__init__(parent)
        self.channels = channels
        self._connected = False
        self._target_position = [0, 0]
        self._pending_target = [False, False]
        self._duty_cycle = [0, 0]
        self._pending_duty = [False, False]
        self._feedback = [0, 0]
        self._devices = []
        self._running = True

    def run(self):
        count = 0
        while self._running:
            count += 1
            # Update device list periodically
            if count > 20:
                devices = str(yaml.safe_load(jrk2cmd('--list')))
                self._devices = re.findall(r"\b\d{8}\b", devices)
                count = 0

            if self._connected:
                for i in range(len(self.channels)):
                    status = yaml.safe_load(
                        jrk2cmd('-d', self.channels[i], '-s', '--full')
                    )
                    self._feedback[i] = status['Scaled feedback']

                    if self._pending_target[i]:
                        jrk2cmd('-d', self.channels[i], '--target',
                                str(int(self._target_position[i])))
                        self._pending_target[i] = False

                    if self._pending_duty[i]:
                        jrk2cmd('-d', self.channels[i], '--force-duty-cycle-target',
                                str(int(self._duty_cycle[i])))
                        self._pending_duty[i] = False

            QThread.msleep(30)  # yield for scheduler

    def stop(self):
        self._running = False
        self.wait()

    # API methods
    def connect_devices(self):
        for ch in self.channels:
            if ch not in self.get_devices_list():
                print("Device not found.")
                return
        self._connected = True

    def disconnect_devices(self):
        self._connected = False

    def get_devices_list(self):
        devices = str(yaml.safe_load(jrk2cmd('--list')))
        return re.findall(r"\b\d{8}\b", devices)

    def set_target_position(self, target: int, axis: VerticalAxis):
        self._target_position[axis.value] = target
        self._pending_target[axis.value] = True

    def set_duty_cycle(self, target: int, axis: VerticalAxis):
        self._duty_cycle[axis.value] = target
        self._pending_duty[axis.value] = True

    def get_position(self, axis: VerticalAxis) -> int:
        return self._feedback[axis.value]

    def is_connected(self):
        return self._connected


class JRKInterface:
    channels = ["00425280", "00425253"]
    _worker: JRKWorker | None = None

    @staticmethod
    def init():
        if JRKInterface._worker is None:
            JRKInterface._worker = JRKWorker(JRKInterface.channels)
            JRKInterface._worker.start()

    @staticmethod
    def shutdown():
        if JRKInterface._worker:
            JRKInterface._worker.stop()
            JRKInterface._worker = None

    @staticmethod
    def connect():
        if JRKInterface._worker:
            JRKInterface._worker.connect_devices()

    @staticmethod
    def disconnect():
        if JRKInterface._worker:
            JRKInterface._worker.disconnect_devices()

    @staticmethod
    def get_devices_list():
        if JRKInterface._worker:
            return JRKInterface._worker.get_devices_list()
        return []

    @staticmethod
    def set_target_position(target: int, vertical_axis: VerticalAxis):
        if JRKInterface._worker:
            JRKInterface._worker.set_target_position(target, vertical_axis)

    @staticmethod
    def set_duty_cycle(target: int, vertical_axis: VerticalAxis):
        if JRKInterface._worker:
            JRKInterface._worker.set_duty_cycle(target, vertical_axis)

    @staticmethod
    def get_position(vertical_axis: VerticalAxis) -> int:
        if JRKInterface._worker:
            return JRKInterface._worker.get_position(vertical_axis)
        return 0

    @staticmethod
    def is_connected():
        if JRKInterface._worker:
            return JRKInterface._worker.is_connected()
        return False