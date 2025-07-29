from PyQt6.QtWidgets import QApplication, QStyleFactory
from Frontend.MainWindow.MainWindow import MainWindow

from Frontend.VerticalActuatorWidget.VerticalActuatorWidget import VerticalActuatorWidget
from Frontend.MacroControlWidget.MacroControlWidget import MacroControlWidget
from Frontend.HorizontalLinearStagetWidget.HorizontalLinearStageWidget import HorizontalLinearStageWidget

import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)

    horizontal_widget = HorizontalLinearStageWidget()
    vertical_widget0 = VerticalActuatorWidget()
    vertical_widget1 = VerticalActuatorWidget()
    macro_widget = MacroControlWidget()
    window = MainWindow((vertical_widget0, vertical_widget1),horizontal_widget, macro_widget)

    window.XPositionDisp.display(999)

    # with open("Interfaces/ui_interface/assets/icons/stylesheet.qss", "r") as stylesheet:
    #     app.setStyleSheet(stylesheet.read())
    # window = MainService()
    window.show()
    app.setStyle(QStyleFactory.create("Fusion"))
    sys.exit(app.exec())