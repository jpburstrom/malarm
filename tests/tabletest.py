#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2007 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"


import os
import sys
import random
import copy

from PyQt4 import QtGui, QtCore, uic

import tabletestUI
from qtosc import Emitter, OscHelper
from param import *

MainUI, dummy = uic.loadUiType(os.path.join(sys.path[0], "tabletest.ui"))

class PixelDelegate(QtGui.QItemDelegate):
    
    def __init__(self, *args):
        QtGui.QItemDelegate.__init__(self, *args)

        self.pixelSize = 24

    def paint (self, painter, option, index):

        if (option.state & QtGui.QStyle.State_Selected):
           painter.fillRect(option.rect, QtGui.QColor(255,255, 200))
        

        #size = min((option.rect.width(), option.rect.height()))
        size = index.model().data(index, QtCore.Qt.DisplayRole)
        w = max(size[0]/255.0, 0.03)
        h = max(size[1]/255.0, 0.03)
        sat = size[2]
        r = option.rect
        width = r.width() * w
        height = r.height() * h

        #if (radius == 0.0):
        # return;

        painter.save();
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(QtCore.Qt.NoPen);
        color = QtGui.QColor()
        color.setHsv(0, sat, 128)
        painter.setBrush(QtGui.QBrush(color))

        painter.drawRoundedRect(QtCore.QRectF(r.x() + (r.width() * ((1-w) / 2)),
                                 r.y() + (r.height() * ((1-h) / 2)),
                                 width, height), 5.0, 5.0)
        painter.restore();

    def sizeHint(self, option, index):
        return QSize(pixelSize, pixelSize);

    def createEditor(self, parent, option, index):
        editor = MyEditor(parent, index);
        editor.setMinimum(0)
        editor.setMaximum(255)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        editor.setValue(value)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def setModelData(self, editor, model, index):
        value = editor.value()
        #del editor
        model.setData(index, value, QtCore.Qt.EditRole)

    def setPixelSize(self, size):
        self.pixelSize = size

class MyEditor(QtGui.QLabel):
    def __init__(self, parent, index, *args):
        QtGui.QLabel.__init__(self, parent, *args)

        self.setMargin(0)
        self.setAlignment(QtCore.Qt.AlignLeft)

        self._value = None
        

        self.initpos = self.cursor().pos()
        self.model = parent.parent().model()
        self.mi = parent.parent().currentIndex()
        self.min = None
        self.max = None
        self.olddelta = 1
        self.delta = 0

        self.easingTimer = QtCore.QTimer(self)
        self.easingTimer.setInterval(10)
        self.doEasing = False

        self.connect(self.easingTimer, QtCore.SIGNAL("timeout()"), self.easing)
        self.connect(self.model, QtCore.SIGNAL("deltaChanged"), self.setValueFromDelta)

    def setValueFromDelta(self, v, mult=2.0, buttons=[]):
        if v and buttons:
            v = (v + self.olddelta) / float(mult)
            self.olddelta = v
            self.delta = v
            l = self.value()
            for i in buttons:
                i = i - 1
                i = min(i, 2)
                l[i] = l[i] + v
            self.setValue(l)

    def mouseMoveEvent(self, ev):
        if self.doEasing or not self.model.buttons: 
            return
        newpos = self.cursor().pos().y()
        self.delta = (self.initpos.y() - newpos)
        self.model.emit(QtCore.SIGNAL("deltaChanged"), self.delta, 2.0, self.model.buttons)
        self.cursor().setPos(self.initpos)

    def mousePressEvent(self, ev):
        self.model.addbutton(ev.button())
        if self.doEasing:
            self.easingTimer.stop()
            self.doEasing = False
            self.grabMouse()
            self.setMouseTracking(1)
        ev.ignore()

    def mouseReleaseEvent(self, ev):
        self.releaseMouse()
        self.easingbuttons = copy.copy(self.model.buttons)
        self.model.removebutton(ev.button())
        self.setMouseTracking(0)
        self.released = True

        if abs(self.delta) > 0.0002:
            self.doEasing = True
            self.easingTimer.start()
        ev.ignore()

    def easing(self):
        delta = self.delta
        if abs(delta) > 0.0002 and self._value not in (self.min, self.max):
            self.model.emit(QtCore.SIGNAL("deltaChanged"), delta, 2.2, self.easingbuttons)
        else:
            self.easingTimer.stop()

    def setMaximum(self, m):
        self.max = m

    def setMinimum(self, m):
        self.min = m

    def setValue(self, v):
        self._value = self._within(copy.copy(v))
        self.setText("%.02f|%.02f|%.02f" % (self._value[0], self._value[1], self._value[2]))
        self.model.setData(self.mi, self._value, QtCore.Qt.EditRole)

    def value(self):
        return copy.copy(self._value)

    def showEvent(self, ev):
        self.grabMouse()
        self.setMouseTracking(1)
        QtGui.QLabel.showEvent(self,ev)

    def _within(self, v):
        try:
            v = [min(max(i, self.min), self.max) for i in v]
        except AttributeError:
            pass
        return v

class ImageModel(QtCore.QAbstractTableModel):
    def __init__(self, *args):
        QtCore.QAbstractTableModel.__init__(self, *args)

        self.dat = []
        for f in range(10):
            r = random.random
            self.dat.append([[r()*255, r()*255, r()*255] for f in range(10)])

        self.buttons = []

    def setImage(self, image):
        self.modelImage = image
        self.reset()
        
    def rowCount(self, parent):
        return len(self.dat)

    def columnCount(self, parent):
        return len(self.dat[0])

    def data(self, index, role):
        if (not index.isValid() or role not in  (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole)):
            return QtCore.QVariant()
        return self.dat[index.row()][index.column()]

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.QAbstractItemModel.flags(self, index) | QtCore.Qt.ItemIsEditable

    def setData(self, index, value, role):
        if (index.isValid() and role == QtCore.Qt.EditRole):
            self.dat[index.row()][index.column()] = value
            self.emit(QtCore.SIGNAL("dataChanged"), (index, index))
            return True
        return False

    def addbutton(self, b):
        if b not in self.buttons:
            self.buttons.append(b)
    
    def removebutton(self, b):
        try:
            self.buttons.remove(b)
        except ValueError:
            pass

class DotTable(QtGui.QTableView):
    def __init__(self, *args):
        QtGui.QTableView.__init__(self, *args)
        
        self.horizontalHeader().setMinimumSectionSize(24)
        self.verticalHeader().setMinimumSectionSize(24)
        self.setSelectionMode(self.ExtendedSelection)
        #self.setShowGrid(0)
        #self.setMouseTracking(1)

    def selectionChanged(self, sel, desel):
        for index in sel.indexes():
            self.openPersistentEditor(index)
        for index in desel.indexes():
            self.closePersistentEditor(index)

    def mousePressEvent(self, ev):
        if not ev.modifiers():
            self.model().addbutton(ev.button())
            QtGui.QTableView.mousePressEvent(self, ev)
        elif ev.modifiers() & QtCore.Qt.ShiftModifier:
            pass
            #TODO: drag and drop copy values

    def mouseReleaseEvent(self, ev):
        self.model().removebutton(ev.button())
        QtGui.QTableView.mouseReleaseEvent(self, ev)


class MainWindow(MainUI, QtGui.QMainWindow):
    def __init__(self, *args):  
        QtGui.QMainWindow.__init__(self, *args)
        self.setupUi(self)

        self.tableView = DotTable(self.centralwidget)
        self.verticalLayout.addWidget(self.tableView)

        model = ImageModel(self)
        self.tableView.setModel(model)

        delegate = PixelDelegate(self)
        self.tableView.setItemDelegate(delegate)


        #OSC setup

        self.oscServer = OscHelper()
        self.oscServer.start()


a = QtGui.QApplication(sys.argv)


win = MainWindow()
win.show()
sys.exit(a.exec_())
