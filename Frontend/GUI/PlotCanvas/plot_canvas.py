import bisect

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from Backend.Schedulers.DataLogger.datastruct_timeseries import Timeseries

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.line_actual = None
        self.line_ref = None
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.init_plot()
        self.maximum_time = 30.0 # [sec]
        self.auto_x = True
        self.maximum_plot_time = 10

    def init_plot(self):
        self.line_actual, = self.axes.plot([], [], 'r-')
        self.line_ref, = self.axes.plot([], [], 'b--')
        # self.axes.set_xlabel('Time [sec]')  # Set x-axis label
        # self.axes.set_ylabel('')  # Set y-axis label
        self.axes.grid(True, linestyle='--', alpha=0.7)  # Enable grid with dashed lines
        self.fig.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)  # Adjust margins

    def update_data(self, data_ref: Timeseries, data_actual: Timeseries):

        def update_line(line, data, plot_time_length, auto_x):
            if len(data.data) == 0:
                return

            if auto_x:
                line.set_ydata(data.data)
                line.set_xdata(data.timestamp)
            else:
                index = bisect.bisect_right(data.timestamp, data.timestamp[-1] - plot_time_length)
                line.set_ydata(data.data[index:])
                line.set_xdata(data.timestamp[index:])

        update_line(self.line_ref, data_ref, self.maximum_plot_time * 1000.0, self.auto_x)
        update_line(self.line_actual, data_actual,  self.maximum_plot_time * 1000.0, self.auto_x)

        self.axes.relim()  # Recalculate limits
        self.axes.autoscale_view(True, True, True)  # Autoscale
        self.draw()

    def update_y_limits(self, lb, up):
        self.axes.set_ylim(lb, up)

    def set_auto_x(self, auto_x: bool):
        self.auto_x = auto_x

    def set_maximum_plot_time(self, time):
        self.maximum_plot_time = time