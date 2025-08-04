from enum import Enum
import xml.etree.ElementTree as ET
from xml.dom import minidom

class MacroStep:

    def __init__(self):
        self.actions = []
        self.end_conditions = []
        self.name = "Step"

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

def macro_steps_to_xml(macro_steps: list[MacroStep], file_path: str):
    root = ET.Element("MacroSteps")

    for step in macro_steps:
        step_elem = ET.SubElement(root, "Step", name=step.name)

        # Actions
        actions_elem = ET.SubElement(step_elem, "Actions")
        for action in step.actions:
            if isinstance(action, MacroStep.ActionChangeVerticalPIDParams):
                a = ET.SubElement(actions_elem, "ActionChangeVerticalPIDParams", axis=action.axis.name)
                ET.SubElement(a, "kp").text = str(action.kp)
                ET.SubElement(a, "ki").text = str(action.ki)
                ET.SubElement(a, "kd").text = str(action.kd)
                ET.SubElement(a, "i_limit").text = str(action.i_limit)
                ET.SubElement(a, "out_limit").text = str(action.out_limit)

            elif isinstance(action, MacroStep.ActionMoveVertical):
                a = ET.SubElement(actions_elem, "ActionMoveVertical", axis=action.axis.name, mode=action.mode.name)
                ET.SubElement(a, "target").text = str(action.target)

            elif isinstance(action, MacroStep.ActionMoveHorizontal):
                a = ET.SubElement(actions_elem, "ActionMoveHorizontal")
                ET.SubElement(a, "target_position").text = str(action.target_position)
                ET.SubElement(a, "max_vel").text = str(action.max_vel)
                ET.SubElement(a, "max_accel").text = str(action.max_accel)

            elif isinstance(action, MacroStep.ActionStopPrevious):
                ET.SubElement(actions_elem, "ActionStopPrevious", axis=action.axis.name)

        # End Conditions
        endconds_elem = ET.SubElement(step_elem, "EndConditions")
        for cond in step.end_conditions:
            if isinstance(cond, MacroStep.EndConditionForce):
                c = ET.SubElement(endconds_elem, "EndConditionForce", axis=cond.axis.name)
                ET.SubElement(c, "target").text = str(cond.target)
                ET.SubElement(c, "threshold").text = str(cond.threshold)

            elif isinstance(cond, MacroStep.EndConditionPosition):
                c = ET.SubElement(endconds_elem, "EndConditionPosition", axis=cond.axis.name)
                ET.SubElement(c, "target").text = str(cond.target)
                ET.SubElement(c, "threshold").text = str(cond.threshold)

            elif isinstance(cond, MacroStep.EndConditionTime):
                ET.SubElement(endconds_elem, "EndConditionTime", wait_time=str(cond.wait_time))

    # Beautify & write to file
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    with open(file_path, "w") as f:
        f.write(xml_str)

def macro_steps_from_xml(file_path: str) -> list[MacroStep]:
    tree = ET.parse(file_path)
    root = tree.getroot()
    macro_steps = []

    for step_elem in root.findall("Step"):
        step = MacroStep()
        step.name = step_elem.get("name", "Step")

        # Parse Actions
        actions_elem = step_elem.find("Actions")
        if actions_elem is not None:
            for action_elem in actions_elem:
                tag = action_elem.tag

                if tag == "ActionChangeVerticalPIDParams":
                    axis = MacroStep.ActionChangeVerticalPIDParams.Axis[action_elem.get("axis")]
                    kp = float(action_elem.findtext("kp"))
                    ki = float(action_elem.findtext("ki"))
                    kd = float(action_elem.findtext("kd"))
                    i_limit = float(action_elem.findtext("i_limit"))
                    out_limit = float(action_elem.findtext("out_limit"))
                    action = MacroStep.ActionChangeVerticalPIDParams(axis, kp, ki, kd, i_limit, out_limit)

                elif tag == "ActionMoveVertical":
                    axis = MacroStep.ActionMoveVertical.Axis[action_elem.get("axis")]
                    mode = MacroStep.ActionMoveVertical.Mode[action_elem.get("mode")]
                    target = float(action_elem.findtext("target"))
                    action = MacroStep.ActionMoveVertical(axis, mode, target)

                elif tag == "ActionMoveHorizontal":
                    target_position = float(action_elem.findtext("target_position"))
                    max_vel = float(action_elem.findtext("max_vel"))
                    max_accel = float(action_elem.findtext("max_accel"))
                    action = MacroStep.ActionMoveHorizontal(target_position, max_vel, max_accel)

                elif tag == "ActionStopPrevious":
                    axis = MacroStep.ActionStopPrevious.Axis[action_elem.get("axis")]
                    action = MacroStep.ActionStopPrevious(axis)

                else:
                    continue

                step.actions.append(action)

        # Parse End Conditions
        endconds_elem = step_elem.find("EndConditions")
        if endconds_elem is not None:
            for cond_elem in endconds_elem:
                tag = cond_elem.tag

                if tag == "EndConditionForce":
                    axis = MacroStep.EndConditionForce.Axis[cond_elem.get("axis")]
                    target = float(cond_elem.findtext("target"))
                    threshold = float(cond_elem.findtext("threshold"))
                    cond = MacroStep.EndConditionForce(axis, target, threshold)

                elif tag == "EndConditionPosition":
                    axis = MacroStep.EndConditionPosition.Axis[cond_elem.get("axis")]
                    target = float(cond_elem.findtext("target"))
                    threshold = float(cond_elem.findtext("threshold"))
                    cond = MacroStep.EndConditionPosition(axis, target, threshold)

                elif tag == "EndConditionTime":
                    wait_time = int(cond_elem.get("wait_time"))
                    cond = MacroStep.EndConditionTime(wait_time)

                else:
                    continue

                step.end_conditions.append(cond)

        macro_steps.append(step)

    return macro_steps