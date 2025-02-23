import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from plotpy.plot import BasePlot
from plotpy.items import ImageItem
from plotpy.styles import ImageParam
import numpy as np

class RotatedAxisScaleDraw:
    """Custom scale draw that rotates tick labels"""
    def __init__(self, plot: BasePlot, axis_id):
        self.plot = plot
        self.axis_id = axis_id
        
    def set_angle(self, angle):
        """Set rotation angle for tick labels"""
        widget = self.plot.axisWidget(self.axis_id)
        font = widget.font()
        widget.setLabelRotation(angle)
        # widget.setTickFont(font)

class SpectralRibbonPlot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spectral Ribbon Plot")
        self.setGeometry(100, 100, 800, 600)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 10, 10, 40)

        # Create plot widget
        self.plot = BasePlot()
        
        # Create sample data
        self.num_channels = 50
        self.num_bins = 1024
        data = []
        for i in range(self.num_channels):
            hist = np.random.normal(loc=50, scale=10, size=self.num_bins)
            data.append(hist)
        data = np.rot90(np.array(data))

        # Create image parameters
        image_param = ImageParam()
        image_param.colormap = "turbo"  # Using turbo colormap like in spectralribbon.py
        
        # Create and setup image item
        self.image_item = ImageItem(data, image_param)
        self.image_item.set_interpolation(0)
        
        # Add image to plot
        self.plot.add_item(self.image_item)
        
        # Setup axes
        font = QFont("Times", 12)
        self.plot.set_axis_title("bottom", "Wavelength")
        self.plot.set_axis_title("left", "Intensity")
        
        # Set axis fonts and colors
        for axis_id in [self.plot.X_BOTTOM, self.plot.Y_LEFT]:
            self.plot.set_axis_font(axis_id, font)
            # self.
            self.plot.set_axis_color(axis_id, "black")

        # Create wavelength ticks with 45° rotation
        rotated_draw = RotatedAxisScaleDraw(self.plot, self.plot.X_BOTTOM)
        rotated_draw.set_angle(45)

        # Create wavelength scale (400nm to 700nm)
        start_wavelength = 400
        end_wavelength = 700
        wavelengths = np.linspace(start_wavelength, end_wavelength, self.num_channels)
        ticks = [(i, f"{int(w)}") for i, w in enumerate(wavelengths)]
        self.plot.set_axis_ticks(self.plot.X_BOTTOM, len(ticks))

        # Set plot appearance
        self.plot.set_antialiasing(True)
        self.plot.setCanvasBackground(Qt.GlobalColor.white)
        self.plot.setMouseTracking(True)
        
        # Add to layout
        layout.addWidget(self.plot)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SpectralRibbonPlot()
    window.show()
    sys.exit(app.exec())