from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QGroupBox, QLCDNumber, QGraphicsView, QMenu, QMenuBar, QStatusBar, QWidget
from PyQt6.QtGui import QAction

from Frontend.VerticalActuatorWidget import VerticalActuatorWidget
from Frontend.MacroControlWidget import MacroControlWidget
from Frontend.HorizontalLinearStagetWidget import HorizontalLinearStageWidget

class MainWindow(QtWidgets.QMainWindow):

    HorizontalAxisControlBox: QGroupBox
    VerticalAxis1ControlBox: QGroupBox
    VerticalAxis2ControlBox: QGroupBox

    XPositionDisp: QLCDNumber

    ZForce1Graph: QGraphicsView
    ZForce2Graph: QGraphicsView
    ZPos1Graph: QGraphicsView
    ZPos2Graph: QGraphicsView

    menuRoller_Lamination_Controller: QMenu
    actionOpen: QAction
    actionSave_Data: QAction
    actionSave_as: QAction
    actionSave_macro: QAction

    statusbar: QStatusBar
    foo_macro: QWidget

    def __init__(self, vertical_widgets: (VerticalActuatorWidget, VerticalActuatorWidget), horizontal_widget: HorizontalLinearStageWidget, macro_widget: MacroControlWidget):
        super(MainWindow, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/MainWindow/mainwindow.ui', self) # Load the .ui file

        self.HorizontalAxisControlBox.layout().addWidget(horizontal_widget)
        self.VerticalAxis1ControlBox.layout().addWidget(vertical_widgets[0])
        self.VerticalAxis2ControlBox.layout().addWidget(vertical_widgets[1])
        self.foo_macro.layout().addWidget(macro_widget)

    # def load_widgets(self):
