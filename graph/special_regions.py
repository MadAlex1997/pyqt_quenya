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
    roi_changed = pyqtSignal()
    clicked = pyqtSignal(int)
    def __init__(self, top, bottom, region:TimeRegion, roi_id):
        self.roi_id = roi_id
        self.region = region
        if bottom>top:
            top, bottom = bottom, top
        self.top = top
        self.bottom = bottom
        self.left, self.right = region.getRegion()

        pos = [self.left,self.bottom]
        size = [self.right-self.left, self.top-self.bottom]
        print(pos, size)
        self.edditable = True
        super().__init__(pos, size)
        self.edditable = False
        self.region.sigRegionChanged.connect(self.reshape)
        self.addScaleHandle((.5,0),(.5,.5))
        self.addScaleHandle((.5,1),(.5,.5))
    
    # def mouse
    def mouseClickEvent(self, event):
        super().mouseClickEvent(event)
        print("roi double click")
        self.clicked.emit(self.roi_id)

    def reshape(self):
        self.left, self.right = self.region.getRegion()

        pos = [self.left,self.bottom]
        size = [self.right-self.left, self.top-self.bottom]
        # print(pos, size)
        
        self.edditable = True
        self.setPos(pos)
        self.setSize(size)
        self.edditable = False
        # self.roi_changed.emit()
    
    def setPos(self, pos, y=None, update=True, finish=True):
        if not self.edditable:
            pos = QPointF(self.pos()[0], pos.y())
            # self.top=
            super().setPos(pos)
            
        else:
            super().setPos(pos, y, update, finish)
        self.roi_changed.emit()
        # else:
              # Keep x fixed, allow y to change
        #     print(pos)
        #     )
    def setSize(self, size, center=None, centerLocal=None, snap=False, update=True, finish=True):
        super().setSize(size, center, centerLocal, snap, update, finish)
        self.bottom = self.pos()[1]
        self.top = self.bottom + size[1]
        self.roi_changed.emit()
    
    