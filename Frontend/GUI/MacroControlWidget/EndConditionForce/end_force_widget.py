from PyQt6 import uic
from PyQt6.QtWidgets import (QWidget, QComboBox, QDoubleSpinBox)
from Backend.Schedulers.ActionExecute.macro_step import MacroStep

class EndForceWidget(QWidget):

    AxisComboBox: QComboBox
    TargetSpinBox: QDoubleSpinBox
    ThresholdSpinBox: QDoubleSpinBox
    condition : MacroStep.EndConditionForce

    def __init__(self):
        super(EndForceWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/MacroControlWidget/EndConditionForce/endforcewidget.ui', self) # Load the .ui file
        self.condition = MacroStep.EndConditionForce(MacroStep.EndConditionForce.Axis(self.AxisComboBox.currentIndex()), 0.0,0.0)
        self.AxisComboBox.currentIndexChanged.connect(self.__axis_combobox_change)
        self.TargetSpinBox.valueChanged.connect(self.__target_spinbox_change)
        self.ThresholdSpinBox.valueChanged.connect(self.__threshold_spinbox_change)

    def __axis_combobox_change(self):
        self.condition.axis = MacroStep.EndConditionForce.Axis(self.AxisComboBox.currentIndex())

    def __target_spinbox_change(self):
        self.condition.target = self.TargetSpinBox.value()

    def __threshold_spinbox_change(self):
        self.condition.threshold = self.ThresholdSpinBox.value()

    def load_condition(self,condition: MacroStep.EndConditionForce):
        self.TargetSpinBox.setValue(condition.target)
        self.ThresholdSpinBox.setValue(condition.threshold)
        self.AxisComboBox.setCurrentIndex(condition.axis.value)
