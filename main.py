from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QApplication, QStyleFactory

from Backend.Interfaces.interface_horizontal_stage import HorizontalStageInterface
from Backend.Interfaces.interface_jrk import JRKInterface
from Backend.Interfaces.interface_phidget import PhidgetInterface
from Backend.Interfaces.vertical_axis_base import VerticalAxis
from Backend.Schedulers.ActionExecute.scheduler_action_execute import ActionExecuteScheduler
from Backend.Schedulers.DataLogger.scheduler_data_logger import DataLoggerScheduler
from Frontend.GUI.MainWindow.main_window import MainWindow
from Frontend.GUI.PhidgetControlWidget.phidget_control_widget import PhidgetControlWidget

from Frontend.GUI.VerticalActuatorWidget.vertical_actuator_widget import VerticalActuatorWidget
from Frontend.GUI.MacroControlWidget.macro_control_widget import MacroControlWidget
from Frontend.GUI.HorizontalLinearStagetWidget.horizontal_linear_stage_widget import HorizontalLinearStageWidget

import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    HorizontalStageInterface.init()
    JRKInterface.init()


    # PhidgetInterface.connect()

    DataLoggerScheduler.init()
    ActionExecuteScheduler.init()

    # DataLoggerScheduler.start_recording()

    horizontal_widget = HorizontalLinearStageWidget()
    vertical_widget0 = VerticalActuatorWidget(VerticalAxis.AXIS_0)
    vertical_widget1 = VerticalActuatorWidget(VerticalAxis.AXIS_1)
    phidget_widget = PhidgetControlWidget()

    macro_widget = MacroControlWidget()
    window = MainWindow(phidget_widget,(vertical_widget0, vertical_widget1),horizontal_widget, macro_widget)
    # with open("Backend/Interfaces/ui_interface/assets/icons/stylesheet.qss", "r") as stylesheet:
    #     app.setStyleSheet(stylesheet.read())
    # window = MainService()
    window.show()
    app.setStyle(QStyleFactory.create("Fusion"))
    sys.exit(app.exec())