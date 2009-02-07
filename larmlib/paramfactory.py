#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2009 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision: 79 $"

import os
import sys
import copy

from PyQt4 import QtGui, QtCore, uic
import PyQt4.Qwt5 as Qwt

from globals import *
from param import *

class ParamFactory(object):
    """Factory class to create params from widgets."""

    def __init__(self):

        self._mapping = { int : IntParam, float : FloatParam, str : StringParam, bool : BoolParam, Bang : BangParam }
        self._typemethods = {
                "QPoint" : self._pointToIterable,
                "QPointF" : self._pointToIterable,
                "QColor" : self._colorToIterable
                }



    def createParam(self, obj):
        """Create param, connect to widget and return param.

        @param obj -- widget

        Widgets, or in fact any class that hasattr(paramPath) and hasattr(types), are passed to this method which creates
        (and returns) a corresponding param and tries to connect them together.

        Returns None if object lacks the right attributes.
        """
        try:
            p = obj.paramPath
        except AttributeError:
            return None
        if not p:
            return None

        if len(obj.types) == 1:
            param = self._mapping[obj.types[0]](p, default=obj.paramDefault, min=obj.paramMin, max=obj.paramMax)
        else:
            default = self.makeIterable(obj.paramDefault)
            min = self.makeIterable(obj.paramMin)
            max = self.makeIterable(obj.paramMax)
            param = ListParam(p, obj.types, default=default, min=min, max=max)

        obj.setParam(param)
        return param

    def makeIterable(self, v):
        """Converts misc Qt types to a list.

        @param v anything -- type to convert.

        The widgets created through Qt's designer might well define their default, min and max values through some strange
        Qt type. Here they are brute-forcily converted to a plain python list, while waiting for the day when you will be
        able to edit python types through Designer's properties window.

        This method is stupid and slow.
        """
        try:
            return list(v)
        except TypeError:
            pass
        try:
            return self._typemethods[v.__class__.__name__](v)
        except KeyError:
            raise NotImplementedError, "Can not convert type %s to list" % v.__class__.__name__

    def _pointToIterable(self, p):
        return (p.x(), p.y())

    def _colorToIterable(self, c):
        return (c.redF(), c.greenF(), c.blueF(), c.alphaF())
        






