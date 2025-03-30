from graph.graph_page import GraphWindow
from PyQt6.QtWidgets import QMainWindow, QApplication


app = QApplication([])
window = GraphWindow()
window.show()
app.exec()