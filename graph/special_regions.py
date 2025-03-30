from pyqtgraph import LinearRegionItem, ROI
from PyQt6.QtCore import QPointF, pyqtSignal, Qt
class TimeRegion(LinearRegionItem):
    clicked = pyqtSignal(int)
    def __init__(self, values, trid):
        super().__init__(values)
        self.trid = trid
        
    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        self.clicked.emit(self.trid)



class BoundROI(ROI):
    def __init__(self, pos, size, angle=0, invertible=False, maxBounds=None, snapSize=1, scaleSnap=False, translateSnap=False, rotateSnap=False, parent=None, pen=None, hoverPen=None, handlePen=None, handleHoverPen=None, movable=True, rotatable=True, resizable=True, removable=False, aspectLocked=False, antialias=True):
        super().__init__(pos, size, angle, invertible, maxBounds, snapSize, scaleSnap, translateSnap, rotateSnap, parent, pen, hoverPen, handlePen, handleHoverPen, movable, rotatable, resizable, removable, aspectLocked, antialias)