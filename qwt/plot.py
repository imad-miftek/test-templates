from enum import auto
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from plotpy.plot import BasePlot, PlotManager
from plotpy.tools import SelectTool, AnnotatedRectangleTool
from log10 import Log10ScaleEngine, Log10ScaleDraw
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
        self.plot.setAxisScaleEngine(BasePlot.yLeft, Log10ScaleEngine())
        self.plot.setAxisScaleEngine(BasePlot.xBottom, Log10ScaleEngine())
        self.plot.setAxisScaleDraw(BasePlot.yLeft, Log10ScaleDraw())
        self.plot.setAxisScaleDraw(BasePlot.xBottom, Log10ScaleDraw())
        
        layout.addWidget(self.plot)

        self.manager = PlotManager(self.plot)
        self.manager.add_plot(self.plot)

        self.select_tool = self.manager.add_tool(SelectTool)
        self.select_tool.activate()
        self.rect_tool = self.manager.add_tool(AnnotatedRectangleTool, handle_final_shape_cb=self.handle_final_shape, switch_to_default_tool=True)

        self.plot.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.plot.addAction("Add Rectangle", lambda: self.rect_tool.activate())

    def handle_final_shape(self, shape):
        print(f"Final shape: {shape}")
        self.plot.unselect_all()
        self.plot.select_item(shape)

    def add_shape(self, tool):
        self.manager.get_tool(tool).activate()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Plot()
    window.show()
    sys.exit(app.exec())