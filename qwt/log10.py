from qwt import QwtScaleDiv, QwtScaleDraw, QwtText
from qwt.scale_engine import QwtScaleEngine
from qwt.transform import QwtTransform
import numpy as np

LOG_MIN, LOG_MAX = 1, 10**8

class Log10ScaleDraw(QwtScaleDraw):
    def __init__(self):
        super().__init__()
        self.setLabelRotation(0)

    def label(self, value):
        if value < 1: return QwtText('0')
        if value == 1:
            return QwtText('1')
        else:
            exponent = int(np.log10(value))
            return QwtText('10<sup>%d</sup>' % exponent, QwtText.RichText)


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