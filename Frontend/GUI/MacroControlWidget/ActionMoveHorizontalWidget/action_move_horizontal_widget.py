from PyQt6 import uic
from PyQt6.QtWidgets import (QWidget, QDoubleSpinBox)
from Backend.Schedulers.ActionExecute.macro_step import MacroStep

class ActionMoveHorizontalWidget(QWidget):

    AccelSpinBox: QDoubleSpinBox
    PositionSpinBox: QDoubleSpinBox
    SpeedSpinBox: QDoubleSpinBox
    action : MacroStep.ActionMoveHorizontal

    def __init__(self):
        super(ActionMoveHorizontalWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/MacroControlWidget/ActionMoveHorizontalWidget/actionmovehorizontalwidget.ui', self) # Load the .ui file
        self.action = MacroStep.ActionMoveHorizontal( 0.0,0.0,0.0)
        self.AccelSpinBox.valueChanged.connect(self.__accel_spinbox_change)
        self.PositionSpinBox.valueChanged.connect(self.__position_spinbox_change)
        self.SpeedSpinBox.valueChanged.connect      (self.__speed_spinbox_change)

    def __position_spinbox_change(self):
        self.action.target_position = self.PositionSpinBox.value()

    def __speed_spinbox_change(self):
        self.action.max_vel = self.SpeedSpinBox.value()

    def __accel_spinbox_change(self):
        self.action.max_accel = self.AccelSpinBox.value()

    def load_action(self, action: MacroStep.ActionMoveHorizontal):
        self.AccelSpinBox.setValue(action.max_accel)
        self.PositionSpinBox.setValue(action.target_position)
        self.SpeedSpinBox.setValue(action.max_vel)