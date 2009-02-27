#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2009 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision: 85 $"
"""A library of more or less useful plugins used by the ParamBoxController.
To make your own, just subclass the _AbstractPlugin class and reimplement the __call__ method.
All classes are instantiated once per ParamBoxController, so variables specific to a 
single ParamBox is possible to define.
"""

#TODO: Make some nice plugins


import sys
import random

from PyQt4 import QtGui

import param

class _AbstractPlugin(object):
    """
    Abstract plugin to extend with nice functions.
    """

    def __init__(self, paramlist):
        """
        Constructor.
        @param paramlist list -- list of params to 
        @param label string -- label of plugin

        This most importantly puts all params in a dictionary, organized by type. All params are defined as
        a 4-item tuple, with state reference, min value(s), max value(s) and typelist.
        This is used to change the param values in the __call__ function.
        """
        
        self._params = {}
        for t in (int, float, str, bool, list, param.Bang):
            self._params[t] = [(p.getStateReference(), p.min, p.max, p.typelist) for p in paramlist if p.type is t]

        print self._params

    def __call__(self):
        """
        Do some things with the param.
        Implement this in your subclasses.
        """
        raise NotImplementedError


class RandomizeNumbers(_AbstractPlugin):
    """Set float, int and list[float, int] to a random value between the param min and max values."""
    def __init__(self, paramlist):
        _AbstractPlugin.__init__(self, paramlist)

    def __call__(self):
        random = random.random
        for p in self._params[float]:
            p[0][0] = (random() * p[2][0]) + p[1][0]
        for p in self._params[int]:
            p[0][0] = int(random() * p[2][0]) + p[1][0]
        for p in self._params[list]:
            for i, t in enumerate(p[3]):
                if t in (float, int):
                    p[0][i] = t(random() * p[2][i]) + p[1][i]

class ScrambleStrings(_AbstractPlugin):
    """Scramble strings of string params. (Pretty useless, yes)."""
    def __init__(self, paramlist):
        _AbstractPlugin.__init__(self, paramlist)

    def __call__(self):
        for p in self._params[str]:
            p[0][0] = "".join(random.sample(p[0][0], len(p[0][0])))




if __name__ == "__main__":

    a = QtGui.QApplication(sys.argv)
    win = QtGui.QMainWindow(None)

    p = param.StringParam("/test/foo")
    p.setState("Fishball")
    p.printDebugInfo()
    r = ScrambleStrings([p])
    r()
    p.printDebugInfo()

    win.show()

    sys.exit(a.exec_())


        
