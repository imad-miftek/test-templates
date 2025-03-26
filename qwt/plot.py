import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from plotpy.plot import BasePlot
from plotpy.items import ImageItem, XYImageItem
from plotpy.styles import XYImageParam
from log10 import Log10ScaleEngine
import numpy as np



class Plot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Base Plot")
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        self.image_item = XYImageItem(
            x=np.array([0, 1, 2, 3, 4]), 
            y=np.linspace(0, 5, 1024),
            data=np.random.rand(1024, 5)           
        )



        # Create PlotWidget
        self.plot = BasePlot()
        self.plot.setAxisScaleEngine(BasePlot.Y_LEFT, Log10ScaleEngine())
        # self.plot.add_item(self.image_item)
        layout.addWidget(self.plot)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Plot()
    window.show()
    sys.exit(app.exec())