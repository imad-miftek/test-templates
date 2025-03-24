from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget
import pyqtgraph as pg

class Plot(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Base Plot")
        self.setGeometry(100, 100, 800, 600)

        # Create PlotWidget
        self.plot = pg.PlotWidget()
        self.plot.showGrid(True, True)
        self.plot.setBackground('w')

        # Add plot to layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.plot)
        