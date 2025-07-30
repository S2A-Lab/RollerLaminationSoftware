from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication

from Backend.Schedulers.ActionExecute.scheduler_action_execute import ActionExecuteScheduler
from Backend.Schedulers.ActionExecute.macro_step import MacroStep

import sys

class www(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
    MacroExec: ActionExecuteScheduler

if __name__ == '__main__':
    app = QApplication(sys.argv)

    macro_step0 = MacroStep()
    macro_step0.actions.append(
        MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis.X0, MacroStep.ActionMoveVertical.Mode.FORCE,
                                     10.0))
    macro_step0.actions.append(
        MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis.X1, MacroStep.ActionMoveVertical.Mode.FORCE,
                                     10.0))

    macro_step0.actions.append(MacroStep.ActionMoveHorizontal(10, 20, 0.5))
    macro_step0.end_conditions.append(MacroStep.EndConditionTime(2000))

    macro_step1 = MacroStep()
    macro_step1.actions.append(
        MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis.X0, MacroStep.ActionMoveVertical.Mode.FORCE,
                                     10.0))
    macro_step1.actions.append(
        MacroStep.ActionMoveVertical(MacroStep.ActionMoveVertical.Axis.X1, MacroStep.ActionMoveVertical.Mode.FORCE,
                                     10.0))

    macro_step1.actions.append(MacroStep.ActionMoveHorizontal(10, 20, 0.5))
    macro_step1.end_conditions.append(MacroStep.EndConditionTime(4000))


    ActionExecuteScheduler.init()
    ActionExecuteScheduler.run_step_sequence([macro_step0, macro_step1])

    window = www()

    # window.XPositionDisp.display(999)

    # with open("Interfaces/ui_interface/assets/icons/stylesheet.qss", "r") as stylesheet:
    #     app.setStyleSheet(stylesheet.read())
    # window = MainService()
    window.show()
    # while step_exec_controller.get_execute_state() != ActuatorsControllerState.END:
    #     # print("Executing step 0...\n")
    #     # print(f"{step_exec_controller.get_execute_state().name}")
    #     pass

    # app.setStyle(QStyleFactory.create("Fusion"))

    sys.exit(app.exec())



