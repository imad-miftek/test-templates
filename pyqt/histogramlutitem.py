import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

class HistogramLUTDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HistogramLUTItem Demo")
        self.resize(800, 500)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Create PlotWidget for the image
        image_view = pg.PlotWidget()
        layout.addWidget(image_view, stretch=3)
        
        # Create random test image
        self.img_data = np.random.normal(size=(500, 500))
        self.img_data[200:300, 200:300] += 2  # Add bright square in center
        self.img_data = np.clip(self.img_data, 0, 10)
        
        # Create and configure the ImageItem
        self.img_item = pg.ImageItem(self.img_data)
        image_view.addItem(self.img_item)
        image_view.setAspectLocked(True)
        
        # Create a GraphicsView for the histogram
        hist_view = pg.GraphicsView()
        layout.addWidget(hist_view, stretch=1)
        
        # Create the HistogramLUTItem and add it to the GraphicsView
        self.hist_lut = pg.HistogramLUTItem()
        hist_view.setCentralItem(self.hist_lut)
        
        # Link the histogram to the image
        self.hist_lut.setImageItem(self.img_item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HistogramLUTDemo()
    window.show()
    sys.exit(app.exec())
