from PyQt6 import uic
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QDoubleSpinBox, QComboBox, QLabel, QLineEdit
)

from Backend.Interfaces.interface_horizontal_stage import HorizontalStageInterface, get_ports
from Backend.Interfaces.interface_jrk import JRKInterface
from Backend.Interfaces.interface_phidget import PhidgetInterface
from Backend.Schedulers.ActionExecute.macro_step import MacroStep
from Backend.Schedulers.ActionExecute.scheduler_action_execute import ActionExecuteScheduler


class HorizontalLinearStageWidget(QWidget):
    # === Motion Buttons ===
    YLeftMoveBtn: QPushButton
    YRightMoveBtn: QPushButton
    YStopBtn: QPushButton

    # === Parameter Inputs ===
    AccelSpinBox: QDoubleSpinBox
    SpeedSpinBox: QDoubleSpinBox
    PosStepSpinBox: QDoubleSpinBox

    # === Device Controls ===
    DeviceComboBox: QComboBox
    DeviceSetBtn: QPushButton

    # === Labels ===
    foo_label_1: QLabel
    foo_label_2: QLabel
    foo_label_3: QLabel
    foo_label_4: QLabel

    __thread : QThread
    __ports_name_hash : tuple


    def __init__(self):
        super(HorizontalLinearStageWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/HorizontalLinearStagetWidget/horizontallinearstagewidget.ui', self) # Load the .ui file
        self.__thread = QThread()
        self.__thread.run = self.__run
        self.__ports_name_hash = ()
        self.DeviceSetBtn.clicked.connect(self.__connect_btn_pressed)
        self.YLeftMoveBtn.clicked.connect(self.__left_btn_pressed)
        self.YRightMoveBtn.clicked.connect(self.__right_btn_pressed)
        self.YStopBtn.clicked.connect(self.__stop_btn_pressed)
        self.YLeftMoveBtn.setEnabled(False)
        self.YRightMoveBtn.setEnabled(False)
        self.YStopBtn.setEnabled(False)
        self.__thread.start()

    def __run(self):
        while True:
            try:
                ports = get_ports()
                descriptions = tuple(port.description() for port in ports)
                if descriptions!=self.__ports_name_hash:
                    # Update combobox
                    self.DeviceComboBox.clear()
                    self.DeviceComboBox.addItems(descriptions)
                self.__ports_name_hash = descriptions

                if HorizontalStageInterface.get_connected():
                    self.YLeftMoveBtn.setEnabled(True)
                    self.YRightMoveBtn.setEnabled(True)
                    self.YStopBtn.setEnabled(True)
                else:
                    self.YLeftMoveBtn.setEnabled(False)
                    self.YRightMoveBtn.setEnabled(False)
                    self.YStopBtn.setEnabled(False)
            except Exception as e:
                print(e)
            QThread.msleep(200)

    def __connect_btn_pressed(self):
        print(self.DeviceComboBox.currentIndex())
        if self.DeviceComboBox.currentIndex() < 0:
            print("Device not set")
            return
        try:
            if not JRKInterface.is_connected() or not HorizontalStageInterface.get_connected() or not PhidgetInterface.get_connected():
                HorizontalStageInterface.connect(get_ports()[self.DeviceComboBox.currentIndex()].portName(), 115200)
                self.DeviceSetBtn.setText("Disconnect")
            else:
                HorizontalStageInterface.disconnect()
                self.DeviceSetBtn.setText("Connect")
        except Exception as e:
            print(e)

    def __left_btn_pressed(self):
        step = MacroStep()
        action = MacroStep.ActionMoveHorizontal(HorizontalStageInterface.get_position()-self.PosStepSpinBox.value(), self.SpeedSpinBox.value(), self.AccelSpinBox.value())
        step.actions.append(action)
        ActionExecuteScheduler.run_step_sequence([step])

    def __right_btn_pressed(self):
        step = MacroStep()
        action = MacroStep.ActionMoveHorizontal(HorizontalStageInterface.get_position()+self.PosStepSpinBox.value(), self.SpeedSpinBox.value(), self.AccelSpinBox.value())
        step.actions.append(action)
        ActionExecuteScheduler.run_step_sequence([step])

    def __stop_btn_pressed(self):
        step = MacroStep()
        action = MacroStep.ActionMoveHorizontal(HorizontalStageInterface.get_position(), self.SpeedSpinBox.value(), self.AccelSpinBox.value())
        step.actions.append(action)
        ActionExecuteScheduler.run_step_sequence([step])