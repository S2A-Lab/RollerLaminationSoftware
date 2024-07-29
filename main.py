from phidget_interface import *
from qt_plotter import *

if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = QtPlotterUI()
    pif = PhidgetInterface()

    ex.set_connect_button_function(pif.connect_button_handler)
    ex.show()

    sys.exit(app.exec_())
