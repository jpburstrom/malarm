#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2008 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"

from PyQt4 import QtCore, QtGui, QtDesigner
import PyQt4.Qwt5 as Qwt
from soundfileviewer import *

#============================================================================#
# The group name in designer widgetbox                                       #
#----------------------------------------------------------------------------#
DESIGNER_GROUP_NAME = "malarm misc widgets"

#============================================================================#
# Plugin for AbstractParamWidget                                             #
#----------------------------------------------------------------------------#
class SoundFileViewerPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self, parent)
        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return
        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="SoundFileViewer" name="soundfileViewer">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "soundfileviewer"

    def name(self):
        return "SoundFileViewer"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return SoundFileViewer(parent)

