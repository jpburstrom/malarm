#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2009 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision: 81 $"


import os
import sys
import copy

from PyQt4 import QtGui, QtCore, uic, QtDesigner

import larmlib.param as param

class AbstractParamWidget(object):
    """Subclass this together with a Qt Widget class."""

    def __init__(self, *args):
        object.__init__(self, *args)
        
        try:
            self._length
        except AttributeError:
            self._length = 1

        #Param coupled with widget
        self._param = None
        #Types of widget. For most ordinary widgets, this is a 1-item list, but can be as many
        #as wanted. Has to match the param.
        self._types = [None for i in range(self._length)]
        #These are shared by the param (that is, the param passes the reference to its own
        #_min and _max lists upon connection)
        self._min = [0 for i in range(self._length)]
        self._max = [1 for i in range(self._length)]
        self._state = [0 for i in range(self._length)]
        
        
        self._paramPath = ""
        #These are used as pyqtProperties, to be set by designer.
        #They update the param when connecting to it, making the param effectively stupid.
        self._paramDefault = [0 for i in range(self._length)]
        self._paramMin = [0 for i in range(self._length)]
        self._paramMax = [0 for i in range(self._length)]

        
        if len(self._types) == 1 and self._types[0] in (str, bool, param.Bang):
            self.setMin = self._setMinMaxDummy
            self.setMax = self._setMinMaxDummy

        self.selectpalette = QtGui.QPalette()
        self.selectpalette.setColor(self.selectpalette.Base, QtGui.QColor("#ffbbaa"))
        self.selected = False


    def getLength(self):
        return self._length

    length = property(getLength)

    def getTypes(self):
        return self._types

    types = property(getTypes)
    
    def getParam(self):
        return self._param

    param = property(getParam)

    def setParam(self, param):
        """Sync the properties of the widget and the param.
        
        param (Param) : param object
        """
        if param.typecheck(self._types):
            self._param = param
            #FIXME: set min, max, default
            #self.updateParamConnections()
            #And get them as references from param.
            self._min = self._param.getMinReference()
            self._max = self._param.getMaxReference()
            self._state = self._param.getStateReference()
            self.connect(param, QtCore.SIGNAL("paramUpdate"), self.guiUpdate)
            self._param.update()
            self.setEnabled(True)
        else:
            raise TypeError, "Widget=>Param connection didn't work."

    def removeParam(self, param):
        self._param = None

    def guiUpdate(self, i):
        p = self.sender()
        if i == p.UpdateState:
            self.updateState()
        elif i == p.UpdateMin:
            self.updateMin()
        elif i == p.UpdateMax:
            self.updateMax()


    def updateState(self):
        """Subclass this to set values for your widget"""
        #FIXME: These three shoudl not do anything, perhaps
        raise NotImplementedError

    def updateMin(self):
        """Subclass this to set min values for your widget"""
        raise NotImplementedError

    def updateMax(self):
        """Subclass this to set max values for your widget"""
        raise NotImplementedError

    def mousePressEvent(self, ev):
        if QtCore.Qt.ControlModifier & ev.modifiers():
            self.startDrag()
        elif QtCore.Qt.ShiftModifier & ev.modifiers():
            self.toggleSelect()
    
    def toggleSelect(self):
        if self.selected:
            self.setPalette(QtGui.qApp.palette())
            self.selected = False
        else:
            self.setPalette(self.selectpalette)
            self.selected = True

    def setSelected(self, boo=True):
        if boo and not self.selected:
            self.setPalette(self.selectpalette)
        elif not boo and self.selected:
            self.setPalette(QtGui.qApp.palette())
        self.selected = boo
    
    def startDrag(self):
        drag = QtGui.QDrag(self)
        data = QtCore.QMimeData()
        if self._length is 1 and self._state is not None:
            data.setText(str(self._state[0]))
        drag.setMimeData(data)
        self.dropAction = drag.exec_()

    def dragEnterEvent(self, ev):
        if ev.mimeData().hasFormat("text/plain") or \
                ev.mimeData().hasFormat(
                        "application/x-qabstractitemmodeldatalist") or ev.mimeData(
                                ).hasUrls():
            ev.acceptProposedAction()
    
    def dropEvent(self, ev):
        if ev.mimeData().hasFormat(
                "application/x-qabstractitemmodeldatalist"):
            self.setParamPath(str(ev.source().currentItem().text()))
            ev.acceptProposedAction()
            return
        elif ev.mimeData().hasUrls():
            text = ev.mimeData().urls()[0].toLocalFile()
        else:
            text = ev.mimeData().text()
        try:
            self.setText(str(text))
        except AttributeError:
            pass
        ev.acceptProposedAction()

    def _setMinMaxDummy(self, i, v):
        pass
    
    def _scaleFrom(self, val, slot=0):
        """Scale a float (val) btwn 0-1 to boundaries of slot."""

        return (val * (self._max[slot] - self._min[slot])) + self._min[slot] 

    def _scaleTo(self, scaleto, slot=0):
        """Scale current state of slot to a value btwn 0 and x"""
        try:
            v = self._state[slot]
        except TypeError:
            if self._state is None:
                return 0
            else:
                raise TypeError
        return (v - self._min[slot]) / (
                    self._max[slot] - self._min[slot])  * scaleto
            
    def setParamPath(self, path):
        """Set path of param.

        This method is used by subclasses as setter/getter for a pyqtProperty.
        It sets the OSC path currently associated with the widget.
        Setting these after connecting to a param has no effect.
        """
        if self._param:
            return
        self._paramPath = path
        self.setToolTip(path)

    def getParamPath(self):
        """Get path of param.

        Get the OSC path currently associated with the widget.
        """
        return self._paramPath

    def setParamMin(self, v):
        """Set min value(s).

        Set the min value(s) used to set up the connection with the param.
        """
        if self._length is 1:
            self._paramMin[0] = v
        else:
            raise NotImplementedError, "Cannot set multiple min values"

    def getParamMin(self):
        """Set min value(s).

        Sets the min value(s) used to set up the connection with the param.
        After connecting, this has no effect.
        """
        if self._length == 1:
            return self._paramMin[0]
        else:
            return tuple(self._paramMin)


    def setParamMax(self, v):
        """Set max value(s).

        Set the max value(s) used to set up the connection with the param.
        """
        if self._length is 1:
            self._paramMax[0] = v
        else:
            raise NotImplementedError, "Cannot set multiple min values"

    def getParamMax(self):
        """Set max value(s).

        Sets the max value(s) used to set up the connection with the param.
        After connecting, this has no effect.
        """
        if self._length == 1:
            return self._paramMax[0]
        else:
            return tuple(self._paramMax)

    def setParamDefault(self, v):
        """Set default value(s).

        Set the default value(s) used to set up the connection with the param.
        """
        if self._length is 1:
            self._paramDefault[0] = v
        else:
            raise NotImplementedError, "Cannot set multiple default values"

    def getParamDefault(self):
        """Set default value(s).

        Sets the default value(s) used to set up the connection with the param.
        After connecting, this has no effect.
        """
        if self._length == 1:
            return self._paramDefault[0]
        else:
            return tuple(self._paramDefault)

    #These are later on overridden by pyqtProperties, if needed.
    paramMin = property(getParamMin, setParamMin)
    paramMax = property(getParamMax, setParamMax)
    paramDefault = property(getParamDefault, setParamDefault)
    
