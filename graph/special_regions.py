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
    def __init__(self, top, bottom, region:TimeRegion):
        self.region = region
        if bottom>top:
            top, bottom = bottom, top
        self.top = top
        self.bottom = bottom
        self.left, self.right = region.getRegion()

        pos = [self.left,self.bottom]
        size = [self.right-self.left, self.top-self.bottom]
        print(pos, size)
        super().__init__(pos, size)
        self.region.sigRegionChanged.connect(self.reshape)

    def reshape(self):
        self.left, self.right = self.region.getRegion()

        pos = [self.left,self.bottom]
        size = [self.right-self.left, self.top-self.bottom]
        # print(pos, size)
        self.setSize(size)
        self.setPos(pos)
        