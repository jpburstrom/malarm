#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2008 Johannes Burström, <johannes@ljud.org>

import os
import sys
import shutil
import pprint

from PyQt4 import QtCore, QtGui

class _AbstractSettings(QtCore.QObject):
    """Abstract class for simple settings/preset saving."""
    def __init__(self, path = None, *args):
        """
        Constructor.
        """
        QtCore.QObject.__init__(self, *args)

        self._path = path 
        self._dict = self._readFile()

    def setPath(self, path):
        self._path = path
        self._readFile()

    def getPath(self):
        return self._path

    def get(self, key, default=None):
        """Get settings value of key, or default if not existing.

        @param key str -- settings key
        @param default -- value if key doesn't exist
        """
        return self._dict.get(key, default)

    def setdefault(self, key, default=None):
        """Get settings key, or set and return a default if not existing.

        @param key  -- settings key
        @param default -- value if key doesn't exist
        """
        self._dict.setdefault(key, default)
        self._writeFile()
        return self._dict[key]

    def update(self, key, val):
        """Set key and save to disk.
        @param key -- settings key
        @param val -- settings value
        """
        old = self._dict.get(key, None)
        self._dict[key] = val
        self._writeFile()
        self.emit(QtCore.SIGNAL("settingsEdited"), key, old, val)

    def _readFile(self):
        """Load settings file.
        """
        f = self._path
        if not os.path.exists(f):
            fi = open(f, 'w')
            fi.write("{}")
            fi.close()
            return {}
        else:
            fi = open(f, 'r')
            config_string = fi.read()
            return eval(config_string)
            f.close()

    def _writeFile(self):
        try:
            f = open(self._path, 'w')
        except IOError, e:
            self._handleError(e)
        else:
            pprint.pprint(self._dict, f)
            f.close()

    def _handleError(self, e, err):
        sys.stderr.write(e + "\n")
        print err

    def getSettings(self):
        return self._dict.copy()

class SettingsHandler(_AbstractSettings):
    """Simple saving of settings"""

    def __init__(self, path = None, *args):
        _AbstractSettings.__init__(self, path, *args)


class PresetHandler(_AbstractSettings):
    """Simple saving of presets for params."""
    __pyqtSignals__ = (
            "loadPreset(PyQt_PyObject)",
            "recallPresets(const QString &, PyQt_PyObject)"
            )
    
    def __init__(self, path = None, *args):
        _AbstractSettings.__init__(self, path, *args)
        
    def savePreset(self, group, name, paramlist):
        """Saves params.

        @param group QString -- preset group
        @param name QString -- preset name
        @param paramlist list -- list of params to save
        """ 
        #add dictionaries if they don't exist
        di = self._dict.setdefault(str(group), {}).setdefault(str(name), {})
        [di.setdefault(el.address, el.getState()) for el in paramlist if el.isSaveable()]
        self._writeFile()
        
    def loadPreset(self, group, name):
        """Finds preset, emits load signal with dict.
        @param group QString -- preset group
        @param name QString -- preset name
        """
        #Find the node in question
        try:
            self.emit(QtCore.SIGNAL("loadPreset(PyQt_PyObject)"), self._dict[str(group)][str(name)])
        except KeyError, e:
            self._handleError(e)
    
    def deletePreset(self, group, name):
        """
        @param group QString -- preset group
        @param name QString -- preset name
        """
        if not self._dict[param.full_address].pop(presetname, None):
            self._handleError("EasySave: Couldn't find preset to delete")
        else:
            self._writeFile()
        self._writeFile()

    def renamePreset(self, group, oldname, newname):
        """
        @param group QString -- preset group
        @param oldname QString -- preset name
        @param newname QString -- preset name
        """
        group = str(group)
        oldname = str(oldname)
        newname = str(newname)
        s = self._dict[group].pop(oldname, None)
        if s:
            self._dict[group][newname] = s
        self._writeFile()
    
    def recallPresets(self, group=None):
        """Emits dictionary with current preset keys for group.

        If group = None, emits keys for all existing groups.
        
        @param group str/None -- preset group
        """
        if not group:
            [QtGui.qApp.emit(QtCore.SIGNAL("recallPresets(const QString &, PyQt_PyObject)"), 
                    QtCore.QString(group), d.keys()) for group, d in self._dict.items()]
        else:
            QtGui.qApp.emit(QtCore.SIGNAL("recallPresets(const QString &, PyQt_PyObject)"), 
                    QtCore.QString(group), self._dict[group].keys()) 
    
if __name__  == "__main__":
    s = PresetHandler("/tmp/foo")

