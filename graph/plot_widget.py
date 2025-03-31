from pyqtgraph import PlotWidget, PlotDataItem, DateAxisItem, ViewBox, LinearRegionItem, ROI
from PyQt6.QtGui import QAction, QCursor, QKeySequence
from PyQt6.QtCore import QPointF, pyqtSignal, Qt
import numpy as np
from datetime import datetime,timezone, timedelta

from PyQt6.QtWidgets import QMainWindow, QApplication
from .color import colors
from .trace_table import ButtonTable
from .mouse_near_table import NearTable
from .special_regions import TimeRegion, BoundROI
from .linked_table import TimeTable

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
    # trace_added = pyqtSignal(str,str)
    time_region_added = pyqtSignal(str, str, int)
    time_region_changed = pyqtSignal(str, str, int)
    def __init__(self, trace_table:ButtonTable, near_table: NearTable, time_selections:TimeTable):
        super().__init__()
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.trace_table = trace_table
        self.near_table = near_table
        self.time_selections  = time_selections
        self.setAxisItems({"bottom":DateAxisItem(utcOffset=0)})
        self.time_selections.itemSelectionChanged.connect(self.reset_v_select)
        self.init_variables()
        self.init_actions()
    
    def reset_v_select(self):
        self.initial = None
        
    def init_variables(self):
        self.traces = dict()
        self.time_start = None
        self.initial = None
        self.time_regions = dict()
        self.time_region_next_id = 0

    def init_actions(self):
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

        
    def demo(self):
        for i in range(48):
            self.plot_data(i)  
    
    def plot_data(self,i):
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
        for key in self.traces.keys():
            trace:PlotDataItem = self.traces[key]["trace"]
            trace.setSymbolBrush("white")
            trace.setOpacity(.5)
    
    def color_mode(self):
        for key in self.traces.keys():
            trace:PlotDataItem = self.traces[key]["trace"]
            trace.setSymbolBrush(colors[self.traces[key]["i"]])
            trace.setOpacity(1)

    def hide_trace(self,trace:PlotDataItem):
        trace.setVisible(not trace.isVisible())

    def get_coords(self):
        """Handles mouse movement and prints coordinates in graph space."""
        
        pos = QPointF(self.mapFromGlobal(QCursor().pos()))
        if self.sceneBoundingRect().contains(pos):
            mouse_point = self.getViewBox().mapSceneToView(pos)
            return mouse_point
    
    def near_mouse_table(self):
        """Handles mouse movement and prints coordinates in graph space."""
        
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

                self.time_regions[trid] = lr
                self.time_region_next_id += 1
                self.time_start = None
    
    def change_time_region(self, linear_region:LinearRegionItem):
        key = None
        for k in self.time_regions.keys():
            if linear_region is self.time_regions[k]:
                key = k
        
        if key is None:
            return
        
        start,stop = linear_region.getRegion()

        start_string = datetime.fromtimestamp(round(start,3)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
        stop_string = datetime.fromtimestamp(round(stop,3)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
                
        self.time_region_changed.emit(start_string, stop_string, key)

    def remove_time_selection(self, trid):
        region  = self.time_regions.pop(trid)
        self.removeItem(region)
    
    def add_roi(self):
        trid = self.time_selections.id_from_selection()
        if trid is not None:
            region = self.time_regions[trid]
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
            v_select = BoundROI(high, low, region)
            self.addItem(v_select)
            self.initial=None



        


