#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2009 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"


import os
import sys
import copy

from PyQt4 import QtGui, QtCore, uic, QtDesigner

import larmlib.param as param

#ParamDialog, dummy = uic.loadUiType(os.path.join(sys.path[0], "widgetparamdialog.ui"))

class MyListModel(QtCore.QAbstractListModel):
    def __init__(self, list = [], *args):
        QtCore.QAbstractListModel.__init__(self, *args)

        self._list = list

    def rowCount(self, mi):
        return len(self._list)

    def data(self, index, role):
        if (not index.isValid() or role != QtCore.Qt.DisplayRole):
            return QtCore.QVariant()
        else:
            return QtCore.QVariant(str(self._list[index.row()]))

    def setList(self, li):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, len(self._list))
        self._list = []
        self.endRemoveRows()
        self.beginInsertRows(QtCore.QModelIndex(), 0, len(li))
        self._list.extend(li)
        self.endInsertRows()

    def append(self, param):
        i = len(self._list)
        self.beginInsertRows(QtCore.QModelIndex(), i, i+1)
        self._list.append(param)
        self.endInsertRows()

    def extend(self, param):
        i = len(self._list)
        self.beginInsertRows(QtCore.QModelIndex(), i, i + len(param))
        self._list.extend(param)
        self.endInsertRows()

    def insert(self, i, param):
        self.beginInsertRows(QtCore.QModelIndex(), i, i + 1)
        self._list.insert(index, param)
        self.endInsertRows()

    def remove(self, param):
        i = self._list.index(param)
        self.beginRemoveRows(QtCore.QModelIndex(), i, i+1)
        self._list.remove(param)
        self.endRemoveRows()

    def pop(self, index=None):
        i = index or len(self._list) - 1 
        self.beginRemoveRows(QtCore.QModelIndex(), i, i+1)
        return self._list.pop(i)
        self.endRemoveRows()

    def count(self, i):
        return self._list.count(i)

    def reverse(self):
        self._list.reverse()

    def sort(self):
        self._list.sort()

    def __iter__(self):
        for i in self._list:
            yield i

    def __repr__(self):
        return self._list.__repr__()

    def __str__(self):
        return self._list.__str__()

    def __setitem__(self, k, v):
        self._list[k] = v

    def __getitem__(self, k):
        if isinstance(k, slice):
            return [self.__getitem__(i)
                    for i in xrange(k.start, k.stop, k.step)]
        return self._list[k]

    def __getslice__(self, i, j):
        return self._list[i:j]

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
        self._types = [None]
        #These are shared by the param (that is, the param passes the reference to its own
        #_min and _max lists upon connection)
        self._min = [0 for i in range(self._length)]
        self._max = [1 for i in range(self._length)]
        self._state = None
        
        
        self._paramPath = ""
        #These are used as pyqtProperties, to be set by designer.
        #They update the param when connecting to it, making the param effectively stupid.
        self._paramDefault = None
        self._paramMin = [0 for i in range(self._length)]
        self._paramMax = [1 for i in range(self._length)]
        
        self.paramUpdateSignal = "valueChanged(int)" #gets connected to Param setState method

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

    def setParam(self, param):
        """Method called by the connected param, to set the props of the widget.
        
        widslot (int) : internal widget slot for param to connect to
        param (Param) : param object
        paramslot (int) : internal param slot
        """
        if param.typecheck(self._types):
            self._param = param
            #FIXME: set min, max, default
            self.updateParamConnections()
            #Pass on our own values to param
            if self._length == 1:
                self._paramMin = self._min[0]
                self._paramMax = self._max[0]
            self._param.setMinValue[self._min]
            self._param.setMaxValue[self._min]
            #And get them as references from param.
            self._min = self._param.getMinReference()
            self._max = self._param.getMaxReference()
            self._state = self._param.getStateReference()
            self.connect(param, QtCore.SIGNAL("paramUpdate"), self.guiUpdate)
        else:
            raise TypeError, "Widget=>Param connection didn't work."

    def removeParam(self, param):
        param.disconnect(self, QtCore.SIGNAL(self.paramUpdateSignal))
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
        self.setState(str(text))
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

    def getParamMin(self):
        """Set min value(s).

        Sets the min value(s) used to set up the connection with the param.
        After connecting, this has no effect.
        """
        if self._length == 1:
            return self._paramMin[0]

    def setParamMax(self, v):
        """Set max value(s).

        Set the max value(s) used to set up the connection with the param.
        """
        if self._length is 1:
            self._paramMax[0] = v

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

    def getParamDefault(self):
        """Set default value(s).

        Sets the default value(s) used to set up the connection with the param.
        After connecting, this has no effect.
        """
        if self._length == 1:
            return self._paramDefault[0]
        else:
            return tuple(self._paramDefault)
    

class ParamSpinBox(AbstractParamWidget, QtGui.QSpinBox):

    def __init__(self, *args):
        AbstractParamWidget.__init__(self, *args)
        QtGui.QSpinBox.__init__(self, *args)

        self._types = [int]
        self._paramDefault = [t() for t in self._types]

        self.setAcceptDrops(1)

        self._foo = "pripp"
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

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramMin = QtCore.pyqtProperty("int", getParamMin, setParamMin)
    paramMax = QtCore.pyqtProperty("int", getParamMax, setParamMax)
    paramDefault = QtCore.pyqtProperty("int", getParamDefault, setParamDefault)
        
class ParamPushButton(AbstractParamWidget, QtGui.QPushButton):
    def __init__(self, *args):
        AbstractParamWidget.__init__(self, *args)
        QtGui.QPushButton.__init__(self, *args)

        self._types = [param.Bang]
        self._paramDefault = [t() for t in self._types]
        self.setAcceptDrops(1)
        self.setContentsMargins(1,1,1,1)

    def updateState(self):
        #FIXME: These three shoudl not do anything, perhaps
        self.animateClick()

    def updateMin(self):
        pass

    def updateMax(self):
        pass

    @QtCore.pyqtSignature("saveParam()")
    def saveParam(self):
        qApp.emit(QtCore.SIGNAL("saveMe"), self._param)

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
                        
class ParamToggleButton(ParamPushButton):
    def __init__(self, *args):
        ParamPushButton.__init__(self, *args)

        self._types = [bool]
        self._paramDefault = [t() for t in self._types]
        self.setCheckable(1)
        self.color = QtGui.qApp.palette()
        self.green = QtGui.QPalette(QtCore.Qt.green)
        
        self.connect(self, QtCore.SIGNAL("toggled(bool)"), self.toggleColors)

    def updateState(self):
        self.setValue(self._state[0])

    def updateMin(self):
        pass

    def updateMax(self):
        pass

    def toggleColors(self, boo):
        if boo:
            self.setPalette(self.green)
        else:
            self.setPalette(self.color)

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramDefault = QtCore.pyqtProperty("bool", getParamDefault, setParamDefault)

class ParamThreeStateButton(ParamPushButton):
    def __init__(self, *args):
        ParamPushButton.__init__(self, *args)

        self._types = [int]
        self._paramDefault = [t() for t in self._types]

        self._colors = (
                QtGui.qApp.palette(),
                QtGui.QPalette(QtCore.Qt.green),
                QtGui.QPalette(QtCore.Qt.red)
                )

    def updateState(self):
        s = self._state[0]
        self.setPalette(self._colors[s])

    def updateMin(self):
        pass

    def updateMax(self):
        pass

    def mousePressEvent(self, ev):
        if QtCore.Qt.ShiftModifier & ev.modifiers() == QtCore.Qt.ShiftModifier:
            self.toggleSelect()
            return
        s = ev.button()
        if s == 1 and self._state[0] is not 1:
            ns = 1
        elif s == 2 and self._state[0] is not 2:
            ns = 2
        elif s in (1,2):
            ns = 0
        else:
            return
        self.setText(str(ns))
        self._param.setState(s)

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault

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

        self.accelerator = 0
        self.deltacount = 0
        self.valuestring = "%.02f"
        
        #We send a custom valueChanged signal, otherwise the updates 
        #from QProgressbar will destroy things...
        self.paramUpdateSignal = "thisValueChanged"
        QtGui.QProgressBar.setRange(self, 0,1000)

        self.setAcceptDrops(1)
        self.dblclick_value = self._min[0]

        self.connect(QtGui.qApp, QtCore.SIGNAL("deltaChanged"), self.doDelta)
        
        self.updateMin = self.updateState
        self.updateMax = self.updateState

    @QtCore.pyqtSignature("saveParam()")
    def saveParam(self):
        print "saveme"
        qApp.emit(QtCore.SIGNAL("saveMe"), self._param)

    def updateState(self):
        #this handles gui
        self.setValue(self._scaleTo(1000))
        if self.width() > 30:
            QtGui.QProgressBar.setFormat(self, self.valuestring % self._state[0])

    def doDelta(self, d):
        if self.selected and self.sender() != self:
            f = self._max[0] - self._min[0]
            self._state[0] += (d * f / 1000.0)
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
        self.deltaTimer = self.startTimer(10)
        if QtCore.Qt.ControlModifier & e.modifiers():
            self.startDrag()
            return
        elif QtCore.Qt.ShiftModifier & e.modifiers():
            self.toggleSelect()
        else:
            self.setMinimumWidth(200)
            self.raise_()
        self.origo = self.mapToGlobal(e.pos())
        self.offset = e.pos().y()
        self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        #print self.origo.y()

    def mouseMoveEvent(self, e):
        """Move slider up/down with mouse movement"""
        if e.pos().y() == self.origo.y():
            return
        adder = (self.offset - e.y())
        self.deltacount += adder
        adder *= self.accelerator
        self._state[0] = max(self._min[0], min(self._max[0], self._state[0] + adder))
        #This sends to param
        self._param.update()
        #Sending to other (selected) gui elements
        QtGui.qApp.emit( QtCore.SIGNAL("deltaChanged"), adder)
        QtGui.QCursor.setPos(self.origo)

    def timerEvent(self, e):
        self.accelerator = (self.accelerator + max(abs(self.deltacount) * 0.0001, 0.0001)) / 2
        self.deltacount = 0

    def mouseReleaseEvent(self, e):
        self.setFormat("")
        self.setMinimumWidth(20)
        self.adjustSize()
        self.killTimer(self.deltaTimer)
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramMin = QtCore.pyqtProperty("double", getParamMin, setParamMin)
    paramMax = QtCore.pyqtProperty("double", getParamMax, setParamMax)
    paramDefault = QtCore.pyqtProperty("double", getParamDefault, setParamDefault)

class ParamMinMaxSlider(AbstractParamWidget, QtGui.QFrame):
    def __init__(self, *args):
        
        self._length = 2
        
        AbstractParamWidget.__init__(self, *args)
        QtGui.QFrame.__init__(self, *args)

        self.setFrameShape(self.StyledPanel)
        self.setFrameShadow(self.Sunken)
        self.setLineWidth(1)

        self.paramUpdateSignal = "valueChanged"

        self._types = [float, float]
        self._paramDefault = [t() for t in self._types]
        self._btns = []

        self.setAcceptDrops(1)

        self.updateMin = self.updateState
        self.updateMax = self.updateState

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
            pass
        p = QtGui.QPainter(self)
        p.setBrush(self.palette().text())
        p.drawRect(mi, 0, ma-mi, self.height())

    def mousePressEvent(self, ev):
        self._btns.append(ev.button())
        if QtCore.Qt.RightButton in self._btns:
            self._state[1] = self._scaleFrom(ev.pos().x() / float(self.width()), 1)
        if QtCore.Qt.LeftButton in self._btns:
            self._state[0] = self._scaleFrom(ev.pos().x() / float(self.width()), 0)
        self._param.update()
    
    def mouseMoveEvent(self, ev):
        if QtCore.Qt.RightButton in self._btns:
            self._state[1] = self._scaleFrom(ev.pos().x() / float(self.width()), 1)
        if QtCore.Qt.LeftButton in self._btns:
            self._state[0] = self._scaleFrom(ev.pos().x() / float(self.width()), 0)
        self._param.update()

    def mouseReleaseEvent(self, ev):
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
        return QtCore.QPoint(m[0], m[1])

    def setParamMax(self, v):
        m = self._paramMax
        m[0] = v.x()
        m[1] = v.y()

    def getParamMax(self):
        m = self._paramMax
        return QtCore.QPoint(m[0], m[1])

    def setParamDefault(self, v):
        m = self._paramDefault
        m[0] = v.x()
        m[1] = v.y()

    def getParamDefault(self):
        m = self._paramDefault
        return QtCore.QPoint(m[0], m[1])

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramMin = QtCore.pyqtProperty("QPoint", getParamMin, setParamMin)
    paramMax = QtCore.pyqtProperty("QPoint", getParamMax, setParamMax)
    paramDefault = QtCore.pyqtProperty("QPoint", getParamDefault, setParamDefault)

    
class ParamGrid(AbstractParamWidget, QtGui.QFrame):
    def __init__(self, *args):
        
        self._length = 2
        
        AbstractParamWidget.__init__(self, *args)
        QtGui.QFrame.__init__(self, *args)

        self.setFrameShape(self.StyledPanel)
        self.setFrameShadow(self.Sunken)
        self.setLineWidth(4)

        self.paramUpdateSignal = "valueChanged"

        self._types = [float, float]
        self._paramDefault = [t() for t in self._types]
        self.resize(400,400)
        
        self.timer = None
        self.setAcceptDrops(1)
        
        self.smooth = 1

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
        self.mY = self._scaleFrom(((pos.y() / float(self.height()))), 1)
    
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
        self._state[0] = min(self._max[0], max((self.mX + (self._state[0] * self.smooth)) / (
                self.smooth + 1), self._min[0]))
        self._state[1] = min(self._max[1], max((self.mY + (self._state[1] * self.smooth)) / (
                self.smooth + 1), self._min[1]))
        #self._state[1] = (self.mY + (self._state[1] * self.smooth)) / (
        #        self.smooth + 1)
        self.update()
        self._param.update()
    
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
        return QtCore.QPoint(m[0], m[1])

    def setParamMax(self, v):
        m = self._paramMax
        m[0] = v.x()
        m[1] = v.y()

    def getParamMax(self):
        m = self._paramMax
        return QtCore.QPoint(m[0], m[1])

    def setParamDefault(self, v):
        m = self._paramDefault
        m[0] = v.x()
        m[1] = v.y()

    def getParamDefault(self):
        m = self._paramDefault
        return QtCore.QPoint(m[0], m[1])

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramMin = QtCore.pyqtProperty("QPoint", getParamMin, setParamMin)
    paramMax = QtCore.pyqtProperty("QPoint", getParamMax, setParamMax)
    paramDefault = QtCore.pyqtProperty("QPoint", getParamDefault, setParamDefault)

class ParamLineEdit(AbstractParamWidget, QtGui.QLineEdit):
    """ A simple line edit/dropbox """
    def __init__(self, *args):
        AbstractParamWidget.__init__(self, *args)
        QtGui.QLineEdit.__init__(self, *args)

        self._types = [str]
        self._paramDefault = [t() for t in self._types]
        self.setAcceptDrops(1)
        #Some hackish renames
        self.setState = self.setText
        self.setValue = self.setText
        self.value = self.text

    def updateState(self):
        self.setText(self._state[0])
    
    def updateMin(self):
        pass

    def updateMax(self):
        pass

    @QtCore.pyqtSignature("saveParam()")
    def saveParam(self):
        qApp.emit(QtCore.SIGNAL("saveMe"), self._param)

    def dropEvent(self, ev):
        AbstractParamWidget.dropEvent(self, ev)
        self._state[0] = str(self.text())
        self._param.update()
        self.clearFocus()

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramDefault = QtCore.pyqtProperty("QString", getParamDefault, setParamDefault)

class ParamLabel(AbstractParamWidget, QtGui.QLabel):

    __pyqtSignals__ = ("textChanged(const QString &)",)
    def __init__(self, *args):
        AbstractParamWidget.__init__(self, *args)
        QtGui.QLabel.__init__(self, *args)

        self._types = [str]
        self._paramDefault = [t() for t in self._types]
        self.setAcceptDrops(1)
        #Some hackish renames
        self.setState = self.setText
        self.setValue = self.setText
        self.value = self.text

    def updateState(self):
        self.setText(self._state[0])
    
    def updateMin(self):
        pass

    def updateMax(self):
        pass

    @QtCore.pyqtSignature("saveParam()")
    def saveParam(self):
        qApp.emit(QtCore.SIGNAL("saveMe"), self._param)

    def dropEvent(self, ev):
        AbstractParamWidget.dropEvent(self, ev)
        self._state[0] = str(self.text())
        self.emit(QtCore.SIGNAL("textChanged(const QString &)"), self.text())
        self._param.update()

    setParamPath = AbstractParamWidget.setParamPath
    getParamPath = AbstractParamWidget.getParamPath
    setParamMin = AbstractParamWidget.setParamMin
    getParamMin = AbstractParamWidget.getParamMin
    setParamMax = AbstractParamWidget.setParamMax
    getParamMax = AbstractParamWidget.getParamMax
    setParamDefault = AbstractParamWidget.setParamDefault
    getParamDefault = AbstractParamWidget.getParamDefault

    paramPath = QtCore.pyqtProperty("QString", getParamPath, setParamPath)
    paramDefault = QtCore.pyqtProperty("QString", getParamDefault, setParamDefault)

class ParamBox(QtGui.QFrame):
    """A Grouping box for Param widgets.

    Param Widgets are grouped by ParamBox, which groups the widgets and carries
    some signals and slots for snapshot and preset save/load.
    Snapshots are stored in memory, not on disk. To make a session-persistent 
    snapshot, the snapshot is sent to the saving class, which gives it a name 
    and stores it on disk as a preset.

    @signal paramsCollected(): Emitted on initializing, when all child Params is collected in a neat list.
    """

    #TODO: Should this box have built-in ui for snapshot/save/interpolation?
    #TODO: Snapshot randomization/misinterpretation
    __pyqtSignals__ = ("paramsCollected(PyQt_PyObject)",)

    def __init__(self, *args):
        QtGui.QFrame.__init__(self, *args)

        self._params = tuple() #list of child params, generated by collectParams()

        self.connect(QtGui.qApp, QtCore.SIGNAL("init"), self.initialize)

    def initialize(self):
        """Initializing the object, after all children objects are in place.
        
        Collects all children Params, and sends out the paramsCollected signal.
        """

        self._collectParams(True)
        self.emit(QtCore.SIGNAL("paramsCollected(PyQt_PyObject)"), self._params)

    def _collectParams(self, force = False):
        """Collects all child widget params as a list.
        
        @param force bool

        Collection is normally just done once, but can be forced by
        adding a boolean True as first argument.
        """
        if self._params and not force:
            return
        p = []
        for child in self.findChildren(AbstractParamWidget):
            try:
                p.extend(child.params)
            except AttributeError:
                pass
        self._params = tuple([p[0] for p in p if p is not None])

    def getParams(self):
        """Returns children Params."""
        return self._params
    #FIXME: This should be a list. It's not even used. 
    #params = QtCore.pyqtProperty("QString", getParams)


