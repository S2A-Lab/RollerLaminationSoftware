from argparse import Action

from PyQt6.QtWidgets import QApplication, QStyleFactory

from Backend.Interfaces.vertical_axis_base import VerticalAxis
from Backend.Schedulers.ActionExecute.scheduler_action_execute import ActionExecuteScheduler
from Backend.Schedulers.DataLogger.scheduler_data_logger import DataLoggerScheduler
from Frontend.GUI.MainWindow.main_window import MainWindow

from Frontend.GUI.VerticalActuatorWidget.VerticalActuatorWidget import VerticalActuatorWidget
from Frontend.GUI.MacroControlWidget.main_control_widget import MacroControlWidget
from Frontend.GUI.HorizontalLinearStagetWidget.horizontal_linear_stage_widget import HorizontalLinearStageWidget

import sys

from Frontend.Services.service_plot_update import PlotUpdateModule

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ActionExecuteScheduler.init()
    DataLoggerScheduler.init()

    horizontal_widget = HorizontalLinearStageWidget()
    vertical_widget0 = VerticalActuatorWidget(VerticalAxis.AXIS_0)
    vertical_widget1 = VerticalActuatorWidget(VerticalAxis.AXIS_1)


    macro_widget = MacroControlWidget()
    window = MainWindow((vertical_widget0, vertical_widget1),horizontal_widget, macro_widget)

    PlotUpdateModule.init(window)

    window.XPositionDisp.display("")
    # with open("Backend/Interfaces/ui_interface/assets/icons/stylesheet.qss", "r") as stylesheet:
    #     app.setStyleSheet(stylesheet.read())
    # window = MainService()
    window.show()
    app.setStyle(QStyleFactory.create("Fusion"))
    sys.exit(app.exec())