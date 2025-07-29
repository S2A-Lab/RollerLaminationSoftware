from abc import ABC,abstractmethod

from PyQt6.QtCore import QObject, pyqtSignal, QThread

class Worker(QObject,ABC):
    finished = pyqtSignal()
    @abstractmethod
    def __init__(self, *args, **kwargs):
        super().__init__()
        pass
    @abstractmethod
    def run(self):
        pass

    def execute_run(self):
        self.run()
        self.stop()
        self.finished.emit()

    @abstractmethod
    def stop(self):
        pass


def move_worker_to_thread(worker: Worker, thread: QThread):
    worker.moveToThread(thread)
    thread.started.connect(worker.execute_run)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)