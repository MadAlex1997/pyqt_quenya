import pyqtgraph
from PyQt6.QtWidgets import QMainWindow, QApplication,QDockWidget, QTextEdit
from PyQt6.QtGui import QAction, QCursor, QKeySequence
from  PyQt6.QtCore import Qt
import numpy as np
from datetime import datetime,timezone, timedelta
from uuid import uuid4

from .plot_widget import ScatterPlot
from .trace_table import ButtonTable
from .mouse_near_table import NearTable
from .linked_table import TimeTable


class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        menu = self.menuBar()
        mode_menu = menu.addMenu("Mode")
        contrast = mode_menu.addAction("Contrast Mode")
        color = mode_menu.addAction("Color Mode")

        selections_menu = menu.addMenu("Selections")
        delete_selected_times = selections_menu.addAction("Delete Selected Times")
        delete_selected_times.setShortcut(QKeySequence("Shift+Del"))

        self.trace_table = ButtonTable(12)
        self.near_table = NearTable()
        self.time_selections = TimeTable()
        self.plot = ScatterPlot(self.trace_table,
                                self.near_table,
                                self.time_selections)
        

        color.triggered.connect(self.plot.color_mode)
        contrast.triggered.connect(self.plot.contrast_mode)

        delete_selected_times.triggered.connect(self.time_selections.delete_row)

        self.plot.time_region_added.connect(self.time_selections.insert_time_selection)
        self.plot.time_region_changed.connect(self.time_selections.update_table)
        self.time_selections.time_selection_deleted.connect(self.plot.remove_time_selection)
        # self.plot.trace_added.connect(self.trace_table.add_button)
        self.plot.demo()
        self.init_docks()
        

    def init_docks(self):
        self.setCentralWidget(self.plot)
        
        dock = QDockWidget("Dockable Widget", self)
        dock.setWidget(self.near_table)

        traces_doc = QDockWidget("Dockable Widget", self)
        traces_doc.setWidget(self.trace_table)
        
        time_selections_dock = QDockWidget("Time Selections", self)
        time_selections_dock.setWidget(self.time_selections)

        selection_info_dock = QDockWidget("Selection Info", self)
        selection_info_dock.setWidget(QTextEdit("Selection Info Here"))
        # Add dock widgets to the main window
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, time_selections_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, selection_info_dock)
        
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, traces_doc)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)