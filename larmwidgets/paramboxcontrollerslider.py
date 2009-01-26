#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2008 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"

from PyQt4 import QtGui, QtCore

class ParamBoxControllerSlider(QtGui.QSlider):
    """
    A very special slider.
    """

    def __init__(self, *args):
        """
        Constructor.
        """
        QtGui.QSlider.__init__(self, *args)

    def mousePressEvent(self, ev):
        QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.width(),0)))
        self.origo = QtCore.QPoint(ev.pos())
        self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))

    def mouseMoveEvent(self, ev):
        p = ev.pos()
        if p.y() == 0:
            return
        self.setValue(self.value() - p.y())
        QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.width(),0)))

    def mouseReleaseEvent(self, ev):
        QtGui.QCursor.setPos(self.mapToGlobal(self.origo))
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

