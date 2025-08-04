from abc import ABC, abstractmethod, ABCMeta

from PyQt6.QtCore import QObject, pyqtSignal, QThread

class MetaQObjectABC(type(QObject), ABCMeta):
    pass

class Worker(QObject,metaclass=MetaQObjectABC):
    finished : pyqtSignal

    @abstractmethod
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.finished = pyqtSignal()
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
    print("Go?")
    thread.started.connect(worker.execute_run)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)