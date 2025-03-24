import sys, math
from PyQt5 import QtCore, QtGui, QtWidgets

class PolygonGateWidget(QtWidgets.QWidget):
    polygonChanged = QtCore.pyqtSignal(QtGui.QPolygonF)  # Signal when polygon changes
    
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        
        # Appearance settings
        self.pen = QtGui.QPen(QtGui.QColor(0, 0, 255))  # Blue outline
        self.pen.setWidth(2)
        self.brush = QtGui.QBrush(QtGui.QColor(0, 0, 255, 50))  # Semi-transparent blue fill
        
        # Point appearance
        self.pointPen = QtGui.QPen(QtGui.QColor(255, 0, 0))  # Red outline for points
        self.pointBrush = QtGui.QBrush(QtGui.QColor(255, 0, 0, 180))  # Red fill for points
        self.pointSize = 8
        
        # Initialize empty polygon
        self.polygon = QtGui.QPolygonF()
        self.tempPoint = None  # For drawing the line to current mouse pos
        self.dragPointIndex = -1  # Index of point being dragged
        self.isComplete = False  # Whether polygon is closed
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            pos = event.pos()
            
            # Check if we're clicking near an existing point
            for i in range(len(self.polygon)):
                if self.pointDistance(pos, self.polygon[i]) < self.pointSize:
                    self.dragPointIndex = i
                    return
            
            # If polygon is not complete, add a new point
            if not self.isComplete:
                self.polygon.append(QtCore.QPointF(pos))
                self.update()
                self.polygonChanged.emit(self.polygon)
        
        elif event.button() == QtCore.Qt.RightButton:
            # Complete the polygon if we have at least 3 points
            if len(self.polygon) >= 3 and not self.isComplete:
                self.isComplete = True
                self.update()
                self.polygonChanged.emit(self.polygon)
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.dragPointIndex != -1:
            self.dragPointIndex = -1
            self.polygonChanged.emit(self.polygon)
    
    def mouseMoveEvent(self, event):
        pos = event.pos()
        update_needed = False
        
        # Update for dragging
        if self.dragPointIndex != -1:
            self.polygon[self.dragPointIndex] = QtCore.QPointF(pos)
            update_needed = True
        
        # Update for line preview when creating polygon
        if not self.isComplete and len(self.polygon) > 0:
            self.tempPoint = QtCore.QPointF(pos)
            update_needed = True
        
        if update_needed:
            self.update()
            self.polygonChanged.emit(self.polygon)
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw the polygon
        if len(self.polygon) > 0:
            path = QtGui.QPainterPath()
            
            # Start path at first point
            path.moveTo(self.polygon[0])
            
            # Add all other points
            for i in range(1, len(self.polygon)):
                path.lineTo(self.polygon[i])
            
            # Close the polygon if complete
            if self.isComplete:
                path.closeSubpath()
            
            # Draw path
            painter.setPen(self.pen)
            painter.setBrush(self.brush if self.isComplete else QtCore.Qt.NoBrush)
            painter.drawPath(path)
            
            # Draw line to current mouse position if creating polygon
            if not self.isComplete and self.tempPoint and len(self.polygon) > 0:
                painter.setPen(QtGui.QPen(QtCore.Qt.DashLine))
                painter.drawLine(self.polygon[-1], self.tempPoint)
        
        # Draw the points
        painter.setPen(self.pointPen)
        painter.setBrush(self.pointBrush)
        for point in self.polygon:
            painter.drawEllipse(point, self.pointSize/2, self.pointSize/2)
    
    def pointDistance(self, p1, p2):
        dx = p1.x() - p2.x()
        dy = p1.y() - p2.y()
        return math.sqrt(dx*dx + dy*dy)
    
    def clear(self):
        """Clear the polygon and start over"""
        self.polygon = QtGui.QPolygonF()
        self.isComplete = False
        self.update()
        self.polygonChanged.emit(self.polygon)
    
    def getPolygon(self):
        """Return the current polygon"""
        return self.polygon
    
    def setPolygon(self, polygon):
        """Set polygon from existing QPolygonF"""
        self.polygon = polygon
        self.isComplete = True
        self.update()
        self.polygonChanged.emit(self.polygon)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv) 
    
    mainWindow = QtWidgets.QMainWindow()
    mainWindow.setWindowTitle("Polygon Gate Editor")
    mainWindow.resize(800, 600)
    
    widget = PolygonGateWidget()
    
    # Add some controls
    toolbar = QtWidgets.QToolBar()
    clearAction = toolbar.addAction("Clear")
    clearAction.triggered.connect(widget.clear)
    
    mainWindow.addToolBar(toolbar)
    mainWindow.setCentralWidget(widget)
    mainWindow.show()
    
    sys.exit(app.exec_())