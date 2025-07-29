from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QGroupBox, QLCDNumber, QMenu, QStatusBar, QWidget
from PyQt6.QtGui import QAction

from Frontend.GUI.PlotCanvas.plot_canvas import PlotCanvas
from Frontend.GUI.VerticalActuatorWidget import VerticalActuatorWidget
from Frontend.GUI.MacroControlWidget import MacroControlWidget
from Frontend.GUI.HorizontalLinearStagetWidget import HorizontalLinearStageWidget


class MainWindow(QtWidgets.QMainWindow):

    HorizontalAxisControlBox:         QGroupBox
    VerticalAxis0ControlBox:          QGroupBox
    VerticalAxis1ControlBox:          QGroupBox

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

    def __init__(self, vertical_widgets: (VerticalActuatorWidget, VerticalActuatorWidget), horizontal_widget: HorizontalLinearStageWidget, macro_widget: MacroControlWidget):
        super(MainWindow, self).__init__() # Call the inherited classes __init__ method

        uic.loadUi('Frontend/GUI/MainWindow/mainwindow.ui', self) # Load the .ui file

        self.HorizontalAxisControlBox.layout().addWidget(horizontal_widget)
        self.VerticalAxis0ControlBox.layout().addWidget(vertical_widgets[0])
        self.VerticalAxis1ControlBox.layout().addWidget(vertical_widgets[1])
        self.foo_macro.layout().addWidget(macro_widget)

        self.z_force_canvas = [PlotCanvas(width=5, height=4) for _ in range(2)]
        self.z_position_canvas = [PlotCanvas(width=5, height=4) for _ in range(2)]

        self.ZAxesForceGroup.layout().addWidget(self.z_force_canvas[0])
        self.ZAxesForceGroup.layout().addWidget(self.z_force_canvas[1])
        self.ZAxesPositionGroup.layout().addWidget(self.z_position_canvas[0])
        self.ZAxesPositionGroup.layout().addWidget(self.z_position_canvas[1])

    # def load_widgets(self):
