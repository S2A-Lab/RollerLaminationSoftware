from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from Backend.DataLogger.datastruct_timeseries import Timeseries

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
        self.line_actual, = self.axes.plot([], [], 'r-')
        self.line_ref, = self.axes.plot([], [], 'b--')
        self.axes.set_xlabel('Time [sec]')  # Set x-axis label
        self.axes.set_ylabel('Force [N]')  # Set y-axis label
        self.axes.grid(True, linestyle='--', alpha=0.7)  # Enable grid with dashed lines
        self.fig.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)  # Adjust margins

    def update_data(self, data_ref: Timeseries, data_actual: Timeseries):
        if len(data_ref.data) > 0:
            self.line_ref.set_ydata(data_ref.data)
            self.line_ref.set_xdata(data_ref.timestamp)

        if len(data_actual.data) > 0:
            self.line_actual.set_ydata(data_actual.data)
            self.line_actual.set_xdata(data_actual.timestamp)

        self.axes.relim()  # Recalculate limits
        self.axes.autoscale_view(True, True, False)  # Autoscale
        self.draw()

    def update_y_limits(self, lb, up):
        self.axes.set_ylim(lb, up)