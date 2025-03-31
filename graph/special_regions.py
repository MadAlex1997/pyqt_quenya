from pyqtgraph import LinearRegionItem, ROI
from PyQt6.QtCore import QPointF, pyqtSignal, Qt

class TimeRegion(LinearRegionItem):
    """A linear region item with a unique ID and click signal."""

    clicked = pyqtSignal(int)

    def __init__(self, values, trid):
        """
        Initializes the TimeRegion.

        Args:
            values: Initial region boundaries.
            trid (int): Unique ID for the region.
        """
        super().__init__(values)
        self.trid = trid
        
    def mouseDoubleClickEvent(self, event):
        """
        Handles double-click events and emits the clicked signal.

        Args:
            event: The mouse event.
        """
        super().mouseDoubleClickEvent(event)
        self.clicked.emit(self.trid)

class BoundROI(ROI):
    """A rectangular ROI bound to a TimeRegion."""

    roi_changed = pyqtSignal()
    clicked = pyqtSignal(int)

    def __init__(self, top, bottom, region: TimeRegion, roi_id):
        """
        Initializes the BoundROI.

        Args:
            top (float): Top boundary of the ROI.
            bottom (float): Bottom boundary of the ROI.
            region (TimeRegion): Associated TimeRegion.
            roi_id (int): Unique ID for the ROI.
        """
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
    
    def mouseClickEvent(self, event):
        """
        Handles mouse click events and emits the clicked signal.

        Args:
            event: The mouse event.
        """
        super().mouseClickEvent(event)
        print("roi double click")
        self.clicked.emit(self.roi_id)

    def reshape(self):
        """
        Reshapes the ROI based on the associated TimeRegion.
        """
        self.left, self.right = self.region.getRegion()

        pos = [self.left,self.bottom]
        size = [self.right-self.left, self.top-self.bottom]
        
        self.edditable = True
        self.setPos(pos)
        self.setSize(size)
        self.edditable = False
    
    def setPos(self, pos, y=None, update=True, finish=True):
        """
        Sets the position of the ROI.

        Args:
            pos: New position.
            y: Optional y-coordinate.
            update (bool): Whether to update immediately.
            finish (bool): Whether to finalize the position.
        """
        if not self.edditable:
            pos = QPointF(self.pos()[0], pos.y())
            super().setPos(pos)
            
        else:
            super().setPos(pos, y, update, finish)
        self.roi_changed.emit()

    def setSize(self, size, center=None, centerLocal=None, snap=False, update=True, finish=True):
        """
        Sets the size of the ROI.

        Args:
            size: New size.
            center: Optional center point.
            centerLocal: Optional local center point.
            snap (bool): Whether to snap to grid.
            update (bool): Whether to update immediately.
            finish (bool): Whether to finalize the size.
        """
        super().setSize(size, center, centerLocal, snap, update, finish)
        self.bottom = self.pos()[1]
        self.top = self.bottom + size[1]
        self.roi_changed.emit()

