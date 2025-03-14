import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen
from plotpy.plot import BasePlot
from plotpy.styles import HistogramParam, CurveParam
from plotpy.items import HistogramItem, ImageItem
import numpy as np
from plotpy.config import _


class HistogramPlot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multiple Histograms")
        self.setGeometry(100, 100, 1200, 800)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create plot widget
        self.plot = BasePlot()
        
        # Create different distributions
        distributions = {
            "Normal": np.random.normal(0, 1, 1000),
            "Uniform": np.random.uniform(-3, 3, 1000),
            "Exponential": np.random.exponential(1, 1000),
            "Gamma": np.random.gamma(2, 2, 1000),
            "Laplace": np.random.laplace(0, 1, 1000)
        }

        # Colors for different histograms with alpha (transparency)
        colors = {
            'blue': (0, 0, 255, 50),      # RGB + alpha
            'red': (255, 0, 0, 50),
            'green': (0, 255, 0, 50),
            'purple': (128, 0, 128, 50),
            'orange': (255, 165, 0, 50)
        }

        # Create and add histogram items
        for (name, data), (color_name, rgba) in zip(distributions.items(), colors.items()):
            # Create curve parameters
            curve_param = CurveParam(_(f"{name} Distribution"))
            curve_param.curvestyle = "Steps"
            curve_param.line.color = color_name
            
            curve_param.shade = 0.25  # Fill transparency
            
            # Create histogram parameters
            hist_param = HistogramParam(_(f"{name} Histogram"))
            
            # Create histogram item
            hist_item = HistogramItem(curveparam=curve_param, histparam=hist_param)
            
            # Set histogram properties
            hist_item.set_hist_data(data)
            hist_item.set_bins(50)
            hist_item.set_logscale(False)
            
            # Add histogram to plot
            self.plot.add_item(hist_item)

        # Add plot to layout
        layout.addWidget(self.plot)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HistogramPlot()
    window.show()
    sys.exit(app.exec())