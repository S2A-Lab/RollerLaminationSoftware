from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QComboBox, QLabel, QSpinBox,
    QDoubleSpinBox, QLCDNumber
)
from PyQt6.QtCore import QThread, pyqtSignal

from Backend.Interfaces.interface_jrk import JRKInterface
from Backend.Interfaces.vertical_axis_base import VerticalAxis
from Backend.Schedulers.ActionExecute.macro_step import MacroStep
from Backend.Schedulers.ActionExecute.scheduler_action_execute import ActionExecuteScheduler


class VerticalActuatorWidget(QWidget):
    # Type annotations for UI elements
    PositionLCD: QLCDNumber
    StartForceBtn: QPushButton

    DeviceSelectionBtn: QComboBox
    DeviceSetBtn: QPushButton
    foo_device_label: QLabel

    MoveDownBtn: QPushButton
    MoveUpBtn: QPushButton
    spinBox: QSpinBox

    SetPIDBtn: QPushButton
    ILimInput: QDoubleSpinBox
    KdInput: QDoubleSpinBox
    KiInput: QDoubleSpinBox
    KpInput: QDoubleSpinBox
    OutLimInput: QDoubleSpinBox

    foo_labelilim: QLabel
    foo_labelkd: QLabel
    foo_labelki: QLabel
    foo_labelkp: QLabel
    foo_labeloutlim: QLabel

    axis: VerticalAxis

    __last_device_hash: int
    __thread: QThread

    def __init__(self, axis: VerticalAxis):
        super(VerticalActuatorWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/VerticalActuatorWidget/verticalactuatorwidget.ui', self) # Load the .ui file
        self.axis = axis

        self.SetPIDBtn.clicked.connect(self.pid_set_btn_pressed)
        self.MoveUpBtn.clicked.connect(self.move_up_action)
        self.MoveDownBtn.clicked.connect(self.move_down_action)
        self.DeviceSetBtn.clicked.connect(self.set_device_action)

        self.MoveUpBtn.setEnabled(False)
        self.MoveDownBtn.setEnabled(False)
        self.StartForceBtn.setEnabled(False)
        self.__thread = QThread()
        self.__thread.run = self.__run
        self.__thread.start()
        self.__last_device_hash = 0


    def pid_set_btn_pressed(self):
        macro_step = MacroStep()
        macro_step_action = MacroStep.ActionChangeVerticalPIDParams(MacroStep.ActionChangeVerticalPIDParams.Axis(self.axis.value),
                                                                  float(self.KpInput.value()),
                                                                  float(self.KiInput.value()),
                                                                  float(self.KdInput.value()),
                                                                  float(self.ILimInput.value()),
                                                                  float(self.OutLimInput.value()))
        macro_step.actions.append(macro_step_action)
        ActionExecuteScheduler.run_step_sequence([macro_step])

    def move_up_action(self):
        macro_step = MacroStep()
        macro_step_action = MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis(self.axis.value),MacroStep.ActionMoveVertical.Mode.POSITION,
                                                         JRKInterface.get_position(VerticalAxis(self.axis.value))+self.spinBox.value())
        macro_step.actions.append(macro_step_action)
        ActionExecuteScheduler.run_step_sequence([macro_step])


    def move_down_action(self):
        macro_step = MacroStep()
        macro_step_action = MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis(self.axis.value),MacroStep.ActionMoveVertical.Mode.POSITION,
                                                         JRKInterface.get_position(VerticalAxis(self.axis.value))-self.spinBox.value())
        macro_step.actions.append(macro_step_action)
        ActionExecuteScheduler.run_step_sequence([macro_step])

    def set_device_action(self):
        JRKInterface.channels[self.axis.value] = self.DeviceSelectionBtn.itemText(self.DeviceSelectionBtn.currentIndex())
        JRKInterface.connect()

    def __run(self):
        while True:
            # Refreshing device list
            if hash(tuple(JRKInterface.get_devices_list())) != self.__last_device_hash:
                self.DeviceSelectionBtn.clear()
                for serialcode in JRKInterface.get_devices_list():
                    self.DeviceSelectionBtn.addItem(serialcode)
                self.__last_device_hash = hash(tuple(JRKInterface.get_devices_list()))

            if not JRKInterface.is_connected():
                self.MoveUpBtn.setEnabled(False)
                self.MoveDownBtn.setEnabled(False)
            else:
                self.MoveUpBtn.setEnabled(True)
                self.MoveDownBtn.setEnabled(True)
                self.PositionLCD.display(JRKInterface.get_position(VerticalAxis(self.axis.value)))
            QThread.msleep(200)
