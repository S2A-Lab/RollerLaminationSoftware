from PyQt6 import uic
from PyQt6.QtWidgets import (QWidget, QComboBox,QDoubleSpinBox)
from Backend.Schedulers.ActionExecute.macro_step import MacroStep

class ActionSetPIDWidget(QWidget):

    AxisComboBox: QComboBox

    ILimInput: QDoubleSpinBox
    KdInput: QDoubleSpinBox
    KiInput: QDoubleSpinBox
    KpInput: QDoubleSpinBox
    OutLimInput: QDoubleSpinBox

    action : MacroStep.ActionChangeVerticalPIDParams
    def __init__(self):
        super(ActionSetPIDWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/MacroControlWidget/ActionSetPIDWidget/actionsetpidwidget.ui', self) # Load the .ui file
        self.action = MacroStep.ActionChangeVerticalPIDParams(MacroStep.ActionChangeVerticalPIDParams.Axis(self.AxisComboBox.currentIndex()),
                                      float(self.KpInput.value()),
                                      float(self.KiInput.value()),
                                      float(self.KdInput.value()),
                                      float(self.ILimInput.value()),
                                      float(self.OutLimInput.value()))

        self.KpInput.valueChanged.connect(self.__kp_value_changed)
        self.KiInput.valueChanged.connect(self.__ki_value_changed)
        self.KdInput.valueChanged.connect(self.__kd_value_changed)
        self.ILimInput.valueChanged.connect(self.__ilim_input_changed)
        self.OutLimInput.valueChanged.connect(self.__olim_input_changed)


    def __kp_value_changed(self):
        self.action.kp = self.KpInput.value()

    def __ki_value_changed(self):
        self.action.ki = self.KiInput.value()

    def __kd_value_changed(self):
        self.action.kd = self.KdInput.value()

    def __ilim_input_changed(self):
        self.action.ilim = self.ILimInput.value()

    def __olim_input_changed(self):
        self.action.out_limit = self.OutLimInput.value()

    def load_action(self, action: MacroStep.ActionChangeVerticalPIDParams):
        self.action = action
        self.AxisComboBox.setCurrentIndex(action.axis.value)
        self.KpInput.setValue(action.kp)
        self.KiInput.setValue(action.ki)
        self.KdInput.setValue(action.kd)
        self.ILimInput.setValue(action.i_limit)
        self.OutLimInput.setValue(action.out_limit)
