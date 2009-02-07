#!/usr/bin/env python

"""
"""

from PyQt4.QtCore import QString, QVariant, QPoint, SIGNAL, SLOT, pyqtSignature
from PyQt4.QtDesigner import QExtensionFactory, QPyDesignerTaskMenuExtension, \
                             QDesignerFormWindowInterface
from PyQt4.QtGui import QAction, QDialog, QDialogButtonBox, QGridLayout, \
            QLineEdit, QPushButton, QDoubleSpinBox, QSpinBox, QLabel, QVBoxLayout, \
            QFrame, QCheckBox
from paramwidgets import *


class MalarmWidgetsMenuEntry(QPyDesignerTaskMenuExtension):

    def __init__(self, widget, parent):
    
        QPyDesignerTaskMenuExtension.__init__(self, parent)

        
        self.widget = widget
        
        # Create the action to be added to the form's existing task menu
        # and connect it to a slot in this class.
        self.editOscAddressAction = QAction("Malarm Properties...", self)
        self.connect(self.editOscAddressAction, SIGNAL("triggered()"),
                     self.updateOscAddress)
    
    def preferredEditAction(self):
        return self.editOscAddressAction
    
    def taskActions(self):
        return [self.editOscAddressAction]
    
    # The updateLocation() slot is called when the action that represents our
    # task menu entry is triggered. We open a dialog, passing the custom widget
    # as an argument.
    def updateOscAddress(self):
        dialog = OscAddressDialog(self.widget)
        dialog.exec_()


class MalarmTaskMenuFactory(QExtensionFactory):

    """GeoLocationTaskMenuFactory(QExtensionFactory)
    
    Provides a task menu that can be used to access an editor dialog.
    """
    def __init__(self, parent = None):
    
        QExtensionFactory.__init__(self, parent)
    
    # This standard factory function returns an object to represent a task
    # menu entry.
    def createExtension(self, obj, iid, parent):
    
        if iid != "com.trolltech.Qt.Designer.TaskMenu":
            return None
        
        # We pass the instance of the custom widget to the object representing
        # the task menu entry so that the contents of the custom widget can be
        # modified.
        if hasattr(obj, "paramPath"):
            return MalarmWidgetsMenuEntry(obj, parent)
        
        return None


class OscAddressDialog(QDialog):

    """OscAddressDialog(QDialog)
    
    Provides a dialog that is used to edit the contents of the custom widget.
    """
    
    def __init__(self, widget, parent = None):
    
        QDialog.__init__(self, parent)
        
        # We keep a reference to the widget in the form.
        self.widget = widget
        try:
            self.type = type(widget.paramMin).__name__
        except AttributeError:
            try:
                self.type = type(widget.paramDefault).__name__
            except AttributeError:
                self.type = "Bang"
        
        self.address = QLineEdit(self)
        self.address.setText(widget.paramPath)
        self.address.setSelection(0, self.address.maxLength())
        
        self.default = [None for i in range(self.widget.length)]
        self.max = [None for i in range(self.widget.length)]
        self.min = [None for i in range(self.widget.length)]
        self.setupAtoms()
        self.setValues()
        
        
        buttonBox = QDialogButtonBox()
        okButton = buttonBox.addButton(buttonBox.Ok)
        cancelButton = buttonBox.addButton(buttonBox.Cancel)
        
        self.connect(okButton, SIGNAL("clicked()"),
                     self.updateWidget)
        self.connect(cancelButton, SIGNAL("clicked()"),
                     self, SLOT("reject()"))
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("OSC Path", self))
        layout.addWidget(self.address)
        self.setupAtomUi(layout)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        
        self.setWindowTitle(self.tr("Edit Malarm Properties"))
    
    # When we update the contents of the custom widget, we access its
    # properties via the QDesignerFormWindowInterface API so that Qt Designer
    # can integrate the changes we make into its undo-redo management.
    def updateWidget(self):
    
        formWindow = QDesignerFormWindowInterface.findFormWindow(self.widget)
        
        if formWindow:
            formWindow.cursor().setProperty("paramPath", QVariant(self.address.text()))
            if self.widget.length is 1 and self.min[0] is not None:
                formWindow.cursor().setProperty("paramMin", QVariant(self.min[0].value()))
                formWindow.cursor().setProperty("paramMax", QVariant(self.max[0].value()))
                formWindow.cursor().setProperty("paramDefault", QVariant(self.default[0].value()))
            elif self.type == "str":
                formWindow.cursor().setProperty("paramDefault", QVariant(self.default[0].text()))
            elif self.type == "bool":
                formWindow.cursor().setProperty("paramDefault", QVariant(self.default[0].isChecked()))
            elif self.type == "QPoint":
                formWindow.cursor().setProperty("paramMin", QVariant(
                    QPoint(self.min[0].value(), self.min[1].value())))
                formWindow.cursor().setProperty("paramMax", QVariant(
                    QPoint(self.max[0].value(), self.max[1].value())))
                formWindow.cursor().setProperty("paramDefault", QVariant(
                    QPoint(self.default[0].value(), self.default[1].value())))
        self.accept()

    def setupAtoms(self):
        for i in range(self.widget.length):
            self.setupAtom(i, self.widget.types[i])

    def setupAtom(self, i, type):
        if type is float:
            self.min[i] = QDoubleSpinBox(self)
            self.max[i] = QDoubleSpinBox(self)
            self.default[i] = QDoubleSpinBox(self)
        elif type is int:
            self.default[i] = QSpinBox(self)
            self.min[i] = QSpinBox(self)
            self.max[i] = QSpinBox(self)
        elif type is str:
            self.default[i] = QLineEdit(self)
        elif type is bool:
            self.default[i] = QCheckBox(self)

    def setValues(self):
        if self.widget.length is 1 and self.min[0] is not None:
            self.min[0].setValue(self.widget.paramMin)
            self.max[0].setValue(self.widget.paramMax)
            self.default[0].setValue(self.widget.paramDefault)
        elif self.type == "QString":
            self.default[0].setText(self.widget.paramDefault)
        elif self.type == "bool":
            self.default[0].setChecked(self.widget.paramDefault)
        elif self.type == "QPoint":
            self.min[0].setValue(self.widget.paramMin.x())
            self.min[1].setValue(self.widget.paramMin.y())
            self.max[0].setValue(self.widget.paramMax.x())
            self.max[1].setValue(self.widget.paramMax.y())
            self.default[0].setValue(self.widget.paramDefault.x())
            self.default[1].setValue(self.widget.paramDefault.y())


    def setupAtomUi(self, box):
        if self.type == "Bang":
            return
        frame = QFrame(self)
        box.addWidget(frame)
        layout = QGridLayout(frame)
        layout.setContentsMargins(0,0,0,0)
        for i, default in enumerate(self.default):
            layout.addWidget(QLabel("Default value", self), (i*2)+3, 2, 1, 1)
            layout.addWidget(default, (i*2)+4, 2, 1, 1)
            if not None in (self.min[i], self.max[i]):
                layout.addWidget(QLabel("Min value", self), (i*2)+3, 0, 1, 1)
                layout.addWidget(self.min[i], (i*2)+4, 0, 1, 1)
                layout.addWidget(QLabel("Max value", self), (i*2)+3, 1, 1, 1)
                layout.addWidget(self.max[i], (i*2)+4, 1, 1, 1)
