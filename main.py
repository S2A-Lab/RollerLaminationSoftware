import traceback

from PyQt6.QtCore import qInstallMessageHandler,QThread
from PyQt6.QtWidgets import QApplication, QStyleFactory

from Backend.Interfaces.interface_horizontal_stage import HorizontalStageInterface
from Backend.Interfaces.interface_jrk import JRKInterface
from Backend.Interfaces.vertical_axis_base import VerticalAxis
from Backend.Schedulers.ActionExecute.scheduler_action_execute import ActionExecuteScheduler
from Backend.Schedulers.DataLogger.scheduler_data_logger import DataLoggerScheduler
from Frontend.GUI.MainWindow.main_window import MainWindow
from Frontend.GUI.PhidgetControlWidget.phidget_control_widget import PhidgetControlWidget

from Frontend.GUI.VerticalActuatorWidget.vertical_actuator_widget import VerticalActuatorWidget
from Frontend.GUI.MacroControlWidget.macro_control_widget import MacroControlWidget
from Frontend.GUI.HorizontalLinearStagetWidget.horizontal_linear_stage_widget import HorizontalLinearStageWidget
import faulthandler
import sys

def error_handler(etype, value, tb):
    error_msg = ''.join(traceback.format_exception(etype, value, tb))
    print(error_msg)

def qt_message_handler(mode, context, message):
    sys.stderr.write(f"QtMsg[{mode}]: {message}\n")


if __name__ == '__main__':
    faulthandler.enable()
    sys.excepthook = error_handler
    app = QApplication(sys.argv)
    qInstallMessageHandler(qt_message_handler)

    HorizontalStageInterface.init()
    QThread.msleep(100)
    # HorizontalStageInterface.connect("COM9",115200)
    JRKInterface.init()

    # # We dont need phidget interface to init here. UI will initialize it.
    # PhidgetInterface.connect()
    #
    DataLoggerScheduler.init()
    ActionExecuteScheduler.init()

    horizontal_widget = HorizontalLinearStageWidget()
    vertical_widget0 = VerticalActuatorWidget(VerticalAxis.AXIS_0)
    vertical_widget1 = VerticalActuatorWidget(VerticalAxis.AXIS_1)
    phidget_widget = PhidgetControlWidget()

    macro_widget = MacroControlWidget()
    window = MainWindow(phidget_widget,(vertical_widget0, vertical_widget1),horizontal_widget, macro_widget)

    window.show()
    app.setStyle(QStyleFactory.create("Fusion"))
    sys.exit(app.exec())