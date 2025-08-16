from PyQt6 import uic
from PyQt6.QtWidgets import (QWidget, QComboBox, QDoubleSpinBox)
from Backend.Schedulers.ActionExecute.macro_step import MacroStep

class ActionMoveVerticalWidget(QWidget):

    AxisComboBox: QComboBox
    ModeComboBox: QComboBox
    TargetSpinBox: QDoubleSpinBox
    action : MacroStep.ActionMoveVertical

    def __init__(self):
        super(ActionMoveVerticalWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/MacroControlWidget/ActionMoveVerticalWidget/actionmoveverticalwidget.ui', self) # Load the .ui file
        self.action = MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis.X0,MacroStep.ActionMoveVertical.Mode.POSITION,0.0)
        self.AxisComboBox.currentIndexChanged.connect(self.__axis_combobox_change)
        self.ModeComboBox.currentIndexChanged.connect(self.__mode_combobox_change)
        self.TargetSpinBox.valueChanged.connect      (self.__target_spinbox_change)

    def __axis_combobox_change(self):
        self.action.axis = MacroStep.ActionMoveVertical.Axis(self.AxisComboBox.currentIndex())

    def __mode_combobox_change(self):
        self.action.mode = MacroStep.ActionMoveVertical.Mode(self.ModeComboBox.currentIndex())

    def __target_spinbox_change(self):
        self.action.target = self.TargetSpinBox.value()

    def load_action(self, action: MacroStep.ActionMoveVertical):
        self.action = action
        self.AxisComboBox.setCurrentIndex(action.axis.value)
        self.ModeComboBox.setCurrentIndex(action.mode.value)
        self.TargetSpinBox.setValue(action.target)