from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QTabWidget, QColumnView
)

class MacroControlWidget(QWidget):
    StepView: QColumnView
    DeleteBtn: QPushButton
    MoveDownBtn: QPushButton
    MoveUpBtn: QPushButton

    AddStepBtn: QPushButton
    OperationAddBtn: QPushButton
    OperationTab: QTabWidget
    tab: QWidget
    tab_2: QWidget

    EndConditionAddBtn: QPushButton
    EndConditionTab: QTabWidget
    tab_3: QWidget
    tab_4: QWidget

    ForceStopBtn: QPushButton
    PauseBtn: QPushButton
    ResumeBtn: QPushButton
    RunMacroBtn: QPushButton
    SaveDataBtn: QPushButton

    def __init__(self):
        super(MacroControlWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/MacroControlWidget/macrocontrolwidget.ui', self) # Load the .ui file