from phidget_interface import PhidgetData
from typing import Callable

import matplotlib

matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams

rcParams.update({'figure.autolayout': True})


class QtPlotterUI(QWidget):

    def __init__(self):
        super().__init__()

        self.__file_save_button = None
        self.__file_name_textfield = None
        self.__unit_label = None
        self.__connect_label = None
        self.__refresh_rate_box = None
        self.__refresh_label = None
        self.__force_plots = None
        self.__connect_button = None
        self.__control_layouts = []
        self.__ui_update_thread = None
        self.init_ui()
        self.ui_update_functions = []

    def init_ui(self):
        self.setWindowTitle('Laminator UI')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        # Initialize title bar
        titlebar_layout = QHBoxLayout()
        self.__refresh_label = QLabel('Refresh Rate')
        self.__refresh_rate_box = QLineEdit('300')
        self.__unit_label = QLabel('ms')
        self.__connect_label = QLabel('Device')

        self.__connect_button = QPushButton('Connect', self)

        titlebar_layout.addWidget(self.__refresh_label)
        titlebar_layout.addWidget(self.__refresh_rate_box)
        titlebar_layout.addWidget(self.__unit_label)
        titlebar_layout.addWidget(self.__connect_label)
        titlebar_layout.addWidget(self.__connect_button)

        # Initialize main layout
        main_layout.addLayout(titlebar_layout)
        self.__control_layouts = [ControlLayout(), ControlLayout()]

        # Initialize main layout
        self.__file_name_textfield = QLineEdit('PhidgetData')
        self.__file_save_button = QPushButton('Save Data')
        save_layout = QHBoxLayout()
        save_layout.addWidget(self.__file_name_textfield)
        save_layout.addWidget(self.__file_save_button)

        main_layout.addLayout(self.__control_layouts[0])
        main_layout.addLayout(self.__control_layouts[1])
        main_layout.addLayout(save_layout)
        self.setLayout(main_layout)

    def set_connect_button_function(self, input_function):
        self.__connect_button.clicked.connect(lambda: input_function(self.__connect_button))

    def set_interval_input_function(self, input_function):
        self.__refresh_rate_box.returnPressed.connect(lambda: input_function(self.__refresh_rate_box))

    def update_plot(self, data_ref0: PhidgetData, data_actual0: PhidgetData, data_ref1: PhidgetData,
                    data_actual1: PhidgetData):
        self.__control_layouts[0].update_plot(data_ref0, data_actual0)
        self.__control_layouts[1].update_plot(data_ref1, data_actual1)


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.line_actual = None
        self.line_ref = None
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.init_plot()

    def init_plot(self):
        self.line_actual, = self.axes.plot([], [], 'b--')
        self.line_ref, = self.axes.plot([], [], 'r-')
        self.axes.set_xlabel('Time [sec]')  # Set x-axis label
        self.axes.set_ylabel('Force [N]')  # Set y-axis label
        self.axes.grid(True, linestyle='--', alpha=0.7)  # Enable grid with dashed lines
        self.fig.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)  # Adjust margins

    def update_data(self, data_ref: PhidgetData, data_actual: PhidgetData):

        if len(data_ref.data) > 0:
            self.line_ref.set_ydata(data_ref.data)
            self.line_ref.set_xdata(data_ref.timestamp)

        if len(data_actual.data) > 0:
            self.line_actual.set_ydata(data_actual.data)
            self.line_actual.set_xdata(data_actual.timestamp)

        self.axes.relim()  # Recalculate limits
        self.axes.autoscale_view(True, True, True)  # Autoscale
        self.draw()


class ControlLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.__set_button = QPushButton('Set')
        self.__kp_textfield = QLineEdit('Kp')
        self.__ki_textfield = QLineEdit('Ki')
        self.__kd_textfield = QLineEdit('Kd')
        self.__plot = PlotCanvas(width=5, height=4)
        self.addWidget(self.__plot)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.__kp_textfield)
        input_layout.addWidget(self.__ki_textfield)
        input_layout.addWidget(self.__kd_textfield)
        input_layout.addWidget(self.__set_button)
        self.addLayout(input_layout)

    def update_plot(self, data_ref: PhidgetData, data_actual: PhidgetData):
        self.__plot.update_data(data_ref, data_actual)

    def set_button_handler(self, input_function: Callable[[str, str, str], None]):
        self.__set_button.clicked.connect(lambda: input_function(self.__kp_textfield.text(),
                                                                 self.__ki_textfield.text(),
                                                                 self.__kd_textfield.text()))
