#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2008 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision: 70 $"


import os
import sys
import copy
import shutil
import re

import datetime

from PyQt4 import QtGui, QtCore, uic

MainUI, dummy = uic.loadUiType(os.path.join(os.path.dirname(__file__), "forms/parameditor.ui"))

#TODO: update file writing to use persistance module

class ParamEditor(MainUI, QtGui.QDialog):
    def __init__(self, *args):  
        QtGui.QDialog.__init__(self, *args)
        self.setupUi(self)

        
        self.path = ""
        self.currentAtom = 0
        self.atoms = [] #Definition list: type, default, min, max, widget, widget slot
        self.defaultEdit.hide()
        self.defaultEditLabel.hide()
        self.__default = "int"

        self.buttonBox.setStandardButtons(self.buttonBox.Ok|self.buttonBox.Cancel)

        self.widgetEdit.setAcceptDrops(1)

    def openParams(self):
        try:
            f = open(self.filename, 'r')
        except IOError:
            self.params = {}
            print "Param definition list doesn't exist"
        else:
            config_string = f.read()
            try:
                self.params = eval(config_string)
            except:
                QtGui.QMessageBox.warning(self, "Open error", "There's something wrong with the file. \
                %s \nA backup is made, and a new file is created" % self.filename)
                shutil.copy(self.filename, 
                        self.filename + "backup-%s" % str(datetime.datetime.now()).replace(" ", "_"))
                self.params = {}

        self.paramListWidget.clear()
        for path, foo in self.params.items():
            self.paramListWidget.addItem(path)
        self.paramListWidget.sortItems()

    def setFilename(self, n):
        self.filename = n

    @QtCore.pyqtSignature("const QString &")
    def on_paramListWidget_currentTextChanged(self, s):
        self.path = str(s)
        if s == "":
            self.pathLineEdit.clear()
            return
        print "y"
        self.atoms = copy.deepcopy(self.params.get(str(s), []))
        self.pathLineEdit.setText(s)
        self.atomSpinBox.setValue(len(self.atoms))
        self.atomListWidget.clear()
        [self.atomListWidget.addItem(i[0]) for i in self.atoms]
        self.atomListWidget.setCurrentItem(self.atomListWidget.item(0))

    @QtCore.pyqtSignature("const QString &")
    def on_pathLineEdit_textChanged(self, s):
        oldpath = self.path
        self.path = str(s)
        self.params[self.path] = self.params.pop(oldpath, None)
        if s:
            if self.paramListWidget.currentItem() and self.paramListWidget.currentItem().text() != s:
                self.paramListWidget.currentItem().setText(s)
            self.atomSpinBox.setEnabled(1)
            if not self.atoms:
                self.atomSpinBox.setValue(1)
                self.atomListWidget.setCurrentItem(self.atomListWidget.item(0))
        else:
            self.atomSpinBox.setValue(0)
            self.atomSpinBox.setEnabled(0)
            self.enableItems(0)
        self.deleteButton.setEnabled(len(self.paramListWidget.findItems(self.path, QtCore.Qt.MatchFixedString)) > 0)

    @QtCore.pyqtSignature("const QString &")
    def on_atomListWidget_currentTextChanged(self, s):
        self.enableItems(1)
        i = self.atomListWidget.currentRow()
        if i < 0:
            return
        self.currentAtom = i
        if self.atoms[i][0] != "str":
            self.defaultSpinBox.setValue(self.atoms[i][1])
        else:
            self.defaultEdit.setText(self.atoms[i][1])
        self.typeComboBox.setCurrentIndex(self.typeComboBox.findText(self.atoms[i][0]))
        self.minSpinBox.setValue(self.atoms[i][2])
        self.maxSpinBox.setValue(self.atoms[i][3])
        self.widgetEdit.setText(self.atoms[i][4])
        self.widgetSlot.setValue(self.atoms[i][5])

    def enableItems(self, boo):
        self.typeComboBox.setEnabled(boo)
        self.defaultEdit.setEnabled(boo)
        self.defaultSpinBox.setEnabled(boo)
        self.minSpinBox.setEnabled(boo)
        self.maxSpinBox.setEnabled(boo)
        self.widgetEdit.setEnabled(boo)
        self.widgetSlot.setEnabled(boo)

    @QtCore.pyqtSignature("int")
    def on_atomSpinBox_valueChanged(self, i):
        while len(self.atoms) < i:
            self.atoms.append(["float", 0, 0, 1, "", 0])
            self.atomListWidget.insertItem(i-1, "float")
            self.atomListWidget.setCurrentItem(self.atomListWidget.item(i-1))
        while len(self.atoms) > i:
            self.atoms.pop()
            self.atomListWidget.takeItem(len(self.atoms))
        self.atomListWidget.setEnabled(1)
        self.update()


    @QtCore.pyqtSignature("const QString &")
    def on_typeComboBox_currentIndexChanged(self, s):
        enabled = (s != "str")
        self.minSpinBox.setEnabled(enabled)
        self.maxSpinBox.setEnabled(enabled)
        self.atomListWidget.currentItem().setText(s)
        self.atoms[self.currentAtom][0] = str(s)
        self.toggleDefaultEdit(s)
        self.update()

    def toggleDefaultEdit(self, s):
        if s in ("int", "float", "bool"):
            self.defaultEdit.hide()
            self.defaultSpinBox.show()
            self.defaultEditLabel.hide()
            self.defaultSpinBoxLabel.show()
        elif s == "Bang":
            self.defaultEdit.hide()
            self.defaultSpinBox.hide()
            self.defaultEditLabel.hide()
            self.defaultSpinBoxLabel.hide()
        else:
            self.defaultEdit.show()
            self.defaultEditLabel.show()
            self.defaultSpinBox.hide()
            self.defaultSpinBoxLabel.hide()

    @QtCore.pyqtSignature("const QString &")
    def on_defaultEdit_textChanged(self, s):
        self.atoms[self.currentAtom][1] = str(s)
        self.update()

    @QtCore.pyqtSignature("double")
    def on_defaultSpinBox_valueChanged(self, i):
        self.atoms[self.currentAtom][1] = i
        self.update()
    
    @QtCore.pyqtSignature("double")
    def on_minSpinBox_valueChanged(self, i):
        self.defaultSpinBox.setMinimum(i)
        self.atoms[self.currentAtom][2] = i
        self.update()

    @QtCore.pyqtSignature("double")
    def on_maxSpinBox_valueChanged(self, i):
        self.defaultSpinBox.setMaximum(i)
        self.atoms[self.currentAtom][3] = i
        self.update()

    @QtCore.pyqtSignature("const QString &")
    def on_widgetEdit_textChanged(self, s):
        self.atoms[self.currentAtom][4] = str(s)
        self.update()

    @QtCore.pyqtSignature("int")
    def on_widgetSlot_valueChanged(self, i):
        self.atoms[self.currentAtom][5] = i
        self.update()

    def update(self):
        if not self.path in self.params:
            self.params[self.path] = copy.deepcopy(self.atoms)
        else:
            self.params[self.path] = copy.deepcopy(self.atoms)
        self.deleteButton.setEnabled(1)

    @QtCore.pyqtSignature("")
    def on_deleteButton_clicked(self):
        self.params.pop(self.path)
        self.paramListWidget.takeItem(self.paramListWidget.currentRow())

    @QtCore.pyqtSignature("")
    def on_newButton_clicked(self):
        self.paramListWidget.addItem("")
        self.paramListWidget.setCurrentItem(self.paramListWidget.item(self.paramListWidget.count() - 1))
        self.pathLineEdit.setFocus(QtCore.Qt.OtherFocusReason)

    @QtCore.pyqtSignature("")
    def on_buttonBox_accepted(self):
        try:
            f = open(self.filename, 'w')
        except IOError, e:
            print "Couldn't write"
        else:
            p = re.compile("({|},)")
            string = p.sub(r'\1\n', repr(self.params))
            f.write(string)
            f.close()

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Return:
            self.on_buttonBox_accepted()
            self.accept()
        elif ev.key() == QtCore.Qt.Key_Delete:
            self.deleteButton.click()
        elif ev.key() == QtCore.Qt.Key_Escape:
            self.reject()


if __name__ == '__main__':
    a = QtGui.QApplication(sys.argv)
    w = ParamEditor(None)
    w.setFilename("/tmp/foo")
    w.openParams()
    w.show()
    sys.exit(a.exec_())

