#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2009 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"

import os
import sys

from PyQt4 import QtGui, QtCore

keymap = ["ZSXDCVGBHNJMQ\"W#ER%T&Y/UI)O=P?Å"]

#WORK IN PROGRESS


class ParamKeyboard(QtGui.QLabel):
    def __init__(self, receiver, *args):  
        QtGui.QLabel.__init__(self, *args)

        self.receiver = receiver

class KeyboardKeyHandler(QtCore.QObject):
    """
    An Event Filter for handling keyboard, adding doubleclicks and longclicks.
    """

    eventType = None

    def __init__(self, parent, *args):
        """
        Constructor.
        """
        QtCore.QObject.__init__(self, parent, *args) 
        
        self._single = None
        self._pairs = []

        self._pressed = set()

    def eventFilter(self, obj, ev):
        if ev.type() == QtCore.QEvent.KeyPress:
            return self.handleKeyPress(ev)
        elif ev.type() == QtCore.QEvent.KeyRelease:
            return self.handleKeyRelease(ev)
        else:
            return QtCore.QObject.eventFilter(self, obj, ev)

    def handleKeyPress(self, ev):
        print ev.key()
        return False

    def handleKeyRelease(self, ev):
        return False


if __name__ == "__main__":

    a = QtGui.QApplication(sys.argv)
    win = ParamKeyboard(None)
    evf = KeyboardKeyHandler(win)
    win.installEventFilter(evf)
    win.show()
    sys.exit(a.exec_())

