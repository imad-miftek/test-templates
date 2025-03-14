import sys
import platform
import ctypes
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QRect, Qt, QCoreApplication, QSize, QSizeF
from PySide6.QtGui import QScreen, QGuiApplication, QFont

class MonitorInfoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor Information Test")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont("Consolas", 10))
        layout.addWidget(self.text_display)
        
        # Create refresh button
        refresh_button = QPushButton("Refresh Information")
        refresh_button.clicked.connect(self.gather_display_info)
        layout.addWidget(refresh_button)
        
        self.setCentralWidget(central_widget)
        
        # Gather and display information
        self.gather_display_info()
    
    def gather_display_info(self):
        """Gather and display all monitor/screen information"""
        info = []
        
        # System information
        info.append("=== SYSTEM INFORMATION ===")
        info.append(f"OS: {platform.system()} {platform.release()} {platform.version()}")
        info.append(f"Python: {sys.version}")
        info.append(f"Qt Version: {QCoreApplication.instance().applicationVersion()}")
        info.append("")
        
        # Primary screen information
        primary_screen = QGuiApplication.primaryScreen()
        info.append("=== PRIMARY SCREEN ===")
        info.append(f"Name: {primary_screen.name()}")
        info.append(f"Manufacturer: {primary_screen.manufacturer()}")
        info.append(f"Model: {primary_screen.model()}")
        info.append(f"Serial Number: {primary_screen.serialNumber()}")
        info.append("")
        
        # Screen geometry and resolution
        geometry = primary_screen.geometry()
        info.append("=== SCREEN GEOMETRY ===")
        info.append(f"Width: {geometry.width()} pixels")
        info.append(f"Height: {geometry.height()} pixels")
        info.append(f"Resolution: {geometry.width()}x{geometry.height()} pixels")
        info.append("")
        
        # Physical size and aspect ratio
        physical_size = primary_screen.physicalSize()
        info.append("=== PHYSICAL SIZE ===")
        info.append(f"Width: {physical_size.width() / 10:.2f} cm ({physical_size.width() / 25.4:.2f} inches)")
        info.append(f"Height: {physical_size.height() / 10:.2f} cm ({physical_size.height() / 25.4:.2f} inches)")
        diagonal_inches = ((physical_size.width()**2 + physical_size.height()**2)**0.5) / 25.4
        info.append(f"Diagonal: {diagonal_inches:.2f} inches")
        aspect_ratio = geometry.width() / geometry.height()
        info.append(f"Aspect Ratio: {aspect_ratio:.3f}:1")
        info.append("")
        
        # DPI information
        info.append("=== DPI INFORMATION ===")
        logical_dpi_x = primary_screen.logicalDotsPerInchX()
        logical_dpi_y = primary_screen.logicalDotsPerInchY()
        physical_dpi_x = primary_screen.physicalDotsPerInchX()
        physical_dpi_y = primary_screen.physicalDotsPerInchY()
        
        info.append(f"Logical DPI: {logical_dpi_x:.2f}x{logical_dpi_y:.2f}")
        info.append(f"Physical DPI: {physical_dpi_x:.2f}x{physical_dpi_y:.2f}")
        info.append("")
        
        # Scaling factor
        info.append("=== SCALING INFORMATION ===")
        scale_factor_x = logical_dpi_x / 96.0
        scale_factor_y = logical_dpi_y / 96.0
        info.append(f"Scale Factor: {scale_factor_x:.2f}x{scale_factor_y:.2f}")
        device_pixel_ratio = primary_screen.devicePixelRatio()
        info.append(f"Device Pixel Ratio: {device_pixel_ratio:.2f}")
        
        # Windows-specific DPI awareness information
        if platform.system() == "Windows":
            info.append("")
            info.append("=== WINDOWS DPI AWARENESS ===")
            try:
                # Get DPI awareness context
                awareness = ctypes.windll.user32.GetAwarenessFromDpiAwarenessContext(
                    ctypes.windll.user32.GetThreadDpiAwarenessContext())
                
                awareness_types = {
                    0: "DPI_AWARENESS_UNAWARE",
                    1: "DPI_AWARENESS_SYSTEM_AWARE",
                    2: "DPI_AWARENESS_PER_MONITOR_AWARE"
                }
                awareness_str = awareness_types.get(awareness, f"Unknown ({awareness})")
                info.append(f"DPI Awareness: {awareness_str}")
                
                # Get system DPI
                user32 = ctypes.windll.user32
                system_dpi_x = user32.GetDpiForSystem()
                info.append(f"System DPI: {system_dpi_x}")
                
                # Try to get DPI for the monitor
                try:
                    monitor = user32.MonitorFromWindow(0, 0)  # MONITOR_DEFAULTTOPRIMARY
                    dpi_type = 0  # MDT_EFFECTIVE_DPI
                    dpiX = ctypes.c_uint()
                    dpiY = ctypes.c_uint()
                    res = ctypes.windll.shcore.GetDpiForMonitor(monitor, dpi_type, ctypes.byref(dpiX), ctypes.byref(dpiY))
                    if res == 0:  # S_OK
                        info.append(f"Monitor Effective DPI: {dpiX.value}x{dpiY.value}")
                except Exception as e:
                    info.append(f"Error getting monitor DPI: {str(e)}")
            except Exception as e:
                info.append(f"Error getting Windows DPI information: {str(e)}")
        
        # Available screens
        info.append("")
        info.append("=== ALL AVAILABLE SCREENS ===")
        screens = QGuiApplication.screens()
        for i, screen in enumerate(screens):
            info.append(f"Screen {i}:")
            info.append(f"  Name: {screen.name()}")
            geometry = screen.geometry()
            info.append(f"  Resolution: {geometry.width()}x{geometry.height()}")
            info.append(f"  DPI: {screen.logicalDotsPerInchX()}x{screen.logicalDotsPerInchY()}")
            info.append(f"  Scale Factor: {screen.logicalDotsPerInchX() / 96.0:.2f}x")
            info.append(f"  Device Pixel Ratio: {screen.devicePixelRatio():.2f}")
            info.append("")
        
        # Advanced display capabilities
        info.append("=== DISPLAY CAPABILITIES ===")
        info.append(f"Depth: {primary_screen.depth()} bits")
        refresh_rate = primary_screen.refreshRate()
        info.append(f"Refresh Rate: {refresh_rate:.2f} Hz")
        
        # Virtual desktop information
        virtual_geometry = QGuiApplication.primaryScreen().virtualGeometry()
        info.append("")
        info.append("=== VIRTUAL DESKTOP ===")
        info.append(f"Width: {virtual_geometry.width()} pixels")
        info.append(f"Height: {virtual_geometry.height()} pixels")
        info.append(f"Total Resolution: {virtual_geometry.width()}x{virtual_geometry.height()} pixels")
        
        # Display window client area information
        info.append("")
        info.append("=== WINDOW INFORMATION ===")
        info.append(f"Window size: {self.width()}x{self.height()} pixels")
        info.append(f"Window position: {self.x()},{self.y()}")
        client_area = self.rect()
        info.append(f"Client area: {client_area.width()}x{client_area.height()} pixels")
        
        # Display the information
        self.text_display.setPlainText("\n".join(info))
        
        # Save to file
        with open("monitor_info.txt", "w") as f:
            f.write("\n".join(info))
        print("Information saved to monitor_info.txt")


def test_font_rendering():
    """Create a separate test for font rendering at different sizes"""
    app = QApplication.instance() or QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Font Rendering Test")
    window.setMinimumSize(800, 600)
    
    text_display = QTextEdit()
    window.setCentralWidget(text_display)
    
    html_content = ["<html><body>"]
    html_content.append("<h1>Font Rendering Test</h1>")
    html_content.append("<p>This test shows how fonts render at different sizes and with different DPI settings.</p>")
    
    # Test different font sizes
    for size in [8, 9, 10, 11, 12, 14, 16, 18, 20, 24]:
        html_content.append(f"<h3>Font Size: {size}pt</h3>")
        
        # Regular font
        html_content.append(f"<p style='font-size:{size}pt;'>Regular text at {size}pt - The quick brown fox jumps over the lazy dog.</p>")
        
        # Bold font
        html_content.append(f"<p style='font-size:{size}pt; font-weight:bold;'>Bold text at {size}pt - The quick brown fox jumps over the lazy dog.</p>")
        
        # Monospace font
        html_content.append(f"<p style='font-size:{size}pt; font-family:monospace;'>Monospace text at {size}pt - The quick brown fox jumps over the lazy dog.</p>")
        
    html_content.append("</body></html>")
    
    text_display.setHtml("\n".join(html_content))
    window.show()
    
    return window


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create and show the main info window
    main_window = MonitorInfoWindow()
    main_window.show()
    
    # Optional: Create font rendering test window
    font_window = test_font_rendering()
    
    sys.exit(app.exec())