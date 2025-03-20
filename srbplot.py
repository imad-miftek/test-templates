from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt, QRunnable, QObject, Signal
from PySide6.QtGui import QGuiApplication, QTransform

import pyqtgraph as pg
import numpy as np

LOG_MIN = 0
LOG_MAX = 8

def setup_plot(plot: pg.PlotWidget):
    plot.getPlotItem().setLogMode(x=False, y=True)  # Enable log mode for the y-axis
    plot.setMouseEnabled(x=False, y=False)  # Disable mouse interaction for x-axis
    plot.setBackground("w")
    plot.setXRange(0, 10)
    plot.setYRange(LOG_MIN, LOG_MAX)  # Set y-range for log scale
    plot.getPlotItem().showGrid(x=True, y=False)  # Show grid for better visibility

def setup_image(image: pg.ImageItem):
    image.setColorMap(pg.colormap.get(name='viridis', source='matplotlib'))
    image.setLevels(levels=(0, 10))  # Set levels for better visibility

def generate_data():
    data = np.zeros((10, 1024))  # Initialize data array for 10 ribbons

    # Create pattern across ribbons
    for i in range(10):
        # Vary number of active bins in a pattern
        num_bins = int(20 + 15 * np.sin(i * np.pi / 4))

        # Create positions with increasing spread for higher ribbon numbers
        positions = np.linspace(100, 900, num_bins) 
        positions += np.random.normal(0, i*5, num_bins)  # Add noise proportional to ribbon index
        positions = np.clip(positions, 0, 1023).astype(int)  # Ensure in valid range

        # Vary amplitudes in a pattern 
        amplitudes = 4 + 3 * np.cos(positions/200) + i/2  # Amplitude varies by position and ribbon

        # Set values
        for pos, amp in zip(positions, amplitudes):
            data[i, pos] = amp

    # Add some interesting features
    data[2, 300:350] = np.linspace(0, 9, 50)  # Ramp in ribbon 3
    data[7, 700:800] = 8 * np.sin(np.linspace(0, 4*np.pi, 100))  # Sine wave in ribbon 8
    data[4, 400:600:5] = 7  # Dotted line in ribbon 5

    return data


def transform_image(image: pg.ImageItem):
    # Create a transformation for the ImageItem
    transform = QTransform()
    transform.scale(1, (LOG_MAX - LOG_MIN) / 1024)  # Scale vertical axis
    transform.translate(0, LOG_MIN/((LOG_MAX-LOG_MIN)/1024))
    image.setTransform(transform)  # Apply transformation to the image
    return image

if __name__ == "__main__":
    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("My App")
    window.setGeometry(100, 100, 500, 400)

    layout = QVBoxLayout()

    plot = pg.PlotWidget()
    setup_plot(plot)
    image = pg.ImageItem()
    setup_image(image)

    data = generate_data()
    image.setImage(data)  # Set initial image data
    image = transform_image(image)  # Apply transformation to the image

    layout.addWidget(plot)

    plot.addItem(image)

    widget = QWidget()
    widget.setLayout(layout)

    window.setCentralWidget(widget)

    window.show()

    app.exec()