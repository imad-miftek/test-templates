import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gate Demo")
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create PlotWidget
        self.plot = pg.PlotWidget()
        self.plot.showGrid(True, True)
        self.plot.setBackground('w')
        
        # Create a scatter plot with random data
        self.create_data()
        self.scatter = pg.ScatterPlotItem(
            x=self.x_data, 
            y=self.y_data,
            pen=None, 
            brush=pg.mkBrush(30, 30, 200, 50),
            size=10
        )
        self.plot.addItem(self.scatter)
        
        # Create a rectangular ROI gate
        self.roi = pg.RectROI([0, 0], [100, 100], pen=pg.mkPen('r', width=2))
        self.roi.addScaleHandle([0, 0], [1, 1])
        self.roi.addScaleHandle([1, 1], [0, 0])
        self.roi.addScaleHandle([0, 1], [1, 0])
        self.roi.addScaleHandle([1, 0], [0, 1])
        self.plot.addItem(self.roi)
        
        # Connect ROI changes to our handler function
        self.roi.sigRegionChanged.connect(self.update_gate)
        
        # Add plot to layout
        layout.addWidget(self.plot)
        
        # Set initial gate
        self.update_gate()

    def create_data(self):
        """Create random data for the scatter plot"""
        # Generate random data with two clusters
        np.random.seed(42)
        
        # Cluster 1
        x1 = np.random.normal(100, 30, 500)
        y1 = np.random.normal(100, 30, 500)
        
        # Cluster 2
        x2 = np.random.normal(300, 50, 500)
        y2 = np.random.normal(300, 50, 500)
        
        # Combine data
        self.x_data = np.concatenate([x1, x2])
        self.y_data = np.concatenate([y1, y2])
        
        # Original points for reference
        self.original_points = {
            'x': self.x_data.copy(),
            'y': self.y_data.copy()
        }
    
    def update_gate(self):
        """Update filtered data based on ROI position"""
        # Get ROI bounds
        bounds = self.roi.parentBounds()
        x_min, y_min = bounds.left(), bounds.top()
        x_max, y_max = bounds.right(), bounds.bottom()
        
        # Apply gate: filter points that are inside the ROI
        mask = (
            (self.original_points['x'] >= x_min) & 
            (self.original_points['x'] <= x_max) & 
            (self.original_points['y'] >= y_min) & 
            (self.original_points['y'] <= y_max)
        )
        
        # Get filtered data
        filtered_x = self.original_points['x'][mask]
        filtered_y = self.original_points['y'][mask]
        
        # Create a new scatter plot with highlighted points
        self.plot.removeItem(self.scatter)
        
        # First add all points (gray)
        self.scatter = pg.ScatterPlotItem(
            x=self.original_points['x'],
            y=self.original_points['y'],
            pen=None,
            brush=pg.mkBrush(100, 100, 100, 50),
            size=10
        )
        self.plot.addItem(self.scatter)
        
        # Then add selected points (blue)
        self.selected_scatter = pg.ScatterPlotItem(
            x=filtered_x,
            y=filtered_y,
            pen=None,
            brush=pg.mkBrush(30, 30, 200, 200),
            size=10
        )
        self.plot.addItem(self.selected_scatter)
        
        # Update status
        print(f"Selected {len(filtered_x)} points")


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()