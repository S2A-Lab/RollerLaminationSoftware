from PyQt6 import uic
from PyQt6.QtWidgets import (QWidget, QComboBox,QDoubleSpinBox)
from Backend.Schedulers.ActionExecute.macro_step import MacroStep

class EndPositionWidget(QWidget):

    AxisComboBox: QComboBox
    TargetSpinBox: QDoubleSpinBox
    ThresholdSpinBox: QDoubleSpinBox
    condition : MacroStep.EndConditionPosition

    def __init__(self):
        super(EndPositionWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/MacroControlWidget/EndConditionPosition/endpositionwidget.ui', self) # Load the .ui file
        self.condition = MacroStep.EndConditionPosition(MacroStep.EndConditionPosition.Axis.X0,0.0, 0.0)
        self.AxisComboBox.currentIndexChanged.connect(self.__axis_combobox_change)
        self.TargetSpinBox.valueChanged.connect(self.__target_spinbox_change)
        self.ThresholdSpinBox.valueChanged.connect(self.__threshold_spinbox_change)

    def __axis_combobox_change(self):
        self.condition.axis = MacroStep.EndConditionPosition.Axis(self.AxisComboBox.currentIndex())

    def __target_spinbox_change(self):
        self.condition.target = self.TargetSpinBox.value()

    def __threshold_spinbox_change(self):
        self.condition.threshold = self.ThresholdSpinBox.value()

    def load_condition(self, condition: MacroStep.EndConditionPosition):
        self.ThresholdSpinBox.setValue(condition.threshold)
        self.TargetSpinBox.setValue(condition.target)
        self.AxisComboBox.setCurrentIndex(condition.axis.value)