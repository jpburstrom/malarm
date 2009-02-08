#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2007-2009 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"

#TODO: update preset menu on sibling delete
#FIXME: Param setState and setMinValue/setMaxValue diffar i hur de fungerar. setState tar single values för non-list params,
#medan de andra tar single-value list (om inte index är not None).

import sys
from time import sleep
import copy
import traceback 

from PyQt4 import QtGui, QtCore

_SIGNAL = QtCore.SIGNAL

_tree = {}
    
#from canvaslabel import Canvasinfo
#from larmglobals import getgl, dbp, alert
#from easysave import EasySave

OSCDEBUG = 0


class Bang(object):
    """Simple Bang object. """

    def __init__(self, *args):
        pass
    def __repr__(self):
        return "<Bang>"
    def __str__(self):
        return "Bang"
        
class _Param(QtCore.QObject):
    """Abstract gui element/machine parameter class.
    
    This is the heart of the Larm parameter system. Param inherits QObject, and
    uses its parent->child hierarchy to build parameter trees which are later on
    converted into OSC addresses. 
    

    """
    #TODO: list operations on _Param... 
    #p = _Param([float, float, float])
    #p[0] = 2.3
    #p[:2] =??? 

    _paths = {} # full_address->object dictionary
    _update = True

    def __init__(self, address, t, **kwargs):
        """Constructor.
        
        address (<str>) -- OSC Address of param. An unique identifier, which is used to send values via OSC,
        and also for saving presets.
        
        type (<type>, or list of types). The type can be int, float, bool, str, list or Bang, or any 
        combination of these. 
        
        Keyword arguments:
        
        min -- (int or float param only)
        max -- (int or float param only)
        default -- Initial value.
        label -- a human-readable label for cosmetic use
        """

        QtCore.QObject.__init__(self)

        # These have to be set
        self.address = address # Absolute, full osc address
        self.__class__._paths[self.address] = self

        self.label = kwargs.get('label') or ""

        #Set type of param.
        if t is not list:
            self.type = t #int, str, bool, float, Bang
            self._typelist = [t] #List of types.
        
        #Max and min values, for numbers and list of numbers.
        self.max, self.min = [], []

        #Set default value.
        self._default = []
        self.setDefault(kwargs)

        #self.dirty = False ##currently unused..
        
        #These are used for sending signals when param is updated.
        self.UpdateState = 1
        self.UpdateMin = 2
        self.UpdateMax = 4
        
        #Enable osc sending by default
        self._enableosc = True
        self.oscEmit = QtGui.qApp.emit
        #Enable saving param by default, if type is not bang.
        self._saveable = self.type is not Bang
        
        #Set initial state.
        self._state = [None for i in self._typelist]

        self.connect(QtGui.qApp, _SIGNAL("paramGuiConnect"), self.paramGuiConnect)
        self.connect(QtGui.qApp, _SIGNAL("OscReceive"), self.handle_incoming_osc)

        self._snapshots = {}

        #Some semi-unused variables
        self._connections_send = set()
        self._connections_recv = set()
       # osc.bind(self.handle_incoming_osc, "/incoming" + self.full_address)

    def getTypelist(self):
        return self._typelist

    typelist = property(getTypelist)

    def setLabel(self, label):
        self.label = label

    def setDefault(self, kwargs):
        """Set init values.
        
        Reimplemented in subclasses."""
        raise NotImplementedError
        
    def __repr__(self):
            return '<%s (%s)>' % (self.address, str(self.getState()))
    
    def __iter__(self):
        for i in self._state:
            yield i

    def __len__(self):
        return len(self._state)

    def __getitem__(self, k):
        if isinstance(k, slice):
            return [self.__getitem__(i) for i in xrange(k.start, k.stop, k.step)]
        #size = self.__len__()
        return self._state[k]

    def __setitem__(self, k, v):
        """Default implementation for one-item lists."""
        s = self._state[k] #Try
        self.setState(v)

    def __getslice__(self, i, j):
        return self._state[i:j]

    def __add__(self, n):
        return self._state[0] + n
    def __sub__(self, n):
        return self._state[0] - n
    def __mul__(self, n):
        return self._state[0] * n
    def __div__(self, n):
        return self._state[0] / n
    def __iadd__(self, n):
        self.setState(self._state[0] + n)
    def __isub__(self, n):
        self.setState(self._state[0] - n)
    def __imul__(self, n):
        self.setState(self._state[0] * n)
    def __idiv__(self, n):
        self.setState(self._state[0] / n)

    def paramGuiConnect(self, widget, path):
        if path == self.address:
            widget.setParam(self)

    @staticmethod
    def findParamFromPath(path):
        """Return param object from full path, None if not existing"""
        
        return _Param._paths.get(path)

    def printDebugInfo(self):
        print "Address:", self.address
        print "State:", self.getState()
        print "Min:", self.min
        print "Max:", self.max
        print "Type:", self.type
        if self.type is list:
            print "Typelist:", self._typelist

    def getParamInfo(self):
        f = {
                "Address" : self.address,
                "State": self.getState(),
                "Min": self.min,
                "Max": self.max,
                "Type": self.type,
                }
        if self.type is list:
            f["Typelist"] = self._typelist

        return f

            
    def setSaveable(self, boo):
        """Set if param is possible to save in presets, bool"""
        self._saveable = boo and self.type is not Bang
        
    def isSaveable(self):
        """If param is possible to save in preset"""
        return self._saveable
    
    def isBang(self):
        """Return if param is Bang"""
        return self.type is Bang
        
    def setEnableOsc(self, boo):
        """Enable OSC send, bool"""
        self._enableosc = boo
        if boo:
            self.oscEmit = QtGui.qApp.emit
        else:
            self.oscEmit = None

    def setState(self, v):
        """Change current value of _Param.
        
        The value is internally represented as a list. For one item params, the value
        can be set either as a one item list or a single value according to the _Param type.
        If the param type is list, Changes value, sends to OSC and emits signals to eg gui, notifying
        of the changes."""
        raise NotImplementedError
        

    def update(self):
        """Send current state to ui and OSC."""
        try:
            self.oscEmit(_SIGNAL("OscSend"), self.address, self._state)
        except TypeError:
            pass
        self.emit(_SIGNAL("paramUpdate"), int(self.UpdateState))
    
    def setMaxValue(self, v):
        """Set max value.
        
        This is reimplemented in subclasses. This implementation does nothing."""
        pass
    
    def setMinValue(self, v):
        """Set min value.

        This is reimplemented in subclasses. This implementation does nothing."""
        pass
        
    def getState(self,  index = None):
        """Get current state.
        
        The state is internally represented as a one-item list. 
        This makes it possible to pass the reference to the value to other methods.
        I don't know why you'd want to do that, but I probably had a reason once.
        This method extracts the value from the list and returns it."""
        raise NotImplementedError

    def saveSnapshot(self, key):
        """Set snapshot.

        @param key dict key
        """
        if not self._saveable:
            return
        self._snapshots[key] = copy.copy(self._state)

    def loadSnapshot(self, key):
        """Get snapshot.

        @param key dict key
        """
        if not self._saveable:
            return
        try:
            for i, v in self._snapshots.get(key, None):
                self._state[i] = v
        except TypeError:
            pass
        self.update()

    def interpolateSnapshot(self, a, b, factor):
        """Interpolate btwn 2 snapshot according to factor

        @param a dict key: snapshot A
        @param b dict key: snapshot B
        @param factor float(0-1): interpolation factor

        Interpolates two snapshots like this:
        ((a * factor) + b * (1 - factor)) / 2
        """
        a = self._snapshots.get(a, None)
        b = self._snapshots.get(b, None)
        if None in (a, b):
            return
        for i, t in enumerate(self._typelist):
            if t in (float, int):
                self._state[i] = t(b[i] * factor) + (a[i] * (1-factor))
        self.update()


    def fixedType(self, t, index=None):
        """Correct None values according to param type(s).
        
        Checking type(s) of incoming list or (value, index) so it 
        matches self.typelist. None is converted to 0, False or empty string, depending
        on type. In other cases, it asserts that the type is correct (which if it wasn't
        probably would be an error)."""
        if index is None:
            for i, x in enumerate(t):
                t[i] = self.fixedType(x, i)
            return t
        elif t is not None:
            assert self.typecheck(type(t), index)
            return t
        else:
            return self.typelist[index]()
    
    def typecheck(self, t, index=None):
        """Compares type(s) with param typelist.
        
        @param t list/type -- list of types or single type
        @param index=None int -- index of incoming single value
        
        returns bool
        
        Implemented in subclasses."""
        raise NotImplementedError

    def copyFrom(self, o):
        """Copy value(s) from another param."""
        if self.typecheck(o.typelist):
            for i, v in o.getStateReference():
                self._state[i] = self.within(v)
            self.update()
        
#   def check_connection(self, o):
#       """Looking for feedback loops in param connections
#       
#       Before connecting this param to another, this method checks that the
#       other param isn't currently controlling this one, to avoid feedback 
#       control loops. Works recursively through the connection tree."""
#       
#       if self is o:
#           return False
#       clist = self._connections_recv #sic!
#       if o in clist:
#           return False
#       for connection in clist:
#           f = connection.check_connection(o)
#           if f is False:
#               return False
#       return True

#   def add_connection(self, o):
#       """Adds a connection from this _Param to another one. 
#       
#       Returns True if connection was successful, otherwise False."""
#       
#       if (not self.check_connection(o)) or self is o:
#           return False

#       self._connections_send.add(o)
#       o._connections_recv.add(self)
#       return True
#       
#   def remove_connection(self, o):
#       """Remove connection between self and another."""
#       
#       self._connections_send.discard(o)
#       o._connections_recv.discard(self)
#       return True
    
    def handle_incoming_osc(self, path, tag, args):
        """Takes care of incoming osc messages.
        
        Updates state, sends not to OSC (sic) and emits signals for GUI updates."""
        if path != self.address or tag != "setState":
            return
        self._state[0] = self.within(args[0])
        self.emit(_SIGNAL("paramUpdate"), self.UpdateState)

    def set_updates_enabled(self, updates):
        """ Disable path/tree updates for all params
        
        Useful for faster loading of many params: otherwise a recursive tree
        update is made for every new instance. Just remember to enable updates 
        and do an update from the root when all params are instantiated.
        """
        self.__class__._update = updates

    def getMinReference(self):
        return self.min

    def getMaxReference(self):
        return self.max

    def getStateReference(self):
        return self._state

class ListParam(_Param):
    """
    A subclass of _Param for lists.
    """

    def __init__(self, address, typ, **kwargs):
        
        for t in typ:
            assert isinstance(t, type)
        self.type = list
        self._typelist = list(typ)

        _Param.__init__(self, address, list, **kwargs)

        if not None in (kwargs.get('min'), kwargs.get('max')):
            self.max = []
            self.min = []
            for i, t in enumerate(self._typelist):
                try:
                    self.max.append(kwargs.get('max', t(0.0))[i])
                except IndexError:
                    self.max.append(t(1.0))
                try:
                    self.min.append(kwargs.get('min', t(0.0))[i])
                except IndexError:
                    self.min.append(t(0.0))
        else:
            self.max = [t(1) for t in self._typelist]
            self.min = [t(0) for t in self._typelist]
        
        #stupid check
        a = [i in (float, int) for i in self._typelist]
        if True in a and False in a:
            raise TypeError, "Can't mix numbers and other stuff in List param. This is a bug."
        #Init
        self.setState(self._default)

    def setDefault(self, kwargs):
        """
        Set default init value.
        """
        default = list(kwargs.get('default', [t() for t in self._typelist]))
        #Force correct types
        for i, d in enumerate(default):
            default[i] = self._typelist[i](d)
        self._default = default

    def __setitem__(self, k, v):
        self.setState(v, index=k)

    def setState(self, v,  index=None):
        """State setter, OSC sender and gui updater."""
        #Test if whole list, right types and not the same as current state
        if index is None and self.typecheck(
                [type(a) for a in v]) and not v == self._state:
            for i, va in enumerate(v):
                self._state[i] = va
        #Test if index is right type, and not the same as current
        elif self.typecheck(type(v), index) and not self._state[index] == v:
            self._state[index] = self.within(v, index)
        else:
            return
        try:
            self.oscEmit(_SIGNAL("OscSend"), self.address, self._state)
        except TypeError:
            pass
        self.emit(_SIGNAL("paramUpdate"), int(self.UpdateState))


    def within(self, v, i):
        """Clipping list items between boundaries."""
        if self._typelist[i] in (float, int):
            return max(self.min[i], min(self.max[i], v))
        else:
            return v

    def setMaxValue(self, v, index=None):
        """Set max value for list param.
        
        v -- list/float/str/... If arg 2 is present, takes any
        atom as first argument. If not, the list must match the types of
        current list.
        index -- int. 
        """
        v = self.fixedType(v, index)
        if index:
            self.max[index] = v
            return
        self.max = copy.copy(v)
        self.emit(_SIGNAL("paramUpdate"), self.UpdateMax)
    
    def setMinValue(self, v, index = None):
        """Set min value, for list param."""
        v = self.fixedType(v, index)
        if index:
            self.min[index] = v
            return
        self.min = copy.copy(v)
        self.emit(_SIGNAL("paramUpdate"), self.UpdateMin)
        
    def getState(self,  index = None):
        if index is None:
            return copy.copy(self._state)
        else:
            return self._state[index]
        
    
    def typecheck(self, t, index=None):
        """Compares types with param type.

        @param t type/list -- list of types or (if index) single type
        @param index int -- typelist index to compare
        """
        fi = (float, int)
        #If index, we just pick that one and check if both are numbers
        if index is not None:
            return self._typelist[index] is t or (self._typelist[index] in fi and t in fi)
        #If check the whole list, we check one after another and 
        #if any is mismatching, return false...
        for index, v in enumerate(t):
            if self._typelist[index] is not v or not (
                    self._typelist[index] in fi and v in fi):
                return False
        return True

    def handle_incoming_osc(self, path, tag, args):
        """Takes care of incoming osc messages.
        
        Updates state, sends not to OSC (sic) and emits signals for GUI updates."""
        if path != self.address or tag != "setState":
            return
        for i, v in enumerate(args):
            self._state[i] = v
        self.emit(_SIGNAL("paramUpdate"), self.UpdateState)

class _SingleParam(_Param):
    """
    A subclass of _Param for single items.
    """

    def __init__(self, address, type, **kwargs):
        _Param.__init__(self, address, type, **kwargs)

    def setDefault(self, kwargs):
        """Set init values.
        """
        default = kwargs.get('default', self.type())
        self._default = [self.type(default)]

    def getState(self,  index = None):
        """Get current state.
        
        The state is internally represented as a one-item list. 
        This makes it possible to pass the reference to the value to other methods.
        I don't know why you'd want to do that, but I probably had a reason once.
        This method extracts the value from the list and returns it."""
        return self._state[0]

    def saveSnapshot(self, key):
        """Set snapshot.

        @param key dict key
        """
        if not self._saveable:
            return
        self._snapshots[key] = self._state[0]

    def loadSnapshot(self, key):
        """Get snapshot.

        @param key dict key
        """
        if not self._saveable:
            return
        n = self._snapshots.get(key, None)
        if n is not None:
            self.state[0] = n
            self.update()

    def copyFrom(self, o):
        """Copy value(s) from another param."""
        if self.typecheck(o.typelist[0], 0):
            self.state[0] = o.getStateReference()[0]
            self.update()

    def typecheck(self, t, index=None):
        """Compares type t with param type.

        @param t -- type or list of type(s)
        @param index -- index of type (ignored in _SingleParam subclasses)

        This method is called before setting state, to make sure the types of incoming
        data are correct.
        Returns False if not matching, True if matching.
        """
        try:
            t = t[0]
        except TypeError:
            pass
        return self._typelist[0] is t

class NumParam(_SingleParam):
    """
    A subclass of _Param for numbers.
    """

    def __init__(self, address, type, **kwargs):

        assert type in (float, int)
        _SingleParam.__init__(self, address, type, **kwargs)

        # Set min and max for numbers
        self.max = [kwargs.get('max', type(1.0))]
        self.min = [kwargs.get('min', type(0.0))]

        #Init
        self.setState(self._default[0])
    
    def setState(self, v, echo=False):
        t = self.typecheck(type(v))
        if v == self._state[0] or not t:
            return
        if t is 1:
            self._state[0] = max(self.min[0], min(self.max[0], v))
        else:
            self._state[0] = self.type(max(self.min[0], min(self.max[0], v)))
        self.update()
    
    def setMaxValue(self, v):
        """Set max value, for float and int and list params."""
        v = self.fixedType(v, 0)
        self.max[0] = v
        self.emit(_SIGNAL("paramUpdate"), self.UpdateMax)
    
    def setMinValue(self, v):
        """Set min value, for float and int and list params."""
        v = self.fixedType(v, 0)
        self.max[0] = v
        self.emit(_SIGNAL("paramUpdate"), self.UpdateMin)
        
    def typecheck(self, ty, index=0):
        """Compares type t with param type.

        This method is called before setting state, to make sure the types of incoming
        data are correct.
        Returns 0 if not matching, 1 if matching, and 2 if both are numbers, but not of
        the same type (ie int and float).
        """
        fi = (float, int)
        try:
            ty = ty[0]
        except TypeError:
            pass
        if self.type is fi:
            return 1
        elif self.type in fi and ty in fi:
            return 2
        return 0

    def interpolateSnapshot(self, a, b):
        """Interpolate btwn 2 snapshot according to factor

        @param a dict key: snapshot A
        @param b dict key: snapshot B
        @param factor float(0-1): interpolation factor

        Interpolates two snapshots like this:
        ((a * factor) + b * (1 - factor)) / 2
        """
        #In _SingleParam, snapshots are not lists, but single atoms
        a = self._snapshots.get(a, None)
        b = self._snapshots.get(b, None)
        if None in (a, b):
            return
        self._state[0] = t(b * factor) + (a * (1-factor))
        self.update()
    

class FloatParam(NumParam):
    """
    A subclass of NumParam for floats.
    """
    def __init__(self, address, **kwargs):
        NumParam.__init__(self, address, float, **kwargs)

class IntParam(NumParam):
    """
    A subclass of NumParam for ints.
    """
    def __init__(self, address, **kwargs):
        NumParam.__init__(self, address, int, **kwargs)

class StringParam(_SingleParam):
    """
    A subclass of _Param for strings.
    """

    def __init__(self, address, **kwargs):
        _SingleParam.__init__(self, address, str, **kwargs)
        #Init
        
        self.setState(self._default[0])

    def setState(self, v):
        #XXX Currently remixing all input to strings. bad?
        self._state[0] = str(v)
        try:
            self.oscEmit(_SIGNAL("OscSend"), self.address, self._state)
        except TypeError:
            pass
        self.emit(_SIGNAL("paramUpdate"), int(self.UpdateState))
        
class BoolParam(_SingleParam):
    """
    A subclass of _Param for bools.
    """

    def __init__(self, address, **kwargs):
        _SingleParam.__init__(self, address, bool, **kwargs)
        #Init
        self.setState(self._default[0])

    def setState(self, v=None):
        #If v is none, toggle state.
        if v is None:
            v = not self._state[0]
        self._state[0] = bool(v)
        try:
            self.oscEmit(_SIGNAL("OscSend"), self.address, self._state)
        except TypeError:
            pass
        self.emit(_SIGNAL("paramUpdate"), int(self.UpdateState))


class BangParam(_SingleParam):
    """
    A subclass of _Param for Bang.
    """

    def __init__(self, address, **kwargs):
        _SingleParam.__init__(self, address, Bang, **kwargs)

        self._state = [Bang()]

    def setState(self, v=None):
        """Sends a bang to OSC and gui.
        """
        
        try:
            self.oscEmit(_SIGNAL("OscSend"), self.address, None)
        except TypeError:
            pass
        self.emit(_SIGNAL("paramUpdate"), self.UpdateState)

    def update(self):
        """Send current state to ui and OSC."""
        try:
            self.oscEmit(_SIGNAL("OscSend"), self.address, None)
        except TypeError:
            pass
        self.emit(_SIGNAL("paramUpdate"), self.UpdateState)
    
    def __setitem__(self, k, v):
        self.setState()

    def getState(self):
        return self._state[0]



######
#Below is not much too see...
######

class ParamGroup(QtCore.QObject):
    
    _labels = set()

    def __init__(self, label, *args):
        QtCore.QObject.__init__(self, *args)

        if not label in self.__class__._labels:
            self.label = label
            self.__class__._labels.add(label)
        else:
            print "ParamGroup %s already exists." % label
        
        self._params = [] #list of objects


    def append(self, param):
        self._params.append(param)

    def extend(self, param):
        self._params.extend(param)

    def insert(self, index, param):
        self._params.insert(index, param)

    def remove(self, param):
        self._params.remove(param)

    def pop(self, index=None):
        index = index or len(self._params) - 1 
        return self._params.remove(index)

    def index(self, index):
        return self._params.index(index)
    
    def count(self, i):
        return self._params.count(i)

    def reverse(self):
        self._params.reverse()

    def sort(self):
        self._params.sort()

    def __iter__(self):
        for i in self._params:
            yield i

    def __repr__(self):
        return self._params.__repr__()

    def __str__(self):
        return self._params.__str__()

#class ParamController(QtCore.QObject):
#    def __init__(self, *args):
#        QtCore.QObject.__init__(self, *args)
#        
#        self.send_param = None
#        self.recv_param = None
#        
#        self.min_value = 0
#        self.max_value = 0
#        
#        self.enabled = False
#        self.typecheck()
#        
#    def set_sender(self, send):
#        if not isinstance(send, _Param):
#            raise TypeError, "Has to be _Param instance"
#        self.send_param = send
#        self.typecheck()
#        
#    def set_reciever(self, recv):
#        if not isinstance(recv, _Param):
#            raise TypeError, "Has to be _Param instance"
#        self.recv_param = recv
#        self.typecheck()
#        
#    def typecheck(self):
#        fi = (float, int)
#        try:
#            s = self.send_param.type
#            r = self.recv_param.type
#        except AttributeError:
#            pass
#        else:
#            if not (s is r or s in fi and r in fi):
#                ##alert("ParamController can't convert between %s and %s."\
#                ##% (str(self.send_param.type), str(self.recv_param.type)))
#                self.enabled = 0
#            else:
#                self.enabled = 1
#
#    def handle_update(self, p):
#        if p is self.recv_param.UpdateMax:
#            self.recv_param.max = self.send_param.max
#        elif p is self.recv_param.UpdateMin:
#            self.recv_param.min = self.send_param.min
#        elif p is self.recv_param.UpdateState:
#            if self.send_param.type in (bool, str):
#                self.recv_param.set_state(self.send_param.get_state())
#                return
#            v = (((self.send_param.get_state() - float(self.send_param.min)) / \
#                float(self.send_param.max)) * \
#                float(self.max_value - self.min_value)) + float(self.min_value)
#            self.recv_param.set_state(v)
#    
#    def param_connect(self):
#        self.enabled = self.send_param.add_connection(self.recv_param)
#        if self.enabled:
#            self.connect(self.send_param, _SIGNAL("paramUpdate"),
#                self.handle_update)
#        else:
#            pass
#            ##alert("%s->%s: Can't connect" % (self.send_param.full_address, 
#            ##                    self.recv_param.full_address))
#        return self.enabled
#        
#    def param_disconnect(self):
#        if self.send_param and self.recv_param:
#            self.enabled = False
#            self.disconnect(self.send_param, _SIGNAL("paramUpdate"),
#                    self.handle_update)
#            self.send_param.remove_connection(self.recv_param)
#    
#    def set_enabled(self, boo):
#        if boo:
#            return self.param_connect()
#        else:
#            self.param_disconnect()
#            

#pg = ParamGroup("Label")
#p = _Param("/path/to/param", [float, float])
#p.setMaxValue((1, 22.2))
#p[0] = 1
#print p[0]
#p[0] = 0
#print p[0]
#pg.append(p)
#
#p.printDebugInfo()
#p = _Param("/path/to/param", int)
#p.setMaxValue(1)
#p.setState(0.1)
#pg.append(p)
#p = _Param("/path/to/param", str)
#p.setState("Jesus")
#for i in p:
#    print i
#pg.append(p)
#
#p = _Param("/path/to/param", Bang)
#p.setState("Jesus")
#pg.append(p)
##p.printDebugInfo()

if __name__ == '__main__':

    a = QtGui.QApplication(sys.argv)
    #p = IntParam("/foo", max=222, min=0, default=25)
    p = ListParam("/foo", (float, float))
    #p = StringParam("/foo")
    #p = BangParam("/foo")
    b = Bang()

#    sys.exit(a.exec_())
