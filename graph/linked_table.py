from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt6.QtGui import QColor, QPixmap, QIcon
from PyQt6.QtCore import QPointF, pyqtSignal, Qt

class TimeTable(QTableWidget):
    """A table widget for managing time selections."""

    time_selection_deleted = pyqtSignal(int)

    def __init__(self, parent=None):
        """
        Initializes the TimeTable.

        Args:
            parent: Parent widget (optional).
        """
        super().__init__(0, 2, parent)  # Start with 0 rows
        self.setColumnCount(2)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setHorizontalHeaderLabels(["Start","Stop"])

        self.init_variables()

    def init_variables(self):
        """Initializes internal variables."""
        self.row_info = dict()
        
    def insert_time_selection(self, start, stop, time_id):
        """
        Inserts a new time selection into the table.

        Args:
            start (str): Start time of the selection.
            stop (str): Stop time of the selection.
            time_id (int): Unique ID for the time selection.
        """
        row = self.rowCount()
        self.insertRow(row)
        start_table_item = QTableWidgetItem(start[:-3])
        stop_table_item = QTableWidgetItem(stop[:-3])
        
        
        self.row_info[time_id] = {"start":start_table_item,
                                  "stop":stop_table_item}
        self.setItem(row, 0, self.row_info[time_id]["start"])
        self.setItem(row, 1, self.row_info[time_id]["stop"])
        
        
        
        idx = self.indexFromItem(self.row_info[time_id]["start"])
        print(self.itemFromIndex(idx) is self.row_info[time_id]["start"])
        print(idx)
        
    
    def update_table(self, start, stop, time_id):
        """
        Updates an existing time selection in the table.

        Args:
            start (str): Updated start time.
            stop (str): Updated stop time.
            time_id (int): Unique ID for the time selection.
        """
        self.row_info[time_id]["start"].setText(start[:-3])
        self.row_info[time_id]["stop"].setText(stop[:-3])

    def delete_row(self):
        """Deletes the selected row and emits a signal."""
        selected = self.selectedIndexes()
        if selected:
            selected = selected[0]
        else:
            return
        start = self.takeItem(selected.row(),0)
        self.removeRow(selected.row())
        self.clearSelection()

        key = None
        for k in self.row_info.keys():
            if self.row_info[k]["start"] is start:
                key = k
                print(key)
                break
        
        if key is not None:
            self.row_info.pop(key)
            self.time_selection_deleted.emit(key)

    def id_from_selection(self):
        """
        Gets the ID of the currently selected time selection.

        Returns:
            int: The ID of the selected time selection.
        """
        selected = self.selectedIndexes()
        if selected:
            selected = selected[0]
            start = self.itemFromIndex(selected)
            
            key = None
            for k in self.row_info.keys():
                if self.row_info[k]["start"] is start:
                    key = k
                    print(key)
                    break
            
            return key

    def select_row_from_time_id(self, time_id):
        """
        Selects a row based on the time selection ID.

        Args:
            time_id (int): The ID of the time selection.
        """
        idx = self.indexFromItem(self.row_info[time_id]["start"])
        
        self.selectRow(idx.row())
    
    

class ROITable(QTableWidget):
    """A table widget for managing ROIs."""

    roi_deleted = pyqtSignal(int, int)

    def __init__(self, parent=None):
        """
        Initializes the ROITable.

        Args:
            parent: Parent widget (optional).
        """
        super().__init__(0, 2, parent)  # Start with 0 rows
        self.setColumnCount(2)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setHorizontalHeaderLabels(["Start","Stop"])

        self.init_variables()

    def init_variables(self):
        """Initializes internal variables."""
        self.row_info = dict()
    
    def insert_roi(self, low, high, time_id, roi_id):
        """
        Inserts a new ROI into the table.

        Args:
            low (float): Lower boundary of the ROI.
            high (float): Upper boundary of the ROI.
            time_id (int): Associated time selection ID.
            roi_id (int): Unique ID for the ROI.
        """
        self.time_id = time_id
        row = self.rowCount()
        self.insertRow(row)
        low_table_item = QTableWidgetItem(str(low))
        high_table_item = QTableWidgetItem(str(high))
        
        
        self.row_info[roi_id] = {"low":low_table_item,
                                  "high":high_table_item}
        self.setItem(row, 0, self.row_info[roi_id]["low"])
        self.setItem(row, 1, self.row_info[roi_id]["high"])
    
    def delete_row(self):
        """Deletes the selected row and emits a signal."""
        selected = self.selectedIndexes()
        if selected:
            selected = selected[0]
        else:
            return
        low = self.takeItem(selected.row(),0)
        self.removeRow(selected.row())
        self.clearSelection()

        key = None
        for k in self.row_info.keys():
            if self.row_info[k]["low"] is low:
                key = k
                print(key)
                break
        
        if key is not None:
            self.row_info.pop(key)
            self.roi_deleted.emit(self.time_id, key)
    
    def update_table(self, low, high, roi_id):
        """
        Updates an existing ROI in the table.

        Args:
            low (float): Updated lower boundary.
            high (float): Updated upper boundary.
            roi_id (int): Unique ID for the ROI.
        """
        self.row_info[roi_id]["low"].setText(str(low))
        self.row_info[roi_id]["high"].setText(str(high))
    
    def select_row_from_roi_id(self, roi_id):
        """
        Selects a row based on the ROI ID.

        Args:
            roi_id (int): The ID of the ROI.
        """
        if roi_id in self.row_info.keys(): 
            idx = self.indexFromItem(self.row_info[roi_id]["low"])
            self.selectRow(idx.row())

