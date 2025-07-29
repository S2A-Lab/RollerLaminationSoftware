from enum import Enum

class MacroStep:

    class ChangeVerticalPIDParamsAction:
        class Axis(Enum):
            X0 = 0
            X1 = 1
            ALL= 2

        axis: Axis
        kp:        float
        ki:        float
        kd:        float
        i_limit:   float
        out_limit: float

    class MoveVerticalAction:
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

    class MoveHorizontalAction:
        target_position: float
        max_vel        : float
        max_accel      : float

    class StopPreviousActions:
        class Axis(Enum):
            X0  = 0
            X1  = 1
            Y   = 2
            ALL = 3

        axis: Axis

    class WaitForceEnd:
        class Axis(Enum):
            X0 = 0
            X1 = 1
            ALL = 2
        axis: Axis
        target: float
        threshold: float

    class WaitPositionEnd:
        class Axis(Enum):
            X0 = 0
            X1 = 1
            Y  = 2
        axis: Axis
        target: float
        threshold: float

    class WaitTimeEnd:
        # ms
        wait_time: int

    actions: list
    end_conditions: list
