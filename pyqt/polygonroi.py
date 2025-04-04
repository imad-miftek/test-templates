import numpy as np
import pyqtgraph as pg
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QPainterPath, QPolygonF

class PolygonROI(pg.ROI):
    """
    Polygon ROI that can be created interactively by clicking to add vertices.
    
    The shape terminates when the user clicks near the starting point or double-clicks.
    """
    sigCreationFinished = pyqtSignal(object)  # Emitted when polygon creation is complete
    
    def __init__(self, positions=None, closed=False, **kwargs):
        """
        Initialize the PolygonROI.
        
        Parameters:
        -----------
        positions : list of (x,y) tuples or None
            Initial positions for polygon vertices. If None, starts in creation mode.
        closed : bool
            Whether the polygon is closed initially
        **kwargs : 
            Additional arguments to pass to ROI constructor
        """
        if positions is None:
            positions = [[0, 0]]  # Start with a single point
            
        # Initialize with the first position
        pg.ROI.__init__(self, positions[0], size=[1, 1], **kwargs)
        
        # Attributes for the polygon
        self.creation_mode = positions is None or len(positions) <= 1
        self.closed = closed
        self.segments = []
        self.handles = []
        self.close_threshold = 20  # Pixels within which we close the polygon
        
        # Set up the polygon
        if len(positions) > 1:
            self.setPoints(positions, closed=closed)
        else:
            # For interactive creation, we need to respond to clicks
            self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
    
    def setPoints(self, points, closed=None):
        """Set the polygon vertices."""
        if closed is not None:
            self.closed = closed
            
        # Clear existing points
        self.clearPoints()
        
        # Add handles for each point
        for p in points:
            self.addFreeHandle(p)
            
        # Add segments connecting the handles
        for i in range(len(self.handles)-1):
            self.addSegment(self.handles[i]['item'], self.handles[i+1]['item'])
        
        # If closed, connect the last point to the first
        if self.closed and len(self.handles) > 2:
            self.addSegment(self.handles[-1]['item'], self.handles[0]['item'])
            
        self.creation_mode = False
        self.update()
        
    def clearPoints(self):
        """Remove all handles and segments."""
        while len(self.handles) > 0:
            self.removeHandle(self.handles[0]['item'])
        
        # Clear segments
        for segment in self.segments[:]:
            self.removeSegment(segment)
        
    def addSegment(self, handle1, handle2):
        """Add a line segment between two handles."""
        segment = pg.LineSegmentROI(handles=(handle1, handle2), pen=self.pen, 
                                   movable=False, parent=self)
        self.segments.append(segment)
        return segment
    
    def removeSegment(self, segment):
        """Remove a segment from the polygon."""
        if segment in self.segments:
            self.segments.remove(segment)
            segment.setParentItem(None)
            segment.scene().removeItem(segment)
    
    def closePolygon(self):
        """Close the polygon by connecting the last point to the first."""
        if len(self.handles) > 2:
            # Add a segment from the last to the first handle
            self.addSegment(self.handles[-1]['item'], self.handles[0]['item'])
            self.closed = True
            self.creation_mode = False
            self.sigCreationFinished.emit(self)
        self.update()
    
    def mouseClickEvent(self, ev):
        """Handle mouse clicks during polygon creation."""
        if not self.creation_mode:
            # If not in creation mode, let the parent handle it
            super().mouseClickEvent(ev)
            return
            
        pos = ev.pos()
        
        # Check if the click is near the first point to close the polygon
        if len(self.handles) > 2:
            first_handle_pos = self.handles[0]['item'].pos()
            if (pos - first_handle_pos).manhattanLength() < self.close_threshold:
                # Close the polygon
                self.closePolygon()
                ev.accept()
                return
        
        # Add a new point
        handle = self.addFreeHandle(pos)
        
        # If this isn't the first point, connect to the previous point
        if len(self.handles) > 1:
            prev_handle = self.handles[-2]['item']
            self.addSegment(prev_handle, handle)
        
        ev.accept()
    
    def paint(self, p, *args):
        """Paint the polygon with fill."""
        if len(self.handles) < 2:
            return
            
        # Set up the painter
        p.setRenderHint(p.RenderHint.Antialiasing)
        p.setPen(self.currentPen)
        
        # Create a polygon from the handles
        polygon = QPolygonF()
        for h in self.handles:
            polygon.append(h['item'].pos())
            
        # Fill the polygon with a semi-transparent version of the pen color
        if self.closed:
            color = self.currentPen.color()
            color.setAlpha(50)  # Semi-transparent
            p.setBrush(color)
            p.drawPolygon(polygon)
    
    def shape(self):
        """Return the shape of the polygon for mouse interaction."""
        if len(self.handles) < 2:
            return QPainterPath()
            
        path = QPainterPath()
        path.moveTo(self.handles[0]['item'].pos())
        
        for i in range(1, len(self.handles)):
            path.lineTo(self.handles[i]['item'].pos())
            
        if self.closed:
            path.closeSubpath()
            
        return path
    
    def boundingRect(self):
        """Return the bounding rectangle of the polygon."""
        return self.shape().boundingRect()
    
    def getArrayRegion(self, arr, img, axes=(0, 1), **kwds):
        """Get the image region inside the polygon mask."""
        # Use the ROI._getArrayRegionForArbitraryShape method
        return self._getArrayRegionForArbitraryShape(arr, img, axes, **kwds)
    
    def getPoints(self):
        """Return a list of polygon points in local coordinates."""
        return [h['item'].pos() for h in self.handles]
    
    def getScenePoints(self):
        """Return a list of polygon points in scene coordinates."""
        return [h['item'].scenePos() for h in self.handles]


class PolygonROICreator:
    """Helper class to create PolygonROIs interactively on a PlotWidget."""
    def __init__(self, plot_widget):
        self.plot_widget = plot_widget
        self.current_roi = None
        self.finished_rois = []
        
        # Store the original ViewBox event handlers
        self.viewbox = self.plot_widget.getPlotItem().getViewBox()
        self.original_mouse_click_event = self.viewbox.mouseClickEvent
        self.original_mouse_drag_event = self.viewbox.mouseDragEvent
        
    def start(self):
        """Start creating a new polygon."""
        # Create a new PolygonROI
        self.current_roi = PolygonROI(pen=pg.mkPen('k', width=2), handlePen=pg.mkPen('k', width=2), handleHoverPen=pg.mkPen('r', width=2))
        self.current_roi.sigCreationFinished.connect(self._on_creation_finished)
        
        # Add it to the plot
        self.plot_widget.addItem(self.current_roi)
        
        # Override the ViewBox's mouse handlers to pass events to the ROI
        self.viewbox.mouseClickEvent = self._forward_click_to_roi
        self.viewbox.mouseDragEvent = self._forward_drag_to_viewbox
        
    def _on_creation_finished(self, roi):
        """Handle when a polygon is completed."""
        self.finished_rois.append(roi)
        self.current_roi = None
        
        # Restore original mouse handlers
        self.viewbox.mouseClickEvent = self.original_mouse_click_event
        self.viewbox.mouseDragEvent = self.original_mouse_drag_event
        
    def _forward_click_to_roi(self, event):
        """Forward mouse clicks to the current ROI"""
        if self.current_roi and self.current_roi.creation_mode:
            # Create a custom press event that has the methods MouseClickEvent expects
            class CustomPressEvent:
                def __init__(self, event):
                    self._event = event
                
                def scenePos(self):
                    return self._event.scenePos()
                
                def screenPos(self):
                    return self._event.screenPos()
                
                def button(self):
                    return self._event.button()
                
                def buttons(self):
                    return self._event.buttons()
                
                def modifiers(self):
                    return self._event.modifiers()
            
            # Create a MouseClickEvent using our custom press event
            new_event = MouseClickEvent(CustomPressEvent(event))
            
            # Make sure the event knows about our ROI
            new_event.currentItem = self.current_roi
            
            # Send to ROI
            self.current_roi.mouseClickEvent(new_event)
            
            # Accept the event to prevent further processing
            event.accept()
            return
        
        # Fall back to original behavior if not in creation mode
        self.original_mouse_click_event(event)
    
    def _forward_drag_to_viewbox(self, event):
        """Allow dragging the view while creating the polygon"""
        # Only forward drag events if we're not clicking the left button
        if event.button() != Qt.MouseButton.LeftButton:
            self.original_mouse_drag_event(event)
    
    def is_creating(self):
        """Return whether we're currently creating a polygon."""
        return self.current_roi is not None
        
    def get_rois(self):
        """Return all completed ROIs."""
        return self.finished_rois
    


import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Polygon ROI Demo")
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Add buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        self.create_button = QPushButton("Create Polygon")
        self.create_button.clicked.connect(self.start_polygon)
        button_layout.addWidget(self.create_button)
        
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_button)

        # Create PlotWidget
        self.plot = pg.PlotWidget()
        self.plot.showGrid(True, True)
        self.plot.setBackground('w')
        # self.plot.setMouseEnabled(x=False, y=False)
        
        # Add sample data
        np.random.seed(42)
        x1 = np.random.normal(100, 30, 500)
        y1 = np.random.normal(100, 30, 500)
        x2 = np.random.normal(300, 50, 500)
        y2 = np.random.normal(300, 50, 500)
        
        self.scatter = pg.ScatterPlotItem(
            x=np.concatenate([x1, x2]),
            y=np.concatenate([y1, y2]),
            pen=None,
            brush=pg.mkBrush(30, 30, 200, 50),
            size=10
        )
        self.plot.addItem(self.scatter)
        
        # Set up the ROI creator
        self.roi_creator = PolygonROICreator(self.plot)
        
        # Add plot to layout
        layout.addWidget(self.plot)

    def start_polygon(self):
        """Start creating a new polygon ROI."""
        self.roi_creator.start()
        self.create_button.setEnabled(False)
        self.create_button.setText("Click on plot to add points")
        
        # Connect to the creation finished signal
        self.roi_creator.current_roi.sigCreationFinished.connect(self.on_polygon_finished)
    
    def on_polygon_finished(self, roi):
        """Handle when polygon creation is finished."""
        self.create_button.setEnabled(True)
        self.create_button.setText("Create Polygon")
        
        # # Get points inside the polygon
        # region = roi.getArrayRegion(
        #     np.ones_like(self.scatter.data['x']), 
        #     self.scatter, 
        #     axes=(0, 1)
        # )
        print(f"Polygon created with {len(roi.getPoints())} vertices")
        # print(f"Points in region: {np.sum(region > 0)}")
    
    def clear_all(self):
        """Clear all ROIs from the plot."""
        for roi in self.roi_creator.get_rois():
            self.plot.removeItem(roi)
        
        if self.roi_creator.current_roi is not None:
            self.plot.removeItem(self.roi_creator.current_roi)
            # Restore original ViewBox event handlers if we're in the middle of creation
            if hasattr(self.roi_creator, 'original_mouse_click_event'):
                self.roi_creator.viewbox.mouseClickEvent = self.roi_creator.original_mouse_click_event
                self.roi_creator.viewbox.mouseDragEvent = self.roi_creator.original_mouse_drag_event
                
        self.roi_creator = PolygonROICreator(self.plot)
        self.create_button.setEnabled(True)
        self.create_button.setText("Create Polygon")

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()