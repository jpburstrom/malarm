#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2008 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"

from PyQt4 import QtGui, QtCore

class MyLineEdit(QtGui.QLineEdit):
    def __init__(self, *args):
        QtGui.QLineEdit.__init__(self, *args)

    def dragEnterEvent(self, ev):
        ev.acceptProposedAction()

    def dropEvent(self, ev):
        text = ev.source().objectName()
        self.setText(text)
        ev.acceptProposedAction()

