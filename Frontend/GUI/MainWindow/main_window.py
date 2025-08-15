from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QGroupBox, QLCDNumber, QMenu, QStatusBar, QWidget, QSpinBox, QCheckBox, QPushButton, \
    QSizePolicy
from PyQt6.QtGui import QAction

from Backend.Interfaces.interface_horizontal_stage import HorizontalStageInterface
from Backend.Schedulers.DataLogger.datastruct_timeseries import Timeseries
from Backend.Schedulers.DataLogger.scheduler_data_logger import DataLoggerScheduler
from Frontend.GUI.HorizontalLinearStagetWidget.horizontal_linear_stage_widget import HorizontalLinearStageWidget
from Frontend.GUI.MacroControlWidget.macro_control_widget import MacroControlWidget
from Frontend.GUI.PhidgetControlWidget.phidget_control_widget import PhidgetControlWidget
from Frontend.GUI.PlotCanvas.plot_canvas import PlotCanvas
from Frontend.GUI.VerticalActuatorWidget.vertical_actuator_widget import VerticalActuatorWidget


class MainWindow(QtWidgets.QMainWindow):

    HorizontalAxisControlBox:         QGroupBox
    VerticalAxis0ControlBox:          QGroupBox
    VerticalAxis1ControlBox:          QGroupBox
    DataAreaGroup:                    QGroupBox

    XPositionDisp:                    QLCDNumber

    ZAxesPositionGroup:               QGroupBox
    ZAxesForceGroup:                  QGroupBox

    menuRoller_Lamination_Controller:   QMenu
    actionOpen:                         QAction
    actionSave_Data:                    QAction
    actionSave_as:                      QAction
    actionSave_macro:                   QAction

    statusbar:                          QStatusBar
    foo_macro:                        QWidget

    z_force_canvas:                   list[PlotCanvas]
    z_position_canvas:                list[PlotCanvas]
    __run_thread :                    QThread
    __interval : int

    SamplingTimeSpinBox: QSpinBox
    PlotRangeSpinBox: QSpinBox
    AutoSizeXCheckBox: QCheckBox

    def __init__(self, phidget_widget: PhidgetControlWidget, vertical_widgets: (VerticalActuatorWidget, VerticalActuatorWidget), horizontal_widget: HorizontalLinearStageWidget, macro_widget: MacroControlWidget):
        super(MainWindow, self).__init__() # Call the inherited classes __init__ method

        uic.loadUi('Frontend/GUI/MainWindow/mainwindow.ui', self) # Load the .ui file

        self.DataAreaGroup.layout().addWidget(phidget_widget)

        self.HorizontalAxisControlBox.layout().addWidget(horizontal_widget)
        self.VerticalAxis0ControlBox.layout().addWidget(vertical_widgets[0])
        self.VerticalAxis1ControlBox.layout().addWidget(vertical_widgets[1])
        self.foo_macro.layout().addWidget(macro_widget)

        self.z_force_canvas = [PlotCanvas(width=5, height=4, parent=self.ZAxesForceGroup) for _ in range(2)]
        self.z_position_canvas = [PlotCanvas(width=5, height=4, parent=self.ZAxesPositionGroup) for _ in range(2)]

        self.ZAxesForceGroup.layout().addWidget(self.z_force_canvas[0])
        self.ZAxesForceGroup.layout().addWidget(self.z_force_canvas[1])
        self.ZAxesPositionGroup.layout().addWidget(self.z_position_canvas[0])
        self.ZAxesPositionGroup.layout().addWidget(self.z_position_canvas[1])

        self.z_force_canvas[0].setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.z_force_canvas[1].setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.z_position_canvas[0].setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.z_position_canvas[1].setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.PlotRangeSpinBox.valueChanged.connect(self.__update_plot_params)
        self.SamplingTimeSpinBox.valueChanged.connect(self.__update_plot_params)
        self.AutoSizeXCheckBox.stateChanged.connect(self.__update_plot_params)

        self.__run_thread = QThread()
        self.__run_thread.run = self.__run
        self.__interval = 20
        self.__run_thread.start()

    def __update_plot_params(self):
        self.z_force_canvas[0].set_maximum_plot_time(self.PlotRangeSpinBox.value())
        self.z_force_canvas[1].set_maximum_plot_time(self.PlotRangeSpinBox.value())
        self.z_position_canvas[0].set_maximum_plot_time(self.PlotRangeSpinBox.value())
        self.z_position_canvas[1].set_maximum_plot_time(self.PlotRangeSpinBox.value())

        self.z_force_canvas[0].set_auto_x(self.AutoSizeXCheckBox.isChecked())
        self.z_force_canvas[1].set_auto_x(self.AutoSizeXCheckBox.isChecked())
        self.z_position_canvas[0].set_auto_x(self.AutoSizeXCheckBox.isChecked())
        self.z_position_canvas[1].set_auto_x(self.AutoSizeXCheckBox.isChecked())

        self.__interval = int(self.SamplingTimeSpinBox.value())

    def __run(self):
        while True:
            self.z_force_canvas[0].update_data(DataLoggerScheduler.feedback_force[0], DataLoggerScheduler.target_force[0])
            self.z_force_canvas[1].update_data(DataLoggerScheduler.feedback_force[1], DataLoggerScheduler.target_force[1])
            self.z_position_canvas[0].update_data(DataLoggerScheduler.feedback_position[0], DataLoggerScheduler.target_position[0])
            self.z_position_canvas[1].update_data(DataLoggerScheduler.feedback_position[1], DataLoggerScheduler.target_position[1])
            self.XPositionDisp.display(HorizontalStageInterface.get_position())
            QThread.msleep(self.__interval)