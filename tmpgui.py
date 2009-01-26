# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/johannes/.larm2/default/gui.ui'
#
# Created: Tue Jan 27 00:03:25 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(762, 524)
        Form.setMinimumSize(QtCore.QSize(762, 524))
        self.paramProgress = ParamProgress(Form)
        self.paramProgress.setGeometry(QtCore.QRect(0, 0, 21, 24))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.paramProgress.sizePolicy().hasHeightForWidth())
        self.paramProgress.setSizePolicy(sizePolicy)
        self.paramProgress.setMinimumSize(QtCore.QSize(21, 0))
        self.paramProgress.setMaximumSize(QtCore.QSize(21, 16777215))
        self.paramProgress.setMaximum(1000)
        self.paramProgress.setProperty("paramPath", QtCore.QVariant(QtGui.QApplication.translate("Form", "/default/path/tp", None, QtGui.QApplication.UnicodeUTF8)))
        self.paramProgress.setObjectName("paramProgress")
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(90, 50, 334, 321))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.paramBoxController_2 = ParamBoxController(self.frame)
        self.paramBoxController_2.setMaximumSize(QtCore.QSize(16777215, 46))
        self.paramBoxController_2.setObjectName("paramBoxController_2")
        self.verticalLayout_2.addWidget(self.paramBoxController_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.pingpong = ParamBox(self.frame)
        self.pingpong.setObjectName("pingpong")
        self.gridLayout = QtGui.QGridLayout(self.pingpong)
        self.gridLayout.setObjectName("gridLayout")
        self.soundfileViewer = SoundFileViewer(self.pingpong)
        self.soundfileViewer.setObjectName("soundfileViewer")
        self.gridLayout.addWidget(self.soundfileViewer, 1, 0, 1, 1)
        self.paramLabel = ParamLabel(self.pingpong)
        self.paramLabel.setObjectName("paramLabel")
        self.gridLayout.addWidget(self.paramLabel, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.pingpong)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.paramGrid_2 = ParamGrid(Form)
        self.paramGrid_2.setGeometry(QtCore.QRect(510, 150, 100, 100))
        self.paramGrid_2.setObjectName("paramGrid_2")
        self.fileBrowserWidget = FileBrowserWidget(Form)
        self.fileBrowserWidget.setGeometry(QtCore.QRect(480, 270, 256, 224))
        self.fileBrowserWidget.setObjectName("fileBrowserWidget")
        self.spinBox = QtGui.QSpinBox(Form)
        self.spinBox.setGeometry(QtCore.QRect(140, 400, 121, 22))
        self.spinBox.setMaximum(999999999)
        self.spinBox.setObjectName("spinBox")
        self.paramSpinbox = ParamSpinBox(Form)
        self.paramSpinbox.setGeometry(QtCore.QRect(290, 390, 111, 21))
        self.paramSpinbox.setMaximum(999999999)
        self.paramSpinbox.setObjectName("paramSpinbox")

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.pingpong, QtCore.SIGNAL("paramsCollected(PyQt_PyObject)"), self.paramBoxController_2.addParams)
        QtCore.QObject.connect(self.soundfileViewer, QtCore.SIGNAL("pointSelected(int)"), self.spinBox.setValue)
        QtCore.QObject.connect(self.soundfileViewer, QtCore.SIGNAL("pointSelected(int)"), self.paramSpinbox.setValue)
        QtCore.QObject.connect(self.paramLabel, QtCore.SIGNAL("textChanged(QString)"), self.soundfileViewer.setFilename)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.paramBoxController_2.setGroupLabel(QtGui.QApplication.translate("Form", "KingKong", None, QtGui.QApplication.UnicodeUTF8))

from paramboxcontroller import ParamBoxController
from soundfileviewer import SoundFileViewer
from paramwidgets import ParamBox, ParamSpinBox, ParamProgress, ParamGrid, ParamLabel
from filebrowser import FileBrowserWidget
