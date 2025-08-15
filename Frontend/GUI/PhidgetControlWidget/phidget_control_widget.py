from PyQt6 import uic
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QDoubleSpinBox, QComboBox, QLabel, QLineEdit, QMessageBox
)

from Backend.Interfaces.interface_phidget import PhidgetInterface

class PhidgetControlWidget(QWidget):
    # === Motion Buttons ===
    ConnectBtn: QPushButton
    ZeroBtn: QPushButton


    def __init__(self):
        super(PhidgetControlWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/PhidgetControlWidget/PhidgetWidget.ui', self) # Load the .ui file
        self.ConnectBtn.clicked.connect(self.__connect_btn_pressed)
        self.ZeroBtn.clicked.connect(self.__zero_btn_pressed)

    def __connect_btn_pressed(self):
        try:
            if not PhidgetInterface.get_connected():
                PhidgetInterface.connect()
                self.ConnectBtn.setText("Disconnect")
            else:
                PhidgetInterface.disconnect()
                self.ConnectBtn.setText("Connect")
        except Exception as e:
            MsgBox = QMessageBox()
            MsgBox.setText(str(e))
            MsgBox.exec()

    def __zero_btn_pressed(self):
        PhidgetInterface.zero()