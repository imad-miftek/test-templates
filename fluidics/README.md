# Fluidics Monitoring System - QML Implementation

A real-time fluidics monitoring application built with QML and Qt Charts, featuring a DateTimeAxis and multiple y-axes for comprehensive flow analysis.

## Overview

This application is a QML-based translation of the original PyQt6/pyqtgraph fluidics monitoring system using PySide6 for optimal QML integration. It provides real-time visualization of three key fluidics parameters:

- **Sample Flow** (μl/min) - White line, left axis
- **Sheath Flow** (ml/min) - Blue line, left axis (scaled for visibility)
- **Sample Velocity** (mm/s) - Cyan line, right axis

## Features

- ✅ **Real-time plotting** with 100ms data intervals
- ✅ **DateTimeAxis** showing current time in seconds
- ✅ **Multiple y-axes** (2 left, 1 right) as requested
- ✅ **Interactive controls** for start/stop/clear data
- ✅ **Realistic test data** with correlations and noise
- ✅ **Rolling time window** (1-minute display)
- ✅ **Dark theme** matching original design
- ✅ **Comprehensive test suite**

## Architecture

```
fluidics/
├── SheathSampleChart.qml    # Main QML chart interface
├── data_generator.py        # Python backend for data generation
├── main.py                  # Application entry point
├── test_suite.py           # Comprehensive testing
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

1. **Install dependencies:**
   ```bash
   cd fluidics
   pip install -r requirements.txt
   ```

2. **Verify PySide6 installation:**
   ```bash
   python -c "from PySide6 import QtCharts; print('PySide6 Charts available')"
   ```

## Usage

### Running the Application

```bash
cd fluidics
python main.py
```

The application will open a window with:
- A black background chart matching the original design
- Control buttons at the bottom (Start Data, Stop Data, Clear Data)
- Real-time legend showing all three data series

### Controls

- **Start Data**: Begin generating data every 100ms
- **Stop Data**: Pause data generation
- **Clear Data**: Remove all data points from the chart

### Data Characteristics

The test data generator produces realistic fluidics data with:

- **Sample Flow**: 50 ± 15 μl/min base with occasional spikes
- **Sheath Flow**: 3.5 ± 0.8 ml/min with gradual variations
- **Sample Velocity**: 3000 ± 500 mm/s correlated with flow rates

## Testing

### Run the Test Suite

```bash
cd fluidics
python test_suite.py
```

The test suite includes:
- Unit tests for data generation
- Signal emission validation
- Statistical property verification
- Real-time manual testing option

### Test Data Generator Only

```bash
cd fluidics
python data_generator.py
```

This runs a 10-second console test showing data generation.

## Technical Details

### QML Implementation

The QML chart uses Qt Charts components:
- `ChartView` as the main container
- `DateTimeAxis` for time-based x-axis
- `ValueAxis` for y-axes with different ranges
- `LineSeries` for each data stream
- Real-time data updates via Qt signals

### Multi-Axis Challenge

Qt Charts doesn't natively support multiple y-axes on the same side. The implementation uses:
- Primary left axis for Sample Flow (0-120 μl/min)
- Scaled Sheath Flow data (×20) to share the left axis
- Dedicated right axis for Sample Velocity (0-6100 mm/s)

### Data Generation

The Python backend generates correlated, realistic data:
- Sinusoidal trends with different frequencies
- Gaussian noise for realism
- Occasional spikes in sample flow
- Flow-velocity correlations
- Proper signal emission for QML integration

## Comparison with Original

| Feature | Original PyQt6/pyqtgraph | New QML Implementation |
|---------|-------------------------|------------------------|
| Framework | PyQt6 + pyqtgraph | PySide6 + Qt Charts QML |
| Axes | 3 distinct y-axes | 2 left (1 scaled) + 1 right |
| X-axis | Numeric | DateTimeAxis with real time |
| Theme | Dark background | Matching dark theme |
| Performance | Custom ViewBox | Native Qt Charts |
| Controls | Keyboard shortcuts | Interactive buttons |
| Data rate | Variable | Fixed 100ms intervals |

## Troubleshooting

### Common Issues

1. **"PySide6 not found"**
   ```bash
   pip install PySide6
   ```

2. **QML file not loading**
   - Ensure you're running from the `fluidics` directory
   - Check that `SheathSampleChart.qml` exists

3. **No data appearing**
   - Click "Start Data" button
   - Check console for error messages

4. **Performance issues**
   - Data is limited to 600 points (1 minute at 100ms)
   - Automatic cleanup prevents memory issues

### Debug Mode

Add debug output by modifying `data_generator.py`:
```python
# Uncomment the print statement in generate_data_point()
print(f"Generated: {self.current_sample_flow:.1f}, {self.current_sheath_flow:.2f}, {self.current_sample_velocity:.0f}")
```

## Future Enhancements

Potential improvements for production use:
- [ ] True multiple left y-axes (custom QML component)
- [ ] Data export functionality
- [ ] Real hardware integration
- [ ] Alarm thresholds and alerts
- [ ] Historical data storage
- [ ] Configuration file support
- [ ] Multi-language support

## License

This implementation demonstrates QML-based real-time plotting techniques and can be adapted for various monitoring applications.

## References

- [Qt Charts QML Types](https://doc.qt.io/qt-6/qtcharts-qmlmodule.html)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [QML Language Reference](https://doc.qt.io/qt-6/qmlreference.html) 