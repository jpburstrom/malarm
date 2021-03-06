#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2008 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"

from PyQt4 import QtCore, QtGui, QtDesigner
#from paramwidgets import ParamSpinBox, ParamPushButton, ParamProgress, ParamToggleButton, ParamThreeStateButton, ParamLineEdit, ParamLabel
from paramwidgets import *
from larmlib import param
from malarmtaskmenu import MalarmTaskMenuFactory

#============================================================================#
# The group name in designer widgetbox                                       #
#----------------------------------------------------------------------------#
DESIGNER_GROUP_NAME = "malarm OSC widgets"

#============================================================================#
# Plugin for AbstractParamWidget                                             #
#----------------------------------------------------------------------------#
class ParamSpinBoxPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self, parent)
        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return
        manager = formEditor.extensionManager()
        if manager:
            self.factory = MalarmTaskMenuFactory(manager)
            manager.registerExtensions(
                self.factory, "com.trolltech.Qt.Designer.TaskMenu"
                )

        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="ParamSpinBox" name="paramSpinbox">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "paramwidgets"

    def name(self):
        return "ParamSpinBox"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return ParamSpinBox(parent)

class ParamDoubleSpinBoxPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self, parent)
        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return
        manager = formEditor.extensionManager()
        if manager:
            self.factory = MalarmTaskMenuFactory(manager)
            manager.registerExtensions(
                self.factory, "com.trolltech.Qt.Designer.TaskMenu"
                )

        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="ParamDoubleSpinBox" name="paramDoubleSpinbox">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "paramwidgets"

    def name(self):
        return "ParamDoubleSpinBox"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return ParamDoubleSpinBox(parent)

class ParamPushButtonPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
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
        return '<widget class="ParamPushButton" name="paramPushbutton">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "paramwidgets"

    def name(self):
        return "ParamPushButton"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return ParamPushButton(parent)


class ParamToggleButtonPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self, parent)
        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return

    def isInitialized(self):
        return self.initialized

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="ParamToggleButton" name="paramTogglebutton">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "paramwidgets"

    def name(self):
        return "ParamToggleButton"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return ParamToggleButton(parent)

class ParamCheckBoxPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self, parent)
        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return

    def isInitialized(self):
        return self.initialized

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="ParamCheckBox" name="paramTogglebutton">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "paramwidgets"

    def name(self):
        return "ParamCheckBox"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return ParamCheckBox(parent)

class ParamThreeStateButtonPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self, parent)
        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return

    def isInitialized(self):
        return self.initialized

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="ParamThreeStateButton" name="paramThreeStatebutton">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "paramwidgets"

    def name(self):
        return "ParamThreeStateButton"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return ParamThreeStateButton(parent)

class ParamProgressPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self, parent)
        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return

    def isInitialized(self):
        return self.initialized

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="ParamProgress" name="paramProgress">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "paramwidgets"

    def name(self):
        return "ParamProgress"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return ParamProgress(parent)

class ParamGridPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self, parent)
        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return

    def isInitialized(self):
        return self.initialized

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="ParamGrid" name="paramGrid">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "paramwidgets"

    def name(self):
        return "ParamGrid"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return ParamGrid(parent)

class ParamMinMaxSliderPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self, parent)
        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return

    def isInitialized(self):
        return self.initialized

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="ParamMinMaxSlider" name="paramMinMaxSlider">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "paramwidgets"

    def name(self):
        return "ParamMinMaxSlider"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return ParamMinMaxSlider(parent)

class ParamLineEditPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self, parent)
        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return

    def isInitialized(self):
        return self.initialized

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="ParamLineEdit" name="paramLineedit">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "paramwidgets"

    def name(self):
        return "ParamLineEdit"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return ParamLineEdit(parent)

class ParamLabelPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self, parent)
        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return

    def isInitialized(self):
        return self.initialized

    def isContainer(self):
        return False

    def domXml(self):
        return '<widget class="ParamLabel" name="paramLabel">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "paramwidgets"

    def name(self):
        return "ParamLabel"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return ParamLabel(parent)


