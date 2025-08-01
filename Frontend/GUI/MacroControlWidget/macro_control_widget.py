from PyQt6 import uic
from PyQt6.QtCore import QStringListModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QTabWidget, QColumnView, QLineEdit, QSizePolicy,QListView
)

from Backend.Schedulers.ActionExecute.macro_step import MacroStep


class TwoColumnFixedView(QColumnView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setResizeGripsVisible(False)

    def createColumn(self, index):
        """Override to prevent adding more than 2 columns"""
        if len(self.findChildren(QListView)) >= 2:
            return None  # Stop adding more columns
        return super().createColumn(index)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.__resize_columns()

    def __resize_columns(self):
        columns = self.findChildren(QListView)
        if len(columns) >= 2:
            total_width = self.viewport().width()
            half_width = total_width // 2
            columns[0].setFixedWidth(half_width)
            columns[1].setFixedWidth(total_width - half_width)

    def updateGeometries(self):
        """Ensure resizing when model changes"""
        super().updateGeometries()
        self.__resize_columns()


class MacroControlWidget(QWidget):
    StepView: QListView
    EndConditionView: QListView
    OperationView: QListView
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
        self.__step_model = QStringListModel()
        self.__action_model = QStringListModel()
        self.__end_condition_model = QStringListModel()

        self.__step_strings = []
        self.__action_strings = []
        self.__end_condition_strings = []

        self.StepView.setModel(self.__step_model)
        self.EndConditionView.setModel(self.__end_condition_model)
        self.OperationView.setModel(self.__action_model)

        self.AddStepBtn.clicked.connect(self.__add_step_btn)
        self.EndConditionAddBtn.clicked.connect(self.__add_end_condition_btn)

    def __add_step_btn(self):
        step_index = max(self.StepView.currentIndex().row(), -1) +1

        step = MacroStep()
        step.name = self.StepNameLineEdit.text()
        self.__step_strings.insert(step_index, self.StepNameLineEdit.text())
        self.__step_model.setStringList(self.__step_strings)
        self.__action_sequence.insert(step_index, step)

        index = self.__step_model.index(step_index)
        self.StepView.setCurrentIndex(index)

    def __add_end_condition_btn(self):
        end_condition = MacroStep.EndConditionTime(1000)
        step_index = max(self.StepView.currentIndex().row(), 0)
        if len(self.__step_strings)<=0:
            self.__add_step_btn()
        step_index_obj = self.__step_model.index(step_index)
        self.StepView.setCurrentIndex(step_index_obj)
        self.__end_condition_strings.append(self.StepNameLineEdit.text())
        self.__end_condition_model.setStringList(self.__end_condition_strings)



    def __add_action_btn(self):
        action = MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis.X0, MacroStep.ActionMoveVertical.Mode.POSITION)
        step_index = max(self.StepView.currentIndex().row(), 0)
        if len(self.__step_strings)<=0:
            self.__add_step_btn()
        step_index_obj = self.__step_model.index(step_index)
        self.StepView.setCurrentIndex(step_index_obj)
        self.__action_strings.append(self.StepNameLineEdit.text())
        self.__action_model.setStringList(self.__action_strings)


