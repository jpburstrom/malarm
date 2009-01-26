#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2008 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"

from PyQt4 import QtCore, QtGui, QtDesigner
from filebrowser import FileBrowserWidget

#============================================================================#
# The group name in designer widgetbox                                       #
#----------------------------------------------------------------------------#
DESIGNER_GROUP_NAME = "Larm Widgets"

#============================================================================#
# Plugin for AbstractParamWidget                                             #
#----------------------------------------------------------------------------#
class FileBrowserPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
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
        return '<widget class="FileBrowserWidget" name="fileBrowserWidget">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "filebrowser"

    def name(self):
        return "FileBrowserWidget"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return FileBrowserWidget(parent)

