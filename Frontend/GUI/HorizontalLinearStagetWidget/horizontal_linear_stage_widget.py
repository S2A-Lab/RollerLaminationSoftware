from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QDoubleSpinBox, QComboBox, QLabel, QLineEdit
)

class HorizontalLinearStageWidget(QWidget):
    # === Motion Buttons ===
    YLeftMoveBtn: QPushButton
    YRightMoveBtn: QPushButton
    YStopBtn: QPushButton

    # === Parameter Inputs ===
    YAxisParamSetBtn: QPushButton
    AccelSpinBox: QDoubleSpinBox
    SpeedSpinBox: QDoubleSpinBox
    PositionStep: QLineEdit

    # === Device Controls ===
    DeviceComboBox: QComboBox
    DeviceSetBtn: QPushButton

    # === Labels ===
    foo_label_1: QLabel
    foo_label_2: QLabel
    foo_label_3: QLabel
    foo_label_4: QLabel

    def __init__(self):
        super(HorizontalLinearStageWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/HorizontalLinearStagetWidget/horizontallinearstagewidget.ui', self) # Load the .ui file