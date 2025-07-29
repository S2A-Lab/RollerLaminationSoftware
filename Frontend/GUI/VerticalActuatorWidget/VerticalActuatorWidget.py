from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QComboBox, QLabel, QSpinBox,
    QDoubleSpinBox, QLCDNumber
)

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
    KIInput: QDoubleSpinBox
    KpInput: QDoubleSpinBox
    OutLimInput: QDoubleSpinBox

    foo_labelilim: QLabel
    foo_labelkd: QLabel
    foo_labelki: QLabel
    foo_labelkp: QLabel
    foo_labeloutlim: QLabel

    def __init__(self):
        super(VerticalActuatorWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/VerticalActuatorWidget/verticalactuatorwidget.ui', self) # Load the .ui file