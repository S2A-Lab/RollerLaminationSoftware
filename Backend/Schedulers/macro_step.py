from enum import Enum

class MacroStep:

    def __init__(self):
        self.actions = []
        self.end_conditions = []

    class ActionChangeVerticalPIDParams:
        class Axis(Enum):
            X0 = 0
            X1 = 1
            ALL= 2

        axis:      Axis
        kp:        float
        ki:        float
        kd:        float
        i_limit:   float
        out_limit: float

        def __init__(self, axis: Axis, kp: float, ki: float, kd: float, i_limit: float, out_limit: float):
            self.axis = axis
            self.kp: float = kp
            self.ki: float = ki
            self.kd: float = kd
            self.i_limit: float = i_limit
            self.out_limit: float = out_limit

    class ActionMoveVertical:

        class Axis(Enum):
            X0  = 0
            X1  = 1
            ALL = 2

        class Mode(Enum):
            POSITION = 0
            FORCE    = 1

        axis: Axis
        mode: Mode
        target: float

        def __init__(self, axis: Axis, mode: Mode, target: float):
            self.axis = axis
            self.mode = mode
            self.target: float = target

    class ActionMoveHorizontal:

        target_position: float
        max_vel        : float
        max_accel      : float

        def __init__(self, target_position: float, max_vel: float, max_accel: float):
            self.target_position: float = target_position
            self.max_vel: float = max_vel
            self.max_accel: float = max_accel

    class ActionStopPrevious:
        class Axis(Enum):
            X0  = 0
            X1  = 1
            Y   = 2
            ALL = 3

        axis: Axis

        def __init__(self, axis: Axis):
            self.axis = axis

    class EndConditionForce:
        class Axis(Enum):
            X0 = 0
            X1 = 1
            ALL = 2

        axis: Axis
        target: float
        threshold: float

        def __init__(self, axis: Axis, target: float, threshold: float):
            self.axis = axis
            self.target = target
            self.threshold = threshold

    class EndConditionPosition:
        class Axis(Enum):
            X0 = 0
            X1 = 1
            Y  = 2

        axis: Axis
        target: float
        threshold: float

        def __init__(self, axis: Axis, target: float, threshold: float):
            self.axis = axis
            self.target = target
            self.threshold = threshold

    class EndConditionTime:
        # ms
        wait_time: int

        def __init__(self, wait_time: int):
            self.wait_time = wait_time

    actions: list[ActionChangeVerticalPIDParams | ActionMoveVertical | ActionStopPrevious | ActionMoveHorizontal]
    end_conditions: list[EndConditionTime | EndConditionForce | EndConditionPosition]

