#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2007 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision: 70 $"

import os
import sys
import copy
from collections import deque

from PyQt4 import QtGui, QtCore, uic

#FIXME: Save stats

class RingBuffer(deque):
    """
    inherits deque, pops the oldest data to make room
    for the newest data when size is reached. No duplicate values.
    """
    def __init__(self, size):
        deque.__init__(self)
        self.size = size

        self.old_appendleft = self.appendleft
        
    def full_appendleft(self, item):
        if item in self:
            self.remove(item)
        else:
            self.pop()
        deque.appendleft(self, item)
        # full, pop the oldest item, left most item
        
    def appendleft(self, item):
        if item in self:
            self.remove(item)
        deque.appendleft(self, item)
        if len(self) == self.size:
            self.appendleft = self.full_appendleft
    
    def get(self):
        """Return a list of size items (newest items)"""
        return list(self)

    def set(self, li):
        self.clear()
        self.appendleft = self.old_appendleft
        [self.appendleft(l) for l in li]

class UsageStats(object):
    #TODO
    def __init__(self):

        self._accesstimes = {}
        self._files = []
        self._recent = RingBuffer(50)

    def add(self, f):
        self._recent.appendleft(f)
        if f not in self._files:
            self._files.append(f)
            self._accesstimes[f] = 1
            return
        
        self._accesstimes[f] += 1

    def getMostAccessed(self, limit=50):
        self._files.sort(key=self.sortDesc)
        return self._files[:limit]

    def getLeastAccessed(self, limit=50):
        self._files.sort(key=self.sortAsc)
        return self._files[:limit]

    def sortAsc(self, item):
        return self._accesstimes[item] 

    def sortDesc(self, item):
        return self._accesstimes[item] * -1
    
    def getRecent(self):
        return self._recent.get()

    def getStats(self):
        return (self._accesstimes.copy(), copy.copy(self._files), self._recent.get())

    def setStats(self, stats):
        if not stats:
            return
        self._accesstimes = stats[0].copy()
        self._files = copy.copy(stats[1])
        self._recent.set(stats[2])

class DirModel(UsageStats, QtCore.QAbstractListModel):
    """
    Directory list browser
    """
    def __init__(self, *args):
        """
        Constructor.
        """
        UsageStats.__init__(self)
        QtCore.QAbstractListModel.__init__(self, *args)

        self._viewMode = 0
        self.dir = QtCore.QDir()
        self.dir.setFilter(QtCore.QDir.AllDirs|QtCore.QDir.Files)
        self.dir.setNameFilters(("*wav", "*aif", "*aiff", "*flac", "*wv", "*mp3"))
        self.dir.setSorting(self.dir.Name|self.dir.DirsFirst)
        self.setCurrentDir("/")

        self.iconProvider = QtGui.QFileIconProvider()

    def rowCount(self, mi):
        return len(self._filelist)

    def data(self, mi, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self._filelist[mi.row()])
        elif role == QtCore.Qt.DecorationRole:
            if self.isDir(mi):
                return QtCore.QVariant(self.iconProvider.icon(self.iconProvider.Folder))
            else:
                return QtCore.QVariant(self.iconProvider.icon(self.iconProvider.File))
        else:
            return QtCore.QVariant()

    def handleClick(self, mi):
        if self.dir.cd(self._filelist[mi.row()]):
            self._filelist = self.dir.entryList()
            self._filelist.removeAt(0)
            self.reset()

    def flags(self, mi):
        defaultFlags = QtCore.QAbstractListModel.flags(self,mi)
        if not self.isDir(mi):
            return QtCore.Qt.ItemIsDragEnabled | defaultFlags
        else:
            return defaultFlags

    def mimeTypes(self):
        return ["text/plain", "text/uri-list"]
    
    def mimeData(self, milist):
        [self.add(self.abspath(
            self._filelist[mi.row()])) for mi in milist] 
        mimeData = QtCore.QMimeData()
        li = [QtCore.QUrl("".join(("file://", self.abspath(
            self._filelist[mi.row()])))) for mi in milist] 
        mimeData.setUrls(li)
        return mimeData

    def isDir(self, mi):
        return os.path.isdir(self.abspath(self._filelist[mi.row()]))

    def abspath(self, f):
        return os.path.join(str(self.dir.path()), str(f))
    
    def setNameFilters(self, filters):
        self.dir.setNameFilters(filters)

    def viewFiles(self):
        self._viewMode = 0
        self._filelist = self.dir.entryList()
        self._filelist.removeAt(0)
        self.reset()

    def viewRecent(self):
        self._viewMode = 1
        self._filelist = self.getRecent()
        self.reset()

    def viewMostPopular(self):
        self._viewMode = 2
        self._filelist = self.getMostAccessed(50)
        self.reset()

    def setCurrentDir(self, dir):
        self.dir.cd(dir)
        if self._viewMode is 0:
            self.viewFiles()

class FileBrowser(QtGui.QListView):
    """
    A simple but really nice file browser with some nice features.
    """

    def __init__(self, *args):
        """
        Constructor.
        """
        QtGui.QListView.__init__(self, *args)

        self.setUniformItemSizes(1)
        self.setIconSize(QtCore.QSize(16,16))
        
        m = DirModel(self)
        self.setModel(m)

        self.setDragEnabled(1)

        self.connect(self, QtCore.SIGNAL("clicked(const QModelIndex &)"), self.on_clicked)

        self._settingsKey = "filebrowser"

        self.connect(QtGui.qApp, QtCore.SIGNAL("saveSettings"), self.saveSettings)
        self.connect(QtGui.qApp, QtCore.SIGNAL("loadSettings"), self.loadSettings)

        QtGui.qApp.emit(QtCore.SIGNAL("registerSettingsKey"), self._settingsKey)

    def on_clicked(self, mi):
        self.model().handleClick(mi)

    def loadSettings(self, key, val):
        """Load settings.

        @param currentProject -- name of current project
        @param key -- setting key
        @param value -- setting value
        """
        if self._settingsKey == key:
            self.model().setStats(val)

    def saveSettings(self, currentProject, callback):
        """Save settings.
        @param currentProject -- name of current project
        @param callback -- function to call
        """

        callback((currentProject, self._settingsKey), self.model().getStats())

class FileBrowserWidget(QtGui.QWidget):
    def __init__(self, *args):
        """
        Constructor.
        """
        QtGui.QWidget.__init__(self, *args)

        layout = QtGui.QVBoxLayout(self)
        buttonbox =  QtGui.QFrame(self)
        layout.addWidget(buttonbox)
        layout.setContentsMargins(0,0,0,0)
        
        boxlayout = QtGui.QHBoxLayout(buttonbox)
        boxlayout.setContentsMargins(0,0,0,0)
        b1 = QtGui.QPushButton("Files", buttonbox)
        b2 = QtGui.QPushButton("Recent", buttonbox)
        b3 = QtGui.QPushButton("Most used", buttonbox)
        for b in (b1, b2, b3):
            boxlayout.addWidget(b)

        self.filebrowser = FileBrowser(self)
        layout.addWidget(self.filebrowser)

        self.connect(b1, QtCore.SIGNAL("clicked()"), self.filebrowser.model().viewFiles)
        self.connect(b2, QtCore.SIGNAL("clicked()"), self.filebrowser.model().viewRecent)
        self.connect(b3, QtCore.SIGNAL("clicked()"), self.filebrowser.model().viewMostPopular)

    
if __name__ == '__main__':
    a = QtGui.QApplication(sys.argv)
    win = QtGui.QMainWindow()
    b = FileBrowserWidget()
    win.setCentralWidget(b)
    win.show()
    sys.exit(a.exec_())
