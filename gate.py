import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QMenu
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QCursor, QPainter
import numpy as np
import types

class RubberBandROICreator(pg.ViewBox):
    """ViewBox extension that allows rubber band creation of ROIs"""
    
    def __init__(self, parent=None, border=None, lockAspect=False, enableMenu=True):
        pg.ViewBox.__init__(self, parent, border, lockAspect, enableMenu)
        self.rubber_band_origin = None
        self.temp_roi = None
        self.drawing = False
        self.rois = []  # Store created ROIs
        
        # Set up context menu to add different ROI types
        self.menu.addSeparator()
        self.roi_menu = self.menu.addMenu("Add ROI")
        self.roi_menu.addAction("Rectangle").triggered.connect(lambda: self.start_roi_creation("rect"))
        self.roi_menu.addAction("Ellipse").triggered.connect(lambda: self.start_roi_creation("ellipse"))
        
    def start_roi_creation(self, roi_type):
        """Start drawing ROI of specified type at cursor position"""
        self.roi_type = roi_type
        self.drawing = True
        self.scene().installEventFilter(self)
        
    def mousePressEvent(self, ev):
        if self.drawing and ev.button() == Qt.MouseButton.LeftButton:
            # Start drawing
            self.rubber_band_origin = self.mapToView(ev.pos())
            
            # Create a temporary ROI for visualization with minimum size to avoid div by zero
            temp_pen = pg.mkPen('y', width=1, style=Qt.PenStyle.DashLine)
            
            if self.roi_type == "rect":
                # Create with non-zero size to avoid division by zero
                self.temp_roi = pg.ROI(pos=[self.rubber_band_origin.x(), self.rubber_band_origin.y()], 
                                       size=[1, 1], pen=temp_pen, movable=False)
            elif self.roi_type == "ellipse":
                # Create with non-zero size to avoid division by zero
                self.temp_roi = pg.EllipseROI(pos=[self.rubber_band_origin.x(), self.rubber_band_origin.y()], 
                                             size=[1, 1], pen=temp_pen, movable=False)
            
            view_widget = self.getViewWidget()
            view_widget.addItem(self.temp_roi)
            ev.accept()
            return
        
        # Default behavior for other mouse events
        pg.ViewBox.mousePressEvent(self, ev)
    
    def mouseMoveEvent(self, ev):
        if self.drawing and self.temp_roi is not None:
            # Get current position in view coordinates
            current_pos = self.mapToView(ev.pos())
            
            # Calculate size and position for the temporary ROI
            x = min(self.rubber_band_origin.x(), current_pos.x())
            y = min(self.rubber_band_origin.y(), current_pos.y())
            width = max(1, abs(current_pos.x() - self.rubber_band_origin.x()))  # Min width of 1
            height = max(1, abs(current_pos.y() - self.rubber_band_origin.y())) # Min height of 1
            
            # Update the temporary ROI
            self.temp_roi.setPos(x, y)
            self.temp_roi.setSize([width, height])
            ev.accept()
            return
            
        # Default behavior for other mouse events
        pg.ViewBox.mouseMoveEvent(self, ev)
    
    def mouseReleaseEvent(self, ev):
        if self.drawing and ev.button() == Qt.MouseButton.LeftButton:
            # Finish drawing
            self.drawing = False
            
            if self.temp_roi is not None:
                # Create the final ROI
                pos = self.temp_roi.pos()
                size = self.temp_roi.size()
                
                # Remove temporary ROI
                view_widget = self.getViewWidget()
                view_widget.removeItem(self.temp_roi)
                self.temp_roi = None
                
                # Only create if it's a reasonable size (ensure minimum size)
                if size[0] > 5 and size[1] > 5:
                    self.create_final_roi(pos, size)
                
            ev.accept()
            return
            
        # Default behavior for other mouse events
        pg.ViewBox.mouseReleaseEvent(self, ev)
    
    def create_final_roi(self, pos, size):
        """Create the actual ROI based on the rubber band selection"""
        # Create the appropriate ROI type
        if self.roi_type == "rect":
            # Create fill brush - semi-transparent red
            fill_brush = pg.mkBrush(255, 0, 0, 70)  # Red with 70/255 alpha
            
            roi = pg.RectROI(pos=pos, size=size, pen=pg.mkPen('r', width=2))
            
            # Custom paint method to add fill to RectROI
            def paint_with_fill(self, p, *args):
                # First fill with brush
                r = QRectF(0, 0, self.state['size'][0], self.state['size'][1]).normalized()
                p.setRenderHint(QPainter.RenderHint.Antialiasing, self._antialias)
                p.setPen(self.currentPen)
                p.setBrush(fill_brush)
                p.drawRect(r)
            
            # Replace the paint method
            roi.paint = types.MethodType(paint_with_fill, roi)
            
            # Add handles to the ROI
            roi.addScaleHandle([0, 0], [1, 1])
            roi.addScaleHandle([1, 1], [0, 0])
            roi.addScaleHandle([0, 1], [1, 0])
            roi.addScaleHandle([1, 0], [0, 1])
        elif self.roi_type == "ellipse":
            # Create fill brush - semi-transparent blue
            fill_brush = pg.mkBrush(0, 0, 255, 70)  # Blue with 70/255 alpha
            
            roi = pg.EllipseROI(pos=pos, size=size, pen=pg.mkPen('b', width=2))
            
            # Custom paint method to add fill to EllipseROI
            def paint_with_fill(self, p, *args):
                p.setRenderHint(QPainter.RenderHint.Antialiasing, self._antialias)
                p.setPen(self.currentPen)
                p.setBrush(fill_brush)
                
                # Draw the ellipse with fill
                rect = QRectF(0, 0, self.state['size'][0], self.state['size'][1])
                p.drawEllipse(rect)
            
            # Replace the paint method
            roi.paint = types.MethodType(paint_with_fill, roi)
        
        # Add to view and store reference
        view_widget = self.getViewWidget()
        view_widget.addItem(roi)
        self.rois.append(roi)
        
        # Connect signals if needed
        roi.sigRegionChanged.connect(self.roi_changed)
    
    def roi_changed(self, roi):
        """Handle ROI changes"""
        # You can implement filtering logic here based on the ROI position/shape
        pass
    
    def getViewWidget(self):
        """Helper method to get the parent view widget"""
        return self.parentItem()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive ROI Creation Demo")
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create PlotWidget with custom ViewBox
        self.plot = pg.PlotWidget(viewBox=RubberBandROICreator())
        self.plot.setBackground('w')
        self.plot.showGrid(True, True)
        
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
        
        # Add plot to layout
        layout.addWidget(self.plot)
        
        # Add instructions
        print("Right-click on the plot to open the context menu and select 'Add ROI'")
        print("Then click and drag to create ROIs with rubber band animation")

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

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()