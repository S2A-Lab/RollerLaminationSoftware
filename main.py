from ui_service import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #
    ui = QtPlotterUI()
    ui.show()

    sys.exit(app.exec_())
    # ui_service = UIService()
