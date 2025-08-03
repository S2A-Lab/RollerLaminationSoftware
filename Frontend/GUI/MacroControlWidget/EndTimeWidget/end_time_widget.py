from PyQt6 import uic
from PyQt6.QtWidgets import (QWidget, QSpinBox)

from Backend.Schedulers.ActionExecute.macro_step import MacroStep


class EndTimeWidget(QWidget):
    TimeSpinBox: QSpinBox

    def __init__(self):
        super(EndTimeWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/MacroControlWidget/EndTimeWidget/endtimewidget.ui', self) # Load the .ui file
        self.condition = MacroStep.EndConditionTime(0)
        self.TimeSpinBox.valueChanged.connect(self.__time_spinbox_change)

    def __time_spinbox_change(self):
        self.condition.wait_time = self.TimeSpinBox.value()

    def load_condition(self, condition : MacroStep.EndConditionTime):
        self.TimeSpinBox.setValue(condition.wait_time)