import pyqtgraph as pg
from pyqtgraph.graphicsItems.ROI import Handle
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
import numpy as np
import types
from enum import Enum, auto
import sys

class GateType(Enum):
    RECTANGLE = auto()
    ELLIPSE = auto()

class Gate:
    """Base class for all gates/ROIs"""
    def __init__(self, pos, size, pen=None):
        self.pos = pos
        self.size = size
        self.pen = pen or pg.mkPen('k', width=2)
        self.roi = None
        
    def create(self):
        """Create the ROI - to be implemented by subclasses"""
        raise NotImplementedError
        
    def enhance_handles(self):
        """Add enhanced styling to ROI handles"""
        handles = self.roi.getHandles()
        for handle in handles:
            original_paint = handle.paint
            
            def enhanced_paint(self, p, opt, widget):
                original_paint(p, opt, widget)
                p.setBrush(pg.mkBrush(0, 0, 0, 255))
                p.setPen(pg.mkPen(0, 0, 0, 255))
                p.drawPath(self.shape())

            handle.paint = types.MethodType(enhanced_paint, handle)

class RectGate(Gate):
    def create(self):
        self.roi = pg.RectROI(pos=self.pos, size=self.size, pen=self.pen)
        self.roi.addScaleHandle([0, 0], [1, 1])
        self.roi.addScaleHandle([1, 1], [0, 0])
        self.roi.addScaleHandle([1, 0], [0, 1])
        self.roi.addScaleHandle([0, 1], [1, 0])
        self.enhance_handles()
        return self.roi

class EllipseGate(Gate):
    def create(self):
        self.roi = pg.EllipseROI(pos=self.pos, size=self.size, pen=self.pen)
        self.enhance_handles()
        return self.roi

class SelectableROI(pg.RectROI):
    """Custom ROI that changes handle opacity based on selection state"""
    
    def __init__(self, pos, size, **kwargs):
        super().__init__(pos, size, **kwargs)
        # Set initial handle appearance
        self.dimHandles()
        
    def dimHandles(self, opacity=30):
        """Make handles semi-transparent"""
        for h in self.getHandles():
            # Create a semi-transparent black pen
            dim_pen = pg.mkPen(0, 0, 0, opacity)
            dim_brush = pg.mkBrush(0, 0, 0, opacity)
            
            # Store the original paint method if not already stored
            if not hasattr(h, '_original_paint'):
                h._original_paint = h.paint
                
                # Create a custom paint method
                def custom_paint(self, p, opt, widget):
                    p.setPen(self._pen)
                    p.setBrush(self._brush)
                    p.drawPath(self.shape())
                
                h.paint = types.MethodType(custom_paint, h)
            
            # Store the current appearance
            h._pen = dim_pen
            h._brush = dim_brush
            
            # Force update
            h.update()
            
    def highlightHandles(self, opacity=255):
        """Make handles fully visible"""
        for h in self.getHandles():
            # Create a fully opaque black pen
            bright_pen = pg.mkPen(0, 0, 0, opacity)
            bright_brush = pg.mkBrush(0, 0, 0, opacity)
            
            # Update the appearance
            h._pen = bright_pen
            h._brush = bright_brush
            
            # Force update
            h.update()
    
    def setSelected(self, selected):
        """Override setSelected to change handle opacity based on selection state"""
        super().setSelected(selected)
        if selected:
            self.highlightHandles()
        else:
            self.dimHandles()
        
        # Enable or disable mouse interaction for handles based on selection
        for h in self.getHandles():
            if selected:
                h.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
            else:
                h.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

class SelectableEllipseROI(pg.EllipseROI):
    """Custom Ellipse ROI with handle opacity control"""
    
    def __init__(self, pos, size, **kwargs):
        super().__init__(pos, size, **kwargs)
        self.dimHandles()
        
    def dimHandles(self, opacity=30):
        for h in self.getHandles():
            # Create a semi-transparent black pen
            dim_pen = pg.mkPen(0, 0, 0, opacity)
            dim_brush = pg.mkBrush(0, 0, 0, opacity)
            
            # Store the original paint method if not already stored
            if not hasattr(h, '_original_paint'):
                h._original_paint = h.paint
                
                # Create a custom paint method
                def custom_paint(self, p, opt, widget):
                    p.setPen(self._pen)
                    p.setBrush(self._brush)
                    p.drawPath(self.shape())
                
                h.paint = types.MethodType(custom_paint, h)
            
            # Store the current appearance
            h._pen = dim_pen
            h._brush = dim_brush
            
            # Force update
            h.update()
            
    def highlightHandles(self, opacity=255):
        for h in self.getHandles():
            # Create a fully opaque black pen
            bright_pen = pg.mkPen(0, 0, 0, opacity)
            bright_brush = pg.mkBrush(0, 0, 0, opacity)
            
            # Update the appearance
            h._pen = bright_pen
            h._brush = bright_brush
            
            # Force update
            h.update()
    
    def setSelected(self, selected):
        super().setSelected(selected)
        if selected:
            self.highlightHandles()
        else:
            self.dimHandles()
            
        # Enable or disable mouse interaction for handles based on selection
        for h in self.getHandles():
            if selected:
                h.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
            else:
                h.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

class SelectableGateViewBox(pg.ViewBox):
    """ViewBox that handles ROI selection/deselection"""
    
    def __init__(self, parent=None, border=None, lockAspect=False, enableMenu=True):
        super().__init__(parent, border, lockAspect, enableMenu)
        self.current_selected_roi = None
        
    def addROI(self, roi_type, pos=None, size=None):
        """Add a new ROI of specified type"""
        if pos is None:
            # Use center of current view
            rect = self.viewRect()
            center = rect.center()
            pos = [center.x() - 50, center.y() - 50]
            
        if size is None:
            size = [100, 100]
            
        if roi_type == 'rect':
            roi = SelectableROI(pos=pos, size=size, pen=pg.mkPen('r', width=2))
        elif roi_type == 'ellipse':
            roi = SelectableEllipseROI(pos=pos, size=size, pen=pg.mkPen('r', width=2))
        
        self.addItem(roi)
        roi.sigClicked.connect(self.onROIClicked)
        
        # Make sure ROI can receive mouse clicks
        roi.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        
        return roi
    
    def onROIClicked(self, roi, event):
        """Handle ROI selection"""
        # Deselect previously selected ROI
        if self.current_selected_roi is not None and self.current_selected_roi != roi:
            self.current_selected_roi.setSelected(False)
        
        # Select this ROI
        roi.setSelected(True)
        self.current_selected_roi = roi
        
        # Accept the event
        event.accept()
    
    def mouseClickEvent(self, event):
        """Handle clicks on the background to deselect ROIs"""
        # Only process left clicks that aren't on ROIs
        if event.button() == Qt.MouseButton.LeftButton and not event.isAccepted():
            # Deselect current ROI
            if self.current_selected_roi is not None:
                self.current_selected_roi.setSelected(False)
                self.current_selected_roi = None
            event.accept()
        else:
            super().mouseClickEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gate Creation Demo")
        self.setGeometry(100, 100, 800, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Use the new GateViewBox
        self.plot = pg.PlotWidget(viewBox=SelectableGateViewBox())
        self.plot.setBackground('w')
        self.plot.showGrid(True, True)
        
        # Create scatter plot with random data
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
        layout.addWidget(self.plot)

        # Add some ROIs
        view_box = self.plot.getViewBox()
        view_box.addROI('rect', [50, 50], [100, 100])
        view_box.addROI('ellipse', [200, 200], [150, 100])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()