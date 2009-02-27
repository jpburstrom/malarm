#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2009 Johannes Burström, <johannes@ljud.org>
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
        self._lengthLabel = ["S", "L", "D", "R"]

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

    def __init__(self, key):
        if self.__class__._eventType is None:
            self.__class__._eventType = \
            QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
        QtCore.QEvent.__init__(self, self.__class__._eventType)
        
        self._key = Gesture(key)

    def type(self):
        return self.__class__._eventType
    
    def key(self):
        return self._key

class Gesture(object):
    """Class defining an input gesture, consisting of conditions and a trigger.

    Conditions are programmatically set (like InputMode) or depending on input events
    (like KeyHold). Triggers are common mouse/kbd presses and releases.

    Both conditions and triggers are defined by a label ID and any value (bool or int, 
    or even None). These are stored as a tuple.
    """
    def __init__(self, init=None):
        self._gesture = [None]

        self._conditionLabels = ["InputMode", "KeyHold", "MouseButtonHold", "MousePosition"]
        self._triggerLabels = ["KeyPress", "KeyRelease", "MousePress", "MouseRelease", "Wheel", "Enter", "Leave"]

        self._trigger = None
        self._conditions = {}
        if init:
            self.setTrigger(*init[0])
            [self.setCondition(*i) for i in init[1:]]

    def __iter__(self):
        return self._gesture.__iter__()

    def getTrigger(self):
        return self._trigger

    def setTrigger(self, k, v):
        self._trigger = (k, v)
        self._gesture[0] = (k, v)

    trigger = property(getTrigger, setTrigger)

    def setCondition(self, k, v):
        self._conditions[k] = v
        #We need to re-sort the whole thing... or do we really?
        del self._gesture[1:]
        for label in self._conditionLabels:
            if label in self._conditions:
                self._gesture.append((label, self._conditions["label"]))

    def getConditionLabels(self):
        """Getter function for condition labels"""
        return [i for i in self._conditionLabels]
    
    conditionLabels = property(getConditionLabels)

class GestureMapping(object):
    #FIXME: callbacks aren't persistrnt. We need to do this with signals instead.
    """Map tuples of arbitrary gestures to a callback function.

    The "gestures" are tuples containing an event and any number of conditions.
    To compare an event, first add conditions which narrows down the selection, and then
    use the getCallbackFromTrigger method to see if any callback matches the combination of
    conditions and event.

    This can be used to handle any kind of events grouped into conditions and triggers.
    """

    def __init__(self, parent):
        self._gestureMap = {}
        self._reverseGestureMap = {}
        self._gestureSet = set()

        self._currentConditions = set()
        self._currentMap = set()

        self._parent = parent

    def __setitem__(self, gesture, callback):
        """Set key and value of a new gesture."""
        self._gestureMap[gesture] = callback
        self._gestureSet.add(gesture)
        for x in gesture:
            self._reverseGestureMap[x].add(gesture)
        #Add no-condition gestures to current
        if len(gesture) is 1:
            self._currentMap.add(gesture)

    def __delitem__(self, gesture):
        """Delete gesture."""
        if not gesture in self._gestureMap:
            return
        del self._gestureMap[gesture]
        self._gestureMap.remove(gesture)
        for x in gesture:
            self._reverseGestureMap[x].remove(gesture)
    
    def __getitem__(self, x):
        """Get gesture from key."""
        return self._gestureMap[x]
    
    def setCondition(self, cond):
        """Add condition to current set of conditions."""
        self._currentMap = self._currentMap & self._reverseGestureMap.get(cond, set())
        self._currentConditions.add(cond)

    def unsetCondition(self, cond):
        """Remove condition from current set of conditions."""
        self._currentMap = self._currentMap - self._reverseGestureMap.get(cond, set()) 
        self._currentConditions.remove(cond)

    def getCallbackFromTrigger(self, ev):
        """Check trigger mapping and return callback, if any. Otherwise return None."""
        p = None
        self._currentMap = self._currentMap & self._reverseGestureMap.get(ev, set())
        self._currentConditions.add(ev)
        for map in self._currentMap:
            if set(map) == self._currentConditions:
                p = _allmaps[map]
                break
        self._currentConditions.remove(ev)
        return p
    
    def triggerCallback(self, ev):
        """Check trigger mapping and call callback, if any."""
        p = None
        self._currentMap = self._currentMap & self._reverseGestureMap.get(ev, set())
        self._currentConditions.add(ev)
        for map in self._currentMap:
            if set(map) == self._currentConditions:
                _allmaps[map]()
                break
        print tuple(self._currentConditions)
        QtGui.qApp.sendEvent(self._parent, SpecialKeyEvent(tuple(self._currentConditions)))
        self._currentConditions.remove(ev)

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
        
        self._holdtimers = {}

        self.gestureMapping = GestureMapping(self.parent())

        self.connect(QtGui.qApp, QtCore.SIGNAL("registerGesture"), self.registerGesture)
        self.connect(QtGui.qApp, QtCore.SIGNAL("unregisterGesture"), self.unregisterGesture)

    def registerGesture(self, gesture, callback):
        """Register and associate incoming gesture with a callback."""
        self.gestureMapping[tuple(gesture)] = callback
    
    def unregisterGesture(self, gesture):
        """Unregister and unassociate a gesture."""
        del self.gestureMapping[tuple(gesture)]

    def eventFilter(self, obj, ev):
        
        ###################
        #Handle key presses
        if ev.type() == QtCore.QEvent.KeyPress:
            if not ev.isAutoRepeat():
                #In this order, we don't get the same key being a condition to the press
                self.gestureMapping.triggerCallback(("KeyPress", ev.key()))
                self.gestureMapping.setCondition(("KeyHold", ev.key()))

            return True

        ###################
        #Handle key releases
        elif ev.type() == QtCore.QEvent.KeyRelease:
            if not ev.isAutoRepeat():
                #In this order, we don't get the same key being a condition to the release
                self.gestureMapping.unsetCondition(("KeyHold", ev.key()))
                self.gestureMapping.triggerCallback(("KeyRelease", ev.key()))
            return True

        ###################
        #Handle mouse presses
        if ev.type() in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonDblClick):
            #In this order, we don't get the same key being a condition to the press
            self.gestureMapping.triggerCallback(("MouseButtonPress", ev.button()))
            self.gestureMapping.setCondition(("MouseButtonHold", ev.button()))
            return True

        ###################
        #Handle mouse releases
        elif ev.type() == QtCore.QEvent.MouseButtonRelease:
            #In this order, we don't get the same key being a condition to the release
            self.gestureMapping.unsetCondition(("MouseButtonHold", ev.button()))
            self.gestureMapping.triggerCallback(("MouseButtonRelease", ev.button()))
            return True

        ###################
        #Handle Wheel events
        elif ev.type() == QtCore.QEvent.Wheel:
            self.gestureMapping.triggerCallback(("Wheel", ev.delta()))
            return True
        
        ###################
        #Handle enter/leave main window
        elif ev.type() == QtCore.QEvent.Enter:
            #In this order, we don't get the same key being a condition to the release
            self.gestureMapping.triggerCallback(("Enter", None))
            return True
        elif ev.type() == QtCore.QEvent.Leave:
            #In this order, we don't get the same key being a condition to the release
            self.gestureMapping.triggerCallback(("Leave", None))
            return True


        else:
            return QtCore.QObject.eventFilter(self, obj, ev)
        

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
        #Otherwise send long release
        QtGui.qApp.sendEvent(self.parent(), SpecialKeyEvent(k, 3))
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
