import copy

from PyQt6 import uic
from PyQt6.QtCore import QStringListModel
from PyQt6.QtWidgets import (QWidget, QPushButton, QTabWidget, QColumnView, QLineEdit, QListView, QFileDialog)

from Backend.Schedulers.ActionExecute.macro_step import MacroStep, macro_steps_to_xml, macro_steps_from_xml
from Backend.Schedulers.ActionExecute.scheduler_action_execute import ActionExecuteScheduler
from Backend.Schedulers.DataLogger.scheduler_data_logger import DataLoggerScheduler
from Frontend.GUI.MacroControlWidget.ActionMoveHorizontalWidget.action_move_horizontal_widget import \
    ActionMoveHorizontalWidget
from Frontend.GUI.MacroControlWidget.ActionMoveVerticalWidget.action_move_vertical_widget import ActionMoveVerticalWidget
from Frontend.GUI.MacroControlWidget.ActionSetPIDWidget.action_set_pid_widget import ActionSetPIDWidget
from Frontend.GUI.MacroControlWidget.EndConditionForce.end_force_widget import EndForceWidget
from Frontend.GUI.MacroControlWidget.EndConditionPosition.end_position_widget import EndPositionWidget
from Frontend.GUI.MacroControlWidget.EndTimeWidget.end_time_widget import EndTimeWidget


class TwoColumnFixedView(QColumnView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setResizeGripsVisible(False)

    def createColumn(self, index):
        """Override to prevent adding more than 2 columns"""
        if len(self.findChildren(QListView)) >= 2:
            return None  # Stop adding more columns
        return super().createColumn(index)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.__resize_columns()

    def __resize_columns(self):
        columns = self.findChildren(QListView)
        if len(columns) >= 2:
            total_width = self.viewport().width()
            half_width = total_width // 2
            columns[0].setFixedWidth(half_width)
            columns[1].setFixedWidth(total_width - half_width)

    def updateGeometries(self):
        """Ensure resizing when model changes"""
        super().updateGeometries()
        self.__resize_columns()


class MacroControlWidget(QWidget):
    StepView: QListView
    EndConditionView: QListView
    ActionView: QListView

    MoveDownBtn: QPushButton
    MoveUpBtn: QPushButton

    AddStepBtn: QPushButton
    DeleteBtn: QPushButton

    ActionAddBtn: QPushButton
    ActionDeleteBtn: QPushButton
    ActionSetBtn: QPushButton
    ActionTab: QTabWidget

    EndConditionAddBtn: QPushButton
    EndConditionDeleteBtn: QPushButton
    EndConditionSetBtn: QPushButton
    EndTimeAddBtn: QPushButton
    EndConditionTab: QTabWidget

    ForceStopBtn: QPushButton
    # PauseBtn: QPushButton
    # ResumeBtn: QPushButton
    RunMacroBtn: QPushButton
    SaveDataBtn: QPushButton
    OpenMacroBtn: QPushButton
    SaveMacroBtn: QPushButton

    StepNameLineEdit: QLineEdit

    __step_sequence: list[MacroStep]
    __step_model : QStringListModel
    __action_model : QStringListModel
    __end_condition_model : QStringListModel
    __current_index : list[int]
    __action_widgets : list[ActionMoveVerticalWidget|ActionSetPIDWidget|ActionMoveHorizontalWidget]
    __end_condition_widgets : list[EndForceWidget|EndPositionWidget|EndTimeWidget]

    def __init__(self):
        super(MacroControlWidget, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Frontend/GUI/MacroControlWidget/macrocontrolwidget.ui', self) # Load the .ui file
        self.__step_sequence = []
        self.__step_model = QStringListModel()
        self.__action_model = QStringListModel()
        self.__end_condition_model = QStringListModel()

        self.__step_strings = []
        self.__action_strings = []
        self.__end_condition_strings = []

        self.__current_index = [-1,-1,-1]

        self.StepView.setModel(self.__step_model)
        self.EndConditionView.setModel(self.__end_condition_model)

        self.ActionView.setModel(self.__action_model)

        self.AddStepBtn.clicked.connect(self.__add_step_btn)
        self.DeleteBtn.clicked.connect(self.__step_delete_btn_clicked)
        self.MoveUpBtn.clicked.connect(self.__move_up_btn_clicked)
        self.MoveDownBtn.clicked.connect(self.__move_down_btn_clicked)

        self.RunMacroBtn.clicked.connect(self.__run_macro_btn_clicked)
        self.SaveDataBtn.clicked.connect(self.__save_data_btn_clicked)
        self.ForceStopBtn.clicked.connect(self.__stop_macro_btn_clicked)
        self.OpenMacroBtn.clicked.connect(self.__open_macro_btn_clicked)
        self.SaveMacroBtn.clicked.connect(self.__save_macro_btn_clicked)

        self.ActionAddBtn.clicked.connect(self.__add_action_btn)
        self.ActionDeleteBtn.clicked.connect(self.__action_delete_btn_clicked)
        self.ActionSetBtn.clicked.connect(self.__action_set_btn_clicked)

        self.EndConditionAddBtn.clicked.connect(self.__add_end_condition_btn)
        self.EndConditionDeleteBtn.clicked.connect(self.__end_condition_delete_btn_clicked)
        self.EndConditionSetBtn.clicked.connect(self.__end_condition_set_btn_clicked)

        self.StepView.clicked.connect(self.__step_view_clicked)
        self.ActionView.clicked.connect(self.__action_view_clicked)
        self.EndConditionView.clicked.connect(self.__end_condition_view_clicked)

        self.__action_widgets = []
        self.__action_widgets.append(ActionMoveVerticalWidget())
        self.__action_widgets.append(ActionSetPIDWidget())
        self.__action_widgets.append(ActionMoveHorizontalWidget())

        self.__action_widgets_type = [action_widget.action.__class__.__name__ for action_widget in self.__action_widgets]

        self.__end_condition_widgets = []
        self.__end_condition_widgets.append(EndForceWidget())
        self.__end_condition_widgets.append(EndPositionWidget())
        self.__end_condition_widgets.append(EndTimeWidget())

        self.__end_condition_widgets_type = [end_condition_widget.condition.__class__.__name__ for end_condition_widget in self.__end_condition_widgets]
        self.ActionTab.clear()
        self.EndConditionTab.clear()
        for action_widget in self.__action_widgets:
            self.ActionTab.addTab(action_widget,action_widget.__class__.__name__.replace('Action',''))
        for end_condition_widget in self.__end_condition_widgets:
            self.EndConditionTab.addTab(end_condition_widget,end_condition_widget.__class__.__name__.replace('EndCondition',''))

        DataLoggerScheduler.add_save_end_callback(self.__save_end)

    def __add_step_btn(self):
        step_index = max(self.StepView.currentIndex().row(), -1) +1
        step = MacroStep()
        step.name = self.StepNameLineEdit.text()
        self.__current_index = [step_index, -1, -1]
        self.__step_sequence.insert(step_index, step)
        self.__refresh_ui()

    def __add_end_condition_btn(self):
        end_condition = copy.deepcopy(self.__end_condition_widgets[self.EndConditionTab.currentIndex()].condition)
        if len(self.__step_strings)<=0:
            self.__add_step_btn()
        self.__step_sequence[self.__current_index[0]].end_conditions.append(end_condition)
        self.__current_index[2] += 1
        self.__refresh_ui()

    def __add_action_btn(self):
        action = copy.deepcopy(self.__action_widgets[self.ActionTab.currentIndex()].action)
        if len(self.__step_strings)<=0:
            self.__add_step_btn()
        self.__step_sequence[self.__current_index[0]].actions.append(action)
        self.__current_index[1] += 1
        self.__refresh_ui()

    def __step_view_clicked(self):
        self.__current_index[0] = self.StepView.currentIndex().row()
        if len(self.__step_sequence) > 0:
            self.__current_index[1] = len(self.__step_sequence[self.__current_index[0]].actions) - 1
            self.__current_index[2] = len(self.__step_sequence[self.__current_index[0]].end_conditions) - 1
        else:
            self.__current_index[1] = -1
            self.__current_index[2] = -1
        self.__refresh_ui()

    def __action_view_clicked(self):
        self.__current_index[1] = self.ActionView.currentIndex().row()
        index = self.__action_widgets_type.index(self.__step_sequence[self.__current_index[0]].actions[self.__current_index[1]].__class__.__name__)
        self.ActionTab.setCurrentIndex(index)
        self.__action_widgets[index].load_action(self.__step_sequence[self.__current_index[0]].actions[self.__current_index[1]])

    def __end_condition_view_clicked(self):
        self.__current_index[2] = self.EndConditionView.currentIndex().row()
        index = self.__end_condition_widgets_type.index(self.__step_sequence[self.__current_index[0]].end_conditions[self.__current_index[2]].__class__.__name__)
        self.EndConditionTab.setCurrentIndex(index)
        self.__end_condition_widgets[index].load_condition(self.__step_sequence[self.__current_index[0]].end_conditions[self.__current_index[2]])

    def __refresh_ui(self):
        try:
            self.__step_strings = []

            for step in self.__step_sequence:
                self.__step_strings.append(step.name)
            self.__action_strings = []
            self.__end_condition_strings = []
            if len(self.__step_strings) > self.__current_index[0] >= 0:
                for action in self.__step_sequence[self.__current_index[0]].actions:
                    self.__action_strings.append(action.__class__.__name__.replace('Action', ''))
                for end_condition in self.__step_sequence[self.__current_index[0]].end_conditions:
                    self.__end_condition_strings.append(end_condition.__class__.__name__.replace('EndCondition', ''))

            self.__step_model.setStringList(self.__step_strings)
            self.__action_model.setStringList(self.__action_strings)
            self.__end_condition_model.setStringList(self.__end_condition_strings)

            step_index = self.__step_model.index(self.__current_index[0])
            action_index = self.__action_model.index(self.__current_index[1])
            end_condition_index = self.__end_condition_model.index(self.__current_index[2])

            self.StepView.setCurrentIndex(step_index)
            self.ActionView.setCurrentIndex(action_index)
            self.EndConditionView.setCurrentIndex(end_condition_index)
        except Exception as e:
            print(e)

    def __step_delete_btn_clicked(self):
        if len(self.__step_sequence) > 0:
            self.__current_index[0] = max(self.__current_index[0],0)
            self.__step_sequence.pop(self.__current_index[0])
            self.__current_index[0] -= 1
            self.__current_index[0] = max(self.__current_index[0], 0)
            if self.__current_index[0] > 0:
                self.__current_index[1] = len(self.__step_sequence[self.__current_index[0]].actions) - 1
                self.__current_index[2] = len(self.__step_sequence[self.__current_index[0]].end_conditions) - 1
            self.__refresh_ui()

    def __action_delete_btn_clicked(self):
        if len(self.__step_sequence) > 0 and len(self.__step_sequence[self.__current_index[0]].actions) > self.__current_index[1] >= 0:
            self.__step_sequence[self.__current_index[0]].actions.pop(self.__current_index[1])
            self.__current_index[1] -= 1
        self.__refresh_ui()

    def __end_condition_delete_btn_clicked(self):
        if len(self.__step_sequence) > 0 and len(self.__step_sequence[self.__current_index[0]].end_conditions) > self.__current_index[2] >= 0:
            self.__step_sequence[self.__current_index[0]].end_conditions.pop(self.__current_index[2])
            self.__current_index[2] -= 1
        self.__refresh_ui()

    def __action_set_btn_clicked(self):
        action = copy.deepcopy(self.__action_widgets[self.ActionTab.currentIndex()].action)
        if len(self.__step_sequence) > 0 and len(self.__step_sequence[self.__current_index[0]].actions) > self.__current_index[1] >= 0:
            self.__step_sequence[self.__current_index[0]].actions[self.__current_index[1]] = action
        else:
            self.__add_action_btn()
        self.__refresh_ui()

    def __end_condition_set_btn_clicked(self):
        condition = copy.deepcopy(self.__end_condition_widgets[self.EndConditionTab.currentIndex()].condition)
        if len(self.__step_sequence) > 0 and len(self.__step_sequence[self.__current_index[0]].end_conditions) > self.__current_index[2] >= 0:
            self.__step_sequence[self.__current_index[0]].end_conditions[self.__current_index[2]] = condition
        else:
            self.__add_end_condition_btn()
        self.__refresh_ui()

    def __move_up_btn_clicked(self):
        if len(self.__step_sequence) > 0 and self.__current_index[0] > 0:
            self.__step_sequence[self.__current_index[0]], self.__step_sequence[self.__current_index[0]-1] = (
                self.__step_sequence[self.__current_index[0]-1], self.__step_sequence[self.__current_index[0]])
            self.__current_index[0] -= 1
            self.__refresh_ui()
    def __move_down_btn_clicked(self):
        if len(self.__step_sequence) > 0 and self.__current_index[0] < len(self.__step_sequence) - 1:
            self.__step_sequence[self.__current_index[0]], self.__step_sequence[self.__current_index[0]+1] = (
                self.__step_sequence[self.__current_index[0]+1], self.__step_sequence[self.__current_index[0]])
            self.__current_index[0] += 1
            self.__refresh_ui()

    def __run_macro_btn_clicked(self):
        DataLoggerScheduler.start_recording()
        ActionExecuteScheduler.run_step_sequence(self.__step_sequence)

    @staticmethod
    def __stop_macro_btn_clicked():
        DataLoggerScheduler.stop_recording()
        ActionExecuteScheduler.stop()

    def __save_data_btn_clicked(self):
        filename = QFileDialog.getSaveFileName()
        if len(filename[0]) > 0:
            DataLoggerScheduler.set_file_name(filename[0])
            self.SaveDataBtn.setEnabled(False)
            DataLoggerScheduler.save_data()

    def __save_end(self):
        self.SaveDataBtn.setEnabled(True)

    def __save_macro_btn_clicked(self):
        filename = QFileDialog.getSaveFileName()
        if len(filename[0]) > 0:
            macro_steps_to_xml(self.__step_sequence,filename[0])

    def __open_macro_btn_clicked(self):
        filename = QFileDialog.getOpenFileName()
        if len(filename[0]) > 0:
            self.__step_sequence = macro_steps_from_xml(filename[0])
            self.__refresh_ui()