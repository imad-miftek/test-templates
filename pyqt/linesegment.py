import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt, QPointF

class LineSegmentCreator:
    """Class to create line segments using PyQtGraph's LineSegmentROI"""
    def __init__(self, plot_widget):
        self.plot = plot_widget
        self.segments = []
        self.creating = False
        
        # Store original viewbox event handlers
        self.viewbox = self.plot.getPlotItem().getViewBox()
        self.orig_mouse_click = self.viewbox.mouseClickEvent
        
        # Preview line to show while drawing
        self.preview_line = pg.PlotDataItem(
            pen=pg.mkPen('r', width=2, style=Qt.PenStyle.DashLine)
        )
        self.preview_line.setZValue(100)
        
        # Latest point
        self.last_point = None
    
    def start_creation(self):
        """Start creating line segments"""
        self.creating = True
        
        # Set up click handling
        self.viewbox.mouseClickEvent = self.handle_click
        
        # Add preview line
        self.plot.addItem(self.preview_line)
        
        # Connect mouse move events to update the preview line
        self.plot.scene().sigMouseMoved.connect(self.update_preview)
    
    def finish_creation(self):
        """End the line segment creation"""
        self.creating = False
        
        # Restore original handlers
        self.viewbox.mouseClickEvent = self.orig_mouse_click
        
        # Remove preview line
        self.plot.removeItem(self.preview_line)
        
        # Disconnect mouse move handler
        self.plot.scene().sigMouseMoved.disconnect(self.update_preview)
        
        self.last_point = None
    
    def handle_click(self, event):
        """Handle mouse clicks for creating line segments"""
        if not self.creating:
            return self.orig_mouse_click(event)
        
        # Get click position
        pos = event.scenePos()
        
        # If this is the first point, just store it
        if self.last_point is None:
            self.last_point = (pos.x(), pos.y())
            
            # Create a marker at the first point
            self.plot.plot([pos.x()], [pos.y()], 
                         pen=None, symbol='o', symbolSize=8, 
                         symbolBrush='b')
        else:
            # Create a LineSegmentROI between the last point and this point
            segment = pg.LineSegmentROI(
                positions=[(self.last_point[0], self.last_point[1]), 
                           (pos.x(), pos.y())],
                pen=pg.mkPen('b', width=2),
                movable=True,
                removable=True
            )
            
            # Add to the plot
            self.plot.addItem(segment)
            self.segments.append(segment)
            
            # Update the last point for the next segment
            self.last_point = (pos.x(), pos.y())
        
        # Accept the event to prevent further processing
        event.accept()
    
    def update_preview(self, scene_pos):
        """Update the preview line when mouse moves"""
        if self.creating and self.last_point is not None:
            # Map scene position to view coordinates
            view_pos = self.plot.getPlotItem().getViewBox().mapSceneToView(scene_pos)
            
            # Update the preview line
            self.preview_line.setData(
                [self.last_point[0], view_pos.x()],
                [self.last_point[1], view_pos.y()]
            )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LineSegmentROI Demo")
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
        self.start_button = QPushButton("Start Drawing")
        self.start_button.clicked.connect(self.start_drawing)
        layout.addWidget(self.start_button)
        
        self.finish_button = QPushButton("Finish Drawing")
        self.finish_button.clicked.connect(self.finish_drawing)
        self.finish_button.setEnabled(False)
        layout.addWidget(self.finish_button)
        
        # Create the line segment creator
        self.segment_creator = LineSegmentCreator(self.plot)
    
    def start_drawing(self):
        """Start the line creation process"""
        self.segment_creator.start_creation()
        self.start_button.setEnabled(False)
        self.finish_button.setEnabled(True)
    
    def finish_drawing(self):
        """End the line creation process"""
        self.segment_creator.finish_creation()
        self.start_button.setEnabled(True)
        self.finish_button.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())