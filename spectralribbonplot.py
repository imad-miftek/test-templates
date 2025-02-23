import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from plotpy.plot import BasePlot
from plotpy.items import ImageItem
from plotpy.styles import ImageParam
import numpy as np

class SpectralRibbonPlot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spectral Ribbon Plot")
        self.setGeometry(100, 100, 800, 600)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create plot widget
        self.plot = BasePlot()
        
        # Create sample data
        num_channels = 50
        num_bins = 50
        data = []
        for i in range(num_channels):
            hist = np.random.normal(loc=50, scale=10, size=num_bins)
            data.append(hist)
        data = np.rot90(np.array(data))

        # Create image parameters
        image_param = ImageParam()
        image_param.colormap = "rainbow"  # Using built-in colormap
        
        # Create and setup image item
        self.image_item = ImageItem(data, image_param)
        
        # Add image to plot
        self.plot.add_item(self.image_item)
        
        # Setup axes
        self.plot.set_axis_title("bottom", "Wavelength")
        self.plot.set_axis_title("left", "Intensity")
        
        # Set wavelength ticks
        wavelengths = [(i, f"λ{i}") for i in range(num_channels)]
        # self.plot.set_axis_ticks("bottom", wavelengths)
        
        # Add to layout
        layout.addWidget(self.plot)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SpectralRibbonPlot()
    window.show()
    sys.exit(app.exec())