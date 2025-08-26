from PyQt6 import uic
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QDoubleSpinBox, QComboBox, QLabel, QLineEdit, QMessageBox, QFileDialog
)

from Backend.Interfaces.interface_phidget import PhidgetInterface
from Backend.Schedulers.DataLogger.scheduler_data_logger import DataLoggerScheduler


class PhidgetControlWidget(QWidget):
    # === Motion Buttons ===
    ConnectBtn: QPushButton
    ZeroBtn: QPushButton
    StopRecordBtn: QPushButton
    StartRecordBtn: QPushButton


    def __init__(self):
        super(PhidgetControlWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/PhidgetControlWidget/PhidgetWidget.ui', self) # Load the .ui file
        self.ConnectBtn.clicked.connect(self.__connect_btn_pressed)
        self.ZeroBtn.clicked.connect(self.__zero_btn_pressed)
        self.StartRecordBtn.clicked.connect(self.__start_btn_pressed)
        self.StopRecordBtn.clicked.connect(self.__stop_btn_pressed)
        DataLoggerScheduler.add_save_end_callback(self.__save_end)

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

    def __start_btn_pressed(self):
        DataLoggerScheduler.clear_data()
        DataLoggerScheduler.start_recording()

    def __stop_btn_pressed(self):
        filename = QFileDialog.getSaveFileName()
        if len(filename[0]) > 0:
            DataLoggerScheduler.set_file_name(filename[0])
            self.StopRecordBtn.setEnabled(False)
            DataLoggerScheduler.save_data()

    def __save_end(self):
        self.StopRecordBtn.setEnabled(True)