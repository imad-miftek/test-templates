import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt, QPointF

class SingleLineSegmentCreator:
    """Class to create a single line segment with two points"""
    def __init__(self, plot_widget):
        self.plot = plot_widget
        self.segment = None
        self.creating = False
        
        # Store original viewbox event handlers
        self.viewbox = self.plot.getPlotItem().getViewBox()
        self.orig_mouse_click = self.viewbox.mouseClickEvent
        
        # Preview line to show while drawing
        self.preview_line = pg.PlotDataItem(
            pen=pg.mkPen('r', width=2, style=Qt.PenStyle.DashLine)
        )
        self.preview_line.setZValue(100)
        
        # Start point
        self.start_point = None
    
    def start_creation(self, button=None):
        """Start creating a line segment"""
        self.creating = True
        self.button = button  # Store reference to the button
        
        # Set up click handling
        self.viewbox.mouseClickEvent = self.handle_click
        
        # Add preview line
        self.plot.addItem(self.preview_line)
        
        # Connect mouse move events to update the preview line
        self.plot.scene().sigMouseMoved.connect(self.update_preview)
    
    def finish_creation(self):
        """End the line creation process"""
        self.creating = False
        
        # Restore original handlers
        self.viewbox.mouseClickEvent = self.orig_mouse_click
        
        # Remove preview line
        self.plot.removeItem(self.preview_line)
        
        # Disconnect mouse move handler
        self.plot.scene().sigMouseMoved.disconnect(self.update_preview)
        
        self.start_point = None
    
    def handle_click(self, event):
        """Handle mouse clicks for creating a line segment"""
        if not self.creating:
            return self.orig_mouse_click(event)
        
        # Get click position in view coordinates (data coordinates)
        scene_pos = event.scenePos()
        view_pos = self.plot.getPlotItem().getViewBox().mapSceneToView(scene_pos)
        
        # If this is the first point, just store it
        if self.start_point is None:
            # Store in view coordinates
            self.start_point = (view_pos.x(), view_pos.y())
            
            # Create a marker at the start point (in view coordinates)
            self.plot.plot([view_pos.x()], [view_pos.y()], 
                         pen=None, symbol='o', symbolSize=8, 
                         symbolBrush='b')
            
            # Update button text
            if hasattr(self, 'button'):
                self.button.setText("Click to set end point...")
        else:
            # Create a LineSegmentROI between the start point and this point
            # Use view coordinates for both points
            self.segment = pg.LineSegmentROI(
                positions=[(self.start_point[0], self.start_point[1]), 
                           (view_pos.x(), view_pos.y())],
                pen=pg.mkPen('b', width=2),
                movable=True,
                removable=True
            )
            
            # Add to the plot
            self.plot.addItem(self.segment)
            
            # Finish creation automatically after creating the segment
            self.finish_creation()
            
            # Reset button text if we have a reference
            if hasattr(self, 'button'):
                self.button.setText("Create Line Segment")
        
        # Accept the event to prevent further processing
        event.accept()
    
    def update_preview(self, scene_pos):
        """Update the preview line when mouse moves"""
        if self.creating and self.start_point is not None:
            # Map scene position to view coordinates
            view_pos = self.plot.getPlotItem().getViewBox().mapSceneToView(scene_pos)
            
            # Update the preview line
            self.preview_line.setData(
                [self.start_point[0], view_pos.x()],
                [self.start_point[1], view_pos.y()]
            )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Single Line Segment Creator")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Plot widget
        self.plot = pg.PlotWidget()
        self.plot.setBackground('w')
        self.plot.setLabel('bottom', 'X Axis')
        self.plot.setLabel('left', 'Y Axis')
        layout.addWidget(self.plot)
        
        # Control buttons
        self.start_button = QPushButton("Create Line Segment")
        self.start_button.clicked.connect(self.start_drawing)
        layout.addWidget(self.start_button)
        
        # Create the line segment creator
        self.segment_creator = SingleLineSegmentCreator(self.plot)
    
    def start_drawing(self):
        """Start the line creation process"""
        self.segment_creator.start_creation(button=self.start_button)
        self.start_button.setText("Click to set start point...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())