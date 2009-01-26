#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2007 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"


import os
import sys
from PyQt4 import QtGui, QtCore, uic

class SpecialKey(QtCore.QObject):
    def __init__(self, key, length=0):

        if not hasattr(key, "__iter__") and not hasattr(key, "__len__"):
            key = [key]
        elif not hasattr(key, "__iter__"):
            key = list(key)

        self._key = frozenset(key)
        self._length = length
        self._lengthLabel = ["S", "L", "D"]

    def length(self):
        return self._length
    
    def key(self):
        return self._key

    def text(self):
        x = QtCore.QString()
        [x.append(QtGui.QKeySequence(k).toString()) for k in self._key]
        x.prepend(QtCore.QString(self._lengthLabel[self._length]))
        return x
    
    def __eq__(self, other):
        try:
            return self._key == other.key() and self._length == other.length()
        except (TypeError, AttributeError):
            return False

    def __ne__(self, other):
        try:
            return self._key != other.key() and self._length != other.length()
        except (TypeError, AttributeError):
            return True

    def __repr__(self):
        return unicode(self.text()).encode("utf-8")

class SpecialKeyEvent(QtCore.QEvent):
    
    _eventType = None

    def __init__(self, key, length = 0):
        if self.__class__._eventType is None:
            self.__class__._eventType = \
            QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
        QtCore.QEvent.__init__(self, self.__class__._eventType)
        
        self._key = SpecialKey(key, length)

    def type(self):
        return self.__class__._eventType
    
    def key(self):
        return self._key

class KeyHandler(QtCore.QObject):
    """
    An Event Filter for handling keyboard, adding doubleclicks and longclicks.
    """

    eventType = None

    def __init__(self, parent, *args):
        """
        Constructor.
        """
        QtCore.QObject.__init__(self, parent, *args) 
        
        self._single = None
        self._pairs = []

        self._pressed = set()

        self._doubletimers = {}
        self._longtimers = {}

    def eventFilter(self, obj, ev):
        if ev.type() == QtCore.QEvent.KeyPress:
            return self.handleKeyPress(ev)
        elif ev.type() == QtCore.QEvent.KeyRelease:
            return self.handleKeyRelease(ev)
        else:
            return QtCore.QObject.eventFilter(self, obj, ev)

    def handleKeyPress(self, ev):
        if ev.isAutoRepeat():
            return True
        self._pressed.add(ev.key())
        k = ev.key()
        #If we already have a single key, let's hook up with it in a pair
        if self._single is not None:
            #remove timer
            [self._longtimers.pop(id, None) for id, key in self._longtimers.items() if key is self._single]
            k = set((k, self._single))
            self._pairs.append(k)
            #remove it as single
            self._single = None
        else:
            self._single = k
        self._longtimers[self.startTimer(200)] = k
        return True

    def handleKeyRelease(self, ev):
        if ev.isAutoRepeat():
            return True
        k = ev.key()
        if k is self._single:
            gesture = 0
            self._single = None
        else:
            #find key among pairs
            #find out if pair key has been released
            for pair in self._pairs:
                if k in pair and len(pair & self._pressed) == 1:
                    k = pair
                    self._pairs.remove(pair)
                    break
            gesture = 1

        #if longtimer hasn't expired, it's a single shot
        if [self._longtimers.pop(id, None) for id, val in self._longtimers.items() if val == k]:
            #And if doubletimer hasn't, it's a doublecklic
            if [self._doubletimers.get(id, None) for id, val in self._doubletimers.items() if val == k]:
                #Send Double click event
                QtGui.qApp.sendEvent(self.parent(), SpecialKeyEvent(k, 2))
            else:
                #Send Single click event
                QtGui.qApp.sendEvent(self.parent(), SpecialKeyEvent(k))
        #start timer, to check for doublecklick
        self._doubletimers[self.startTimer(200)] = k
        self._pressed.discard(ev.key())
        return True

    def timerEvent(self, ev):
        long = self._longtimers.pop(ev.timerId(), None)
        double = self._doubletimers.pop(ev.timerId(), None)
        if long:
            if long is self._single:
                self._single = None
                long = set((long,))
            else:
                self._pairs.remove(long)
            QtGui.qApp.sendEvent(self.parent(), SpecialKeyEvent(long, 1))
        self.killTimer(ev.timerId())


if __name__ == "__main__":

    class Widg(QtGui.QMainWindow):
        def customEvent(self, e):
            if isinstance(e, SpecialKeyEvent):
                print "type", e.key()

    a = QtGui.QApplication(sys.argv)
    win = Widg()
    evf = KeyHandler(win)
    win.installEventFilter(evf)
    win.show()
    sys.exit(a.exec_())
