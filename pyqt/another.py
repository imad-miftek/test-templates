import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class SemiLogAxisItem(pg.AxisItem):
    """
    Custom axis with visually linear spacing for 0-100 and then
    logarithmic major ticks at powers of 10 from 1000 to 10^8.
    """
    def __init__(self, orientation, linear_threshold=100.0, **kwargs):
        super().__init__(orientation, **kwargs)
        self.linear_threshold = linear_threshold
        
    def setLinearThreshold(self, threshold):
        """Set the threshold between linear and logarithmic regions"""
        self.linear_threshold = threshold
        self.picture = None
        self.update()
        
    def tickValues(self, minVal, maxVal, size):
        """Generate tick values for the axis"""
        # Scale values
        minVal *= self.scale
        maxVal *= self.scale
        
        # Initialize tick arrays
        major_ticks = []
        minor_ticks = []
        
        # Linear region (0 to linear_threshold)
        if minVal < self.linear_threshold:
            # Use 0, 20, 40, 60, 80, 100 as major ticks in linear region
            spacing = 20.0 if self.linear_threshold == 100.0 else self.linear_threshold / 5
            
            # Generate linear major ticks
            start = max(0, minVal)
            end = min(self.linear_threshold, maxVal)
            
            major_linear = np.arange(
                start - (start % spacing), 
                end + spacing, 
                spacing
            )
            major_linear = major_linear[(major_linear >= start) & (major_linear <= end)]
            major_ticks.extend(major_linear.tolist())
            
            # Minor ticks in linear region (e.g., 5, 10, 15...)
            minor_spacing = spacing / 4
            minor_linear = np.arange(
                start - (start % minor_spacing),
                end + minor_spacing,
                minor_spacing
            )
            minor_linear = minor_linear[(minor_linear >= start) & (minor_linear <= end)]
            # Convert to list first
            minor_linear_list = minor_linear.tolist()
            # Then filter
            minor_linear_filtered = [t for t in minor_linear_list if t not in major_linear]
            # Add to minor ticks
            minor_ticks.extend(minor_linear_filtered)
        
        # Rest of the code remains the same
        # Log region (100 to 10^8) - only use powers of 10 as major ticks
        if maxVal > self.linear_threshold:
            # Add major ticks at powers of 10
            power_ticks = [10**i for i in range(3, 9)]  # 10^3 to 10^8
            
            # Add 100, 1000 if within range
            if self.linear_threshold <= maxVal:
                if self.linear_threshold not in major_ticks:
                    major_ticks.append(self.linear_threshold)  # Add 100
                
            # Add selected powers of 10 as major ticks
            major_ticks.extend([t for t in power_ticks if t >= minVal and t <= maxVal])
            
            # Add intermediate logarithmic minor ticks
            for decade in range(2, 9):  # 10^2 (100) to 10^8
                base = 10**decade
                if base >= minVal and base <= maxVal:
                    # Add 2, 3, 4, 5, 6, 7, 8, 9 × 10^n as minor ticks
                    for i in [2, 3, 4, 5, 6, 7, 8, 9]:
                        tick = i * base / 10
                        if tick >= max(self.linear_threshold, minVal) and tick <= maxVal and tick not in major_ticks:
                            minor_ticks.append(tick)
    
        # Remove duplicates and convert to format expected by pyqtgraph
        major_ticks = sorted(list(set(major_ticks)))
        minor_ticks = [x for x in sorted(list(set(minor_ticks))) if x not in major_ticks]
        
        return [
            (None, [t / self.scale for t in major_ticks]),
            (None, [t / self.scale for t in minor_ticks])
        ]
        
    def tickStrings(self, values, scale, spacing):
        """Generate formatted strings for the tick values"""
        strings = []
        for v in values:
            vs = v * scale
            if abs(vs) < 1e-10:
                strings.append('0')
            elif vs >= 1e6:
                # Use scientific notation for millions and above
                exponent = int(np.floor(np.log10(vs)))
                mantissa = vs / 10**exponent
                if mantissa == 1.0:  # For clean powers of 10
                    strings.append(f"10^{exponent}")
                else:
                    strings.append(f"{mantissa:.1f}×10^{exponent}")
            elif vs >= 1e3:
                # Use K notation for thousands
                if vs == 1e3:  # Exactly 1000
                    strings.append("1K")
                else:
                    strings.append(f"{vs/1000:.1f}K")
            elif vs >= 100:
                # Integer for values over 100
                strings.append(f"{int(vs)}")
            else:
                # Regular formatting for smaller values
                strings.append(f"{vs:.0f}")
                
        return strings


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Semi-Log Plot")
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create custom y-axis with semi-log scaling
        y_axis = SemiLogAxisItem(orientation='left', linear_threshold=100.0)
        
        # Create PlotWidget with custom y-axis
        self.plot = pg.PlotWidget(background='w', axisItems={'left': y_axis})
        self.plot.setXRange(0, 10)
        self.plot.setYRange(0, 1e8)  # Set full range
        self.plot.showGrid(True, True)
        
        # Add sample data to demonstrate the scale
        x = np.linspace(0, 10, 1000)
        
        # Linear region data (0-100)
        y1 = x * 10
        self.plot.plot(x, y1, pen={'color': 'blue', 'width': 2}, name="0-100")
        
        # Low log region data (100-1000)
        y2 = 100 * 10**(x/5)
        y2 = np.clip(y2, 100, 1000)
        self.plot.plot(x, y2, pen={'color': 'green', 'width': 2}, name="100-1K")
        
        # Mid log region data (1K-100K)
        y3 = 1000 * 10**(x/3.3)
        y3 = np.clip(y3, 1000, 100000)
        self.plot.plot(x, y3, pen={'color': 'red', 'width': 2}, name="1K-100K")
        
        # High log region data (100K-10M)
        y4 = 100000 * 10**(x/2.5)
        y4 = np.clip(y4, 100000, 10000000)
        self.plot.plot(x, y4, pen={'color': 'purple', 'width': 2}, name="100K-10M")
        
        # Very high region data (10M-100M)
        y5 = 10000000 * (1 + x/10)
        self.plot.plot(x, y5, pen={'color': 'orange', 'width': 2}, name="10M-100M")
        
        # Add legend
        self.plot.addLegend()
        
        # Add plot to layout
        layout.addWidget(self.plot)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()