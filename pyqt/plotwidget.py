import pyqt as pg
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
        self.plot = pg.PlotWidget()
        self.plot.showGrid(True, True)
        self.plot.setBackground('w')

        # Add plot to layout
        layout.addWidget(self.plot)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()