# coding: shift-jis

from hwx import simlab
import os, sys
import tkinter as tk

## global
PROJECT_DIR = (os.path.dirname(os.path.realpath(__file__)))
if not PROJECT_DIR in sys.path:
    sys.path.append(PROJECT_DIR)

## local import
import simlablib

## Menu history (changes blue button)
class MenuHistory():
    def __init__(self, gui):
        self.name = 'MenuHistory'
        self.value = 0
        self.gui = gui
        self.enums = {
            'FaceMergeSplit'        : [1 << 0,   gui.btnfaceMergeSplit],
            'FilletWelding'         : [1 << 1,   gui.btnFilletWelding],
            'GrooveWelding'         : [1 << 2,   gui.btnGrooveWelding],
            'ButtWelding'           : [1 << 3,   gui.btnButtWelding],
            'IntermittentWelding'   : [1 << 4,   gui.btnIntermittentWelding],
            'YomoriWelding'         : [1 << 5,   gui.btnYomoriWelding],
            'StraightLine'          : [1 << 7,   gui.btnLineStraight],
            'SplitEdge'             : [1 << 8,   gui.btnSplitEdge],
            'ProjectEdge'           : [1 << 9,   gui.btnProjectEdge],
            'JoinBead'              : [1 << 10,  gui.btnJoinBead],
            'ConnectBeads'          : [1 << 11,  gui.btnBeadConnect],
            'FillGap'               : [1 << 12,  gui.btnFillGap],
            'SplitCircumference'    : [1 << 13,  gui.btnCircumEdge],
            'BeadRetouch'           : [1 << 14,  gui.btnBeadRetouch],
        }

        if simlab.isParameterPresent(self.name):
            self.value = simlab.getIntParameter('$' + self.name)
        self.Update()

    def Add(self, enumType):
        if not enumType in self.enums.keys():
            return

        n = self.enums[enumType][0]
        if self.value & n:
            return

        self.value += n
        simlablib.AddIntParameters(self.name, self.value)
        self.Update()

    def DeleteAll(self):
        self.value = 0
        simlablib.AddIntParameters(self.name, self.value)
        self.Update()   

    def Get(self):
        return self.value

    def Restore(self, value):
        self.value = value
        self.Update()

    def Update(self):
        for item in self.enums.values():
            n, widget = item
            if self.value & n:
                widget.config(fg='blue')
            else:
                widget.config(fg='SystemButtonText')
