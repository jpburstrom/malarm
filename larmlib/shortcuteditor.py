#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright 2009 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"

import os
import sys

from PyQt4 import QtGui, QtCore

from gesture import *

#TODO

class _ShortcutButton(QtGui.QPushButton):
    def __init__(self, model, *args):
        QtGui.QPushButton.__init__(self, *args)

        self.model = model

        self.installEventFilter(GestureEventHandler(self))
        self.font().setBold(1)

        self.startTimer(1000)
        self.grabMouse()
        self.grabKeyboard()
    
    def customEvent(self, ev):
        string = self.model.keyToString(ev.key())
        self.setText(string)

    def contextMenuEvent(self, ev):
        pass
    
    def leaveEvent(self, ev):
        self.releaseMouse()
        self.releaseKeyboard()
        self.close()

    def mouseMoveEvent(self, ev):
        if not self.rect().contains(ev.pos()):
            self.close()


class _ShortcutTableDelegate(QtGui.QItemDelegate):
    def __init__(self, *args):
        """
        Constructor.
        """
        QtGui.QItemDelegate.__init__(self, *args)

    def createEditor(self, parent, option, mi):
        return _ShortcutButton(mi.model(), parent)
    
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

        self._keymap = globals.KEYS
        #Since this was an enum to begin with, we just reverse it to
        #make lookup a bit faster...
        self._revKeymap = {}
        for k, v in self._keymap.items():
            self._revKeymap[v] = k

        for k in data:
            if data[k]:
                data[k] = self.keyToString(eval(data[k]))

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
        f = self._data.copy()
        for k in f:
            f[k] = self.stringToKey(f[k])
        return f

    def keyToString(self, key):
        """Convert key (spelled out as tuple w/ ascii codes) to string (nicer to read)."""
        #FIXME: This looks like my first php experiments
        f = list(key)
        string = u""
        for i, t in enumerate(f):
            if i > 0:
                string += u"+"
            if t[0] in ("KeyPress", "KeyRelease", "KeyHold"):
                t = tuple([t[0], self._revKeymap[t[1]]])
            else:
                t = tuple([t[0], u"%d" % t[1]])
            string += u"%s[%s]" % t
        return string
    
    def stringToKey(self, string):
        """Convert nice-read string to computer-friendly tuple."""
        string = unicode(string)
        li = [s.split("[") for s in string.split("+") if s]
        for i, t in enumerate(li):
            if t[0] in ("KeyPress", "KeyRelease", "KeyHold"):
                li[i] = tuple([t[0], self._keymap[t[1][:-1]]])
            else:
                li[i] = tuple([t[0], int(t[1][:-1])])
        return tuple(li)
    
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
        self.setSelectionMode(0)
        self.adjustSize()

    def wheelEvent(self, ev):
        pass

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
