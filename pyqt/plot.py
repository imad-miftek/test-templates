from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QGraphicsScene, QGraphicsView
from PySide6.QtCore import Qt, Signal
import pyqtgraph as pg

class Plot(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Base Plot")
        self.setGeometry(100, 100, 800, 600)

        # Create PlotWidget
        self.plot = pg.PlotWidget()
        self.plot.showGrid(True, True)
        self.plot.setBackground('w')

        # Add plot to layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.plot)

        roi = pg.RectROI([0, 0], [1, 1], pen='r')
        roi.setAcceptedMouseButtons(pg.QtCore.Qt.MouseButton.LeftButton)
        roi.sigClicked.connect(lambda: print("Clicked"))
        roi.sigHoverEvent.connect(lambda:  print("Hovering"))
        roi.sigRegionChangeStarted.connect(lambda: print("Region change started"))
        roi.sigRegionChangeFinished.connect(lambda: print("Region change ended"))
        self.plot.addItem(roi)



# When using the PlotWidget in a QGraphicsProxyWidget, the ROI does not respond to mouse events.
if __name__ == '__main__':
    app = QApplication([])
    plot = Plot()
    view = QGraphicsView()
    scene = QGraphicsScene()
    proxy = scene.addWidget(plot)
    view.setScene(scene)
    view.show()
    app.exec()

# # When using the PlotWidget as a standalone widget, the ROI responds to mouse events.
# if __name__ == '__main__':
#     app = QApplication([])
#     plot = Plot()
#     plot.show()
#     app.exec()


# # When using the PlotWidget in an QMdiSubWindow, the ROI responds to mouse events.
# if __name__ == '__main__':
#     app = QApplication([])
#     window = QMainWindow()
#     mdi = pg.QtWidgets.QMdiArea()
#     window.setCentralWidget(mdi)
#     sub = pg.QtWidgets.QMdiSubWindow()
#     plot = Plot()
#     sub.setWidget(plot)
#     mdi.addSubWindow(sub)
#     window.show()
#     app.exec()