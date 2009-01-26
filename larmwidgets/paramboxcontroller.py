#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2008 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision: 70 $"

import os
import sys

import datetime

from PyQt4 import QtGui, QtCore, uic

from paramboxcontrollerui import Ui_Form

class ParamBoxController(Ui_Form, QtGui.QWidget):

    __pyqtSignals__ = (
            "loadSnapshot(const QString &)",
            "saveSnapshot(const QString &)",
            )

    def __init__(self, *args):  
        QtGui.QWidget.__init__(self, *args)
        self.setupUi(self)

        self.presetComboBox.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        for o in self.findChildren(QtGui.QPushButton):
            o.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.presetComboBox.setEditable(0)
        self.presetComboBox.clear()
        
        self._snapshots = {}
        self._params = set()
        self._grouplabel = QtCore.QString()
        
        self.connect(QtGui.qApp, QtCore.SIGNAL("recallPresets(const QString &, PyQt_PyObject)"), self.addPresets)

    @QtCore.pyqtSignature("const QString &")
    def on_presetComboBox_activated(self, s):
        QtGui.qApp.emit(QtCore.SIGNAL("loadPreset(const QString &, const QString &)"), self._grouplabel, s)

    @QtCore.pyqtSignature("const QPoint &")
    def on_presetComboBox_customContextMenuRequested(self, qp):
        """Interface for saving, renaming and deleting presets"""
        #FIXME: preset name standard. merged qstring? tuple? two qstrings?
        p = self.presetComboBox
        old = p.currentText()
        pp = QtGui.QMenu()
        a = pp.addAction("Save")
        if not old:
            a.setEnabled(0)
        pp.addAction("Save as...")
        pp.addAction("Rename")
        pp.addAction("Delete")
        a = pp.exec_(p.mapToGlobal(qp))
        
        if not a:
            pass

        elif a.text() == "Save" and self._confirm("Save preset \"%s\"?" % str(old)):
            QtGui.qApp.emit(QtCore.SIGNAL(
                "savePreset(const QString &, const QString &, PyQt_PyObject)"), self._grouplabel, old, self._params)

        elif a.text() == "Save as...":
            new, boo = QtGui.QInputDialog.getText(self, "Save Preset as", "Enter preset name:")
            if boo and (p.findText(new) is -1 or self._confirm("Overwrite preset %s?" % str(new))):
                p.addItem(new)
                p.setCurrentIndex(p.count() - 1)
                QtGui.qApp.emit(QtCore.SIGNAL(
                    "savePreset(const QString &, const QString &, PyQt_PyObject)"), self._grouplabel, new, self._params)
        
        elif a.text() == "Rename":
            new, boo = QtGui.QInputDialog.getText(self, "Rename Preset", "Enter new name:")
            if boo:
                p.setItemText(p.currentIndex(), new)
                QtGui.qApp.emit(QtCore.SIGNAL(
                    "renamePreset(const QString &, const QString &, const QString &)"), self._grouplabel, old, new)
        
        elif a.text() == "Delete" and self._confirm("Delete preset %s" % str(old)):
            p.removeItem(p.currentIndex())
            QtGui.qApp.emit(QtCore.SIGNAL("deletePreset(const QString &, const QString &)"), self._grouplabel, old)
        
        del pp
    
    def _confirm(self, s):
        """Popup confirmation dialog.

        @returns bool
        """
        ok = QtGui.QMessageBox.Ok
        cancel = QtGui.QMessageBox.Cancel
        if QtGui.QMessageBox.question(self, "Confirm", s, cancel | ok, ok) == ok:
            return True
        else:
            return False
    ###########
    #snapshot LOAD
    ##########
    @QtCore.pyqtSignature("")
    def on_snapshotButton_1_pressed(self):
        self.loadSnapshot(1)

    @QtCore.pyqtSignature("")
    def on_snapshotButton_2_pressed(self):
        self.loadSnapshot(2)

    @QtCore.pyqtSignature("")
    def on_snapshotButton_3_pressed(self):
        self.loadSnapshot(3)

    @QtCore.pyqtSignature("")
    def on_snapshotButton_4_pressed(self):
        self.loadSnapshot(4)

    @QtCore.pyqtSignature("")
    def on_snapshotButton_A_pressed(self):
        self.loadSnapshot("A")

    @QtCore.pyqtSignature("")
    def on_snapshotButton_B_pressed(self):
        self.loadSnapshot("B")

    def loadSnapshot(self, snap):
        """Send load snapshot signal
        snap -- Snapshot key
        """
        [p.loadSnapshot(snap) for p in self._params]
        self.emit(QtCore.SIGNAL("loadSnapshot(const QString &)"), QtCore.QString(snap))

    ###########
    #snapshot SAVE
    ##########
    
    @QtCore.pyqtSignature("const QPoint &")
    def on_snapshotButton_1_customContextMenuRequested(self):
        self.saveSnapshot(1)

    @QtCore.pyqtSignature("const QPoint &")
    def on_snapshotButton_2_customContextMenuRequested(self):
        self.saveSnapshot(2)

    @QtCore.pyqtSignature("const QPoint &")
    def on_snapshotButton_3_customContextMenuRequested(self):
        self.saveSnapshot(3)

    @QtCore.pyqtSignature("const QPoint &")
    def on_snapshotButton_4_customContextMenuRequested(self):
        self.saveSnapshot(4)

    @QtCore.pyqtSignature("const QPoint &")
    def on_snapshotButton_A_customContextMenuRequested(self):
        self.saveSnapshot("A")

    @QtCore.pyqtSignature("const QPoint &")
    def on_snapshotButton_B_customContextMenuRequested(self):
        self.saveSnapshot("B")

    def saveSnapshot(self, snap):
        """Send load snapshot signal
        snap -- Snapshot key
        """
        s = self.sender()
        f = s.font()
        f.setBold(True)
        s.setFont(f)
        s.setText("[%s]" % snap)
        [p.saveSnapshot(snap) for p in self._params]
        self.emit(QtCore.SIGNAL("saveSnapshot(const QString &)"), QtCore.QString(snap))

    @QtCore.pyqtSignature("")
    def getGroupLabel(self):
        """Get group label, for designer.
        """
        return self._grouplabel

    @QtCore.pyqtSignature("const QString &")
    def setGroupLabel(self, s):
        """Set group label, for designer.
        """
        self._grouplabel = s
        self.mainLabel.setText(s)
        
    groupLabel = QtCore.pyqtProperty("const QString &", getGroupLabel, setGroupLabel)

    @QtCore.pyqtSignature("const QString &, PyQt_PyObject")
    def addPresets(self, group, presetlist):
        if group == self._grouplabel:
            self.presetComboBox.addItems(presetlist)

    @QtCore.pyqtSignature("PyQt_PyObject")
    def addParams(self, params):
        """Add Params as children.
        
        @param params -- iterable of params to add
        """
        [self._params.add(p) for p in params]
    
    @QtCore.pyqtSignature("int")
    def on_snapshotSlider_valueChanged(self, i):
        i = i * 0.001
        [p.interpolateSnapshot("A", "B", i) for p in self._params]


if __name__ == '__main__':
    a = QtGui.QApplication(sys.argv)
    w = ParamBoxController(None)
    w.setGroupLabel("foo")
    w.show()
    sys.exit(a.exec_())
