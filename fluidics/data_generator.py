"""
Data generator for fluidics sheath sample monitoring.
Generates realistic test data for sample flow, sheath flow, and sample velocity.
"""

import sys
import time
import math
import random
from datetime import datetime
from PySide6.QtCore import QObject, QTimer, Signal, Slot
from PySide6.QtQml import qmlRegisterType


class FluidicsDataGenerator(QObject):
    """
    Generates realistic test data for fluidics monitoring.
    
    This class simulates real-world fluidics data with:
    - Sample flow: 0-100 μl/min with occasional spikes
    - Sheath flow: 1-6 ml/min with gradual variations
    - Sample velocity: 1000-5000 mm/s with flow-dependent changes
    """
    
    # Signals for QML integration
    dataReady = Signal(float, float, float)  # sample_flow, sheath_flow, sample_velocity
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Data generation parameters
        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_data_point)
        self.timer.setInterval(100)  # 100ms intervals
        
        # Current state variables
        self.time_elapsed = 0
        self.base_sample_flow = 50.0  # μl/min
        self.base_sheath_flow = 3.5   # ml/min  
        self.base_sample_velocity = 3000.0  # mm/s
        
        # Variation parameters
        self.sample_flow_noise = 5.0
        self.sheath_flow_noise = 0.3
        self.velocity_noise = 200.0
        
        # Current data values
        self.current_sample_flow = self.base_sample_flow
        self.current_sheath_flow = self.base_sheath_flow
        self.current_sample_velocity = self.base_sample_velocity
        
        # Data history for moving averages
        self.max_history = 1000
        self.sample_flow_history = []
        self.sheath_flow_history = []
        self.velocity_history = []
        
    @Slot()
    def start_data_generation(self):
        """Start generating data every 100ms."""
        print("Starting data generation...")
        self.time_elapsed = 0
        self.timer.start()
        
    @Slot()
    def stop_data_generation(self):
        """Stop data generation."""
        print("Stopping data generation...")
        self.timer.stop()
        
    @Slot(result='QVariant')
    def get_latest_data(self):
        """Return the latest data values as a dictionary."""
        return {
            'sample_flow': self.current_sample_flow,
            'sheath_flow': self.current_sheath_flow,
            'sample_velocity': self.current_sample_velocity,
            'timestamp': datetime.now().isoformat()
        }
        
    def generate_data_point(self):
        """Generate a single data point with realistic variations."""
        self.time_elapsed += 0.1  # 100ms = 0.1 seconds
        
        # Generate sample flow with occasional spikes and gradual drift
        sample_trend = 10 * math.sin(self.time_elapsed * 0.05)  # Slow oscillation
        sample_spike = 0
        if random.random() < 0.02:  # 2% chance of spike
            sample_spike = random.uniform(15, 30)
        sample_noise = random.gauss(0, self.sample_flow_noise)
        
        self.current_sample_flow = max(0, 
            self.base_sample_flow + sample_trend + sample_spike + sample_noise)
        
        # Generate sheath flow with gradual variations
        sheath_trend = 0.8 * math.sin(self.time_elapsed * 0.03)  # Slower oscillation
        sheath_noise = random.gauss(0, self.sheath_flow_noise)
        
        self.current_sheath_flow = max(0.5, 
            self.base_sheath_flow + sheath_trend + sheath_noise)
        
        # Generate sample velocity correlated with flows
        flow_influence = (self.current_sample_flow / self.base_sample_flow) * 500
        sheath_influence = (self.current_sheath_flow / self.base_sheath_flow) * 300
        velocity_trend = 400 * math.sin(self.time_elapsed * 0.04)
        velocity_noise = random.gauss(0, self.velocity_noise)
        
        self.current_sample_velocity = max(500,
            self.base_sample_velocity + flow_influence + sheath_influence + 
            velocity_trend + velocity_noise)
        
        # Store history
        self.sample_flow_history.append(self.current_sample_flow)
        self.sheath_flow_history.append(self.current_sheath_flow)
        self.velocity_history.append(self.current_sample_velocity)
        
        # Limit history size
        if len(self.sample_flow_history) > self.max_history:
            self.sample_flow_history.pop(0)
            self.sheath_flow_history.pop(0)
            self.velocity_history.pop(0)
        
        # Emit signal for QML
        self.dataReady.emit(
            self.current_sample_flow,
            self.current_sheath_flow, 
            self.current_sample_velocity
        )
        
        # Print data occasionally for debugging
        if int(self.time_elapsed * 10) % 50 == 0:  # Every 5 seconds
            print(f"Time: {self.time_elapsed:.1f}s - "
                  f"Sample: {self.current_sample_flow:.1f} μl/min, "
                  f"Sheath: {self.current_sheath_flow:.2f} ml/min, "
                  f"Velocity: {self.current_sample_velocity:.0f} mm/s")
    
    def get_statistics(self):
        """Return statistical information about the generated data."""
        if not self.sample_flow_history:
            return {}
            
        return {
            'sample_flow': {
                'mean': sum(self.sample_flow_history) / len(self.sample_flow_history),
                'min': min(self.sample_flow_history),
                'max': max(self.sample_flow_history),
                'current': self.current_sample_flow
            },
            'sheath_flow': {
                'mean': sum(self.sheath_flow_history) / len(self.sheath_flow_history),
                'min': min(self.sheath_flow_history),
                'max': max(self.sheath_flow_history),
                'current': self.current_sheath_flow
            },
            'sample_velocity': {
                'mean': sum(self.velocity_history) / len(self.velocity_history),
                'min': min(self.velocity_history),
                'max': max(self.velocity_history),
                'current': self.current_sample_velocity
            }
        }


def register_qml_types():
    """Register QML types for use in QML files."""
    qmlRegisterType(FluidicsDataGenerator, "FluidicsData", 1, 0, "DataGenerator")


if __name__ == "__main__":
    # Test the data generator
    from PySide6.QtCore import QCoreApplication
    
    app = QCoreApplication(sys.argv)
    
    generator = FluidicsDataGenerator()
    
    def print_data(sample, sheath, velocity):
        print(f"Sample: {sample:.1f} μl/min, "
              f"Sheath: {sheath:.2f} ml/min, "
              f"Velocity: {velocity:.0f} mm/s")
    
    generator.dataReady.connect(print_data)
    generator.start_data_generation()
    
    # Run for 10 seconds
    QTimer.singleShot(10000, app.quit)
    
    sys.exit(app.exec()) 