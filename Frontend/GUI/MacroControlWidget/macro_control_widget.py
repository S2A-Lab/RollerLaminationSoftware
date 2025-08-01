from PyQt6 import uic
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QTabWidget, QColumnView, QLineEdit
)

from Backend.Schedulers.ActionExecute.macro_step import MacroStep


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

    StepNameLineEdit: QLineEdit

    __action_sequence: list[MacroStep]
    __data_model: QStandardItemModel

    def __init__(self):
        super(MacroControlWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/MacroControlWidget/macrocontrolwidget.ui', self) # Load the .ui file
        self.__action_sequence = []
        self.__data_model = QStandardItemModel()
        self.StepView.setModel(self.__data_model)
        self.AddStepBtn.clicked.connect(self.__add_step_btn)


    def __add_step_btn(self):
        self.__action_sequence.append(MacroStep())
        item = QStandardItem()
        item.setText(self.StepNameLineEdit.text())
        self.__data_model.appendRow(item)

