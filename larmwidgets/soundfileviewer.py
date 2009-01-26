#!/usr/bin/env python

import sys
from PyQt4 import Qt, QtCore, QtGui
import PyQt4.Qwt5 as Qwt
import wave
import numpy
import struct
import scikits.audiolab as audiolab

class LoadingThread(QtCore.QThread):
    def __init__(self, a, indexarray, soundarray, *args):
        QtCore.QThread.__init__(self, *args)

        self._soundfile = a
        self._soundindexarray = indexarray
        self._soundarray = soundarray
        self.chunksize = int(a.nframes / len(indexarray))

    def run(self):
        [self.setData(i, numpy.average(self._soundfile.read_frames(self.chunksize))) for i in self._soundindexarray]

    def setData(self, i, data):
        self._soundarray[i] = data

class MyPlotPicker(Qwt.QwtPlotPicker):
    def __init__(self, *args):
        Qwt.QwtPlotPicker.__init__(self, *args)
        self.beginning = None
        self.end = None
        self.new = 0

        self.connect(
            self, Qt.SIGNAL('selected(const QwtPolygon&)'), self.endRect)
        self.connect(
                self, Qt.SIGNAL('moved(const QPoint &)'), self.moveRect)

    def drawRubberBand(self, p):
        if self.beginning is None:
            return
        pa = self.selection()
        p1 = pa[0]
        p1.setY(0)
        pRect = self.pickRect()
        p2 = pa[int(pa.count() - 1)]
        p2.setY(pRect.height())
        
        rect = QtCore.QRect(p1, p2)
        pen = QtGui.QPen(QtGui.QColor("black"))
        pen.setWidth(2)
        p.setPen(pen)

        Qwt.QwtPainter.drawRect(p, rect)

    def moveRect(self, p):
        x = p.x()
        if self.beginning is None:
            self.beginning = x
            self.end = x
        else:
            self.end = x
    
    def endRect(self, p):
        self.beginning, self.end = None, None

    def widgetKeyPressEvent(self, ev):
        self.plot().emit(Qt.SIGNAL("keyPressed"), ev)

    def widgetKeyReleaseEvent(self, ev):
        self.plot().emit(Qt.SIGNAL("keyReleased"), ev)

class MyPlotMagnifier(Qwt.QwtPlotMagnifier):
    def __init__(self,  *args):
        Qwt.QwtPlotMagnifier.__init__(self, *args)
        self.current = 1

    def rescale(self, factor):
        factor = factor * factor
        self.current = self.current * factor
        if self.current > 1:
            p = self.plot()
            a = p.xBottom
            p.setAxisScale(a, 0, 20000)
            p.setAxisAutoScale(a)
            self.current = 1
            return
        Qwt.QwtPlotMagnifier.rescale(self, factor)

class MyPlotPanner(Qwt.QwtPlotPanner):
    
    def __init__(self,  *args):
        Qwt.QwtPlotPanner.__init__(self, *args)

        self.setMouseButton(QtCore.Qt.MidButton)
        self.setOrientations(QtCore.Qt.Horizontal)

    def widgetMouseMoveEvent(self, ev):
        Qwt.QwtPlotPanner.widgetMouseMoveEvent(self, ev)

class SoundFileViewer(QtGui.QWidget):
    """A Soundfile viewing widget.

    Features: Not-so-fast loading of soundfiles. A selectable range (RMB) and 
    point (LMB), which could be used for many purposes. 
    These can be used with some key press/release signals for endless functionality
    without any visual feedback.
    """

    __pyqtSignals__ = (
            "rangeSelected(PyQt_PyObject)", # 2-item tuple
            "pointSelected(int)",
            "keyReleased(const QKeyReleaseEvent &)",
            "keyPressed(const QKeyPressEvent &)"
            )

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)

        self.plot = Qwt.QwtPlot(self)
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.plot)
        layout.setContentsMargins(0,0,0,0)

        self.curve = Qwt.QwtPlotCurve("Curve1")
        self.chunks = 2000
        self.chunksize = 0

        self.markerL = Qwt.QwtPlotMarker()
        self.markerL.setLineStyle(Qwt.QwtPlotMarker.VLine)
        self.markerL.setLabelAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        self.markerL.setLabel(Qwt.QwtText(QtCore.QString("L")))
        self.markerL.setLinePen(QtGui.QPen(QtGui.QColor("red")))
        self.markerR = Qwt.QwtPlotMarker()
        self.markerR.setLineStyle(Qwt.QwtPlotMarker.VLine)
        self.markerR.setLabelAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.markerR.setLabel(Qwt.QwtText(QtCore.QString("R")))
        self.markerR.setLinePen(QtGui.QPen(QtGui.QColor("green")))
        self.markerL.setXValue(3000)

        self.setMinimumHeight(30)
        self.setMinimumWidth(100)


        self.plot.enableAxis(0, 0)
        self.plot.enableAxis(2, 0)
        self.curve.attach(self.plot)
        self.markerL.attach(self.plot)
        self.markerR.attach(self.plot)
        self.picker = MyPlotPicker(Qwt.QwtPlot.xBottom,
                                   Qwt.QwtPlot.yLeft,
                                   Qwt.QwtPicker.RectSelection | Qwt.QwtPicker.DragSelection,
                                   Qwt.QwtPlotPicker.RectRubberBand,
                                   Qwt.QwtPicker.AlwaysOff,
                                   self.plot.canvas())
        self.picker.setMousePattern([Qwt.QwtEventPattern.MousePattern(
            Qt.Qt.RightButton,Qt.Qt.NoModifier)])
        self.picker2 = Qwt.QwtPlotPicker(Qwt.QwtPlot.xBottom,
                                   Qwt.QwtPlot.yLeft,
                                   Qwt.QwtPicker.PointSelection,
                                   Qwt.QwtPlotPicker.VLineRubberBand,
                                   Qwt.QwtPicker.AlwaysOff,
                                   self.plot.canvas())
        #mag = MyPlotMagnifier(self.canvas())
        #mag.setAxisEnabled(self.yLeft, False)
        #self.pan = MyPlotPanner(self.canvas())
        self.beginning = None
        self.end = None
        self.connect(
            self.picker, Qt.SIGNAL('selected(const QwtPolygon&)'), self.endRect)
        self.connect(
                self.picker, Qt.SIGNAL('moved(const QPoint &)'), self.moveRect)
        self.connect(
            self.picker2, Qt.SIGNAL('appended(const QPoint &)'), self.pointSelected)
        self.connect(
            self.picker2, Qt.SIGNAL('moved(const QPoint &)'), self.pointSelected)


        self._filename = QtCore.QString()
        self._cache = {}

        self.setMarker(0,0)

        self.setAcceptDrops(1)


    def test (self, x, y):
        print x,y

    def moveRect(self, p):
        x = p.x()
        if self.beginning is None:
            self.beginning = x
            self.end = x
        else:
            self.end = x
    
    def endRect(self, p):
        if None in (self.beginning, self.end):
            return
        xb = self.plot.xBottom
        it = self.plot.invTransform
        beg = min(max(it(xb, min(self.end, self.beginning)), 0), self.chunks)
        end = min(max(it(xb, max(self.end, self.beginning)), 0), self.chunks)
        self.beginning, self.end = None, None
        self.setMarker(beg, end)
        beg, end = int(beg * self.chunksize), int(end * self.chunksize)
        self.emit(Qt.SIGNAL("rangeSelected"), (beg, end))

    def pointSelected(self, p):
        p = int(min(max(self.plot.invTransform(self.plot.xBottom, p.x()), 0), self.chunks) * self.chunksize)
        self.emit(Qt.SIGNAL("pointSelected(int)"), p)
    
    def setMarker(self, beg, end):
        self.markerL.setXValue(beg)
        self.markerR.setXValue(end)
        self.plot.replot()

    @QtCore.pyqtSignature("int, int")
    def setMarkerSample(self, beg=None, end=None):
        if beg:
            beg = beg / self.chunksize
            self.markerL.setXValue(beg)
        if end:
            end = end / self.chunksize
            self.markerR.setXValue(end)
        self.plot.replot()

    def getFilename(self):
        return self._filename

    @QtCore.pyqtSignature("const QString &")
    def setFilename(self, filename):
        self._filename = QtCore.QString(filename)
        a = self._cache.get(self._filename, None)
        if a is not None:
            self._soundindexarray = numpy.arange(0, self.chunks, 1)
            self.curve.setData(self._soundindexarray, a)
        try:
            a = audiolab.Sndfile(str(filename), 'read')
        except IOError, e:
            print "Couldn't load soundfile %s:" % filename, e
            return
        chunks = int(min(a.nframes, self.chunks))
        if chunks is 0:
            print "Zero-length file. Aborting..."
            return
        self.chunksize = int(a.nframes / chunks)
        self._soundarray = numpy.zeros(chunks)
        self._soundindexarray = numpy.arange(0, chunks, 1)
        self.dt = LoadingThread(a, self._soundindexarray, self._soundarray, self)
        self._replotTimer = self.startTimer(100)
        self.dt.start()
        #max_data = [numpy.maximum.reduce(d, 1) for d in data]
        #min_data = [tmp for tmp in [a.read_frames(self.chunksize) for i in range(chunks)]]

    filename = QtCore.pyqtProperty("const QString &", getFilename, setFilename)

    def timerEvent(self, ev):
        self.curve.setData(self._soundindexarray, self._soundarray)
        self.plot.replot()
        if self.dt.isFinished():
            self.killTimer(self._replotTimer)
            self._cache[self._filename] = self._soundarray

    def dragEnterEvent(self, ev):
        if ev.mimeData().hasFormat("text/plain") or \
                ev.mimeData().hasFormat(
                        "application/x-qabstractitemmodeldatalist") or ev.mimeData(
                                ).hasUrls():
            ev.acceptProposedAction()
    
    def dropEvent(self, ev):
        if ev.mimeData().hasFormat(
                "application/x-qabstractitemmodeldatalist"):
            if self._numberOfParams > 1:
                widslot = QtGui.QInputDialog.getInteger(self, "Which slot?", QtCore.QString("Choose widget slot"), 0,
                        0, self._numberOfParams - 1)
            self.setParamPath(str(ev.source().currentItem().text()))
            ev.acceptProposedAction()
            return
        elif ev.mimeData().hasUrls():
            text = ev.mimeData().urls()[0].toLocalFile()
        else:
            text = ev.mimeData().text()
        self.setFilename(text)
        ev.acceptProposedAction()

def main(args):
    app = Qt.QApplication(args)
    win = QtGui.QMainWindow(None)
    demo = SoundFileViewer(win)
    k = QtGui.QLineEdit(win)
    k.connect(k, Qt.SIGNAL("textChanged(const QString &)"), demo.setFilename)
    win.show()
    demo.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)
