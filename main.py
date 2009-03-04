#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2009 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"

#TODO: action groups for edit actions -- disable in "performance mode"
#TODO: Update and add docs
#TODO: plugin system for paramboxcontroller
#TODO: find a good way to highlight selected ParamBox
#TODO: shortcuteditor: Create new UI
#FIXME: grab mouse/wheel/kbd when defining new shortcuts

"""A system for creating OSC sending (and receiving) guis.

malarm is an app-creating app created with Python and PyQt4. 
The aim is to be able to rapidly create guis for sound (and other)
applications which communicates with the Open Sound Control (OSC)
protocol.  With hopefully as little work as possible (we
all know this is not true) it can create apps with all the bells 
& whistles we know from ordinary programs: Keyboard shortcuts, fancy widgets and
state saving (presets).
"""


import os
import sys
import random
import copy
import shutil

#from pdb import rpdb2
#import pida.utils.rpdb2 as rpdb2

from PyQt4 import QtGui, QtCore, uic

from larmlib.param import *
from larmlib.projectcontainer import ProjectContainer
from larmlib.gesture import *
from larmlib.globals import *

#rpdb2.start_embedded_debugger("d")

if not os.path.exists(RCDIR):
    os.mkdir(RCDIR)

sys.path.append(os.path.join(sys.path[0], "larmwidgets"))

MainUI, dummy = uic.loadUiType(os.path.join(sys.path[0], "forms/main.ui"))
class MyApplication(QtGui.QApplication):
    def __init__(self, *args):
        QtGui.QApplication.__init__(self, *args)
        
class MainWindow(MainUI, QtGui.QMainWindow):

    def __init__(self, *args):  
        QtGui.QMainWindow.__init__(self, *args)

        self.installEventFilter(GestureEventHandler(self))

        self.setupUi(self) #Setup main window

        self.projectContainer = ProjectContainer(self) #This is the hard working class, doing all the work

        QtGui.qApp.setPalette(QtGui.QPalette(QtCore.Qt.darkGray)) #Set some cosmetics.

        self.projectContainer.rebuild() #Refresh container
        
        self.selecting = False
        self.currentSelectedChild = self
        self.setMouseTracking(1)

        self.connect(self.actionQuit, QtCore.SIGNAL("activated()"), self.quit)

    def mousePressEvent(self, e):
        if QtCore.Qt.ShiftModifier & e.modifiers() == QtCore.Qt.ShiftModifier:
            self.selecting = True
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))

    def mouseMoveEvent(self, ev):
        if self.selecting:
            thisChild = self.childAt(ev.pos())
            if thisChild != self.currentSelectedChild:
                try:
                    thisChild.toggleSelect()
                except AttributeError:
                    pass
                self.currentSelectedChild = thisChild
        
    def mouseReleaseEvent(self, ev):
        self.selecting = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def quit(self):
        self.projectContainer.closeProject()
        self.close()
    
a = MyApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(a.exec_())
