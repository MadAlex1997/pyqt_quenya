from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt6.QtGui import QColor, QPixmap, QIcon
from PyQt6.QtCore import QPointF, pyqtSignal, Qt

class TimeTable(QTableWidget):
    time_selection_deleted = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(0, 2, parent)  # Start with 0 rows
        self.setColumnCount(2)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setHorizontalHeaderLabels(["Start","Stop"])

        self.init_variables()


    def init_variables(self):
        self.row_info = dict()
        
    def insert_time_selection(self,start,stop,time_id):
        # print("Insert")
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
        
    
    def update_table(self,start,stop, time_id):
        # self.indexFromItem(self.row_info[time_id]["start"])
        # self.set
        self.row_info[time_id]["start"].setText(start[:-3])
        self.row_info[time_id]["stop"].setText(stop[:-3])

    def delete_row(self):
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
        idx = self.indexFromItem(self.row_info[time_id]["start"])
        
        self.selectRow(idx.row())
    
    

class ROITable(QTableWidget):
    roi_deleted = pyqtSignal(int, int)
    def __init__(self, parent=None):
        super().__init__(0, 2, parent)  # Start with 0 rows
        self.setColumnCount(2)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setHorizontalHeaderLabels(["Start","Stop"])

        self.init_variables()

    def init_variables(self):
        self.row_info = dict()
    
    def insert_roi(self, low, high, time_id, roi_id):
        # print("Insert")
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
        # self.indexFromItem(self.row_info[time_id]["start"])
        # self.set
        self.row_info[roi_id]["low"].setText(str(low))
        self.row_info[roi_id]["high"].setText(str(high))
    
    def select_row_from_roi_id(self, roi_id):
        if roi_id in self.row_info.keys(): 
            idx = self.indexFromItem(self.row_info[roi_id]["low"])
            self.selectRow(idx.row())

    