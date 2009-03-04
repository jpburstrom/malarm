#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2009 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision: 86 $"


import os
import sys
from PyQt4 import QtGui, QtCore, uic

import globals

class GestureEvent(QtCore.QEvent):
    """Custom Gesture event class."""
    
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

    If you roll your oen qt events, you can get this class to use them by appending a 
    label for them to the _conditionLabels or _triggerLabels, depending on what they are, and

    """
    def __init__(self, init=None):

        self._gesture = [None]

        self._conditionLabels = ["InputMode", "KeyHold", "MouseButtonHold", "MousePosition"]
        self._triggerLabels = ["KeyPress", "KeyRelease", "MouseButtonPress", "MouseButtonRelease", "Wheel", "Enter", "Leave"]

        self._trigger = None
        self._conditions = {}
        [self._conditions.setdefault(lab, []) for lab in self._conditionLabels]
        for i in init:
            if i[0] in self._triggerLabels:
                self.setTrigger(*i)
            else:
                self.setCondition(*i)

    def __iter__(self):
        return self._gesture.__iter__()

    def getTrigger(self):
        """Return the gesture trigger.

        The trigger fires off the gesture event.
        """
        return self._trigger

    def setTrigger(self, k, v):
        """Set the gesture trigger."""
        self._trigger = (k, v)
        self._gesture[0] = (k, v)

    trigger = property(getTrigger, setTrigger)

    def setCondition(self, k, v):
        """Set a single condition for the trigger.
        
        Many conditions can be set for the same gesture, acting as
        modifier keys."""
        self._conditions[k].append(v)
        #We need to re-sort the whole thing... or do we really?
        del self._gesture[1:]
        for label, v in self._conditions.items():
            [self._gesture.append((label, value)) for value in v]

    def getConditionLabels(self):
        """Getter function for condition labels"""
        return [i for i in self._conditionLabels]
    
    conditionLabels = property(getConditionLabels)

class GestureMapping(object):
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
            try:
                self._reverseGestureMap[x].add(gesture)
            except KeyError:
                self._reverseGestureMap[x] = set([gesture])
        #Add no-condition gestures to current
        if len(gesture) == 1:
            self._currentMap.add(gesture)

    def __delitem__(self, gesture):
        """Delete gesture."""
        if not gesture in self._gestureMap:
            return
        del self._gestureMap[gesture]
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
        try:
            self._currentConditions.remove(cond)
        except KeyError:
            pass
    
    def triggerCallback(self, ev):
        """Check trigger mapping and call callback, if any.
        
        Yes, it's not a callback, but a Qt Signal with a unique string as id, the same string
        used for registering the callback in the main GestureEventHandler class."""

        p = None
        if self._currentMap:
            self._currentMap = self._currentMap & self._reverseGestureMap.get(ev, set())
        else:
            self._currentMap = self._reverseGestureMap.get(ev, set())
        self._currentConditions.add(ev)
        k = GestureEvent(tuple(self._currentConditions))
        QtGui.qApp.sendEvent(self._parent, GestureEvent(tuple(self._currentConditions)))
        for map in self._currentMap:
            if set(map) == self._currentConditions:
                QtGui.qApp.emit(QtCore.SIGNAL("gestureActivated"), self._gestureMap[map])
                break
        self._currentConditions.remove(ev)

class GestureEventHandler(QtCore.QObject):
    """
    An Event Filter for handling input gestures, consisting of mouse, keyboard and (possibly) whatever
    events qt catches. 

    If you roll your own qt events, you can have this class use them by defining new rules in the event handler, 
    and appending them to the proper list in the Gesture class. For example, you may create a MIDI event handler,
    and set NoteOns as triggers or a sustain pedal as condition for regular key events.
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

    def registerGesture(self, key, gesture):
        """Register and associate incoming gesture with a callback."""
        if gesture:
            self.gestureMapping[eval(gesture)] = key
    
    def unregisterGesture(self, gesture):
        """Unregister and unassociate a gesture."""
        if gesture:
            del self.gestureMapping[eval(gesture)]

    def eventFilter(self, obj, ev):
        """Main event handler.

        Take incoming event and let the GestureMapping class instance trigger a callback
        if needed. Well, it's not really a callback, it's more like a signal with a id string.
        """
        
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
        
        if ev.type() is QtCore.QEvent.ContextMenu:
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
        
        elif ev.type() in (QtCore.QEvent.Shortcut, QtCore.QEvent.ShortcutOverride, QtCore.QEvent.InputMethod):
            return True
        else:
            return False

if __name__ == "__main__":

    class Widg(QtGui.QMainWindow):
        def customEvent(self, e):
            if isinstance(e, GestureEvent):
                print "type", tuple(e.key())

    a = QtGui.QApplication(sys.argv)
    win = Widg()
    evf = GestureEventHandler(win)
    win.installEventFilter(evf)
    win.show()
    sys.exit(a.exec_())
