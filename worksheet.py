import sys, numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from plotpy.plot import BasePlot
from plotpy.items import ImageItem
from plotpy.styles import ImageParam
from qwt import QwtScaleDiv, QwtScaleDraw, QwtText
from qwt.scale_engine import QwtScaleEngine
from qwt.transform import QwtTransform

WAVELENGTHS = ["371nm", "382nm", "393nm", "404nm", "415nm"]
LOG_MIN, LOG_MAX = 1, 10**8

class WavelengthTransform(QwtTransform):
    def transform(self, value): return value
    def invTransform(self, value): return value
    def copy(self): return WavelengthTransform()

class WavelengthScaleDraw(QwtScaleDraw):
    def __init__(self, wavelengths):
        super().__init__()
        self.wavelengths = wavelengths
        self.setLabelRotation(45)
        self.setLabelAlignment(Qt.AlignBottom)
        self.setSpacing(10)
        self.setPenWidth(1.5)
    
    def label(self, value):
        idx = int(round(value))
        if 0 <= idx < len(self.wavelengths):
            text = QwtText(self.wavelengths[idx])
            text.setFont(QFont("Arial", 9))
            return text
        return QwtText("")

class WavelengthScaleEngine(QwtScaleEngine):
    def __init__(self, wavelengths):
        super().__init__()
        self.wavelengths = wavelengths
        self.setAttribute(QwtScaleEngine.Floating, False)
        self.setAttribute(QwtScaleEngine.Symmetric, False)
        self.setAttribute(QwtScaleEngine.IncludeReference, True)
    
    def transformation(self): return WavelengthTransform()
    def autoScale(self, maxNumSteps, x1, x2, stepSize): return -1, len(self.wavelengths) + 1, 1.0
    
    def divideScale(self, x1, x2, maxMajor, maxMinor, stepSize=0):
        x1, x2 = -1, len(self.wavelengths) + 1
        major_ticks = list(range(len(self.wavelengths)))
        return QwtScaleDiv(x1, x2, [], [], major_ticks)

class Log10Transform(QwtTransform):
    def __init__(self):
        super().__init__()
        self.LogMin, self.LogMax = LOG_MIN, LOG_MAX

    def bounded(self, value): return np.clip(value, self.LogMin, self.LogMax)
    def copy(self): return Log10Transform()
    def invTransform(self, value): return 10**self.bounded(value)
    def transform(self, value): return np.log10(self.bounded(value))

class Log10ScaleEngine(QwtScaleEngine):
    def transformation(self): return Log10Transform()
    def autoScale(self, maxNumSteps, x1, x2, stepSize): return LOG_MIN, LOG_MAX, 1
    
    def divideScale(self, x1, x2, maxMajor, maxMinor, stepSize=0):
        x1, x2 = LOG_MIN, LOG_MAX
        major_ticks = [10**i for i in range(9)]
        minor_ticks = [base * j for i in range(8) for base in [10**i] for j in range(2, 10)]
        return QwtScaleDiv(x1, x2, minor_ticks, [], major_ticks)

class MultiHistogramPlot(QMainWindow):
    def __init__(self, rotate=False):
        super().__init__()
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        self.rotate = rotate
        self.plot = BasePlot()
        layout.addWidget(self.plot)
        self.setup_plot()

    def setup_plot(self):
        self.setup_axes()
        self.num_bins = 1024
        
        # Initialize data array based on orientation
        self.initialH = np.zeros((self.num_bins, len(WAVELENGTHS)) if not self.rotate else (len(WAVELENGTHS), self.num_bins))

        # Configure image parameters
        self.image_param = ImageParam()
        self.image_param.lock_position = True
        
        # Set axis limits based on orientation
        if not self.rotate:
            self.image_param.xmin, self.image_param.xmax = -0.5, len(WAVELENGTHS)-0.5
            self.image_param.ymin, self.image_param.ymax = LOG_MIN, LOG_MAX
        else:
            self.image_param.xmin, self.image_param.xmax = LOG_MIN, LOG_MAX
            self.image_param.ymin, self.image_param.ymax = -0.5, len(WAVELENGTHS)-0.5
        
        self.image_param.colormap = "jet"
        
        print(f"Before adding image item: ")
        print(f"self.image_param.xmin: {self.image_param.xmin}, \
              self.image_param.xmax: {self.image_param.xmax}, \
              self.image_param.ymin: {self.image_param.ymin}, \
              self.image_param.ymax: {self.image_param.ymax}")
        
        # Create and add image item
        self.hist = ImageItem(self.initialH, self.image_param)
        self.plot.set_aspect_ratio(ratio=None, lock=False)  # Prevent overflow errors
        self.plot.add_item(self.hist)

        print(f"After adding image item: ") 
        print(f"self.image_param.xmin: {self.image_param.xmin}, \
              self.image_param.xmax: {self.image_param.xmax}, \
              self.image_param.ymin: {self.image_param.ymin}, \
              self.image_param.ymax: {self.image_param.ymax}")

    
    def setup_axes(self):
        if not self.rotate:
            # Normal orientation
            self.plot.setAxisTitle(BasePlot.X_BOTTOM, "Wavelength")
            self.plot.setAxisTitle(BasePlot.Y_LEFT, "Intensity")
            self.plot.setAxisScaleEngine(BasePlot.X_BOTTOM, WavelengthScaleEngine(WAVELENGTHS))
            self.plot.setAxisScaleDraw(BasePlot.X_BOTTOM, WavelengthScaleDraw(WAVELENGTHS))
            self.plot.setAxisScaleEngine(BasePlot.Y_LEFT, Log10ScaleEngine())
        else:
            # Rotated orientation
            self.plot.setAxisTitle(BasePlot.X_BOTTOM, "Intensity")
            self.plot.setAxisTitle(BasePlot.Y_LEFT, "Wavelength")
            self.plot.setAxisScaleEngine(BasePlot.X_BOTTOM, Log10ScaleEngine())
            self.plot.setAxisScaleEngine(BasePlot.Y_LEFT, WavelengthScaleEngine(WAVELENGTHS))
            self.plot.setAxisScaleDraw(BasePlot.Y_LEFT, WavelengthScaleDraw(WAVELENGTHS))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MultiHistogramPlot(rotate=False)
    
    # Create logarithmic bins and generate sample data
    log_bins = np.logspace(np.log10(LOG_MIN), np.log10(LOG_MAX), window.num_bins)
    sample_data = np.zeros((len(WAVELENGTHS), window.num_bins-1) if window.rotate else (window.num_bins-1, len(WAVELENGTHS)))
    
    # Generate histogram data for each wavelength
    for i in range(len(WAVELENGTHS)):
        # Generate raw data with multiple peaks
        num_samples = 100000
        mean1, std1 = 10**(2 + i*0.7), 10**(2 + i*0.7) * 0.3
        mean2, std2 = 10**(4 + i*0.5), 10**(4 + i*0.5) * 0.2
        
        # Create and combine samples
        raw_data = np.abs(np.concatenate([
            np.random.normal(mean1, std1, num_samples // 2),
            np.random.normal(mean2, std2, num_samples // 2)
        ]))
        
        # Create histogram with logarithmic bins
        hist_values, _ = np.histogram(raw_data, bins=log_bins)
        
        # Store histogram values in appropriate orientation
        if window.rotate:
            sample_data[i, :] = hist_values
        else:
            sample_data[:, i] = hist_values
    
    # Update the plot with the histogram data
    window.hist.set_data(sample_data)

    print(f"After setting data: ")
    print(f"self.image_param.xmin: {window.image_param.xmin}, \
          self.image_param.xmax: {window.image_param.xmax}, \
          self.image_param.ymin: {window.image_param.ymin}, \
          self.image_param.ymax: {window.image_param.ymax}")
    
    window.show()
    sys.exit(app.exec())