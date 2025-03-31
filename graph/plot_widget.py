from pyqtgraph import PlotWidget, PlotDataItem, DateAxisItem, ViewBox, LinearRegionItem, ROI
from PyQt6.QtGui import QAction, QCursor, QKeySequence
from PyQt6.QtCore import QPointF, pyqtSignal, Qt
import numpy as np
from datetime import datetime, timezone, timedelta

from PyQt6.QtWidgets import QMainWindow, QApplication
from .color import colors
from .trace_table import ButtonTable
from .mouse_near_table import NearTable
from .special_regions import TimeRegion, BoundROI
from .linked_table import TimeTable, ROITable

def gen_data():
    stop = datetime.now().astimezone(timezone.utc)
    start = stop - timedelta(hours=1)
    stop = stop.timestamp()
    start = start.timestamp()

    t = start
    data = []
    while t<stop:
    
        t = t+abs(float(np.random.normal(100,1000,1)))
        data.append(t)
    return data

class ScatterPlot(PlotWidget):
    """A custom scatter plot widget with interactive features."""

    time_region_added = pyqtSignal(str, str, int)
    time_region_changed = pyqtSignal(str, str, int)

    def __init__(self, 
                 trace_table:ButtonTable, 
                 near_table:NearTable, 
                 time_selections:TimeTable,
                 roi_table:ROITable):
        """
        Initializes the ScatterPlot.

        Args:
            trace_table (ButtonTable): Table for managing traces.
            near_table (NearTable): Table for displaying nearby points.
            time_selections (TimeTable): Table for time selections.
            roi_table (ROITable): Table for ROI selections.
        """
        super().__init__()
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.trace_table = trace_table
        self.near_table = near_table
        self.time_selections  = time_selections
        self.roi_table = roi_table
        self.setAxisItems({"bottom":DateAxisItem(utcOffset=0)})
        self.time_selections.itemSelectionChanged.connect(self.reset_v_select)
        self.init_variables()
        self.init_actions()
    
    def reset_v_select(self):
        """Resets the vertical selection state."""
        self.initial = None
        
    def init_variables(self):
        """Initializes internal variables."""
        self.traces = dict()
        self.time_start = None
        self.initial = None
        self.time_regions = dict()
        self.time_region_next_id = 0

    def init_actions(self):
        """Initializes actions and shortcuts."""
        get_coords = QAction("mouse coords",self)
        get_coords.setShortcut(QKeySequence("Shift+Z"))
        get_coords.triggered.connect(self.near_mouse_table)
        self.addAction(get_coords)

        time_region = QAction("make time selection",self)
        time_region.setShortcut(QKeySequence("Shift+C"))
        time_region.triggered.connect(self.add_time_selection)
        self.addAction(time_region)

        v_region = QAction("make v selection",self)
        v_region.setShortcut(QKeySequence("Shift+X"))
        v_region.triggered.connect(self.add_roi)
        self.addAction(v_region)

        auto_range = QAction("Auto Range",self)
        auto_range.setShortcut(QKeySequence("Shift+A"))
        auto_range.triggered.connect(self.autoRange)
        self.addAction(auto_range)
    def demo(self):
        """Generates demo data for the plot."""
        for i in range(48):
            self.plot_data(i)  
    
    def plot_data(self,i):
        """
        Plots data for a given trace index.

        Args:
            i (int): Trace index.
        """
        x = np.array(gen_data())
        y = np.diff(x)
        x=x[1:]
        name = str(i).zfill(4)
        # self.trace_added.emit(colors[i],name)
        
        data = PlotDataItem(x=x,y=y,pen=None,symbol='o',symbolBrush=colors[i])
        self.traces[name] = {"trace":data,"x":x,"y":y,"i":i}
        self.trace_table.add_button(colors[i],name,lambda: self.hide_trace(self.traces[name]["trace"]))
        self.addItem(data)

    def contrast_mode(self):
        """Switches to contrast mode for traces."""
        for key in self.traces.keys():
            trace:PlotDataItem = self.traces[key]["trace"]
            trace.setSymbolBrush("white")
            trace.setOpacity(.5)
    
    def color_mode(self):
        """Switches to color mode for traces."""
        for key in self.traces.keys():
            trace:PlotDataItem = self.traces[key]["trace"]
            trace.setSymbolBrush(colors[self.traces[key]["i"]])
            trace.setOpacity(1)

    def hide_trace(self,trace:PlotDataItem):
        """
        Toggles the visibility of a trace.

        Args:
            trace (PlotDataItem): The trace to toggle.
        """
        trace.setVisible(not trace.isVisible())

    def get_coords(self):
        """
        Gets the current mouse coordinates in graph space.

        Returns:
            QPointF: The mouse coordinates.
        """
        pos = QPointF(self.mapFromGlobal(QCursor().pos()))
        if self.sceneBoundingRect().contains(pos):
            mouse_point = self.getViewBox().mapSceneToView(pos)
            return mouse_point
    
    def near_mouse_table(self):
        """Populates the near table with points close to the mouse cursor."""
        vb: ViewBox = self.getViewBox()
        view_range = vb.getState()["viewRange"]
        xrange, yrange = view_range
        xwidth = xrange[1] - xrange[0]
        ywidth = yrange[1] - yrange[0]

        self.near_table.reset_table()
        mouse_point = self.get_coords()
        if mouse_point:
            for key in self.traces.keys():
                if self.traces[key]["trace"].isVisible():

                    color = colors[self.traces[key]["i"]]
                    name = str(self.traces[key]["i"]).zfill(4)

                    x = mouse_point.x()
                    y = mouse_point.y()

                    xvals = np.array(self.traces[key]["x"])
                    xmask = (np.abs(x-xvals)<xwidth/10)&(np.abs(x+xvals)>xwidth/10)

                    yvals = np.array(self.traces[key]["y"])
                    ymask = (np.abs(y-yvals)<ywidth/10)&(np.abs(y+yvals)>ywidth/10)

                    
                    mask = xmask & ymask
                
                    x_n_range = xvals[mask].tolist()
                    y_n_range = yvals[mask].tolist()

                    for i in range(len(x_n_range)):
                        self.near_table.new_row(color,name,x_n_range[i],y_n_range[i])
    
    def add_time_selection(self):
        """Adds a time selection region."""
        if self.time_start is None:
            coords = self.get_coords()
            if coords:
                self.time_start = coords.x()
        else:
            coords = self.get_coords()
            if coords:
                start = self.time_start
                stop = coords.x()
                if start > stop:
                    start, stop = stop, start
                start_string = datetime.fromtimestamp(round(start,3)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
                stop_string = datetime.fromtimestamp(round(stop,3)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
                trid = self.time_region_next_id + 0
                
                lr = TimeRegion((start, stop),trid)
                lr.sigRegionChanged.connect(self.change_time_region)
                

                self.time_region_added.emit(start_string,stop_string,trid)
                lr.clicked.connect(lambda: self.time_selections.select_row_from_time_id(trid))
                self.addItem(lr)

                self.time_regions[trid] = {"tr": lr,"vl":dict(),"vc":0}
                self.time_region_next_id += 1
                self.time_start = None
    
    def change_time_region(self, linear_region:LinearRegionItem):
        """
        Handles changes to a time region.

        Args:
            linear_region (LinearRegionItem): The changed region.
        """
        key = None
        for k in self.time_regions.keys():
            if linear_region is self.time_regions[k]["tr"]:
                key = k
        
        if key is None:
            return
        
        start,stop = linear_region.getRegion()

        start_string = datetime.fromtimestamp(round(start,3)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
        stop_string = datetime.fromtimestamp(round(stop,3)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
                
        self.time_region_changed.emit(start_string, stop_string, key)

    def remove_time_selection(self, trid):
        """
        Removes a time selection region.

        Args:
            trid (int): The ID of the time region to remove.
        """
        item  = self.time_regions.pop(trid)
        region = item["tr"]
        self.removeItem(region)
        for roi in item["vl"].values():
            self.removeItem(roi)
        self.roi_table.clearContents()
        self.roi_table.setRowCount(0)
    
    def add_roi(self):
        """Adds a vertical ROI within a time region."""
        trid = self.time_selections.id_from_selection()
        if trid is not None:
            region = self.time_regions[trid]["tr"]
        else:
            return

        coords = self.get_coords()
        x,y = coords.x(), coords.y()
        left, right = region.getRegion()
        
        if left <= x <= right:
            pass
        else:
            return
        
        if self.initial is None:
            self.initial = y
        else:
            low, high  = self.initial, y
            if low>high:
                low, high = high, low
            count = self.time_regions[trid]["vc"]
            v_select = BoundROI(high, low, region, count)
            v_select.roi_changed.connect(self.show_roi)
            
            self.addItem(v_select)
            
            
            self.time_regions[trid]["vl"][count] = v_select
            self.time_regions[trid]["vc"]+=1
            self.initial=None
            v_select.clicked.connect(lambda: self.roi_table.select_row_from_roi_id(count))
            v_select.clicked.connect(lambda: self.time_selections.select_row_from_time_id(trid))

            v_select.roi_changed.emit()
    
    def remove_roi(self, trid,roi_id):
        """
        Removes a vertical ROI.

        Args:
            trid (int): The ID of the associated time region.
            roi_id (int): The ID of the ROI to remove.
        """
        roi  = self.time_regions[trid]["vl"].pop(roi_id)
        self.removeItem(roi)

    def show_roi(self):
        """Displays ROIs for the selected time region."""
        trid = self.time_selections.id_from_selection()
        if trid is None:
            return
        vert_dict = self.time_regions[trid]["vl"]
        self.roi_table.clearContents()
        self.roi_table.setRowCount(0)
        if vert_dict:
            for k in vert_dict.keys():
                roi: BoundROI = vert_dict[k]
                y = roi.pos()[1]
                dy = roi.size()[1]
                y2 = y+dy
                self.roi_table.insert_roi(round(y,3),round(y2,3), trid, k)
    
    def setview(self, top, bottom, left, right):
        """
        Sets the view range of the plot.

        Args:
            top (float): Top boundary.
            bottom (float): Bottom boundary.
            left (float): Left boundary.
            right (float): Right boundary.
        """
        view_box = self.getViewBox()
        view_box.setRange(xRange=(left, right), yRange=(bottom, top))






