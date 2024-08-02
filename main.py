from PyQt5.QtWidgets import QApplication
from main_service import *
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)

    with open("assets/stylesheet.qss", "r") as stylesheet:
        app.setStyleSheet(stylesheet.read())
    window = MainService()
    window.show()

    sys.exit(app.exec_())