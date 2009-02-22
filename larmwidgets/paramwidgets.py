#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2009 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"


"""
Widget->param setup
===================

mouse/keybd => widget event handler (updating state) => param.update => widget.updateState
param.setState (from OSC or state saving) => widget.updateState

"""


import os
import sys
import copy
from math import pow

from PyQt4 import QtGui, QtCore, uic, QtDesigner

from abstractparamwidget import AbstractParamWidget
from larmlib import param

class ParamSpinBox(AbstractParamWidget, QtGui.QSpinBox):

    def __init__(self, *args):
        AbstractParamWidget.__init__(self, *args)
        QtGui.QSpinBox.__init__(self, *args)

        self._types = [int]
        self._paramDefault = [t() for t in self._types]

        self.setAcceptDrops(1)

        #self.setObjectName("paramSpinBox")

    def updateState(self):
        #FIXME: These three shoudl not do anything, perhaps
        self.setValue(self._state[0])

    def updateMin(self):
        self.setMinValue(self._min[0])

    def updateMax(self):
        self.setMaxValue(self._min[0])


    @QtCore.pyqtSignature("saveParam()")
    def saveParam(self):
        qApp.emit(QtCore.SIGNAL("saveMe"), self._param)

    def mousePressEvent(self, ev):
        if QtCore.Qt.ControlModifier & ev.modifiers() == QtCore.Qt.ControlModifier:
            self.startDrag()
        elif QtCore.Qt.ShiftModifier & ev.modifiers() == QtCore.Qt.ShiftModifier:
            self.toggleSelect()
        else:
            QtGui.QSpinBox.mousePressEvent(self, ev)

    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault
    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    getStandardAction = AbstractParamWidget.getStandardAction
    setStandardAction = AbstractParamWidget.setStandardAction

    standardAction = QtCore.pyqtProperty("int", getStandardAction, setStandardAction)
    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramMin = QtCore.pyqtProperty("int", getParamMin, setParamMin)
    paramMax = QtCore.pyqtProperty("int", getParamMax, setParamMax)
    paramDefault = QtCore.pyqtProperty("int", getParamDefault, setParamDefault)

class ParamDoubleSpinBox(AbstractParamWidget, QtGui.QDoubleSpinBox):

    def __init__(self, *args):
        AbstractParamWidget.__init__(self, *args)
        QtGui.QDoubleSpinBox.__init__(self, *args)

        self._types = [float]
        self._paramDefault = [t() for t in self._types]

        self.setAcceptDrops(1)

        #self.setObjectName("paramSpinBox")

    def updateState(self):
        #FIXME: These three shoudl not do anything, perhaps
        self.setValue(self._state[0])

    def updateMin(self):
        self.setMinValue(self._min[0])

    def updateMax(self):
        self.setMaxValue(self._min[0])


    @QtCore.pyqtSignature("saveParam()")
    def saveParam(self):
        qApp.emit(QtCore.SIGNAL("saveMe"), self._param)

    def mousePressEvent(self, ev):
        if QtCore.Qt.ControlModifier & ev.modifiers() == QtCore.Qt.ControlModifier:
            self.startDrag()
        elif QtCore.Qt.ShiftModifier & ev.modifiers() == QtCore.Qt.ShiftModifier:
            self.toggleSelect()
        else:
            QtGui.QDoubleSpinBox.mousePressEvent(self, ev)

    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault
    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    getStandardAction = AbstractParamWidget.getStandardAction
    setStandardAction = AbstractParamWidget.setStandardAction

    standardAction = QtCore.pyqtProperty("int", getStandardAction, setStandardAction)
    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramMin = QtCore.pyqtProperty("double", getParamMin, setParamMin)
    paramMax = QtCore.pyqtProperty("double", getParamMax, setParamMax)
    paramDefault = QtCore.pyqtProperty("double", getParamDefault, setParamDefault)
        
class ParamPushButton(AbstractParamWidget, QtGui.QPushButton):
    #TODO: TEST
    def __init__(self, *args):
        AbstractParamWidget.__init__(self, *args)
        QtGui.QPushButton.__init__(self, *args)

        self._types = [param.Bang]
        self._paramDefault = [t() for t in self._types]
        self.setAcceptDrops(1)
        self.setContentsMargins(1,1,1,1)

    def updateState(self):
        self.animateClick()

    def updateMin(self):
        pass

    def updateMax(self):
        pass

    @QtCore.pyqtSignature("saveParam()")
    def saveParam(self):
        qApp.emit(QtCore.SIGNAL("saveMe"), self._param)

    def mousePressEvent(self, ev):
        AbstractParamWidget.mousePressEvent(self, ev)
        self._param.update()

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault
    getStandardAction = AbstractParamWidget.getStandardAction
    setStandardAction = AbstractParamWidget.setStandardAction

    standardAction = QtCore.pyqtProperty("int", getStandardAction, setStandardAction)
    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
                        
class ParamToggleButton(ParamPushButton):
    #TODO: TEST
    def __init__(self, *args):
        ParamPushButton.__init__(self, *args)

        self._types = [bool]
        #FIXME: needed?
        self._paramDefault = [t() for t in self._types]
        self.setCheckable(1)
        self.color = QtGui.qApp.palette()
        green = QtGui.QColor(0, 255, 0, 128)
        self.green = QtGui.QPalette(green)

        self._offText = ""
        self._onText = ""
        self._textSet = False
        
    def updateState(self):
        self.setChecked(self._state[0])
        if self._state[0]:
            self.setPalette(self.green)
            if self._textSet:
                self.setText(self._onText)
            self.adjustSize()
        else:
            self.setPalette(self.color)
            if self._textSet:
                self.setText(self._offText)
            self.adjustSize()

    def updateMin(self):
        pass

    def updateMax(self):
        pass

    def mousePressEvent(self, ev):
        AbstractParamWidget.mousePressEvent(self, ev)
        self._state[0] = not self._state[0]
        self._param.update()

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault
    getStandardAction = AbstractParamWidget.getStandardAction
    setStandardAction = AbstractParamWidget.setStandardAction

    standardAction = QtCore.pyqtProperty("int", getStandardAction, setStandardAction)

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramDefault = QtCore.pyqtProperty("bool", getParamDefault, setParamDefault)

    def getOffText(self):
        return self._offText
    def setOffText(self, e):
        self._offText = e
        self._textSet = len(self._offText + self._onText) > 0
    def getOnText(self):
        return self._onText
    def setOnText(self, e):
        self._onText = e
        self._textSet = len(self._offText + self._onText) > 0

    onText = QtCore.pyqtProperty("QString", getOnText, setOnText)
    offText = QtCore.pyqtProperty("QString", getOffText, setOffText)


class ParamCheckBox(QtGui.QCheckBox, AbstractParamWidget):
    def __init__(self, *args):
        AbstractParamWidget.__init__(self, *args)
        QtGui.QCheckBox.__init__(self, *args)

        self._types = [bool]
        self._paramDefault = [t() for t in self._types]

        self.setEnabled(self._param is not None)

    def updateState(self):
        self.setChecked(self._state[0])

    def updateMin(self):
        pass

    def updateMax(self):
        pass

    def mousePressEvent(self, ev):
        AbstractParamWidget.mousePressEvent(self, ev)
        self._state[0] = not self._state[0]
        self._param.update()

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault
    getStandardAction = AbstractParamWidget.getStandardAction
    setStandardAction = AbstractParamWidget.setStandardAction

    standardAction = QtCore.pyqtProperty("int", getStandardAction, setStandardAction)

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramDefault = QtCore.pyqtProperty("bool", getParamDefault, setParamDefault)

class ParamThreeStateButton(ParamPushButton):
    def __init__(self, *args):
        ParamPushButton.__init__(self, *args)

        self._types = [int]
        self._paramDefault = [t() for t in self._types]
        self._paramMin = [0]
        self._paramMax = [2]

        self._texts = ["", "", ""]
        self._textSet = False

        green = QtGui.QColor(0, 255, 0, 128)
        red = QtGui.QColor(255, 0, 0, 128)
        self._colors = (
                QtGui.qApp.palette(),
                QtGui.QPalette(green),
                QtGui.QPalette(red)
                )

    def updateState(self):
        s = self._state[0]
        self.setPalette(self._colors[s])
        if self._textSet:
            self.setText(self._texts[s])

    def updateMin(self):
        pass

    def updateMax(self):
        pass

    def mousePressEvent(self, ev):
        if QtCore.Qt.ShiftModifier & ev.modifiers() == QtCore.Qt.ShiftModifier:
            self.toggleSelect()
            return
        s = ev.button()
        if s == 1 and self._state[0] != 1:
            ns = 1
        elif s == 2 and self._state[0] != 2:
            ns = 2
        elif s in (1,2):
            ns = 0
        else:
            return
        self._state[0] = ns
        self._param.update()

    def getZeroText(self):
        return self._texts[0]
    def setZeroText(self, e):
        self._texts[0] = e
        self._textSet = len("".join([str(t) for t in self._texts])) > 0
    def defaultZeroText(self):
        return ""
    def getOneText(self):
        return self._texts[1]
    def setOneText(self, e):
        self._texts[1] = e
        self._textSet = len("".join([str(t) for t in self._texts])) > 0
    def defaultOneText(self):
        return ""
    def getTwoText(self):
        return self._texts[2]
    def setTwoText(self, e):
        self._texts[2] = e
        self._textSet = len("".join([str(t) for t in self._texts])) > 0
    def defaultTwoText(self):
        return ""

    zeroText = QtCore.pyqtProperty("QString", getZeroText, setZeroText, defaultZeroText)
    oneText = QtCore.pyqtProperty("QString", getOneText, setOneText, defaultOneText)
    twoText = QtCore.pyqtProperty("QString", getTwoText, setTwoText, defaultTwoText)


    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault
    getStandardAction = AbstractParamWidget.getStandardAction
    setStandardAction = AbstractParamWidget.setStandardAction

    standardAction = QtCore.pyqtProperty("int", getStandardAction, setStandardAction)

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramMin = QtCore.pyqtProperty("int", getParamMin, setParamMin)
    paramMax = QtCore.pyqtProperty("int", getParamMax, setParamMax)
    paramDefault = QtCore.pyqtProperty("int", getParamDefault, setParamDefault)

class ParamProgress(AbstractParamWidget, QtGui.QProgressBar):
    def __init__(self, *args):
        AbstractParamWidget.__init__(self, *args)
        QtGui.QProgressBar.__init__(self, *args)

        self._types = [float]
        self._paramDefault = [t() for t in self._types]
        self._paramMin = [0 for i in range(self._length)]
        self._paramMax = [1 for i in range(self._length)]

        self.accelerator = 0
        self.deltacount = 0
        self.valuestring = "%.02f"
        self._resizing = False
        self._resizeTo = 200
        
        #We send a custom valueChanged signal, otherwise the updates 
        #from QProgressbar will destroy things...
        QtGui.QProgressBar.setRange(self, 0,1000)

        self.setAcceptDrops(1)
        self.dblclick_value = self._min[0]

        self.connect(QtGui.qApp, QtCore.SIGNAL("deltaChanged"), self.doDelta)
        
        self.updateMin = self.updateState
        self.updateMax = self.updateState
        self.setFormat("")

    @QtCore.pyqtSignature("saveParam()")
    def saveParam(self):
        print "saveme"
        qApp.emit(QtCore.SIGNAL("saveMe"), self._param)

    def updateState(self):
        #this handles gui
        self.setValue(self._scaleTo(1000))
        if self.width() > 30:
            QtGui.QProgressBar.setFormat(self, self.valuestring % self._state[0])

    def doDelta(self, s, d):
        if s == self or self.selected:
            f = self._max[0] - self._min[0]
            self._state[0] = min(self._max[0], max(self._min[0], self._state[0] + (d * f / 1000.0)))
            self._param.update()

    def mouseDoubleClickEvent(self, e):
        s = self._state[0]
        if s == self._min[0]:
            self._state[0] = self.dblclick_value
        else:
            self.dblclick_value = s
            self._state[0] = self._min[0]
        self._param.update()
            
    def mousePressEvent(self, e):
        #self.deltaTimer = self.startTimer(10)
        if QtCore.Qt.ControlModifier & e.modifiers():
            self.startDrag()
            return
        elif QtCore.Qt.ShiftModifier & e.modifiers():
            self.toggleSelect()
        elif self._resizing:
            self.setMinimumWidth(self._resizeTo)
            self.raise_()
        self.origo = self.mapToGlobal(e.pos())
        self.offset = e.pos().y()
        self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        #print self.origo.y()

    def mouseMoveEvent(self, e):
        """Move slider up/down with mouse movement"""
        if e.pos().y() == self.offset:
            return
        adder = (self.offset - e.y())
        self.deltacount += adder
        #adder *= self.accelerator
        adder *= (abs(adder) * 0.01)
        #self._state[0] = max(self._min[0], min(self._max[0], self._state[0] + adder))
        QtGui.qApp.emit( QtCore.SIGNAL("deltaChanged"), self, adder)
        #self._param.update()
        QtGui.QCursor.setPos(self.origo)

    def timerEvent(self, e):
        QtGui.qApp.emit( QtCore.SIGNAL("deltaChanged"), self, self.adder)
        self.accelerator = (self.accelerator + max(abs(self.deltacount), 0.0001)) / 2
        self.deltacount = 0

    def mouseReleaseEvent(self, e):
        self.setFormat("")
        if self._resizing:
            self.setMinimumWidth(20)
        self.adjustSize()
        #self.killTimer(self.deltaTimer)
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def setResizing(self, b):
        self._resizing = b
    def getResizing(self):
        return self._resizing

    def setResizeTo(self, i):
        self._resizeTo = i
    def getResizeTo(self):
        return self._resizeTo
    def defaultResizeTo(self):
        return 200

    resizing = QtCore.pyqtProperty("bool", getResizing, setResizing)
    resizeTo = QtCore.pyqtProperty("int", getResizeTo, setResizeTo, defaultResizeTo)

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault
    getStandardAction = AbstractParamWidget.getStandardAction
    setStandardAction = AbstractParamWidget.setStandardAction

    standardAction = QtCore.pyqtProperty("int", getStandardAction, setStandardAction)

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramMin = QtCore.pyqtProperty("double", getParamMin, setParamMin)
    paramMax = QtCore.pyqtProperty("double", getParamMax, setParamMax)
    paramDefault = QtCore.pyqtProperty("double", getParamDefault, setParamDefault)

class ParamMinMaxSlider(AbstractParamWidget, QtGui.QFrame):
    def __init__(self, *args):
        
        self._length = 2
        
        AbstractParamWidget.__init__(self, *args)
        QtGui.QFrame.__init__(self, *args)

        self.setMinimumSize(QtCore.QSize(30, 10))

        self.setFrameShape(self.StyledPanel)
        self.setFrameShadow(self.Sunken)
        self.setLineWidth(1)

        self._types = [float, float]
        self._paramDefault = [t() for t in self._types]
        self._paramMin = [0 for i in range(self._length)]
        self._paramMax = [1 for i in range(self._length)]
        self._btns = []

        self.setAcceptDrops(1)

        self.updateMin = self.updateState
        self.updateMax = self.updateState

        #This initiates the mouse event handlers
        self.setEnabled(self._param is not None)

    def minimumSizeHint(self):
        return QtCore.QSize(30, 5)

    def updateState(self):
        self.update()

    def paintEvent(self, ev):
        w = self.width()
        QtGui.QFrame.paintEvent(self, ev)
        try:
            mi = self._scaleTo(w, 0)
            ma = self._scaleTo(w, 1)
        except TypeError:
            mi = 0
            ma = 0
        p = QtGui.QPainter(self)
        p.setBrush(self.palette().text())
        p.drawRect(mi, 0, ma-mi, self.height())

    def setEnabled(self, boo):
        """Enables mouse event processing."""
        if boo:
            self.mousePressEvent = self.mousePressEventEnabled
            self.mouseMoveEvent = self.mouseMoveEventEnabled
            self.mouseReleaseEvent = self.mouseReleaseEventEnabled
        else:
            self.mousePressEvent = self.notEnabledDummy
            self.mouseMoveEvent = self.notEnabledDummy
            self.mouseReleaseEvent = self.notEnabledDummy

    def notEnabledDummy(self, ev):
        """Dummy method used to pass mouse events when disabled."""
        pass

    def mousePressEventEnabled(self, ev):
        """Mouse press event handler."""

        self._btns.append(ev.button())
        if QtCore.Qt.MidButton in self._btns or QtCore.Qt.ControlModifier & ev.modifiers():
            self._midButtonPrevious = ev.pos().x()
        elif QtCore.Qt.RightButton in self._btns:
            self._state[1] = max(self._scaleFrom(ev.pos().x() / float(self.width()), 1), self._state[0])
        elif QtCore.Qt.LeftButton in self._btns:
            self._state[0] = min(self._scaleFrom(ev.pos().x() / float(self.width()), 0), self._state[1])

        self._param.update()
    
    def mouseMoveEventEnabled(self, ev):
        """Mouse move event handler."""
        x = ev.pos().x()
        if QtCore.Qt.MidButton in self._btns or QtCore.Qt.ControlModifier & ev.modifiers():
            s0 = self._state[0] + (self._scaleFrom((x - self._midButtonPrevious) / float(self.width()), 0))
            s1 = self._state[1] + (self._scaleFrom((x - self._midButtonPrevious) / float(self.width()), 1))
            if not s0 < self._min[0] and not s1 > self._max[1]:
                self._state[0], self._state[1] = s0, s1
            self._midButtonPrevious = x
        elif QtCore.Qt.RightButton in self._btns:
            self._state[1] = max(self._scaleFrom(x / float(self.width()), 1), self._state[0])
        elif QtCore.Qt.LeftButton in self._btns:
            self._state[0] = min(self._scaleFrom(x / float(self.width()), 0), self._state[1])
        self._param.update()


    def mouseReleaseEventEnabled(self, ev):
        """Mouse Release event handler."""

        self._btns.remove(ev.button())
    
    def value(self):
        #FIXME: why have a value() ? 
        return self._state[0][0]

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath

    def setParamMin(self, v):
        m = self._paramMin
        m[0] = v.x()
        m[1] = v.y()

    def getParamMin(self):
        m = self._paramMin
        return QtCore.QPointF(m[0], m[1])

    def setParamMax(self, v):
        m = self._paramMax
        m[0] = v.x()
        m[1] = v.y()

    def getParamMax(self):
        m = self._paramMax
        return QtCore.QPointF(m[0], m[1])

    def setParamDefault(self, v):
        m = self._paramDefault
        m[0] = v.x()
        m[1] = v.y()

    def getParamDefault(self):
        m = self._paramDefault
        return QtCore.QPointF(m[0], m[1])

    def setStandardAction(self, v):
        m = self._standardAction
        m[0] = v.x()
        m[1] = v.y()

    def getStandardAction(self):
        m = self._standardAction
        return QtCore.QPoint(m[0], m[1])

    standardAction = QtCore.pyqtProperty("QPoint", getStandardAction, setStandardAction)

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramMin = QtCore.pyqtProperty("QPointF", getParamMin, setParamMin)
    paramMax = QtCore.pyqtProperty("QPointF", getParamMax, setParamMax)
    paramDefault = QtCore.pyqtProperty("QPointF", getParamDefault, setParamDefault)

    
class ParamGrid(AbstractParamWidget, QtGui.QFrame):
    def __init__(self, *args):
        
        self._length = 2
        
        AbstractParamWidget.__init__(self, *args)
        QtGui.QFrame.__init__(self, *args)

        self._paramMin = [0 for i in range(self._length)]
        self._paramMax = [1 for i in range(self._length)]
        self._paramDefault = [0 for i in range(self._length)]

        self.setFrameShape(self.StyledPanel)
        self.setFrameShadow(self.Sunken)
        self.setLineWidth(4)

        self._types = [float, float]
        self._paramDefault = [t() for t in self._types]
        self.resize(400,400)
        
        self.timer = None
        self.setAcceptDrops(1)
        
        self._smooth = 5

        self.updateMin = self.updateState
        self.updateMax = self.updateState

    def minimumSizeHint(self):
        return QtCore.QSize(100,100)

    def updateState(self):
        self.update()

    def paintEvent(self, ev):
        s = self.width() * 0.08
        QtGui.QFrame.paintEvent(self, ev)
        x = self._scaleTo(self.width() - s, 0)
        h = self.height() - s
        y = (h - self._scaleTo(h, 1))
        p = QtGui.QPainter(self)
        p.setBrush(self.palette().text())
        p.drawEllipse(x,y, s, s)

    def mousePressEvent(self, ev):
        if QtCore.Qt.ControlModifier & ev.modifiers():
            self.startDrag()
            return
        elif QtCore.Qt.ShiftModifier & ev.modifiers():
            self.toggleSelect()
        if not self.timer:
            self.timer = self.startTimer(40)
        pos = ev.pos()
        self.mX = self._scaleFrom(((pos.x() / float(self.width()))), 0)
        h = float(self.height())
        self.mY = self._scaleFrom((((h - pos.y()) / h)), 1)
    
    def mouseMoveEvent(self, ev):
        pos = ev.pos()
        if not self.rect().contains(pos, True):
            c = self.cursor()
            pos = self.mapFromGlobal(c.pos())
            #c.setPos(self.mapToGlobal(QtCore.QPoint(
            #    max(0, min(pos.x(), self.width())), 
            #    max(0, min(pos.y(), self.height())))))
        self.mX = self._scaleFrom(((pos.x() / float(self.width()))), 0)
        h = self.height()
        self.mY = self._scaleFrom((((h - pos.y())/ float(h))), 1)
        self.update()
    
    def mouseDoubleClickEvent(self, ev):
        self._state[0], self._state[1] = self.mX, self.mY 
        self.update()
        self._param.update()

    def mouseReleaseEvent(self, ev):
        if self.timer:
            self.killTimer(self.timer)
        self.timer = None
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def timerEvent(self, ev):
        self._state[0] = min(self._max[0], max((self.mX + (self._state[0] * self._smooth)) / (
                self._smooth + 1), self._min[0]))
        self._state[1] = min(self._max[1], max((self.mY + (self._state[1] * self._smooth)) / (
                self._smooth + 1), self._min[1]))
        #self._state[1] = (self.mY + (self._state[1] * self._smooth)) / (
        #        self._smooth + 1)
        self.update()
        self._param.update()

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath

    def setParamMin(self, v):
        m = self._paramMin
        m[0] = v.x()
        m[1] = v.y()

    def getParamMin(self):
        m = self._paramMin
        return QtCore.QPointF(m[0], m[1])

    def setParamMax(self, v):
        m = self._paramMax
        m[0] = v.x()
        m[1] = v.y()

    def getParamMax(self):
        m = self._paramMax
        return QtCore.QPointF(m[0], m[1])

    def setParamDefault(self, v):
        m = self._paramDefault
        m[0] = v.x()
        m[1] = v.y()

    def getParamDefault(self):
        m = self._paramDefault
        return QtCore.QPointF(m[0], m[1])

    def setStandardAction(self, v):
        m = self._standardAction
        m[0] = v.x()
        m[1] = v.y()

    def getStandardAction(self):
        m = self._standardAction
        return QtCore.QPoint(m[0], m[1])

    standardAction = QtCore.pyqtProperty("QPoint", getStandardAction, setStandardAction)
    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramMin = QtCore.pyqtProperty("QPointF", getParamMin, setParamMin)
    paramMax = QtCore.pyqtProperty("QPointF", getParamMax, setParamMax)
    paramDefault = QtCore.pyqtProperty("QPointF", getParamDefault, setParamDefault)
    
    
    def getSmooth(self):
        return self._smooth
    
    def setSmooth(self, v):
        self._smooth = v

    def defaultSmooth(self, v):
        return 1.0

    smooth = QtCore.pyqtProperty("double", getSmooth, setSmooth, defaultSmooth)

class ParamLineEdit(AbstractParamWidget, QtGui.QLineEdit):
    """ A simple line edit/dropbox. """
    def __init__(self, *args):
        """Constructor."""
        AbstractParamWidget.__init__(self, *args)
        QtGui.QLineEdit.__init__(self, *args)

        self._types = [str]
        self._paramDefault = [t() for t in self._types]
        self.setAcceptDrops(1)

        self.connect(self, QtCore.SIGNAL("editingFinished()"), self.on_editingFinished)

    def updateState(self):
        """Sync ui with current state."""
        QtGui.QLineEdit.setText(self, self._state[0])
    
    def updateMin(self):
        """Does nothing."""
        pass

    def updateMax(self):
        """Does nothing."""
        pass

    @QtCore.pyqtSignature("saveParam()")
    def saveParam(self):
        """Sends a request for being saved."""
        qApp.emit(QtCore.SIGNAL("saveMe"), self._param)

    def setText(self, t):
        """Sets param state, and calls for update."""
        #self._state[0] = str(t)
        self._param.update()

    def dropEvent(self, ev):
        """Drop event handler."""
        AbstractParamWidget.dropEvent(self, ev)
        self.clearFocus()

    @QtCore.pyqtSignature("")
    def on_editingFinished(self):
        self.setText(self.text())
        self.clearFocus()

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault
    getStandardAction = AbstractParamWidget.getStandardAction
    setStandardAction = AbstractParamWidget.setStandardAction

    standardAction = QtCore.pyqtProperty("int", getStandardAction, setStandardAction)

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramDefault = QtCore.pyqtProperty("QString", getParamDefault, setParamDefault)

class ParamLabel(AbstractParamWidget, QtGui.QLabel):
    """Drag-droppable OSC sending label."""

    __pyqtSignals__ = ("textChanged(const QString &)",)
    def __init__(self, *args):
        AbstractParamWidget.__init__(self, *args)
        QtGui.QLabel.__init__(self, *args)
        self.setMinimumWidth(10)

        self._types = [str]
        self._paramDefault = [t() for t in self._types]
        self.setAcceptDrops(1)

    def updateState(self):
        """Sync ui with current state."""
        QtGui.QLabel.setText(self, self._state[0])
    
    def updateMin(self):
        """Does nothing."""
        pass

    def updateMax(self):
        """Does nothing."""
        pass

    @QtCore.pyqtSignature("saveParam()")
    def saveParam(self):
        """Sends a request for being saved."""
        qApp.emit(QtCore.SIGNAL("saveMe"), self._param)

    def setText(self, text):
        """Set param state, and call for update."""
        self._state[0] = str(text)
        self._param.update()

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault
    getStandardAction = AbstractParamWidget.getStandardAction
    setStandardAction = AbstractParamWidget.setStandardAction

    standardAction = QtCore.pyqtProperty("int", getStandardAction, setStandardAction)

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramDefault = QtCore.pyqtProperty("QString", getParamDefault, setParamDefault)

class StandardActionButton(AbstractParamWidget, QtGui.QPushButton):
    def __init__(self, action, *args):
        AbstractParamWidget.__init__(self, *args)
        QtGui.QPushButton.__init__(self, *args)
        self._types = [action[2]]
        self.setParam(action[0])

        self.deltacount = 0
        cursor = QtGui.QCursor
        pos = self.mapFromGlobal(cursor().pos())
        self.move(pos.x() - (self.width()/2), pos.y() - (self.height() / 2))
        self._origo = cursor().pos()
        self._offset = self.mapFromGlobal(self._origo).y()
        self.setMouseTracking(1)
        self.setPalette(QtGui.QPalette(QtCore.Qt.white))
        self.font().setBold(1)
        self.show()
        
        self.grabMouse()
        self.setCursor(cursor(QtCore.Qt.BlankCursor))

    def updateState(self):
        pass

    def mousePressEvent(self, ev):
        QtGui.QPushButton.mousePressEvent(self, ev)
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.releaseMouse()
        self.deleteLater()

    def mouseMoveEvent(self, e):
        """Move slider up/down with mouse movement"""
        if e.pos().y() == self._offset:
            return
        adder = (self._offset - e.y())
        self.deltacount += adder
        adder *= (abs(adder) * 0.01)
        f = self._max[0] - self._min[0]
        self._state[0] = min(self._max[0], max(self._min[0], self._state[0] + (adder * f / 1000.0)))
        self._param.update()
        QtGui.QCursor.setPos(self._origo)
