import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log-Spaced Ticks")
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create PlotWidget with custom y-axis
        self.plot = pg.PlotWidget(background='w')
        
        # Get the view box and set it to log mode
        view = self.plot.getPlotItem().getViewBox()
        view.setLimits(xMin=0, xMax=10, yMin=1, yMax=10**8)
        view.setRange(xRange=[0, 10], yRange=[10**0, 10**8])
        
        # Add plot to layout
        layout.addWidget(self.plot)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()