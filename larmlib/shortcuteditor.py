#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright 2009 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"

import os
import sys

from PyQt4 import QtGui, QtCore

from keyhandler import *

#TODO

class _ShortcutButton(QtGui.QLineEdit):
    def __init__(self, *args):
        QtGui.QPushButton.__init__(self, *args)
        self._keys = ""

        self.installEventFilter(KeyHandler(self))
        self.font().setBold(1)
    
    def customEvent(self, ev):
        self.setText(ev.key().text())

class _ShortcutTableDelegate(QtGui.QItemDelegate):
    def __init__(self, *args):
        """
        Constructor.
        """
        QtGui.QItemDelegate.__init__(self, *args)

    def createEditor(self, parent, option, mi):
        return _ShortcutButton(parent)
    
    def setEditorData(self, editor, mi):
        """
        @param editor -- editor widget
        @param mi -- model index
        """
        editor.setText(mi.model().data(mi, QtCore.Qt.EditRole).toString())
    
    def updateEditorGeometry(self, editor, option, mi): 
        editor.setGeometry(option.rect)
    
    def setModelData(self, editor, model, mi):
        model.setData(mi, editor.text(), QtCore.Qt.EditRole)

class _ShortcutTableModel(QtCore.QAbstractTableModel):
    """
    
    """

    def __init__(self, data, *args):
        """
        Constructor.
        """
        QtCore.QAbstractTableModel.__init__(self, *args)

        self._data = data

    def rowCount(self, mi):
        return len(self._data)

    def columnCount(self, mi):
        return 2

    def data(self, mi, role):
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return QtCore.QVariant(self._data.items()[mi.row()][mi.column()])
        else:
            return QtCore.QVariant()

    def setData(self, mi, value, role):
        if role == QtCore.Qt.EditRole:
            self._data[self._data.keys()[mi.row()]] = value
            return True

    def flags(self, mi):
        if mi.column() == 1:
            return QtCore.QAbstractTableModel.flags(self, mi) | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.QAbstractTableModel.flags(self, mi)

    def getShortcuts(self):
        return self._data.copy()
    
class ShortcutTableView(QtGui.QTableView):
    """
    
    """

    def __init__(self, data, *args):
        """
        Constructor.
        """
        QtGui.QTableView.__init__(self, *args)
        
        model = _ShortcutTableModel(data, self)
        self.setModel(model)

        self.setItemDelegateForColumn(1, _ShortcutTableDelegate(self))

        self.setEditTriggers(self.AllEditTriggers)
        self.adjustSize()

class ShortcutEditor(QtGui.QDialog):
    """
    
    """

    def __init__(self, settings, *args):
        """
        Constructor.
        """
        QtGui.QDialog.__init__(self, *args)

        layout = QtGui.QVBoxLayout(self)

        self._settings = settings

        self.table = ShortcutTableView(settings.getSettings(), self)
        layout.addWidget(self.table)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        layout.addWidget(self.buttonBox)

        self.connect(self, QtCore.SIGNAL("accepted()"), self.on_accepted)

    def on_accepted(self):
        [self._settings.update(k, unicode(v)) for k, v in self.table.model().getShortcuts().items()]

if __name__ == "__main__":
    import persistance
    a = QtGui.QApplication(sys.argv)
    d = persistance.SettingsHandler("/tmp/foo")
    win = ShortcutEditor(d)
    win.show()
    a.exec_()
    print d.getSettings()
