from PyQt5.QtCore import QThread
from PyQt6.QtWidgets import QApplication
from fontTools.misc.cython import returns

from Backend.Interfaces.interface_horizontal_stage import HorizontalStageInterface
import sys

def run():

    HorizontalStageInterface.connect("COM9",115200)
    i = 0
    while i < 5:
        print(HorizontalStageInterface.get_position())
        QThread.sleep(1)
        i+=1

    HorizontalStageInterface.disconnect()
    QThread.sleep(1)

    i = 0
    HorizontalStageInterface.connect("COM9",115200)
    while i < 5:
        print(HorizontalStageInterface.get_position())
        QThread.sleep(1)
        i+=1

    HorizontalStageInterface.disconnect()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    HorizontalStageInterface.init()
    thread= QThread()
    thread.run = run
    thread.start()

    sys.exit(app.exec())