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

from PyQt4 import Qt, QtGui, QtCore, uic

MainUI, dummy = uic.loadUiType(os.path.join(sys.path[0], "test.ui"))

#TODO: update file writing to use persistance module

class Viewer(MainUI, QtGui.QDialog):
    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)

        MainUI.setupUi(self)


def main(args):
    app = Qt.QApplication(args)
    win = Viewer(None)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)


