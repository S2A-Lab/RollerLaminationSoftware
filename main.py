import math
import sys
import random
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(10)  # Update every 100 milliseconds (10 Hz)
        self.xx=0

    def initUI(self):
        self.setWindowTitle('GUI Example')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        # Create the plot areas
        plot_layout = QHBoxLayout()

        self.plot1 = PlotCanvas(self, width=5, height=4)
        plot_layout.addWidget(self.plot1)

        self.plot2 = PlotCanvas(self, width=5, height=4)
        plot_layout.addWidget(self.plot2)

        main_layout.addLayout(plot_layout)

        # Create the control areas
        control_layout = QHBoxLayout()

        control_layout.addLayout(self.create_controls())
        control_layout.addLayout(self.create_controls())

        main_layout.addLayout(control_layout)

        self.setLayout(main_layout)

    def create_controls(self):
        control_layout = QVBoxLayout()

        param_layout = QHBoxLayout()

        kp_label = QLabel('Kp')
        kp_entry = QLineEdit()

        ki_label = QLabel('Ki')
        ki_entry = QLineEdit()

        kd_label = QLabel('Kd')
        kd_entry = QLineEdit()

        param_layout.addWidget(kp_label)
        param_layout.addWidget(kp_entry)
        param_layout.addWidget(ki_label)
        param_layout.addWidget(ki_entry)
        param_layout.addWidget(kd_label)
        param_layout.addWidget(kd_entry)

        control_layout.addLayout(param_layout)

        set_button = QPushButton('Set Button')
        control_layout.addWidget(set_button)

        return control_layout

    def update_plot(self):
        self.xx = self.xx+1
        new_data = [math.sin((i+self.xx)*0.01) for i in range(1000)]
        self.plot1.update_data(new_data)
        self.plot2.update_data(new_data)

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.init_plot()

    def init_plot(self):
        self.data = [random.random() for _ in range(10)]
        self.line, = self.axes.plot(self.data, 'r-', linewidth=2, marker='o', markersize=6, markerfacecolor='blue')
        self.axes.set_xlabel('Time [sec]', fontsize=12, fontweight='bold')  # Set x-axis label
        self.axes.set_ylabel('Force [N]', fontsize=12, fontweight='bold')  # Set y-axis label
        self.axes.set_title('Real-Time Plot', fontsize=14, fontweight='bold')  # Set title
        self.axes.grid(True, linestyle='--', alpha=0.7)  # Enable grid with dashed lines

        # Fetch the parent widget's background color and set it to the plot background
        parent_background_color = self.parent().palette().color(self.parent().backgroundRole()).name()
        self.axes.set_facecolor(parent_background_color)  # Set plot background color to parent background color
        self.figure.patch.set_facecolor(parent_background_color)  # Set the figure patch (background) to parent background color

    def update_data(self, new_data):
        self.line.set_ydata(new_data)
        self.line.set_xdata(np.arange(len(new_data)))
        self.axes.relim()  # Recalculate limits
        self.axes.autoscale_view(True, True, True)  # Autoscale
        self.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())
