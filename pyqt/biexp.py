import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Base Plot")
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create PlotWidget
        self.plot = pg.PlotWidget(background='w')
        self.plot.setXRange(0, 10)
        self.plot.setYRange(0, 100)
        self.plot.setLogMode(x=False, y=False)
        self.plot.showGrid(True, True)

        # Add plot to layout
        layout.addWidget(self.plot)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()