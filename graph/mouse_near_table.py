from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt6.QtGui import QColor, QPixmap, QIcon

class NearTable(QTableWidget):
    
    def __init__(self, parent=None):
        super().__init__(0, 3, parent)  # Start with 0 rows
        self.setColumnCount(3)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setHorizontalHeaderLabels(["Trace","Time","Diff"])
        self.row_count = 0
    
    def new_row(self,color,name,x,y):
        self.insertRow(self.row_count+0)
        
        self.setItem(self.row_count,0,QTableWidgetItem(self.create_color_icon(QColor(color)),name))
        self.setItem(self.row_count,1,QTableWidgetItem(str(x)))
        self.setItem(self.row_count,2,QTableWidgetItem(str(y)))


        self.row_count += 1

    def create_color_icon(self, color: str) -> QIcon:
        """Creates a 20x20 square icon filled with the specified color."""
        pixmap = QPixmap(20, 20)
        pixmap.fill(color)
        return QIcon(pixmap)
    
    def reset_table(self):
        self.clearContents()
        self.setRowCount(0)
        self.row_count = 0