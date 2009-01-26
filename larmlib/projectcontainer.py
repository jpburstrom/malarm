#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2009 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision: 70 $"

import os
import sys
import copy

from PyQt4 import QtGui, QtCore, uic
import PyQt4.Qwt5 as Qwt

import designer
from parameditor import ParamEditor
from larmwidgets.paramwidgets import AbstractParamWidget
from persistance import SettingsHandler, PresetHandler
from shortcuteditor import ShortcutEditor
from globals import *
from param import *
from qtosc import Emitter, OscHelper

ProjectDialogUi, dummy = uic.loadUiType(os.path.join(os.path.dirname(__file__), "forms/projectdialog.ui"))

class ProjectDialog(ProjectDialogUi, QtGui.QDialog):
    def __init__(self, *args):  
        QtGui.QDialog.__init__(self, *args)

        self.setupUi(self)
        self.buttonBox.setStandardButtons(self.buttonBox.Ok|self.buttonBox.Cancel)

ReceiverDialogUi, dummy = uic.loadUiType(os.path.join(os.path.dirname(__file__), "forms/receiverdialog.ui"))

class ReceiverDialog(ReceiverDialogUi, QtGui.QDialog):
    def __init__(self, receivers, *args):  
        QtGui.QDialog.__init__(self, *args)

        self.setupUi(self)

        self.mapping = receivers
        self._currentText = ""

        [self.listWidget.addItem(k) for k in self.mapping.keys()]


    @QtCore.pyqtSignature("")
    def on_lineEdit_returnPressed(self):
        t = str(self.lineEdit.text())
        if not t:
            return
        if t not in self.mapping:
            self.listWidget.addItem(t)
            self.mapping[t] = 0
            self.listWidget.setCurrentRow(self.listWidget.count() - 1)
        self.lineEdit.clear()
        self.spinBox.setFocus()
        self.spinBox.clear()

    @QtCore.pyqtSignature("const QString &")
    def on_listWidget_currentTextChanged(self, s):
        self._currentText = str(s)
        self.spinBox.setValue(self.mapping[self._currentText])

    @QtCore.pyqtSignature("int")
    def on_spinBox_valueChanged(self, i):
        if self._currentText:
            self.mapping[self._currentText] = i

    def keyPressEvent(self, ev):
        pass
    


class ProjectContainer(QtCore.QObject):
    def __init__(self, mainwindow, *args):
        QtCore.QObject.__init__(self, *args)

        self.params = {}
        self._mainwindow = mainwindow
        self._actions = []

        ###############
        #Global Settings
        self._settings = SettingsHandler(os.path.join(RCDIR, "larmrc"))
        self._projects = self._settings.get("projects", ["default"])
        self._currentProject = self._settings.get("currentProject", self._projects[0])
        self.connect(QtGui.qApp, QtCore.SIGNAL("registerSettingsKey"), self.registerSettingsKey)

        ###############
        #Presets
        self.presets = PresetHandler(os.path.join(RCDIR, self._currentProject, "presets.py"))
        self.connect(QtGui.qApp, QtCore.SIGNAL("init"), self.presets.recallPresets)
        self.connect(QtGui.qApp, QtCore.SIGNAL(
            "savePreset(const QString &, const QString &, PyQt_PyObject)"), self.presets.savePreset)
        self.connect(QtGui.qApp, QtCore.SIGNAL(
            "loadPreset(const QString &, const QString &)"), self.presets.loadPreset)
        self.connect(QtGui.qApp, QtCore.SIGNAL(
            "renamePreset(const QString &, const QString &, const QString &)"), self.presets.renamePreset)
        self.connect(QtGui.qApp, QtCore.SIGNAL(
            "deletePreset(const QString &, const QString &)"), self.presets.deletePreset)
        self.connect(self.presets, QtCore.SIGNAL("loadPreset(PyQt_PyObject)"), self.loadPreset)
        
        ###############
        #Keyboard shortcuts
        self.shortcuts = SettingsHandler(os.path.join(RCDIR, self._currentProject, "shortcuts.py"))
        self.connect(self._mainwindow.actionEdit_Shortcuts, QtCore.SIGNAL(
            "activated()"), self.showShortcutEditor)
        self._shortcutRemap = {}
        self.connect(self.shortcuts, QtCore.SIGNAL("settingsEdited"), self.remapShortcuts)
        

        ###############
        #Project Dialog
        self.projectDialog = ProjectDialog(self._mainwindow)
        c = self.projectDialog.comboBox
        c.setCurrentIndex(c.findText(self._currentProject)) 
        c.addItems(self._projects) 
        self.connect(self._mainwindow.actionChoose_project, QtCore.SIGNAL(
            "activated()"), self.projectDialog, QtCore.SLOT("show()"))
        self.connect(self.projectDialog, QtCore.SIGNAL("accepted()"), self.projectDialogAccepted)
        self.connect(self.projectDialog.comboBox, QtCore.SIGNAL(
            "currentIndexChanged(const QString &)"), self.updateProjectList)

        ###############
        #Receivers Dialog
        self.connect(self._mainwindow.actionEdit_Receivers, QtCore.SIGNAL(
            "activated()"), self.editReceivers)
        self._oscReceivers = {}

        ###############
        #Param Editor
        self.parameditor = ParamEditor(self._mainwindow)
        self.connect(self._mainwindow.actionEdit_params, QtCore.SIGNAL("activated()"), 
                self.parameditor, QtCore.SLOT("show()"))
        self.connect(self._mainwindow.action_Rebuild, QtCore.SIGNAL("activated()"), self.rebuild)
        
        ###############
        #Run Designer signal
        self.connect(self._mainwindow.actionEdit_Ui, QtCore.SIGNAL("activated()"), self.runDesigner)

        self.oscServer = OscHelper()
        self.oscServer.start()

        self.initProjects()

    def rebuild(self):
        """Rebuild the current project UI
        """
        
        self.closeProject()
        
        # rebuild ui, if it exists
        self._container = QtGui.QWidget(self._mainwindow)
        self._mainwindow.setCentralWidget(self._container)
        if os.path.exists(self._uifile):
            #XXX sys.path[0]???
            #try:
            fi = open(os.path.join(sys.path[0], "tmpgui.py"),  "w")
            uic.compileUi(self._uifile, fi)
            fi.close()
            import tmpgui
            reload(tmpgui)
            ui = tmpgui.Ui_Form()
            ui.setupUi(self._container)
            self._mainwindow.adjustSize()
            #except:
            #mess = QtGui.QMessageBox.critical(
            #        None, "UI error", "Something went wrong when compiling the UI:\n%s\nWant to re-open the file?" % e,
            #    QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
            #if mess == QtGui.QMessageBox.Ok:
            #    self.runDesigner()
            #return


        children = self._container.findChildren(AbstractParamWidget)

        for p, v in self.parameditor.params.items():
            u = copy.deepcopy(v)
            v = zip(*v)
            v = [[j for j in i] for i in v]
            try:
                t = [eval(t) for t in v[0]]
            except IndexError, err:
                print "Rebuild problem:", err
                continue
            mapping = { int : IntParam, float : FloatParam, str : StringParam, bool : BoolParam, Bang : BangParam }
            if len(t) == 1:
                t = t[0]
                v[1] = v[1][0]
                v[2] = v[2][0]
                v[3] = v[3][0]
                v[4] = v[4][0]
                v[5] = v[5][0]
                obj = mapping[t]
                if t in (bool, Bang):
                    self.params[p] = obj(p)
                    self._createAction(p)
                else:
                    self.params[p] = obj(p, default=v[1], min=v[2], max=v[3])
            else:
                self.params[p] = ListParam(p, t, default=v[1], min=v[2], max=v[3])
            print self.params
            for slot, v in enumerate(u):
                try:
                    o = [i for i in children if str(i.objectName()) == v[4]][0]
                except IndexError:
                    pass
                else:
                    o.setParamPath(self.params[p].address)
            self.oscServer.createSenderFromParam(self.params[p])
        
        #Send an init signal as last thing, 
        #so children can initialize what's needed
        QtGui.qApp.emit(QtCore.SIGNAL("init"))

        #Load misc project-local settings
        self.loadSettings()

    def closeProject(self):
        QtGui.qApp.emit(QtCore.SIGNAL("saveSettings"), self._currentProject, self._settings.update)

        for k, p in self.params.items():
            self.disconnect(QtGui.qApp, QtCore.SIGNAL("paramGuiConnect"), p.paramGuiConnect)
            self.disconnect(QtGui.qApp, QtCore.SIGNAL("OscReceive"), p.handle_incoming_osc)
        self.params.clear()

        if hasattr(self, "_container"):
            self._container.setParent(None)

        QtGui.qApp.emit(QtCore.SIGNAL("closeProject"))

    def projectDialogAccepted(self):
        """Called when changed project from project dialog."""
        self.closeProject()
        self._currentProject = str(self.projectDialog.comboBox.currentText())
        self.initProjects()
        self.rebuild()

    def editReceivers(self):
        r = ReceiverDialog(self._oscReceivers)
        if not r.exec_():
            return
        for k, v in r.mapping.items():
            if k not in self._oscReceivers:
                QtGui.qApp.emit(
                    QtCore.SIGNAL("registerOscReceiver"), k, v)
                self._oscReceivers[k] = v
        self._settings.update((self._currentProject, "oscReceivers"), self._oscReceivers)


    def updateProjectList(self, s):
        if str(s) not in self._projects and self.projectDialog.isShown():
            self._projects.append(str(s))
            self._settings.update("projects", self._projects)

    def runDesigner(self):
        """Run Qt designer.
        """
        self.designer = QtCore.QProcess(self)
        env = self.designer.systemEnvironment()
        env.append("PYQTDESIGNERPATH=%s" % os.path.join(sys.path[0], "larmwidgets"))
        self.designer.setEnvironment(env)
        self.designer.start("/usr/bin/designer", [self._uifile])

    def initProjects(self):

        QtGui.qApp.emit(QtCore.SIGNAL("clearOscReceivers"))
        self.projectPath = os.path.join(RCDIR, self._currentProject)
        if not os.path.exists(self.projectPath):
            os.mkdir(self.projectPath)
        self.parameditor.setFilename(os.path.join(self.projectPath, "params.py"))
        self.parameditor.openParams()
        self._settings.update("currentProject", self._currentProject)

        self._localSettingsList = set()
        self.registerSettingsKey("oscReceivers")
        self._oscReceivers = self._settings.get((self._currentProject, "oscReceivers"))
        [QtGui.qApp.emit(QtCore.SIGNAL("registerOscReceiver"), label, port
                ) for label, port in self._oscReceivers.items()]

        self._mainwindow.setWindowTitle("Larm2 :: %s" % self._currentProject)
        self._uifile = os.path.join(self.projectPath, "gui.ui")
        self.presets.setPath(os.path.join(self.projectPath, "presets.py"))
        self.shortcuts.setPath(os.path.join(self.projectPath, "shortcuts.py"))
        self.remapShortcuts()

    def loadPreset(self, preset):
        #FIXME: optimize?
        [p.setState(v) for p, v in [(
            IntParam.findParamFromPath(k), v) for k, v in preset.items()] if p is not None]

    def _createAction(self, add):
        p = self.params[add]
        t = p.type
        a = QtGui.QAction(add, self._mainwindow)
        if t is bool:
            a.isCheckable(1)
        self.connect(a, QtCore.SIGNAL("triggered(bool)"), p.setState)
        a.setShortcut(self.shortcuts.setdefault(add, ""))
        self._actions.append(a)
    
    def showShortcutEditor(self):
        ShortcutEditor(self.shortcuts, self._mainwindow).show()

    def remapShortcuts(self, key=None, old=None, new=None):
        if key is not None:
            if old in self._shortcutRemap:
                self._shortcutRemap[old].discard(key)
            self._shortcutRemap.setdefault(new, set()).add(key)
        else:
            self._shortcutRemap = {}
            [self.remapShortcuts(k, None, v) for k, v in self.shortcuts.getSettings().items()]
    
    def handleSpecialKey(self, ev):
        try:
            [ListParam.findParamFromPath(p).setState(
                ) for p in self._shortcutRemap.get(
                        unicode(ev.key().text()), None)]
        except TypeError:
            pass

    def registerSettingsKey(self, k):
        self._localSettingsList.add(k)

    def loadSettings(self):
        """Loading misc project-local settings as mapped in _settingsMap.

        """
        [QtGui.qApp.emit(QtCore.SIGNAL(
            "loadSettings"), k, self._settings.get(
                (self._currentProject, k))) for k in self._localSettingsList]

if __name__ == "__main__":

    a = QtGui.QApplication(sys.argv)
    d = ReceiverDialog()
    d.show()

    sys.exit(a.exec_())
