import math
import sys
import random
import numpy as np
import matplotlib

matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.line = None
        self.data = None
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.init_plot()

    def init_plot(self):
        self.data = []
        self.line, = self.axes.plot(self.data, 'r-')
        self.axes.set_xlabel('Time [sec]')  # Set x-axis label
        self.axes.set_ylabel('Force [N]')  # Set y-axis label
        # self.axes.set_title('Real-Time Plot', fontsize=14, fontweight='bold')  # Set title
        self.axes.grid(True, linestyle='--', alpha=0.7)  # Enable grid with dashed lines

    def update_data(self, phidget_data):
        self.line.set_ydata(phidget_data.data)
        self.line.set_xdata(phidget_data.timestamp)
        self.axes.relim()  # Recalculate limits
        self.axes.autoscale_view(True, True, True)  # Autoscale
        self.draw()


class QtPlotterUI(QWidget):

    def __init__(self):
        super().__init__()

        self.__force_plots = None
        self.__connect_button = None

        self.init_ui()

    def init_ui(self):

        self.setWindowTitle('Laminator UI')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        titlebar_layout = QHBoxLayout()
        self.__connect_button = QPushButton('Connect', self)

        titlebar_layout.addWidget(self.__connect_button)

        main_layout.addLayout(titlebar_layout)

        # Create the plot areas
        plot_layout = QHBoxLayout()

        self.__force_plots = [PlotCanvas(width=5, height=4), PlotCanvas(width=5, height=4)]

        plot_layout.addWidget(self.__force_plots[0])
        plot_layout.addWidget(self.__force_plots[1])

        main_layout.addLayout(plot_layout)

        # Create the control areas
        control_layout = QHBoxLayout()

        main_layout.addLayout(control_layout)

        self.setLayout(main_layout)

    def update_plot(self, input_1, input_2):

        self.__force_plots[0].update_data(input_1)
        self.__force_plots[1].update_data(input_2)

    def set_connect_button_function(self, input_function):
        self.__connect_button.clicked.connect(lambda: self.connect_button_handler(input_function))

    def connect_button_handler(self, input_function):
        input_function()
        if self.__connect_button.text() == 'Connect':
            self.__connect_button.setText('Disconnect')
        else:
            self.__connect_button.setText('Connect')
