#!/usr/bin/env python3
"""
Working chart example using PySide6 and QtCharts directly in Python (not QML).
This will verify that the basic chart functionality works.
"""

import sys
import math
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSlider, QLabel
from PySide6.QtCharts import QChart, QChartView, QSplineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import QTimer, QDateTime, Qt
from PySide6.QtGui import QPen, QColor, QPainter

from data_generator import FluidicsDataGenerator


class FluidicsChartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluidics Monitor - Python Chart")
        self.setGeometry(100, 100, 1000, 600)
        
        # Set dark background
        self.setStyleSheet("background-color: #000000; color: #ffffff;")
        
        # Create the chart with sexy styling
        self.chart = QChart()
        self.chart.setTitle("Fluidics Monitoring")
        self.chart.setTitleBrush(QColor("#ffffff"))
        self.chart.setBackgroundBrush(QColor("#000000"))
        
        # Style the legend
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chart.legend().setLabelColor(QColor("#ffffff"))
        self.chart.legend().setBackgroundVisible(False)  # Transparent legend background
        
        # Create spline series for sexy smooth curves
        self.sample_series = QSplineSeries()
        self.sample_series.setName("Sample Flow (μl/min)")
        self.sample_series.setPen(QPen(QColor("#ffffff"), 3))  # Slightly thicker for splines
        
        self.sheath_series = QSplineSeries()
        self.sheath_series.setName("Sheath Flow (ml/min x20)")
        self.sheath_series.setPen(QPen(QColor("#2E2EFE"), 3))
        
        self.velocity_series = QSplineSeries()
        self.velocity_series.setName("Sample Velocity (mm/s)")
        self.velocity_series.setPen(QPen(QColor("#2EFEF7"), 3))
        
        # Add series to chart
        self.chart.addSeries(self.sample_series)
        self.chart.addSeries(self.sheath_series)
        self.chart.addSeries(self.velocity_series)
        
        # Create clean axes without grid lines
        self.x_axis = QValueAxis()
        self.x_axis.setTitleText("Time (seconds)")
        self.x_axis.setRange(0, 60)
        self.x_axis.setLabelFormat("%.0f")
        self.x_axis.setGridLineVisible(False)  # Remove grid for clean look
        self.x_axis.setLabelsColor(QColor("#ffffff"))
        self.x_axis.setTitleBrush(QColor("#ffffff"))
        
        self.y_axis_left = QValueAxis()
        self.y_axis_left.setTitleText("Flow (μl/min)")
        self.y_axis_left.setRange(0, 120)
        self.y_axis_left.setGridLineVisible(False)  # Remove grid for clean look
        self.y_axis_left.setLabelsColor(QColor("#ffffff"))
        self.y_axis_left.setTitleBrush(QColor("#ffffff"))
        
        self.y_axis_right = QValueAxis()
        self.y_axis_right.setTitleText("Velocity (mm/s)")
        self.y_axis_right.setRange(0, 6000)
        self.y_axis_right.setGridLineVisible(False)  # Remove grid for clean look
        self.y_axis_right.setLabelsColor(QColor("#2EFEF7"))
        self.y_axis_right.setTitleBrush(QColor("#2EFEF7"))
        
        # Attach axes
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.y_axis_left, Qt.AlignmentFlag.AlignLeft)
        self.chart.addAxis(self.y_axis_right, Qt.AlignmentFlag.AlignRight)
        
        self.sample_series.attachAxis(self.x_axis)
        self.sample_series.attachAxis(self.y_axis_left)
        
        self.sheath_series.attachAxis(self.x_axis)
        self.sheath_series.attachAxis(self.y_axis_left)
        
        self.velocity_series.attachAxis(self.x_axis)
        self.velocity_series.attachAxis(self.y_axis_right)
        
        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create controls
        self.controls_widget = QWidget()
        self.controls_layout = QHBoxLayout(self.controls_widget)
        
        # Data control buttons
        self.start_button = QPushButton("Start Data")
        self.stop_button = QPushButton("Stop Data")
        self.clear_button = QPushButton("Clear Data")
        
        # Curve width control
        self.width_label = QLabel("Curve Width:")
        self.width_label.setStyleSheet("color: white; font-weight: bold;")
        
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setMinimum(1)
        self.width_slider.setMaximum(8)
        self.width_slider.setValue(3)  # Default width
        self.width_slider.setFixedWidth(150)
        self.width_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #333333;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #2EFEF7;
                border: 2px solid #2EFEF7;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #ffffff;
            }
        """)
        
        self.width_value_label = QLabel("3px")
        self.width_value_label.setStyleSheet("color: #2EFEF7; font-weight: bold; min-width: 30px;")
        
        # Add widgets to layout
        self.controls_layout.addWidget(self.start_button)
        self.controls_layout.addWidget(self.stop_button)
        self.controls_layout.addWidget(self.clear_button)
        self.controls_layout.addWidget(QLabel("   "))  # Spacer
        self.controls_layout.addWidget(self.width_label)
        self.controls_layout.addWidget(self.width_slider)
        self.controls_layout.addWidget(self.width_value_label)
        
        # Create main widget
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(self.chart_view)
        main_layout.addWidget(self.controls_widget)
        
        self.setCentralWidget(main_widget)
        
        # Data generator and timer
        self.data_generator = FluidicsDataGenerator()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chart)
        self.timer.setInterval(100)  # 100ms
        
        self.time_counter = 0
        self.max_points = 600  # 1 minute of data
        
        # Connect buttons and controls
        self.start_button.clicked.connect(self.start_data)
        self.stop_button.clicked.connect(self.stop_data)
        self.clear_button.clicked.connect(self.clear_data)
        self.width_slider.valueChanged.connect(self.update_curve_width)
        
        print("Python chart window created successfully!")
    
    def start_data(self):
        """Start real-time data generation."""
        print("Starting data generation...")
        self.data_generator.start_data_generation()
        self.timer.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
    def stop_data(self):
        """Stop data generation."""
        print("Stopping data generation...")
        self.data_generator.stop_data_generation()
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
    def clear_data(self):
        """Clear all data from charts."""
        print("Clearing data...")
        self.sample_series.clear()
        self.sheath_series.clear()
        self.velocity_series.clear()
        self.time_counter = 0
        
    def update_chart(self):
        """Update chart with new data."""
        data = self.data_generator.get_latest_data()
        
        # Add new data points
        self.sample_series.append(self.time_counter, data['sample_flow'])
        self.sheath_series.append(self.time_counter, data['sheath_flow'] * 20)
        self.velocity_series.append(self.time_counter, data['sample_velocity'])
        
        # Remove old points if too many
        while self.sample_series.count() > self.max_points:
            self.sample_series.removePoints(0, 1)
        while self.sheath_series.count() > self.max_points:
            self.sheath_series.removePoints(0, 1)
        while self.velocity_series.count() > self.max_points:
            self.velocity_series.removePoints(0, 1)
            
        self.time_counter += 0.1
        
        # Update x-axis range for rolling window
        if self.time_counter > 60:
            self.x_axis.setRange(self.time_counter - 60, self.time_counter)
            
    def update_curve_width(self, value):
        """Update the width of all curve lines."""
        # Update the width value label
        self.width_value_label.setText(f"{value}px")
        
        # Create new pens with the updated width
        sample_pen = QPen(QColor("#ffffff"), value)
        sheath_pen = QPen(QColor("#2E2EFE"), value)
        velocity_pen = QPen(QColor("#2EFEF7"), value)
        
        # Apply the new pens to the series
        self.sample_series.setPen(sample_pen)
        self.sheath_series.setPen(sheath_pen)
        self.velocity_series.setPen(velocity_pen)


def main():
    app = QApplication(sys.argv)
    
    window = FluidicsChartWindow()
    window.show()
    
    print("Chart window should be visible now!")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main()) 