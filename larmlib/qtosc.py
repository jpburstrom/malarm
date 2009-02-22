#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2007 Johannes Burström, <johannes@ljud.org>
__version__ = "$Revision$"


import os
import sys
import copy

from PyQt4 import QtGui, QtCore, uic
from liblo import *

from param import Bang

class Emitter(QtCore.QObject):
    def __init__(self, parent = None, *args):
        QtCore.QObject.__init__(self, *args)

        self.server = parent

        self.connect(QtGui.qApp, QtCore.SIGNAL("OscSend"), self.sendOsc)
        self.connect(self, QtCore.SIGNAL("OscReceive"), self.printIncomingOsc)
        self.connect(QtGui.qApp, QtCore.SIGNAL("registerOscReceiver"), self.server.registerReceiver)
        self.connect(QtGui.qApp, QtCore.SIGNAL("clearOscReceivers"), self.clearOscReceivers)

        self._timer = None
        self._tobundle = []

    def clearOscReceivers(self):
        """Clear the osc servers list of receivers."""

        self.server.receivers.clear()

    def sendOsc(self, add, mess):
        """Osc sending method, easiest called with the qApp.OscSend signal.
        
        The OSC receivers are defined with a port and a label. The label is
        prepended to the internal OSC path, and later on stripped out by this method
        to send the message to the right port:
        testport = 9999
        /testport/foo/bar testmessage
        =>
        /foo/bar testmessage sent to localhost:9999
        """

        li = str(add).split("/")
        try:
            recv = li.pop(1)
        except IndexError:
            #FIXME: shouldn't be possible to send from no-address params
            return
        add = "/".join(li)

        self._tobundle.append((recv, add, mess))
        
        self._timer = self._timer or self.startTimer(1)

    def printIncomingOsc(self, path, args, sender):
        """Print incoming OSC msgs for debug."""
        print "Incoming:", path, args, sender

    def timerEvent(self, ev):
        """Ticking clock handling osc sending."""
        b = {}
        r = self.server.receivers
        while self._tobundle:
            recv, path, arg = self._tobundle.pop()
            if arg is not None:
                b.setdefault(recv, Bundle()).add(Message(path, *arg))
            else:
                b.setdefault(recv, Bundle()).add(Message(path))
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
        """Register receiver of outgoing osc msgs.
        The OSC receivers are defined with a port and a label. The label is
        prepended to the internal OSC path, and later on stripped out 
        to send the message to the right port:
        testport = 9999
        /testport/foo/bar testmessage
        =>
        /foo/bar testmessage sent to localhost:9999
        """

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
        #TODO: figure out if this is needed, and how to implement it.
            
        #for receiver, v in self.receivers.items():
        #    if v.get_url() == src.get_url():
        #        break
        #self.create_sender(receiver, args[0], args[1])

        #p = args[0].split("/")
        #p.insert(1, receiver)
        #path= "/".join(p)
        #self.emitter.emit(QtCore.SIGNAL("NewParam"), path, args[1])

        
    def registerAddressFromParam(self, param):
        """Setup OSC handling for a single param."""

        a = str(param.address)
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
        self.registerAddress(receiver, address, typestring)

    def registerAddress(self, receiver, address, type):
        """Register a (main) OSC address and a set of helper addresses.
        
        @param receiver str -- receiver label (used to connect to the right port)
        @param address str -- address to register
        @param type str -- OSC Type Tag String according to OSC specification

        Besides registration of the main OSC address, some receivers are also set up:
        /foo/bar -- set value
        /setup/foo/bar/max -- set max value
        /setup/foo/bar/min -- set min value
        Through these you can update the value and range of a param from the outside.
        NB: As this works right now, a param (the internal representation of 
        an OSC address) can only be controlled from a single receiver. 
        """

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
        self.add_method(address, type, 
                self.incomingParamChange, (receiver, address)) #for incoming messages

    def setDefault(self, path, args, type, src, data):
        """Callback function to set incoming OSC, setting default value for single param."""

        path = self._internalPaths.get((path, data[0]), self.makeInternalPath(path, data[0]))
        QtGui.qApp.emit(QtCore.SIGNAL("OscReceive"), path, "setDefault", [(a, t) for a, t in zip(args, type)])

    def setMax(self, path, args, type, src, data):
        """Callback function to set incoming OSC, setting max value for single param."""
        path = self._internalPaths.get((path, data[0]), self.makeInternalPath(path, data[0]))
        QtGui.qApp.emit(QtCore.SIGNAL("OscReceive"), path, "setMax", [(a, t) for a, t in zip(args, type)])

    def setMin(self, path,args, type, src, data):
        """Callback function to set incoming OSC, setting min value for single param."""
        path = self._internalPaths.get((path, data[0]), self.makeInternalPath(path, data[0]))
        QtGui.qApp.emit(QtCore.SIGNAL("OscReceive"), path, "setMin", [(a, t) for a, t in zip(args, type)])

    def incomingParamChange(self, path, args, type, src, data):
        """Callback function to set incoming OSC, setting value for single param."""
        path = self._internalPaths.get((path, data[0]), self.makeInternalPath(path, data[0], 1))
        QtGui.qApp.emit(QtCore.SIGNAL("OscReceive"), path, "setState", args)
    
    def makeInternalPath(self, path, receiver):
        """Make internal path from incoming (path, receiver). 

        @param path
        @param receiver string -- receiver label

        /fee/foo, recv, 1 => /recv/fee/foo
        /fee/foo, recv, 2 => /fee/recv/foo
        ,,,
        """
        #TODO: some day take a look at this to tell if this stupid juggling is really necessary.

        p = path.split("/")
        p.insert(slot, receiver)
        return self._internalPaths.setdefault((path, receiver), "/".join(p))

    #This seems to short-circuit all other receivers... uncomment make_method below if you need to test anything...
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
