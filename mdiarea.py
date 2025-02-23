import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMdiArea, QMdiSubWindow
from PySide6.QtCore import Qt

class ZoomableMdiArea(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zoomable MDI Area")
        self.setGeometry(100, 100, 800, 600)

        # Create MDI Area
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        
        # Set up zoom factor
        self.zoom_factor = 1.0
        
        # Add some test sub-windows
        self.add_sub_window("Window 1")
        self.add_sub_window("Window 2")

    def add_sub_window(self, title):
        sub_window = QMdiSubWindow()
        sub_window.setWindowTitle(title)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming"""
        if event.modifiers() == Qt.ControlModifier:
            # Zoom in/out with Ctrl + mouse wheel
            if event.angleDelta().y() > 0:
                # Zoom in
                self.zoom_factor *= 1.1
            else:
                # Zoom out
                self.zoom_factor *= 0.9
            
            # Apply zoom
            self.mdi_area.setTransform(
                self.mdi_area.transform().scale(self.zoom_factor, self.zoom_factor)
            )
            event.accept()
        else:
            super().wheelEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ZoomableMdiArea()
    window.show()
    sys.exit(app.exec())