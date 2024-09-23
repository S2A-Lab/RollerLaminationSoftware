from PyQt5.QtGui import QIcon

from datastruct.datastruct_timeseries import *
from typing import Callable
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Qt5Agg')
rcParams.update({'figure.autolayout': True})


class ControlLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.__set_button = QPushButton('Set')
        self.__kp_textfield = QLineEdit()
        self.__ki_textfield = QLineEdit()
        self.__kd_textfield = QLineEdit()
        self.__i_limit_textfield = QLineEdit()
        self.__target_force_textfield = QLineEdit()
        self.__jog_step_textfield = QLineEdit()
        self.__jog_position_label = QLabel()


        self.__kp_textfield.setPlaceholderText('Kp')
        self.__ki_textfield.setPlaceholderText('Ki')
        self.__kd_textfield.setPlaceholderText('Kd')
        self.__i_limit_textfield.setPlaceholderText('i_limit')
        self.__target_force_textfield.setPlaceholderText('Target Force')
        self.__set_target_force_button = QPushButton('Set Target Force')

        self.__jog_up_button = QPushButton()
        self.__jog_down_button = QPushButton()

        self.__jog_all_up_button = QPushButton()
        self.__jog_all_down_button = QPushButton()
        self.__jog_step_textfield.setPlaceholderText('Jog Step')
        self.__jog_up_button.setIcon(QIcon('interfaces/ui_interface/assets/icons/icon_up.svg'))
        self.__jog_down_button.setIcon(QIcon('interfaces/ui_interface/assets/icons/icon_down.svg'))
        self.__jog_all_up_button.setIcon(QIcon('interfaces/ui_interface/assets/icons/icon_all_up.svg'))
        self.__jog_all_down_button.setIcon(QIcon('interfaces/ui_interface/assets/icons/icon_all_down.svg'))

        self.__plot = PlotCanvas(width=5, height=4)
        self.addWidget(self.__plot)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.__kp_textfield)
        input_layout.addWidget(self.__ki_textfield)
        input_layout.addWidget(self.__kd_textfield)
        input_layout.addWidget(self.__i_limit_textfield)
        input_layout.addWidget(self.__set_button)
        self.addLayout(input_layout)
        target_force_layout = QHBoxLayout()
        target_force_layout.addWidget(self.__target_force_textfield)
        target_force_layout.addWidget(self.__set_target_force_button)
        self.addLayout(target_force_layout)
        jog_layout = QHBoxLayout()
        jog_layout.addWidget(self.__jog_position_label)
        jog_layout.addWidget(self.__jog_step_textfield)
        jog_layout.addWidget(self.__jog_up_button)
        jog_layout.addWidget(self.__jog_down_button)
        jog_layout.addWidget(self.__jog_all_up_button)
        jog_layout.addWidget(self.__jog_all_down_button)
        self.addLayout(jog_layout)


    def update_plot(self, data_ref: Timeseries, data_actual: Timeseries):
        self.__plot.update_data(data_ref, data_actual)

    def set_params_button_clicked_handler(self, input_function: Callable[[str, str, str, str], None]):
        self.__set_button.clicked.connect(lambda: input_function(self.__kp_textfield.text(),
                                                                 self.__ki_textfield.text(),
                                                                 self.__kd_textfield.text(),
                                                                 self.__i_limit_textfield.text()))

    def set_target_force_button_clicked_handler(self, input_function: Callable[[str], None]):
        self.__set_target_force_button.clicked.connect(lambda: input_function(self.__target_force_textfield.text()))

    def get_target_force(self):
        return self.__target_force_textfield.text()

    def get_jog_step(self):
        return self.__jog_step_textfield.text()

    def set_up_button_clicked_handler(self, input_function: Callable[[str], None]):
        self.__jog_up_button.clicked.connect(lambda: input_function(self.__jog_step_textfield.text()))

    def set_down_button_clicked_handler(self, input_function: Callable[[str], None]):
        self.__jog_down_button.clicked.connect(lambda: input_function(self.__jog_step_textfield.text()))

    def set_all_up_button_clicked_handler(self, input_function: Callable[[str], None]):
        self.__jog_all_up_button.clicked.connect(lambda: input_function(self.__jog_step_textfield.text()))

    def set_all_down_button_clicked_handler(self, input_function: Callable[[str], None]):
        self.__jog_all_down_button.clicked.connect(lambda: input_function(self.__jog_step_textfield.text()))

    def update_position(self, position: int):
        self.__jog_position_label.setText(str(position))


class UIInterface(QWidget):

    def __init__(self):
        super().__init__()

        self.device_combobox: QComboBox = QComboBox()
        self.__file_clear_button: QPushButton = QPushButton('Clear')
        self.__file_save_button: QPushButton = QPushButton('Save Data')
        self.__file_name_textfield: QLineEdit = QLineEdit('PhidgetData')
        self.__unit_label: QLabel = QLabel('ms')
        self.__connect_label: QLabel = QLabel('Device')
        self.__refresh_rate_box: QLineEdit = QLineEdit('300')
        self.__refresh_label: QLabel = QLabel('Refresh Rate')
        self.__connect_button: QPushButton = QPushButton('Connect', self)
        self.__control_layouts = []

        self.__start_force_control_button = QPushButton('Start Force Control')
        self.__tare_button = QPushButton('Tare')

        self.__horizontal_stage_speed_textfield: QLineEdit = QLineEdit('')
        self.__horizontal_stage_speed_set_button: QPushButton = QPushButton('Set')

        self.__file_name_textfield.setPlaceholderText('Save file name')
        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        # Initialize titlebar
        titlebar_layout = QHBoxLayout()

        titlebar_layout.addWidget(self.__refresh_label)
        titlebar_layout.addWidget(self.__refresh_rate_box)
        titlebar_layout.addWidget(self.__unit_label)
        titlebar_layout.addWidget(self.__connect_label)
        titlebar_layout.addWidget(self.device_combobox)
        titlebar_layout.addWidget(self.__connect_button)

        # Initialize main layout
        self.__control_layouts = [ControlLayout(), ControlLayout()]

        main_layout.addLayout(titlebar_layout)
        main_layout.addLayout(self.__control_layouts[0])
        main_layout.addLayout(self.__control_layouts[1])

        miscellaneous_layout = QHBoxLayout()
        miscellaneous_layout.addWidget(self.__start_force_control_button)
        miscellaneous_layout.addWidget(self.__tare_button)
        main_layout.addLayout(miscellaneous_layout)

        horizontal_stage_layout = QHBoxLayout()
        horizontal_stage_layout.addWidget(self.__horizontal_stage_speed_textfield)
        horizontal_stage_layout.addWidget(self.__horizontal_stage_speed_set_button)
        self.__horizontal_stage_speed_textfield.setPlaceholderText("Linear stage speed")
        main_layout.addLayout(horizontal_stage_layout)

        # Initialize save layout
        save_layout = QHBoxLayout()
        save_layout.addWidget(self.__file_name_textfield)
        save_layout.addWidget(self.__file_clear_button)
        save_layout.addWidget(self.__file_save_button)

        main_layout.addLayout(save_layout)
        self.setLayout(main_layout)

    def set_connect_button_clicked_handler(self, input_function):
        self.__connect_button.clicked.connect(lambda: input_function(self.__connect_button))

    def set_interval_textfield_change_handler(self, input_function):
        self.__refresh_rate_box.returnPressed.connect(lambda: input_function(self.__refresh_rate_box))

    def set_save_button_clicked_handler(self, input_function):
        self.__file_save_button.clicked.connect(lambda: input_function(self.__file_save_button,
                                                                       self.__file_name_textfield))

    def set_clear_button_clicked_handler(self, input_function):
        self.__file_clear_button.clicked.connect(lambda: input_function(self.__file_clear_button))

    def set_start_force_control_button_clicked_handler(self, input_function):
        self.__start_force_control_button.clicked.connect(lambda: input_function(self.__start_force_control_button))

    def set_tare_button_clicked_handler(self, input_function):
        self.__tare_button.clicked.connect(lambda: input_function(self.__tare_button))

    def set_horizontal_stage_speed_set_button_clicked_handler(self, input_function):
        self.__horizontal_stage_speed_set_button.clicked.connect(lambda: input_function(self.__horizontal_stage_speed_set_button,
                                                                                        self.__horizontal_stage_speed_textfield))

    def update_plot(self, data_ref0: Timeseries, data_actual0: Timeseries, data_ref1: Timeseries,
                    data_actual1: Timeseries):
        self.__control_layouts[0].update_plot(data_ref0, data_actual0)
        self.__control_layouts[1].update_plot(data_ref1, data_actual1)

    def update_positions(self, position0: int, position1: int):
        self.__control_layouts[0].update_position(position0)
        self.__control_layouts[1].update_position(position1)

    def get_control_layouts(self, index: int) -> ControlLayout:
        return self.__control_layouts[index]

    def get_target_positions_str(self) -> [str, str]:
        return [self.__control_layouts[0].get_target_force(), self.__control_layouts[1].get_target_force()]

    def get_jog_steps_str(self) -> [str, str]:
        return [self.__control_layouts[0].get_jog_step(), self.__control_layouts[1].get_jog_step()]


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
        self.axes.autoscale_view(True, True, True)  # Autoscale
        self.draw()

