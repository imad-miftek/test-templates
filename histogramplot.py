import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen
from plotpy.plot import BasePlot
from plotpy.styles import HistogramParam, CurveParam
from plotpy.items import HistogramItem, ImageItem
import numpy as np
from plotpy.config import _

class HistDataSource(ImageItem):
    """Simple data source for histogram"""
    def __init__(self, data):
        super().__init__()
        self.data = data
        
    def get_histogram(self, n_bins, bin_range=None):
        """Return histogram data"""
        if bin_range is None:
            bin_range = (self.data.min(), self.data.max())
        return np.histogram(self.data, n_bins, range=bin_range)

class HistogramPlot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Histogram Plot")
        self.setGeometry(100, 100, 800, 600)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create plot widget
        self.plot = BasePlot()
        
        # Create curve parameters
        curve_param = CurveParam(_("Histogram"))
        curve_param.curvestyle = "Steps"  # Important for histogram display
        
        # Create histogram parameters
        hist_param = HistogramParam(_("Histogram"))
        
        # Create histogram item
        self.hist_item = HistogramItem(curveparam=curve_param, histparam=hist_param)
        
        # Generate sample data
        data = np.random.normal(size=1000)
        
        # Set histogram properties
        self.hist_item.set_hist_data(data)  # Set the data
        self.hist_item.set_bins(100)  # Set number of bins
        self.hist_item.set_logscale(False)  # Use linear scale
        
        # Add histogram to plot
        self.plot.add_item(self.hist_item)
        
        # Add plot to layout
        layout.addWidget(self.plot)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HistogramPlot()
    window.show()
    sys.exit(app.exec())