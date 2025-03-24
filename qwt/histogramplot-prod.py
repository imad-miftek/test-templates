import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from plotpy.plot import BasePlot
from plotpy.items import HistogramItem
from plotpy.styles import HistogramParam
import numpy as np
from plotpy.config import _
from plotpy.builder import make
from log10 import Log10ScaleEngine
from qwt import QwtLogScaleEngine
import torch

class HistogramPlot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 800)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create plot widget
        self.plot = BasePlot()
        self.plot.setAxisScaleEngine(BasePlot.X_BOTTOM, Log10ScaleEngine())

        self.hist_param = HistogramParam()
        self.hist = HistogramItem()
        
        self.hist.set_bin_range((1, 10**8))
        self.hist.set_bins(512)
        data : torch.Tensor = torch.load('daq_data.pt')
        data = data.numpy()

        data_shifted = data - (-32768)
        
        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        
        # Log scale transformation
        # Maps 0->0, 65535->10^8
        data_log = np.log10(data_shifted + epsilon) / np.log10(65535)  # Normalize to 0-1
        data_scaled = data_log * 10**8  # Scale to target range
        
        # The Log10Transform will handle the scaling automatically
        self.hist.set_hist_data(data_scaled)
        self.plot.add_item(self.hist)

        # Add plot to layout
        layout.addWidget(self.plot)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HistogramPlot()
    window.show()
    sys.exit(app.exec())