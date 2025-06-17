import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
import pyqtgraph as pg

class JetColormapDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jet Colormap Demonstration")
        self.resize(900, 500)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Add a title
        title_label = QLabel("Jet Colormap Demonstration")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Create a horizontal layout for the images
        display_layout = QHBoxLayout()
        main_layout.addLayout(display_layout)
        
        # Create first plot widget for the test pattern
        plot_widget1 = pg.PlotWidget()
        plot_widget1.setBackground('w')
        plot_widget1.setTitle("Test Pattern")
        display_layout.addWidget(plot_widget1)
        
        # Create test pattern that will show the full colormap range
        test_pattern = self.create_test_pattern()
        
        # Create ImageItem for the test pattern
        self.img1 = pg.ImageItem(test_pattern)
        plot_widget1.addItem(self.img1)
        
        # Create second plot widget for a gradient image
        plot_widget2 = pg.PlotWidget()
        plot_widget2.setBackground('w')
        plot_widget2.setTitle("Continuous Gradient")
        display_layout.addWidget(plot_widget2)
        
        # Create gradient image
        gradient_data = self.create_gradient()
        
        # Create ImageItem for the gradient
        self.img2 = pg.ImageItem(gradient_data)
        plot_widget2.addItem(self.img2)
        
        # Create third plot with the colorbar for reference
        colorbar_layout = QVBoxLayout()
        display_layout.addLayout(colorbar_layout)
        
        colorbar_label = QLabel("Colormap")
        colorbar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        colorbar_layout.addWidget(colorbar_label)
        
        # Create a GraphicsView to contain the GradientEditorItem (for visualization only)
        colorbar_view = pg.GraphicsView()
        colorbar_view.setFixedWidth(100)
        colorbar_layout.addWidget(colorbar_view)
        
        # Create the gradient editor item with the jet colormap
        self.gradient_editor = pg.GradientEditorItem(orientation='right')
        colorbar_view.setCentralItem(self.gradient_editor)
        
        # Set up the jet colormap
        self.setup_jet_colormap()
        
        # Apply the colormap to both images
        self.apply_colormap()
    
    def create_test_pattern(self):
        """Create a test pattern with all possible values to demonstrate the colormap"""
        # Create a 100x100 array
        data = np.zeros((100, 100))
        
        # Fill with varied patterns to ensure we see all colors
        # Central gradient
        for i in range(100):
            data[i, :] = i
            
        # Add some features to help visualize
        data[20:40, 20:40] = 90  # Upper left square - high value (red)
        data[20:40, 60:80] = 70  # Upper right square - mid-high value (yellow)
        data[60:80, 20:40] = 30  # Lower left square - mid-low value (cyan)
        data[60:80, 60:80] = 10  # Lower right square - low value (blue)
        
        # Add diagonal gradient
        for i in range(100):
            data[i, i] = 99  # Max value diagonal (red)
            if i < 90:
                data[i+10, i] = 50  # Mid value diagonal (green)
        
        return data
    
    def create_gradient(self):
        """Create a simple vertical gradient showing all colormap values"""
        data = np.zeros((100, 100))
        
        # Fill with vertical gradient
        for i in range(100):
            data[:, i] = np.linspace(0, 99, 100)
        
        return data
    
    def setup_jet_colormap(self):
        """Set up a jet-style colormap (blue->cyan->green->yellow->red)"""
        # Define the color positions (0 to 1)
        positions = [
            0.0,   # Dark blue
            0.125, # Blue
            0.25,  # Cyan
            0.5,   # Green
            0.75,  # Yellow
            0.875, # Orange
            1.0    # Red
        ]
        
        # Define the colors (RGBA, values 0-1)
        colors = [
            (0, 0, 0.5, 1),      # Dark blue
            (0, 0, 1, 1),        # Blue
            (0, 1, 1, 1),        # Cyan
            (0, 1, 0, 1),        # Green
            (1, 1, 0, 1),        # Yellow
            (1, 0.5, 0, 1),      # Orange
            (1, 0, 0, 1)         # Red
        ]
        
        # Set the colormap in the gradient editor
        self.gradient_editor.restoreState({
            'mode': 'rgb',
            'ticks': list(zip(positions, colors))
        })
    
    def apply_colormap(self):
        """Apply the current colormap to the images"""
        # Get the colormap from the gradient editor
        cmap = self.gradient_editor.colorMap()
        
        # Generate lookup table
        lut = cmap.getLookupTable(0, 1, 256)
        
        # Apply to both images
        self.img1.setLookupTable(lut)
        self.img2.setLookupTable(lut)
        
        # Set levels to ensure we see the full range
        self.img1.setLevels((0, 99))
        self.img2.setLevels((0, 99))

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JetColormapDemo()
    window.show()
    sys.exit(app.exec())