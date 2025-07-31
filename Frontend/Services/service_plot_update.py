from Frontend.GUI.MainWindow.main_window import MainWindow
from Backend.Schedulers.DataLogger.scheduler_data_logger import DataLoggerScheduler
from PyQt6.QtCore import QThread
class PlotUpdateModule:
    interval = 20
    __main_window : MainWindow = None
    __run_thread = QThread()

    @staticmethod
    def init(main_window: MainWindow):
        PlotUpdateModule.__main_window = main_window
        PlotUpdateModule.__run_thread.run = PlotUpdateModule.__run
        PlotUpdateModule.__run_thread.start()

    @staticmethod
    def __run():
        while True:
            PlotUpdateModule.__main_window.update_plot(DataLoggerScheduler.target_force[0], DataLoggerScheduler.target_force[1],
                                                       DataLoggerScheduler.feedback_force[0], DataLoggerScheduler.feedback_force[1],
                                                       DataLoggerScheduler.target_position[0], DataLoggerScheduler.target_position[1],
                                                       DataLoggerScheduler.feedback_position[0], DataLoggerScheduler.feedback_position[1])
            QThread.msleep(PlotUpdateModule.interval)

    @staticmethod
    def change_interval(interval):
        PlotUpdateModule.interval = interval