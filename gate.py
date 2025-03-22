import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
import numpy as np

class RubberBandROICreator(pg.ViewBox):
    """ViewBox extension that allows rubber band creation of ROIs"""
    
    def __init__(self, parent=None, border=None, lockAspect=False, enableMenu=True):
        pg.ViewBox.__init__(self, parent, border, lockAspect, enableMenu)
        self.rubber_band_origin = None
        self.temp_roi = None
        self.drawing = False
        self.rois = []  # Store created ROIs
        
        # Set up context menu
        self.menu.addSeparator()
        self.roi_menu = self.menu.addMenu("Add ROI")
        self.roi_menu.addAction("Rectangle").triggered.connect(lambda: self.start_roi_creation("rect"))
        self.roi_menu.addAction("Ellipse").triggered.connect(lambda: self.start_roi_creation("ellipse"))
        
    def start_roi_creation(self, roi_type):
        """Start drawing ROI of specified type"""
        self.roi_type = roi_type
        self.drawing = True
        
        # Disable panning during gate creation
        self._original_mouse_enabled = self.state['mouseEnabled'][:]
        self.setMouseEnabled(x=False, y=False)
        
    def mousePressEvent(self, ev):
        if self.drawing and ev.button() == Qt.MouseButton.LeftButton:
            # Start drawing
            self.rubber_band_origin = self.mapToView(ev.pos())
            
            # Create temporary ROI based on type
            if self.roi_type == "rect":
                self.temp_roi = pg.RectROI(
                    pos=[self.rubber_band_origin.x(), self.rubber_band_origin.y()], 
                    size=[1, 1],
                    pen=pg.mkPen('r', width=2),
                )
            else:  # ellipse
                self.temp_roi = pg.EllipseROI(
                    pos=[self.rubber_band_origin.x(), self.rubber_band_origin.y()], 
                    size=[1, 1],
                    pen=pg.mkPen('b', width=2),
                )
            
            self.getViewWidget().addItem(self.temp_roi)
            ev.accept()
            return
        
        pg.ViewBox.mousePressEvent(self, ev)
    
    def mouseMoveEvent(self, ev):
        if self.drawing and self.temp_roi is not None:
            # Update ROI size/position
            current_pos = self.mapToView(ev.pos())
            x = min(self.rubber_band_origin.x(), current_pos.x())
            y = min(self.rubber_band_origin.y(), current_pos.y())
            width = max(1, abs(current_pos.x() - self.rubber_band_origin.x()))
            height = max(1, abs(current_pos.y() - self.rubber_band_origin.y()))
            
            self.temp_roi.setPos(x, y)
            self.temp_roi.setSize([width, height])
            ev.accept()
            return
            
        pg.ViewBox.mouseMoveEvent(self, ev)
    
    def mouseReleaseEvent(self, ev):
        if self.drawing and ev.button() == Qt.MouseButton.LeftButton:
            # Finish drawing
            self.drawing = False
            
            if self.temp_roi is not None:
                pos = self.temp_roi.pos()
                size = self.temp_roi.size()
                
                # Remove temporary ROI
                self.getViewWidget().removeItem(self.temp_roi)
                self.temp_roi = None
                
                # Only create if it's a reasonable size
                if size[0] > 5 and size[1] > 5:
                    self.create_final_roi(pos, size)
            
            # Restore original mouse enabled state
            self.setMouseEnabled(x=self._original_mouse_enabled[0], 
                               y=self._original_mouse_enabled[1])
                
            ev.accept()
            return
            
        pg.ViewBox.mouseReleaseEvent(self, ev)
    
    def create_final_roi(self, pos, size):
        """Create the final ROI based on rubber band selection"""
        if self.roi_type == "rect":
            roi = pg.RectROI(
                pos=pos, size=size, 
                pen=pg.mkPen('r', width=2),
            )
            roi.addScaleHandle([0, 0], [1, 1])
            roi.addScaleHandle([1, 1], [0, 0])
        else:  # ellipse
            roi = pg.EllipseROI(
                pos=pos, size=size, 
                pen=pg.mkPen('b', width=2),
            )
        
        # Add to view and store reference
        self.getViewWidget().addItem(roi)
        self.rois.append(roi)
        
    def getViewWidget(self):
        """Helper method to get the parent view widget"""
        return self.parentItem()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROI Creation Demo")
        self.setGeometry(100, 100, 800, 600)

        # Create layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create PlotWidget with custom ViewBox
        self.plot = pg.PlotWidget(viewBox=RubberBandROICreator())
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

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()