from PyQt5.QtWidgets import QApplication
from main_service import *
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = UIService()
    window.show()

    sys.exit(app.exec_())