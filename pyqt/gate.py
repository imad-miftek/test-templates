import pyqt as pg
from pyqtgraph.graphicsItems.ROI import Handle
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
import numpy as np
import types
from enum import Enum, auto

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

class GateViewBox(pg.ViewBox):
    """ViewBox with integrated gate creation and management capabilities"""
    def __init__(self, parent=None, border=None, lockAspect=False, enableMenu=True):
        super().__init__(parent, border, lockAspect, enableMenu)
        self.gates = []
        self.temp_gate = None
        self.drawing = False
        self.setup_menu()
        
    def setup_menu(self):
        """Set up the context menu for gate creation"""
        self.menu.addSeparator()
        self.gate_menu = self.menu.addMenu("Add Gate")
        self.gate_menu.addAction("Rectangle").triggered.connect(
            lambda: self.start_gate_creation(GateType.RECTANGLE))
        self.gate_menu.addAction("Ellipse").triggered.connect(
            lambda: self.start_gate_creation(GateType.ELLIPSE))
    
    def start_gate_creation(self, gate_type):
        """Start drawing a new gate"""
        self.gate_type = gate_type
        self.drawing = True
        self._original_mouse_enabled = self.state['mouseEnabled'][:]
        self.setMouseEnabled(x=False, y=False)
    
    def create_temp_gate(self, pos):
        """Create temporary gate during drawing"""
        if self.gate_type == GateType.RECTANGLE:
            return RectGate(pos=[pos.x(), pos.y()], size=[1, 1]).create()
        else:
            return EllipseGate(pos=[pos.x(), pos.y()], size=[1, 1]).create()
    
    def create_final_gate(self, pos, size):
        """Create the final gate based on type"""
        if size[0] <= 5 or size[1] <= 5:
            return
            
        gate = (RectGate if self.gate_type == GateType.RECTANGLE else EllipseGate)(
            pos=pos, size=size)
        roi = gate.create()
        self.addItem(roi)
        self.gates.append(gate)
        return roi
        
    def mousePressEvent(self, ev):
        if self.drawing and ev.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToView(ev.pos())
            self.temp_gate = self.create_temp_gate(pos)
            self.addItem(self.temp_gate)
            self.rubber_band_origin = pos
            ev.accept()
            return
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if self.drawing and self.temp_gate is not None:
            current_pos = self.mapToView(ev.pos())
            x = min(self.rubber_band_origin.x(), current_pos.x())
            y = min(self.rubber_band_origin.y(), current_pos.y())
            width = max(1, abs(current_pos.x() - self.rubber_band_origin.x()))
            height = max(1, abs(current_pos.y() - self.rubber_band_origin.y()))
            
            self.temp_gate.setPos(x, y)
            self.temp_gate.setSize([width, height])
            ev.accept()
            return
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev):
        if self.drawing and ev.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            
            if self.temp_gate is not None:
                pos = self.temp_gate.pos()
                size = self.temp_gate.size()
                self.removeItem(self.temp_gate)
                self.temp_gate = None
                self.create_final_gate(pos, size)
            
            self.setMouseEnabled(
                x=self._original_mouse_enabled[0],
                y=self._original_mouse_enabled[1]
            )
            ev.accept()
            return
        super().mouseReleaseEvent(ev)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gate Creation Demo")
        self.setGeometry(100, 100, 800, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Use the new GateViewBox
        self.plot = pg.PlotWidget(viewBox=GateViewBox())
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