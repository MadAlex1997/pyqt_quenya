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
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setHorizontalHeaderLabels(["Start","Stop"])

        self.init_variables()


    def init_variables(self):
        self.row_info = dict()
        
    def insert_time_selection(self,start,stop,time_id):
        print("Insert")
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
        selected = self.selectedIndexes()[0]
        start = self.takeItem(selected.row(),0)
        self.removeRow(selected.row())

        key = None
        for k in self.row_info.keys():
            if self.row_info[k]["start"] is start:
                key = k
                print(key)
                break
        
        if key is not None:
            self.row_info.pop(key)
            self.time_selection_deleted.emit(key)



    def select_row_from_time_id(self, time_id):
        idx = self.indexFromItem(self.row_info[time_id]["start"])
        
        self.selectRow(idx.row())

    