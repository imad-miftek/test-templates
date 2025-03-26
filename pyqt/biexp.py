import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class BiExpAxisItem(pg.AxisItem):
    """
    Custom axis that implements a bi-exponential or semi-log scaling.
    
    This axis is linear near zero (between -linear_threshold and +linear_threshold),
    and logarithmic beyond that range.
    """
    def __init__(self, orientation, linear_threshold=1.0, log_base=10.0, **kwargs):
        super().__init__(orientation, **kwargs)
        self.linear_threshold = linear_threshold
        self.log_base = log_base
        self.biexp_mode = False  # Set to True to activate bi-exponential mode
        self.semi_log_mode = False  # Set to True to activate semi-log (positive only)
        
    def enableBiExpMode(self, enable=True, linear_threshold=None):
        """Enable or disable bi-exponential mode"""
        self.biexp_mode = enable
        if linear_threshold is not None:
            self.linear_threshold = linear_threshold
        self.picture = None
        self.update()
        
    def enableSemiLogMode(self, enable=True, linear_threshold=None):
        """Enable or disable semi-log mode (log for positive, linear for negative)"""
        self.semi_log_mode = enable
        if linear_threshold is not None:
            self.linear_threshold = linear_threshold
        self.picture = None
        self.update()
        
    def tickValues(self, minVal, maxVal, size):
        """Generate tick values for the axis"""
        if not self.biexp_mode and not self.semi_log_mode:
            return super().tickValues(minVal, maxVal, size)
            
        # Scale values
        minVal *= self.scale
        maxVal *= self.scale
        
        # Initialize tick arrays
        major_ticks = []
        minor_ticks = []
        
        if self.biexp_mode:
            # Bi-exponential mode (symmetric log scale)
            
            # Linear region ticks
            if -self.linear_threshold <= maxVal and minVal <= self.linear_threshold:
                # Add linear ticks in the central region
                linear_spacing = max(0.1, self.linear_threshold / 5)
                start = max(-self.linear_threshold, minVal)
                end = min(self.linear_threshold, maxVal)
                
                # Major ticks in linear region
                major_linear = np.arange(
                    start - (start % linear_spacing), 
                    end + linear_spacing, 
                    linear_spacing
                )
                major_linear = major_linear[(major_linear >= start) & (major_linear <= end)]
                major_ticks.extend(major_linear.tolist())
                
                # Minor ticks in linear region
                minor_spacing = linear_spacing / 5
                minor_linear = np.arange(
                    start - (start % minor_spacing),
                    end + minor_spacing,
                    minor_spacing
                )
                minor_linear = minor_linear[(minor_linear >= start) & (minor_linear <= end)]
                minor_ticks.extend(minor_linear.tolist())
            
            # Positive logarithmic region ticks
            if maxVal > self.linear_threshold:
                # Add logarithmic ticks for the positive region
                start_decade = int(np.floor(np.log10(self.linear_threshold)))
                end_decade = int(np.ceil(np.log10(maxVal)))
                
                # Major ticks at powers of 10
                for decade in range(start_decade, end_decade + 1):
                    if 10**decade >= self.linear_threshold and 10**decade <= maxVal:
                        major_ticks.append(10**decade)
                
                # Minor ticks at multiples within each decade
                for decade in range(start_decade, end_decade + 1):
                    for i in range(2, 10):
                        tick = i * 10**decade
                        if tick >= self.linear_threshold and tick <= maxVal:
                            minor_ticks.append(tick)
            
            # Negative logarithmic region ticks
            if minVal < -self.linear_threshold:
                # Add logarithmic ticks for the negative region
                start_decade = int(np.floor(np.log10(self.linear_threshold)))
                end_decade = int(np.ceil(np.log10(-minVal)))
                
                # Major ticks at negative powers of 10
                for decade in range(start_decade, end_decade + 1):
                    if 10**decade >= self.linear_threshold and 10**decade <= -minVal:
                        major_ticks.append(-10**decade)
                
                # Minor ticks at negative multiples within each decade
                for decade in range(start_decade, end_decade + 1):
                    for i in range(2, 10):
                        tick = -i * 10**decade
                        if -tick >= self.linear_threshold and tick >= minVal:
                            minor_ticks.append(tick)
                            
        elif self.semi_log_mode:
            # Semi-log mode (log for positive, linear for negative)
            
            # Handle positive (logarithmic) side
            if maxVal > 0:
                # Major ticks at powers of 10
                decade_min = max(0, int(np.floor(np.log10(max(1e-10, minVal)))))
                decade_max = int(np.ceil(np.log10(maxVal)))
                
                for decade in range(decade_min, decade_max + 1):
                    tick = 10**decade
                    if tick >= minVal and tick <= maxVal:
                        major_ticks.append(tick)
                
                # Minor ticks at multiples within each decade
                for decade in range(decade_min, decade_max + 1):
                    for i in range(2, 10):
                        tick = i * 10**decade
                        if tick >= minVal and tick <= maxVal:
                            minor_ticks.append(tick)
            
            # Handle negative (linear) side
            if minVal < 0:
                # Calculate appropriate linear spacing for negative values
                range_size = abs(minVal)
                if range_size <= 1:
                    spacing = 0.1
                elif range_size <= 10:
                    spacing = 1
                else:
                    spacing = 10 ** int(np.floor(np.log10(range_size/5)))
                
                # Major ticks
                start = minVal - (minVal % spacing)
                major_linear = np.arange(start, 0, spacing)
                major_ticks.extend(major_linear.tolist())
                
                # Minor ticks
                minor_spacing = spacing / 5
                minor_linear = np.arange(start, 0, minor_spacing)
                minor_ticks.extend(minor_linear.tolist())

        # Remove duplicates and convert to format expected by pyqtgraph
        major_ticks = sorted(list(set(major_ticks)))
        minor_ticks = [x for x in sorted(list(set(minor_ticks))) if x not in major_ticks]
        
        return [
            (None, [t / self.scale for t in major_ticks]),
            (None, [t / self.scale for t in minor_ticks])
        ]
        
    def tickStrings(self, values, scale, spacing):
        """Generate strings for the tick values"""
        if not self.biexp_mode and not self.semi_log_mode:
            return super().tickStrings(values, scale, spacing)
            
        strings = []
        for v in values:
            if abs(v) < 1e-10:
                strings.append('0')
            elif abs(v) < 0.1 or abs(v) >= 10000:
                strings.append(f"{v*scale:.1e}")
            else:
                strings.append(f"{v*scale:.4g}")
                
        return strings


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bi-Exponential Plot")
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create custom y-axis with bi-exponential scaling
        y_axis = BiExpAxisItem(orientation='left')
        
        # Create PlotWidget with custom y-axis
        self.plot = pg.PlotWidget(background='w', axisItems={'left': y_axis})
        self.plot.setXRange(0, 10)
        self.plot.setYRange(0, 1000)
        self.plot.showGrid(True, True)
        
        # Enable bi-exponential mode
        y_axis.enableSemiLogMode(True, linear_threshold=100.0)
        
        # Add sample data to demonstrate the scaling
        # Linear data
        x = np.linspace(0, 10, 100)
        
        # Small values around zero
        y1 = np.sin(x) * 5
        self.plot.plot(x, y1, pen='b', name="Linear Range")
        
        # Medium positive values
        y2 = 10 + x * 20
        self.plot.plot(x, y2, pen='r', name="Medium Range")
        
        # Large positive values (exponential)
        y3 = 50 * np.exp(x/2)
        self.plot.plot(x, y3, pen='g', name="Exponential Positive")
        
        # Large negative values
        y4 = -50 * np.exp(x/2)
        self.plot.plot(x, y4, pen='m', name="Exponential Negative")

        # Add plot to layout
        layout.addWidget(self.plot)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()