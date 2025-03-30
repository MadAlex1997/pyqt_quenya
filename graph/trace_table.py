import pyqtgraph
from PyQt6.QtWidgets import QTableWidget, QAbstractItemView, QHeaderView, QPushButton
from PyQt6.QtGui import QColor, QPixmap, QIcon
from  PyQt6.QtCore import QSize

class ButtonTable(QTableWidget):
    def __init__(self, columns: int, parent=None):
        super().__init__(0, columns, parent)  # Start with 0 rows
        self.setColumnCount(columns)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # self.setFixedWidth(columns * (84+4))  # Fixed width, dynamic height
        self.setIconSize(QSize(20, 20))

    def add_button(self, color: str, text: str, vis):
        """Adds a button with a colored square icon and text to the table.
        Adds the button to the next available cell, creating a new row if needed.
        """
        current_row_count = self.rowCount()
        current_col_count = self.columnCount()

        # Find the next empty cell
        for row in range(current_row_count):
            for col in range(current_col_count):
                if self.cellWidget(row, col) is None:
                    self._place_button(row, col, color, text, vis)
                    return

        # If no empty cell was found, create a new row
        self.insertRow(current_row_count)
        self._place_button(current_row_count, 0, color, text,vis)

    def _place_button(self, row: int, col: int, color: str, text: str, vis):
        """Places a button in the specified row and column."""
        button = QPushButton(text)
        button.setIcon(self.create_color_icon(QColor(color)))
        button.setIconSize(QSize(20, 20))
        button.setCheckable(True)
        button.clicked.connect(vis)
        
        self.setCellWidget(row, col, button)
        

    def create_color_icon(self, color: str) -> QIcon:
        """Creates a 20x20 square icon filled with the specified color."""
        pixmap = QPixmap(20, 20)
        pixmap.fill(color)
        return QIcon(pixmap)

    # def on_button_click(self, row: int, col: int):
    #     print(f"Button clicked at Row: {row}, Column: {col}")