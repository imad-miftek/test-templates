from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt, QRunnable, QObject, Signal
from PySide6.QtGui import QGuiApplication

import pyqtgraph as pg
import numpy as np

if __name__ == "__main__":
    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("My App")
    window.setGeometry(100, 100, 500, 400)

    layout = QVBoxLayout()

    plot = pg.PlotWidget()
    plot.setXRange(0, 100)
    plot.setYRange(0, 100)
    plot.setBackground("w")
    image = pg.ImageItem()
    image.setColorMap(pg.colormap.get(name='viridis', source='matplotlib'))
    image.setImage(np.random.rand(100, 100))
    plot.addItem(image)
    layout.addWidget(plot)

    widget = QWidget()
    widget.setLayout(layout)

    window.setCentralWidget(widget)

    window.show()

    app.exec()