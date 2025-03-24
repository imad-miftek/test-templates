import numpy as np
import pyqt as pg
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QTransform, QFont


class MainWindow(QMainWindow):
    """ example application main window """
    def __init__(self):
        super().__init__()
        self.resize(440,400)
        self.show()

        plot = pg.PlotWidget()
        self.setCentralWidget(plot)

        # Set To Larger Font
        leftAxis = plot.getAxis('left')
        bottomAxis = plot.getAxis('bottom')
        font = QFont("Roboto", 18)
        leftAxis.setTickFont(font)
        bottomAxis.setTickFont(font)

        # Example: Transformed display of ImageItem
        tr = QTransform()  # prepare ImageItem transformation:
        tr.scale(6.0, 3.0)       # scale horizontal and vertical axes
        tr.translate(-1.5, -1.5) # move 3x3 image to locate center at axis origin

        img = pg.ImageItem(
            image=np.eye(3),
            levels=(0,1)
        ) # create example image
        img.setTransform(tr) # assign transform
        img.setCompositionMode(pg.QtGui.QPainter.CompositionMode.CompositionMode_Plus) # set composition mode

        plot.addItem( img )  # add ImageItem to PlotItem
        plot.showAxes(True)  # frame it with a full set of axes
        plot.invertY(True)   # vertical axis counts top to bottom

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()