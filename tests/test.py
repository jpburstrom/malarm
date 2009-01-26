# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created: Tue Dec  2 00:58:48 2008
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

import os 
import sys
from PyQt4 import QtCore, QtGui, uic

TestUi, dummy = uic.loadUiType(os.path.join(sys.path[0], "test.ui"))

from paramwidgets import ParamSpinBox

if __name__ == "__main__":
    import sys
    import param
    app = QtGui.QApplication(sys.argv)
    p = param._Param("/path/to/param", float, max=3)
    Dialog = QtGui.QDialog()
    ui = TestUi()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

