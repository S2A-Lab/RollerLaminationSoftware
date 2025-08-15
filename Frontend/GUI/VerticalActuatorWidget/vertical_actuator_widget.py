from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QComboBox, QLabel, QSpinBox,
    QDoubleSpinBox, QLCDNumber, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal
import copy
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
    StepSizeSpinBox: QSpinBox

    SetPIDBtn: QPushButton
    ILimInput: QDoubleSpinBox
    KdInput: QDoubleSpinBox
    KiInput: QDoubleSpinBox
    KpInput: QDoubleSpinBox
    OutLimInput: QDoubleSpinBox
    TargetForceSpinBox: QDoubleSpinBox

    foo_labelilim: QLabel
    foo_labelkd: QLabel
    foo_labelki: QLabel
    foo_labelkp: QLabel
    foo_labeloutlim: QLabel

    axis: VerticalAxis

    __last_device_hash: tuple = ()
    __thread: QThread
    __channels = ["",""]
    __target_forces = [0.0, 0.0]
    __target_positions = [0.0, 0.0]

    def __init__(self, axis: VerticalAxis):
        super(VerticalActuatorWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/VerticalActuatorWidget/verticalactuatorwidget.ui', self) # Load the .ui file
        self.axis = axis

        self.SetPIDBtn.clicked.connect(self.__pid_set_btn_pressed)
        self.MoveUpBtn.clicked.connect(self.__move_up_btn_pressed)
        self.MoveDownBtn.clicked.connect(self.__move_down_btn_pressed)
        self.DeviceSetBtn.clicked.connect(self.__set_device_btn_pressed)

        self.MoveUpBtn.setEnabled(False)
        self.MoveDownBtn.setEnabled(False)
        self.StartForceBtn.setEnabled(False)
        self.__thread = QThread()
        self.__thread.run = self.__run
        self.__thread.start()
        self.__last_device_hash = 0
        self.TargetForceSpinBox.valueChanged.connect(self.__target_force_changed)
        self.StartForceBtn.clicked.connect(self.__start_force_control_btn_pressed)
        self.DeviceSelectionBtn.currentIndexChanged.connect(self.__device_selection_btn_changed)

    def __pid_set_btn_pressed(self):
        macro_step = MacroStep()
        macro_step_action = MacroStep.ActionChangeVerticalPIDParams(MacroStep.ActionChangeVerticalPIDParams.Axis(self.axis.value),
                                                                  float(self.KpInput.value()),
                                                                  float(self.KiInput.value()),
                                                                  float(self.KdInput.value()),
                                                                  float(self.ILimInput.value()),
                                                                  float(self.OutLimInput.value()))
        macro_step.actions.append(macro_step_action)
        ActionExecuteScheduler.run_step_sequence([macro_step])

    def __move_up_btn_pressed(self):
        macro_step = MacroStep()
        macro_step_action = MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis(self.axis.value),
                                                         MacroStep.ActionMoveVertical.Mode.POSITION,
                                                         JRKInterface.get_position(VerticalAxis(self.axis.value))
                                                           + self.StepSizeSpinBox.value())
        macro_step.actions.append(macro_step_action)
        ActionExecuteScheduler.run_step_sequence([macro_step])
        VerticalActuatorWidget.__target_positions[self.axis.value] = (
                JRKInterface.get_position(VerticalAxis(self.axis.value)) + self.StepSizeSpinBox.value())


    def __move_down_btn_pressed(self):
        macro_step = MacroStep()
        macro_step_action = MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis(self.axis.value),
                                                         MacroStep.ActionMoveVertical.Mode.POSITION,
                                                         JRKInterface.get_position(VerticalAxis(self.axis.value))
                                                           - self.StepSizeSpinBox.value())
        macro_step.actions.append(macro_step_action)
        ActionExecuteScheduler.run_step_sequence([macro_step])
        VerticalActuatorWidget.__target_positions[self.axis.value] = (
                JRKInterface.get_position(VerticalAxis(self.axis.value)) - self.StepSizeSpinBox.value())

    def __set_device_btn_pressed(self):
        if self.__channels[0] != self.__channels[1] and self.__channels[0] != "" and self.__channels[1]!="":
            JRKInterface.channels = copy.deepcopy(self.__channels)
            JRKInterface.connect()
        else:
            msg_box_name = QMessageBox()
            msg_box_name.setText("Please check your connection! The JRK serial number should not be the same.")
            msg_box_name.exec()

    def __device_selection_btn_changed(self):
        VerticalActuatorWidget.__channels[self.axis.value] = self.DeviceSelectionBtn.itemText(self.DeviceSelectionBtn.currentIndex())

    def __target_force_changed(self):
        VerticalActuatorWidget.__target_forces[self.axis.value] = self.TargetForceSpinBox.value()
        print(VerticalActuatorWidget.__target_forces)

    def __start_force_control_btn_pressed(self):
        macro_step = MacroStep()
        if ActionExecuteScheduler.get_vertical_modes()[self.axis.value] == MacroStep.ActionMoveVertical.Mode.FORCE:
            macro_step_action0 = MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis(VerticalAxis.AXIS_0), MacroStep.ActionMoveVertical.Mode.POSITION,
                                                              VerticalActuatorWidget.__target_positions[0])
            macro_step_action1 = MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis(VerticalAxis.AXIS_1), MacroStep.ActionMoveVertical.Mode.POSITION,
                                                              VerticalActuatorWidget.__target_positions[1])
            self.StartForceBtn.setText("Start Force Control")
        else:
            macro_step_action0 = MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis(VerticalAxis.AXIS_0), MacroStep.ActionMoveVertical.Mode.FORCE,
                                                             VerticalActuatorWidget.__target_forces[0])
            macro_step_action1 = MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis(VerticalAxis.AXIS_1), MacroStep.ActionMoveVertical.Mode.FORCE,
                                                             VerticalActuatorWidget.__target_forces[1])
            self.StartForceBtn.setText("Stop Force Control")
        macro_step.actions.append(macro_step_action0)
        macro_step.actions.append(macro_step_action1)
        ActionExecuteScheduler.run_step_sequence([macro_step])

    def __run(self):
        while True:
            # Refreshing device list
            if tuple(JRKInterface.get_devices_list()) != self.__last_device_hash:
                self.DeviceSelectionBtn.clear()
                for serialcode in JRKInterface.get_devices_list():
                    self.DeviceSelectionBtn.addItem(serialcode)
                self.__last_device_hash = tuple(JRKInterface.get_devices_list())

            if not JRKInterface.is_connected():
                self.MoveUpBtn.setEnabled(False)
                self.MoveDownBtn.setEnabled(False)

            else:
                self.MoveUpBtn.setEnabled(True)
                self.MoveDownBtn.setEnabled(True)
                self.PositionLCD.display(JRKInterface.get_position(VerticalAxis(self.axis.value)))
            QThread.msleep(100)
