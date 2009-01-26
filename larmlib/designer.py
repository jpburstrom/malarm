#!/usr/bin/env python

# This example launches Qt Designer after setting up the environment to point
# at the example plugins.
#
# Copyright (c) 2007 Phil Thompson


import sys
import os.path

from PyQt4 import QtCore, QtGui


# Set a specified environment variable with a directory name.
def setEnvironment(env, var_name, dir_name):
    # Convert the relative directory name to an absolute one.
    dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), dir_name)

    # Remove any existing value so that we have a controlled environment.
    idx = env.indexOf(QtCore.QRegExp("^%s=.*" % var_name, QtCore.Qt.CaseInsensitive))

    if idx >= 0:
        env.removeAt(idx)

    env << "%s=%s" % (var_name, dir)


def runDesigner(filename=None, wait=False):
        
    # Tell Qt Designer where it can find the directory containing the plugins and
    # Python where it can find the widgets.
    env = QtCore.QProcess.systemEnvironment()
    setEnvironment(env, "PYQTDESIGNERPATH", sys.path[0])
    setEnvironment(env, "PYTHONPATH", sys.path[0])

    # Start Designer.
    designer = QtCore.QProcess()
    designer.setEnvironment(env)

    designer_bin = QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.BinariesPath)

    if sys.platform == "darwin":
        designer_bin.append("/Designer.app/Contents/MacOS/Designer")
    else:
        designer_bin.append("/designer")

    if filename and not wait:
        designer.start(designer_bin, [filename])
    else:
        designer.start(designer_bin)
    if wait:
        designer.waitForFinished(-1)
    return designer

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    runDesigner(wait=True)
    sys.exit(designer.exitCode())
