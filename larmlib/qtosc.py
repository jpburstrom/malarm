#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2007 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision: 70 $"


import os
import sys
import copy

from PyQt4 import QtGui, QtCore, uic
from liblo import *

from param import Bang

class Emitter(QtCore.QObject):
    def __init__(self, parent = None, *args):
        QtCore.QObject.__init__(self, *args)

        self.helper = parent

        self.connect(QtGui.qApp, QtCore.SIGNAL("OscSend"), self.sendOsc)
        self.connect(self, QtCore.SIGNAL("OscReceive"), self.printIncomingOsc)
        self.connect(self, QtCore.SIGNAL("NewParam"), self.printNewParam)
        self.connect(QtGui.qApp, QtCore.SIGNAL("registerOscReceiver"), self.registerOscReceiver)
        self.connect(QtGui.qApp, QtCore.SIGNAL("clearOscReceivers"), self.clearOscReceivers)

        self._timer = None
        self._tobundle = []

    def registerOscReceiver(self, *args):
        self.helper.registerReceiver(*args)

    def clearOscReceivers(self):
        self.helper.receivers.clear()

    def sendOsc(self, add, mess):
        """Osc sending method, easiest called with the qApp.OscSend signal."""
        li = add.split("/")
        recv = li.pop(1)
        add = "/".join(li)

        self._tobundle.append((recv, add, mess))
        
        self._timer = self._timer or self.startTimer(1)

    def emitThis(self, path, args, types, sender):
        #FIXME: maybe change to global send..
        self.emitter.emit(QtCore.SIGNAL("OscReceive"), path, [(a, t) for a, t in zip(args, types)], sender)

    def printIncomingOsc(self, path, args, sender):
        print "Incoming:", path, args, sender

    def printNewParam(self, path, args):
        print "New Param:", path, args

    def timerEvent(self, ev):
        b = {}
        r = self.helper.receivers
        while self._tobundle:
            recv, path, arg = self._tobundle.pop()
            b.setdefault(recv, Bundle()).add(Message(path, *arg))
            try:
                [send(r[recv], bun) for recv, bun in b.items()]
            except KeyError:
                pass
        self.killTimer(self._timer)
        self._timer = None


class OscHelper(ServerThread):
    """All-in-one OSC send and receive class.

    Use one instance in your app. The OscReceive signal will be emitted everytime you get an incoming OSC message.
    Emit OscSend signal with address, message and optional receiver as arguments to send osc messages.
    """

    def __init__(self):
        
        self.sendport = 1234

        ServerThread.__init__(self, self.sendport)


        self.receivers = {} # dictionary of recieving hosts
        self.params = {} #dictionary of params... maybe use this as saving

        self._internalPaths = {}

        #FIXME: remove. this should be done from project.

        self.emitter = Emitter(self)
        
    def registerReceiver(self, label, port, host="localhost"):
        """Register receiver of outgoing osc msgs, with label for optional multiple receivers"""

        try:
            path = self._makePath(host, port)
            print "OSC: registered receiver %s at path %s" % (label, path)
            self.receivers[label] = Address(path)
            if label not in self.params:
                self.params[label] = {}
        except AddressError, err:
            self.do_error(err)
    
    def do_error(self, err):
        """Error message handling method."""

        print str(err)

    @make_method("/setup/register", "ss")
    def setup(self, path, args, types, src):
        "Handle incoming setup messages. Not fully implemented."
            
        for receiver, v in self.receivers.items():
            if v.get_url() == src.get_url():
                break
        self.create_sender(receiver, args[0], args[1])

        p = args[0].split("/")
        p.insert(1, receiver)
        path= "/".join(p)
        #self.emitter.emit(QtCore.SIGNAL("NewParam"), path, args[1])

        

    def create_sender(self, receiver, address, type):
        "Create sender and related osc message addresses"

        if not receiver in self.params:
            print "Receiver %s not registered" % receiver
            return
        if address not in self.params[receiver]:
            self.params[receiver][address] = {"type" : type }
        else:
            self.params[receiver][address]["type"] = type
        
        relpath = address[1:]
        self.add_method(os.path.join(
            "/setup", relpath, "default"), type, self.setDefault, (receiver, address)) # default value for param
        self.add_method(os.path.join("/setup", relpath, 
            "max"), type, self.setMax, (receiver, address)) #max value for param (numbers only)
        self.add_method(os.path.join("/setup", relpath, 
            "min"), type, self.setMin, (receiver, address)) #min value for param (numbers only)
        self.add_method(os.path.join("/setup", relpath, 
            "addchoice"), type, self.setMin, (receiver, address)) #for multiple-choice params.
        self.add_method(address, type, 
                self.incomingParamChange, (receiver, address)) #for incoming messages

    def createSenderFromParam(self, param):
        a = param.address
        a = a.split("/")
        receiver = a.pop(1)
        address = "/".join(a)
        #Convert real types to char thingies, ugly 3am version
        types = (("f",float), ("i",int), ("i",bool), ("s",str), ("s", Bang))
        li = [param.type]
        typestring = ""
        if param.type is list:
            li = copy.copy(param.typelist)
        for i, k in enumerate(li):
            for j in types:
                if k in j:
                    typestring += j[0] 
        self.create_sender(receiver, address, typestring)



    def setDefault(self, path, args, type, src, data):
        path = self._internalPaths.get((path, data[0]), None) or self.makeInternalPath(path, data[0])
        QtGui.qApp.emit(QtCore.SIGNAL("OscReceive"), path, "setDefault", [(a, t) for a, t in zip(args, type)])

    def setMax(self, path, args, type, src, data):
        path = self._internalPaths.get((path, data[0]), None) or self.makeInternalPath(path, data[0])
        QtGui.qApp.emit(QtCore.SIGNAL("OscReceive"), path, "setMax", [(a, t) for a, t in zip(args, type)])

    def setMin(self, path,args, type, src, data):
        path = self._internalPaths.get((path, data[0]), None) or self.makeInternalPath(path, data[0])
        QtGui.qApp.emit(QtCore.SIGNAL("OscReceive"), path, "setMin", [(a, t) for a, t in zip(args, type)])

    def incomingParamChange(self, path, args, type, src, data):
        print "inco"
        path = self._internalPaths.get((path, data[0]), None) or self.makeInternalPath(path, data[0], 1)
        QtGui.qApp.emit(QtCore.SIGNAL("OscReceive"), path, "setState", args)
    
    def makeInternalPath(self, path, receiver, slot=2):
        """World's most broken api.

        @param path
        @param receiver string -- receiver label
        @param slot -- where in osc dir to put the receiver string

        /fee/foo, recv, 1 => /recv/fee/foo
        /fee/foo, recv, 2 => /fee/recv/foo
        ,,,
        """
        p = path.split("/")
        p.insert(slot, receiver)
        return self._internalPaths.setdefault((path, receiver), "/".join(p))

    #This seems to short-circuit all other receivers... uncomment this below if you need to test anything...
    #@make_method(None, None)
    def fallback(self, path, args, types, src):
        """Fallback catch-all method for incoming osc messages.

        Emits an OscReceive signal which can be used to get incoming Osc messages."""

        print "fallback", path, args, types, src
        QtGui.qApp.emit(QtCore.SIGNAL("OscReceive"), path, [(a, t) for a, t in zip(args, types)], src.get_url())

    def _makePath(self, host, port):
        """Make path from host and port."""
        return "osc.udp://%s:%d" % (host, port)

if __name__ == "__main__":
    def appendText(self, *args):
        edit.append("Sender %s: %s" % (args[1], " ".join([str(ar[0]) for ar in args[0]])))
    def on_btn_clicked():
        server.emitter.sendOsc("/default/fii/foo", [2,2,3])

    a = QtGui.QApplication(sys.argv)
    server = OscHelper()
    server.start()
    win = QtGui.QMainWindow()
    edit = QtGui.QTextEdit(win)
    edit.connect(QtGui.qApp, QtCore.SIGNAL("OscReceive"), appendText)
    win.setCentralWidget(edit)
    btn = QtGui.QPushButton(win)
    btn.connect(btn, QtCore.SIGNAL("clicked()"), on_btn_clicked)
    

    win.show()

    sys.exit(a.exec_())
