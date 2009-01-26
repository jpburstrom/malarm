#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2009 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"

#TODO: Create params from widget pyqtProperties. This is the only thing making sense.

"""A system for creating OSC sending (and receiving) guis.

malarm is an app-creating app created with Python and PyQt4. 
The aim is to be able to rapidly create guis for sound (and other)
applications which communicates with the Open Sound Control (OSC)
protocol.  With hopefully as little work as possible (we
all know this is not true) it can create apps with all the bells 
& whistles we know from ordinary programs: Keyboard shortcuts, fancy widgets and
state saving (presets).

The workflow could be described like this: 

    1. Make the gui with Qt's Designer.  There are custom widgets, 
    which are later able to connect to the app's OSC sending machinery.

    2. Create "params", small cells which has an OSC address, a type
    and a state (in some cases also min/max values and default), and handles
    all the dirty work. 
    
    3. Connect widgets to params. Certain widgets demand certain param
    types (a slider sending out strings doesn't make much sense for now).

    4. Rebuild and watch your new app spit out OSC goodness.

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
from larmlib.keyhandler import *
from larmlib.globals import *

#rpdb2.start_embedded_debugger("d")

if not os.path.exists(RCDIR):
    os.mkdir(RCDIR)

sys.path.append(os.path.join(sys.path[0], "larmwidgets"))

MainUI, dummy = uic.loadUiType(os.path.join(sys.path[0], "forms/main.ui"))

class MainWindow(MainUI, QtGui.QMainWindow):

    def __init__(self, *args):  
        QtGui.QMainWindow.__init__(self, *args)

        self.installEventFilter(KeyHandler(self))

        self.setupUi(self) #Setup main window

        self.projectContainer = ProjectContainer(self) #This is the hard working class, doing all the work

        self.setPalette(QtGui.QPalette(QtCore.Qt.darkGray)) #Set some cosmetics.

        self.projectContainer.rebuild() #Refresh container
        
        self.selecting = False
        self.currentSelectedChild = self

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

    def customEvent(self, ev):
        if isinstance(ev, SpecialKeyEvent):
            self.projectContainer.handleSpecialKey(ev)

    def quit(self):
        self.projectContainer.closeProject()
        self.close()
    
a = QtGui.QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(a.exec_())
