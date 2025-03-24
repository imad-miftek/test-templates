import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from plotpy.plot import BasePlot
from plotpy.items import XYImageItem
from plotpy.styles import XYImageParam
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

        # Create PlotWidget
        self.plot = BasePlot()
        layout.addWidget(self.plot)

        wavelengths = np.array([400, 500, 600, 700])  # Example wavelengths as NumPy array


        self.image = XYImageItem(x=wavelengths, y=np.linspace(0, 100, 100), data=np.random.normal(size=(4, 4)),
                                 param=XYImageParam())

        self.plot.add_item(self.image)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Plot()
    window.show()
    sys.exit(app.exec())