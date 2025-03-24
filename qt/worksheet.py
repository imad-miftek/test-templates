from PySide6.QtWidgets import (QGraphicsScene, QGraphicsView, QMainWindow, QApplication,
                              QMenu, QGraphicsItem, QPushButton, QGraphicsProxyWidget)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QColor
from loguru import logger
import configparser as cfp
from pyqt.proxyplot import Plot

class Worksheet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = WorksheetScene(self)
        self.view = WorksheetView(self)
        self.setCentralWidget(self.view)
        self.view.setScene(self.scene)
        self.setup_context_menu()

    def setup_context_menu(self):
        self.context_menu = QMenu(self)
        self.add_plot_menu = QMenu("Add Plot", self)
        self.add_plot_menu.addAction("Oscilloscope").triggered.connect(lambda: self.add_new_plot("oscilloscope"))
        self.add_plot_menu.addAction("Pseudocolor").triggered.connect(lambda: self.add_new_plot("pseudocolor"))
        self.add_plot_menu.addAction("Histogram").triggered.connect(lambda: self.add_new_plot("histogram"))
        self.context_menu.addMenu(self.add_plot_menu)
        self.context_menu.addAction("Clear All Plots").triggered.connect(self.clear_scene)
        
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        self.context_menu.exec(self.view.mapToGlobal(position))

    def add_new_plot(self, plot_type):
        plot = Plot()

        view_center = self.view.mapToScene(self.view.viewport().rect().center())
        
        proxy = self.scene.addWidget(plot)
        proxy.setPos(view_center)
        proxy.setFlag(QGraphicsItem.ItemIsMovable, True)
        proxy.setFlag(QGraphicsItem.ItemIsSelectable, True)
        proxy.setFlag(QGraphicsItem.ItemIsFocusable, True)
    
    def clear_scene(self):
        for item in self.scene.items():
            if isinstance(item, QGraphicsProxyWidget):
                item.widget().close()

class WorksheetScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pageWidth = 850
        self.pageHeight = 1100
        self.horizontal_pages = 2
        self.vertical_pages = 1
        self.updateSceneRect()
            
    def updateSceneRect(self):
        width = self.horizontal_pages * self.pageWidth
        height = self.vertical_pages * self.pageHeight
        self.setSceneRect(QRectF(0, 0, width, height))
    
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        painter.fillRect(rect, Qt.white)
        
        # Draw page boundaries
        page_pen = QPen(QColor(130, 130, 130))
        page_pen.setStyle(Qt.DashLine)
        painter.setPen(page_pen)
        
        for i in range(self.horizontal_pages + 1):
            x = i * self.pageWidth
            painter.drawLine(x, rect.top(), x, rect.bottom())
        
        for i in range(self.vertical_pages + 1):
            y = i * self.pageHeight
            painter.drawLine(rect.left(), y, rect.right(), y)

class WorksheetView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)


if __name__ == '__main__':
    app = QApplication([])
    window = Worksheet()
    window.show()
    app.exec()