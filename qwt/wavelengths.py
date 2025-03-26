from qwt import QwtScaleDiv, QwtScaleDraw, QwtText
from qwt.scale_engine import QwtScaleEngine
from qwt.transform import QwtTransform
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

WAVELENGTHS = ["371nm", "382nm", "393nm", "404nm", "415nm"]


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