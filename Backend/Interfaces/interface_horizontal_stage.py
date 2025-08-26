from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QTimer, QIODevice
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
import threading
def get_ports(): return QSerialPortInfo.availablePorts()

def _tid(tag):  # tiny helper for debugging
    return f"{tag} TID={threading.get_ident()}"

class _Worker(QObject):
    positionUpdated = pyqtSignal(float)
    error = pyqtSignal(str)
    connectedChanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._port = None
        self._buffer = bytearray()
        self._buf_len = 1000
        self._running = False
        self._target = 0.0
        self._vmax = 10.0
        self._amax = 10.0
        self._poll = QTimer(self)
        self._poll.setInterval(30)
        self._poll.timeout.connect(self._tick)

    @pyqtSlot(str, int)
    def startIO(self, port_name: str, baud: int):
        # Create the port **in this thread** and parent it to self
        if self._port is None:
            self._port = QSerialPort(self)  # created now, in worker thread
            self._port.readyRead.connect(self._on_ready_read)

        self._port.setPortName(port_name)
        self._port.setBaudRate(baud)

        if self._port.open(QIODevice.OpenModeFlag.ReadWrite):
            self._running = True
            self._poll.start()  # start **after** open, in this thread
            self.connectedChanged.emit(True)
            print("Port open")
        else:
            print("open failed, error:", self._port.error())
            self.connectedChanged.emit(False)

    @pyqtSlot()
    def stopIO(self):
        self._running = False
        self._poll.stop()
        if self._port and self._port.isOpen():
            self._port.close()
        self.connectedChanged.emit(False)

    def _write(self, s: str):
        if self._port and self._port.isOpen():
            self._port.write(s.encode())

    def _tick(self):
        if not self._running or not self._port.isOpen():
            return
        self._write("fb\n")

    def _on_ready_read(self):
        self._buffer.extend(bytes(self._port.readAll()))
        # trim buffer
        if len(self._buffer) > self._buf_len:
            del self._buffer[:len(self._buffer) - self._buf_len]
        # parse last complete line
        lines = self._buffer.splitlines()
        if len(lines) >= 1:
            reading = lines[-1] if self._buffer.endswith(b"\n") else (lines[-2] if len(lines) >= 2 else b"")
            if reading:
                try:
                    pos = float(reading.strip())
                    self.positionUpdated.emit(pos)
                except ValueError:
                    # ignore incomplete/invalid line
                    pass

    @pyqtSlot(float)
    def setTarget(self, x: float):
        self._target = x
        self._write(f"tp{self._target}\n")

    @pyqtSlot(float)
    def setSpeed(self, v: float):
        self._vmax = v
        self._write(f"sp{self._vmax}\n")

    @pyqtSlot(float)
    def setAccel(self, a: float):
        self._amax = a
        self._write(f"ac{self._amax}\n")

class _Invoker(QObject):
    startRequested = pyqtSignal(str, int)
    stopRequested = pyqtSignal()
    setTargetRequested = pyqtSignal(float)
    setSpeedRequested = pyqtSignal(float)
    setAccelRequested = pyqtSignal(float)

class HorizontalStageInterface:
    _thread: QThread | None = None
    _worker: _Worker | None = None
    _invoker: _Invoker | None = None
    _last_position: float = 0.0
    _connected = False

    @staticmethod
    def init():
        if HorizontalStageInterface._thread is not None:
            return
        t = QThread()
        w = _Worker()
        inv = _Invoker()

        w.moveToThread(t)

        # Signals from worker -> manager
        w.positionUpdated.connect(lambda p: setattr(HorizontalStageInterface, "_last_position", p))
        w.connectedChanged.connect(lambda s: setattr(HorizontalStageInterface, "_connected", s))

        # Signals from invoker -> worker (these will be QUEUED across threads)
        inv.startRequested.connect(w.startIO)
        inv.stopRequested.connect(w.stopIO)
        inv.setTargetRequested.connect(w.setTarget)
        inv.setSpeedRequested.connect(w.setSpeed)
        inv.setAccelRequested.connect(w.setAccel)

        # Debug: confirm thread event loop is alive
        t.started.connect(lambda: print(_tid("worker thread started")))
        t.finished.connect(lambda: print(_tid("worker thread finished")))
        t.finished.connect(t.deleteLater)

        HorizontalStageInterface._thread = t
        HorizontalStageInterface._worker = w
        HorizontalStageInterface._invoker = inv

        t.start()
        print(_tid("main thread started worker thread"))

    @staticmethod
    def connect(port_name: str, baud: int):
        HorizontalStageInterface.init()
        HorizontalStageInterface._invoker.startRequested.emit(port_name, baud)

    @staticmethod
    def disconnect():
        if HorizontalStageInterface._invoker:
            HorizontalStageInterface._invoker.stopRequested.emit()

    @staticmethod
    def send_target_position(x: float):
        if HorizontalStageInterface._invoker:
            HorizontalStageInterface._invoker.setTargetRequested.emit(x)

    @staticmethod
    def send_speed_limit(v: float):
        if HorizontalStageInterface._invoker:
            HorizontalStageInterface._invoker.setSpeedRequested.emit(v)

    @staticmethod
    def send_accel_limit(a: float):
        if HorizontalStageInterface._invoker:
            HorizontalStageInterface._invoker.setAccelRequested.emit(a)

    @staticmethod
    def get_position() -> float:
        return HorizontalStageInterface._last_position

    @staticmethod
    def shutdown():
        if HorizontalStageInterface._invoker:
            HorizontalStageInterface._invoker.stopRequested.emit()
        if HorizontalStageInterface._thread:
            HorizontalStageInterface._thread.quit()
            HorizontalStageInterface._thread.wait()
        HorizontalStageInterface._worker = None
        HorizontalStageInterface._thread = None
        HorizontalStageInterface._invoker = None

    @staticmethod
    def get_connected() -> bool:
        return HorizontalStageInterface._connected
