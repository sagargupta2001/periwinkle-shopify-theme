"""Small helpers for writing Apple Shortcuts as binary property lists.

A .shortcut file is a plist of actions. `shortcuts sign` turns it into the signed
file an iPhone will import. Nothing here talks to Apple; signing happens in build.py.
"""
import plistlib
import uuid

OBJ = "￼"  # Shortcuts marks an inline variable with this character
PREFIX = "is.workflow.actions."


class Var:
    """A reference to an action's output, or to a named variable."""

    def __init__(self, name, output_uuid=None):
        self.name, self.output_uuid = name, output_uuid

    def _value(self):
        if self.output_uuid:
            return {"Type": "ActionOutput", "OutputName": self.name, "OutputUUID": self.output_uuid}
        return {"Type": "Variable", "VariableName": self.name}


def named(name):
    return Var(name)


# Conditions, as numbered in the Shortcuts file format
IS, IS_NOT, CONTAINS, HAS_VALUE, NO_VALUE, GREATER, LESS = 4, 5, 99, 100, 101, 2, 0

REPEAT_ITEM = named("Repeat Item")


def attachment(var):
    """A parameter that takes a whole variable."""
    return {"Value": var._value(), "WFSerializationType": "WFTextTokenAttachment"}


def text(*parts):
    """A text parameter mixing literal strings and variables."""
    string, ranges = "", {}
    for part in parts:
        if isinstance(part, Var):
            ranges["{%d, 1}" % (len(string.encode("utf-16-le")) // 2)] = part._value()
            string += OBJ
        else:
            string += part
    return {"Value": {"string": string, "attachmentsByRange": ranges}, "WFSerializationType": "WFTextTokenString"}


class Shortcut:
    def __init__(self, name, glyph=59511, color=4274264319):
        self.name, self.glyph, self.color = name, glyph, color
        self.actions, self.questions, self._groups = [], [], []

    def add(self, identifier, output=None, **params):
        identifier = identifier if "." in identifier and identifier.startswith(("is.", "com.")) else PREFIX + identifier
        action_uuid = str(uuid.uuid4()).upper()
        params["UUID"] = action_uuid
        self.actions.append({"WFWorkflowActionIdentifier": identifier, "WFWorkflowActionParameters": params})
        return Var(output or identifier.split(".")[-1], action_uuid)

    # Control flow. Each block needs a shared group id and a mode: 0 start, 1 middle, 2 end.
    def if_(self, var, condition, string=None, number=None):
        group = str(uuid.uuid4()).upper()
        params = {"GroupingIdentifier": group, "WFControlFlowMode": 0, "WFCondition": condition,
                  "WFInput": {"Type": "Variable", "Variable": attachment(var)}}
        if string is not None:
            params["WFConditionalActionString"] = string
        if number is not None:
            params["WFNumberValue"] = number
        self.add("conditional", **params)
        return group

    def else_(self, group):
        self.add("conditional", GroupingIdentifier=group, WFControlFlowMode=1)

    def end_if(self, group):
        return self.add("conditional", output="If Result", GroupingIdentifier=group, WFControlFlowMode=2)

    def each(self, var):
        group = str(uuid.uuid4()).upper()
        self.add("repeat.each", GroupingIdentifier=group, WFControlFlowMode=0, WFInput=attachment(var))
        return group

    def end_each(self, group):
        return self.add("repeat.each", output="Repeat Results", GroupingIdentifier=group, WFControlFlowMode=2)

    def menu(self, prompt, items):
        group = str(uuid.uuid4()).upper()
        self.add("choosefrommenu", GroupingIdentifier=group, WFControlFlowMode=0, WFMenuPrompt=prompt, WFMenuItems=items)
        return group

    def case(self, group, title):
        self.add("choosefrommenu", GroupingIdentifier=group, WFControlFlowMode=1, WFMenuItemTitle=title)

    def end_menu(self, group):
        return self.add("choosefrommenu", output="Menu Result", GroupingIdentifier=group, WFControlFlowMode=2)

    def write(self, path):
        doc = {
            "WFWorkflowName": self.name,
            "WFWorkflowClientVersion": "2700",
            "WFWorkflowMinimumClientVersion": 900,
            "WFWorkflowMinimumClientVersionString": "900",
            "WFWorkflowIcon": {"WFWorkflowIconGlyphNumber": self.glyph, "WFWorkflowIconStartColor": self.color},
            "WFWorkflowTypes": [],
            "WFWorkflowInputContentItemClasses": [],
            "WFWorkflowImportQuestions": self.questions,
            "WFWorkflowActions": self.actions,
            "WFWorkflowHasOutputFallback": False,
            "WFWorkflowOutputContentItemClasses": ["WFStringContentItem"],
        }
        with open(path, "wb") as f:
            plistlib.dump(doc, f, fmt=plistlib.FMT_BINARY)
