from PyQt6.QtWidgets import QApplication
from fontTools.misc.cython import returns

from Backend.Interfaces.interface_horizontal_stage import HorizontalStageInterface
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    HorizontalStageInterface.init()

    sys.exit(app.exec())