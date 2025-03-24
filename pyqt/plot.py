from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget
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
        self.plot.addItem(roi)
        

if __name__ == '__main__':
    app = QApplication([])
    window = Plot()
    window.show()
    app.exec()