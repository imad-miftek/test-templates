import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from plotpy.plot import BasePlot
from plotpy.items import ImageItem
from plotpy.styles import ImageParam
from qwt.scale_engine import QwtScaleEngine
import numpy as np
from qwt.scale_div import QwtScaleDiv
from qwt.scale_engine import QwtLinearScaleEngine
from PySide6.QtCore import Qt
from qwt.transform import QwtTransform

class Log10Transform(QwtTransform):
    def __init__(self):
        super().__init__()

    def copy(self):
        return Log10Transform()
    
    def invTransform(self, x):
        # Handle possible negative or zero inputs from UI interactions
        if isinstance(x, (int, float)):
            return 10**x
        else:  # numpy array
            return 10**np.asarray(x)
    
    def transform(self, x):
        # Handle possible zero or negative values
        if isinstance(x, (int, float)):
            return np.log10(max(1.0e-20, x))
        else:  # numpy array
            x_safe = np.asarray(x).copy()
            mask = x_safe <= 0
            x_safe[mask] = 1.0e-20
            return np.log10(x_safe)


class Log10ScaleEngine(QwtScaleEngine):
    def __init__(self):
        super().__init__()
        self.setAttribute(QwtScaleEngine.Floating, False)
        self.setAttribute(QwtScaleEngine.Symmetric, False)
        self.setAttribute(QwtScaleEngine.IncludeReference, False)
        
    def transformation(self):
        return Log10Transform()
        
    def autoScale(self, maxNumSteps, x1, x2, stepSize):
        # Always return consistent range from 1 to 10^8
        return 1.0, 1.0e8, 0
        
    def divideScale(self, x1, x2, maxMajor, maxMinor, stepSize=0):
        # Fixed logarithmic scale from 1 to 10^8
        # Always use same values regardless of input parameters
        
        # Set fixed bounds
        x1 = 1.0
        x2 = 1.0e8
        
        # Major ticks at powers of 10
        major_ticks = [10**i for i in range(9)]  # 1, 10, 100, ..., 10^8
        
        # Minor ticks only where needed to prevent clutter
        minor_ticks = []
        for i in range(8):  # For each decade
            base = 10**i
            minor_ticks.extend([base * j for j in [2, 3, 4, 5, 6, 7, 8, 9]])
            
        # Create scale division with proper ticks
        return QwtScaleDiv(x1, x2, minor_ticks, [], major_ticks)


class LinearScaleEngine(QwtLinearScaleEngine):
    def __init__(self):
        super().__init__()
        self.setAttribute(QwtScaleEngine.Floating, False)
        self.setAttribute(QwtScaleEngine.Symmetric, False)
        self.setAttribute(QwtScaleEngine.IncludeReference, True)

    def divideScale(self, x1, x2, maxMajor, maxMinor, stepSize=0):
        # Use fixed scale from 0 to 10
        x1 = 0
        x2 = 10
        
        # Create major ticks at integer positions
        major_ticks = list(range(int(x1), int(x2) + 1))
        
        # Create minor ticks between major ticks
        minor_ticks = []
        
        # Create scale division with proper ticks
        return QwtScaleDiv(x1, x2, [], minor_ticks, major_ticks)

class ScaledImagePlot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scaled Image Plot")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: transparent;")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create plot widget
        self.plot = BasePlot()
        self.plot.setStyleSheet("""
            QwtPlotCanvas {
                background-color: "white";
            }
        """)
        
       # Create a data array that spans the full height range
        rows = 100
        data = np.zeros((rows, 1))
        # Fill with values that span from 1 to 10^8 logarithmically
        for i in range(rows):
            # Calculate logarithmic position in the range
            data[i, 0] = 10**((i / rows) * 8)

        # Create image parameters with proper axis alignment
        image_param = ImageParam()
        # For x-axis alignment with ticks (as you already have)
        image_param.xmin = 0.5
        image_param.xmax = 1.5

        # For y-axis, since we're using a logarithmic scale:
        # Set the bottom of image at y=1
        image_param.ymin = 1.0
        # Set the top of image at y=10^8
        image_param.ymax = 1.0e8
        # Create and setup image item
        self.image_item = ImageItem(data, image_param)

        # Create and setup image item
        self.image_item = ImageItem(data, image_param)
        self.image_item.set_background_color("red")
        
        # Add image to plot
        self.plot.add_item(self.image_item)
        
        # Setup axis titles
        self.plot.set_axis_title("bottom", "X Axis")
        
        # Use your custom scale engine for x-axis
        self.plot.setAxisScaleEngine(self.plot.xBottom, LinearScaleEngine())
        self.plot.setAxisScaleEngine(self.plot.yLeft, Log10ScaleEngine())
        
        # Ensure proper axis labels
        self.plot.set_axis_title("left", "Y Axis")
        self.plot.set_axis_direction("left", reverse=False)
        
        # Add plot to layout
        layout.addWidget(self.plot)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScaledImagePlot()
    window.show()
    sys.exit(app.exec())