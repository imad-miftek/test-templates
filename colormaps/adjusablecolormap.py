import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
import pyqtgraph as pg

class MinimalColorMapDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Adjustable Colormap Demo")
        self.resize(800, 500)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left side: create plot widget with image
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('w')
        layout.addWidget(plot_widget, 3)  # 3:1 ratio
        
        # Create some sample data (for demonstration)
        data = np.zeros((100, 100))
        # Create a more interesting pattern - diagonal gradient with some features
        for i in range(100):
            for j in range(100):
                # Base gradient
                data[i, j] = (i + j) / 2
                
        # Add some test features
        data[20:40, 20:40] += 30  # Add a square
        data[60:80, 60:80] += 50  # Add another square
        data[30:70, 40:45] += 40  # Add a vertical line
        
        # Create ImageItem and add it to the plot
        self.img = pg.ImageItem(data)
        plot_widget.addItem(self.img)
        plot_widget.setAspectLocked(True)
        
        # Right side: GradientEditor for colormap adjustment
        # Create a GraphicsView to contain the GradientEditorItem
        hist_view = pg.GraphicsView()
        layout.addWidget(hist_view, 1)  # 3:1 ratio
        
        # Create the GradientEditorItem and add it to the view
        self.gradient_editor = pg.GradientEditorItem()
        hist_view.setCentralItem(self.gradient_editor)
        
        # Connect the gradient changes to update the colormap
        self.gradient_editor.sigGradientChanged.connect(self.update_colormap)
        
        # Apply initial colormap
        self.update_colormap()
    
    def update_colormap(self):
        """Update the image's colormap based on the gradient editor's current state"""
        # Get the colormap from the gradient editor
        cmap = self.gradient_editor.colorMap()
        
        # Generate a lookup table and apply it to the image
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        self.img.setLookupTable(lut)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinimalColorMapDemo()
    window.show()
    sys.exit(app.exec())