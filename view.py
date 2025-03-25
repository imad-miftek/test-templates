from PySide6.QtWidgets import (QWidget, QVBoxLayout, QMenu, QDialog, QVBoxLayout, QSpinBox, QLabel, 
                               QScrollArea, QDialogButtonBox, QApplication)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, QObject, QEvent, QTimer, Signal, Slot

#---------------LOCAL IMPORTS-------------------#
from pyqtgraph.graphicsItems.ROI import *

#-----------------------------------------------#

import pyqtgraph as pg
import numpy as np
import torch
import uuid
from qwt import QwtText
from loguru import logger
from typing import Optional

class PseudocolorPlotSettings(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # self.colormap = colormaps[0]
        # self.color_scale = 'linear'
        # self.x_scale = 'linear'
        # self.y_scale = 'linear'
        # self.x_feature = 0
        # self.y_feature = 1

    def config(self):
        return vars(self)
    
class PseudocolorPlotEventFilter(QObject):
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.RightButton:
                # Get the PseudocolorPlot instance
                plot = self.parent()
                if not isinstance(plot, PseudocolorPlot):
                    return False

                # Show menu at cursor position
                plot.context_menu.exec(event.globalPos())
                
                # Accept the event to prevent propagation
                event.accept()
                return True
                
        return False  # Let other events pass through

class PseudocolorPlot(QWidget):
    # NOTE (Imad):
    # Important Implementation Note:
    # ----------------------------
    # When using BaseImageItem (or its derivatives like Histogram2DItem), the destination 
    # rectangle coordinates must be integers. This is a requirement of the underlying 
    # plotting system and is handled by BaseImageItem.draw_image():
    
    # ```python
    # dst_rect = tuple(map(int, dst_rect))
    # ```
    
    # Without this integer casting, you'll encounter the error:
    # 'Invalid destination rectangle (expected tuple of 4 integers)'

    s_handle_update = Signal(torch.Tensor)
    gate_added = Signal(object, str)
    gate_removed = Signal(object, str)

    def __init__(self, config=None, parent=None, **kwargs):
        super().__init__(parent)
        self.id = str(uuid.uuid4()).replace('-', '')
        self.name = f'pcolor_{self.id}'
        self.table_name = f'pcolor_{self.id}_cache'

        # Set the property as a bypass proxy
        self.setProperty("bypass-proxy", True)

        self.roi_dict = {}
        self.roi_labels = []

        # Add layout to hold the plot
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # # Create and install event filter
        self.event_filter = PseudocolorPlotEventFilter(self)
        self.installEventFilter(self.event_filter)

        self.parent = parent
        self.config = config
        self.plot_config = kwargs.get('plot_config', None)
        # NOTE: The two variables below are strictly for testing purposes.
        self.scene = kwargs.get('scene', None)
        self.view = kwargs.get('view', None)

        self.selected_x_channel = 0
        self.selected_y_channel = 1
        self.logx = 0
        self.logy = 0
        self.x_gain = 1
        self.y_gain = 1
        self.x_threshold = 0
        self.y_threshold = 0
        self.channel_indices = [] # NOTE: This should only matter for oscilloscope!
        
        self.stats_table = 0

        # NOTE (Imad): Backend to be set up here.
        #self.plot_image = QImage()
        # self.backend.image_ready.connect(self.on_image_ready)
        # def on_image_ready(self, plot_image):
        #     self.plot_image.setPixmap(plot_image)

        # Get settings
        self.settings = PseudocolorPlotSettings(parent=self)

        # input system

        # build the plot
        self.setup_plot()
        self.connect_signals()
        self.setup_context_menu()

        # update timer
        self.update_timer = QTimer()
        # self.update_timer.timeout.connect(lambda: print('update timer timeout'))
        self.update_timer.start(500) #NOTE: This is a placeholder value. Make it a controllable setting.

    def connect_signals(self):
        try:
            pass

        except Exception as err:
            logger.error(f"Error connecting signals: {err}")
            raise

    def apply_plot_config(self):
        """Apply settings from plot_config to the histogram plot"""
        if not self.plot_config:
            return
        
        try:
            # Apply settings that go to self.settings
            if 'identifier' in self.plot_config:
                self.settings.identifier = self.plot_config.get('identifier')
                self.id = self.settings.identifier

            if 'num_bins' in self.plot_config:
                self.settings.num_bins = self.plot_config.get('num_bins')
            
            if 'display_feature' in self.plot_config:
                self.settings.display_feature = self.plot_config.get('display_feature')
                
            if 'x_min_range' in self.plot_config:
                self.settings.x_min_range = self.plot_config.get('x_min_range')
                
            if 'x_max_range' in self.plot_config:
                self.settings.x_max_range = self.plot_config.get('x_max_range')
                
            if 'y_min_range' in self.plot_config:
                self.settings.y_min_range = self.plot_config.get('y_min_range')
                
            if 'y_max_range' in self.plot_config:
                self.settings.y_max_range = self.plot_config.get('y_max_range')
            
            # Apply settings that go directly to self
            if 'x_feature' in self.plot_config:
                self.selected_x_channel = int(self.plot_config.get('x_feature'))
                
            if 'y_feature' in self.plot_config:
                self.selected_y_channel = int(self.plot_config.get('y_feature'))
                
            if 'logx' in self.plot_config:
                self.logx = self.plot_config.get('logx')
                
            if 'logy' in self.plot_config:
                self.logy = self.plot_config.get('logy')
                
            if 'stats_table' in self.plot_config:
                self.stats_table = int(self.plot_config.get('stats_table'))
                
            if 'x_gain' in self.plot_config:
                self.x_gain = self.plot_config.get('x_gain')
                
            if 'y_gain' in self.plot_config:
                self.y_gain = self.plot_config.get('y_gain')
                
            if 'x_threshold' in self.plot_config:
                self.x_threshold = float(self.plot_config.get('x_threshold'))
                
            if 'y_threshold' in self.plot_config:
                self.y_threshold = self.plot_config.get('y_threshold')
                
            if 'current_channels' in self.plot_config:
                # Convert string representation of list to actual list
                channels_str = self.plot_config.get('current_channels')
                self.channel_indices = [int(x.strip()) for x in channels_str]
            
            # After applying all settings, update the axes
            self.update_axes()
            
            logger.info(f"Applied plot configuration to {self.name}")
        
        except Exception as e:
            logger.error(f"Error applying plot configuration: {e}")

    def set_input_type(self, input_type):

        pass

    def clear_signals(self):
        try:
            if self.isSignalConnected(self.s_handle_update):
                self.s_handle_update.disconnect(self.backend.s_handle_update)

        except Exception as err:
            logger.error(f"Error clearing signals: {err}")
            raise

    def setup_plot(self):
        # Create a layout

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(True, True)
        self.plot_widget.setBackground('w')

        self.plot_widget.setStyleSheet("""
            PlotWidget {
                background-color: white;
                border: 2px solid black;
            }
        """)
        self.update_axes()

        # Initialize context menu
        self.context_menu = QMenu(self)

        # Add plot to layout
        self.layout.addWidget(self.plot_widget)

    @Slot()
    def on_plot_ready(self):
        self.backend.update_plot.connect(self.plot_widget.replot, Qt.QueuedConnection)

    def update_axes(self):
        """Update the plot's axes based on the selected channels"""
        # Cache axis text objects if not already created
        if not hasattr(self, '_axis_texts'):
            # Set up fonts and colors once
            label_font = QFont('Segoe UI', 10, QFont.Bold)
            
            # Create and cache QwtText objects
            self._axis_texts = {
                str(i): QwtText.make(text=f"Channel {i} Data", font=label_font)
                for i in range(52)
            }
            
        # Set x-axis title with cached text
        self.plot_widget.setLabel('bottom', self._axis_texts[str(self.selected_x_channel)])
        # Set y-axis title with cached text
        self.plot_widget.setLabel('left', self._axis_texts[str(self.selected_y_channel)])

    def setup_context_menu(self):
        """Setup the custom context menu"""        
        # Add waveform type submenu
        self.select_features_action = self.context_menu.addAction("Select Scaling Features")
        self.select_features_action.triggered.connect(self.open_features_dialog)
        
        # Set context menu policy
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        log_scaling = self.context_menu.addMenu("Log Scaling")
        xlog = log_scaling.addAction("Log Scaling on x-axis")
        xlog.setCheckable(True)
        if self.logx == 1:
            xlog.setChecked(True)
        ylog = log_scaling.addAction("Log Scaling on y-axis")
        ylog.setCheckable(True)
        if self.logy == 1:
            ylog.setChecked(True)

        # Add the ability to set gates
        gate_action = self.context_menu.addMenu("Add Gate")
        # TODO: It would be most ideal for us to be able to draw the gate immediately after clicking
        #       an option, rather than the gate being premade for us.
        rectangle_gate = gate_action.addAction("Rectangle")
        ellipse_gate = gate_action.addAction("Ellipse")
        # polygon_gate = gate_action.addAction("Polygon")
        rectangle_gate.triggered.connect(lambda: self.add_gate('rectangle'))
        ellipse_gate.triggered.connect(lambda: self.add_gate('ellipse'))
        # polygon_gate.triggered.connect(self.open_polygon_gate_dialog)

    def show_context_menu(self, pos):
        """Show the context menu at the cursor position"""
        
        # Show menu at cursor position
        self.context_menu.exec(self.mapToGlobal(pos))

    def apply_feature_changes(self, x_val, y_val, dialog):
        self.selected_x_channel = x_val
        self.selected_y_channel = y_val
        self.update_axes()
        self.backend.update_plot()
        dialog.accept()

    def open_features_dialog(self):
        """Open a dialog to select channels"""
        if not self.config:
            # Create dialog without parent
            dialog = QDialog(None)  # Change from self to None
            dialog.setWindowTitle("No Data Loaded")
            dialog.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)  # Keep dialog on top
            layout = QVBoxLayout(dialog)
            label = QLabel("Please load a data file first.")
            layout.addWidget(label)
            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(dialog.accept)
            layout.addWidget(button_box)
            dialog.exec()
            return
            
        # Create main dialog without parent
        dialog = QDialog(None)  # Change from self to None
        dialog.setWindowTitle("Select Features")
        dialog.resize(300, 400)
        dialog.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)  # Keep dialog on top
        
        # Rest of the code remains the same...
        
        # Create main layout for dialog
        main_layout = QVBoxLayout(dialog)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create widget to hold selection controls
        selection_widget = QWidget()
        selection_layout = QVBoxLayout(selection_widget)

        # X feature selection
        x_label = QLabel("X Channel:")
        selection_layout.addWidget(x_label)
        x_spin = QSpinBox()
        x_spin.setRange(0, 51)  # 52 channels (0-51)
        x_spin.setValue(self.selected_x_channel)
        selection_layout.addWidget(x_spin)
        
        # Y feature selection  
        y_label = QLabel("Y Channel:")
        selection_layout.addWidget(y_label)
        y_spin = QSpinBox()
        y_spin.setRange(0, 51)  # 52 channels (0-51)
        y_spin.setValue(self.selected_y_channel)
        selection_layout.addWidget(y_spin)

        scroll_area.setWidget(selection_widget)
        main_layout.addWidget(scroll_area)
        
        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        main_layout.addWidget(button_box)
        
        if dialog.exec():
            # Update selected channels
            self.selected_x_channel = x_spin.value()
            self.selected_y_channel = y_spin.value()
            self.update_axes()
            self.backend.s_settings_update.emit(self.selected_x_channel, self.selected_y_channel)

    def handle_gate_selection(self, gate_id, selected):
        """Handle a gate being selected"""
        # Only proceed if we're selecting a gate, not deselecting
        if selected:
            # Deselect all other gates without causing recursion
            for id, gate in self.roi_dict.items():
                # TODO: Make sure the gates have these properties!
                if id != gate_id and gate.is_selected:
                    # Use direct state change to avoid circular signals
                    gate.is_selected = False
                    gate.update_selection_appearance()
                    # Don't emit signals; we'll do that after all state changes
                    
            # Now emit signals for gates that actually changed state
            for id, gate in self.roi_dict.items():
                if id != gate_id:
                    gate.gate_selected.emit(False)

    # TODO: Consider adding the hidden_menu() function from granite2
                
    def remove_gate(self):
        """
        @brief Remove a gate from the pseudocolor plot
        
        @details This method is called to remove a gate object from the scatter graph, with the 
                removal all subsequent items tagged to that gate are also removed here. The stats
                table is also updated to reflect the removal of the gate. If the last gate is 
                removed the stats table is hidden.
                
        @return void
        """
        if len(self.roi_dict) == 0:
            return
        list(self.roi_dict.values())[-1].remove()
        self.roi_dict.pop(list(self.roi.keys())[-1])
        # TODO: This base_config part is in relation to the configuration that we would open when
        #       starting the program. It serves the same role as the config used to automatically
        #       load plots on startup. As such, it will need to be integrated later.
        # self.base_config.gate_count -= 1

    # TODO: Maybe change the name of this function to add_new_gate()
    #       See how much of this code can be moved to the worksheet.py file.
    def add_gate(self, shape=None, values: Optional[dict] = None):
        """Add a gate to the pseudocolor plot"""
        try:
            # Get the ViewBox explicitly
            view_box = self.plot_widget.getViewBox()
            if not view_box:
                logger.error("Cannot add gate: No ViewBox found")
                return
            
            # Calculate position based on current view
            view_range = view_box.viewRange()
            x_center = (view_range[0][0] + view_range[0][1]) / 2
            y_center = (view_range[1][0] + view_range[1][1]) / 2
            width = (view_range[0][1] - view_range[0][0]) * 0.2  # 20% of view width
            height = (view_range[1][1] - view_range[1][0]) * 0.2  # 20% of view height
            
            # Create ROI based on shape type
            if shape == 'ellipse':
                roi = pg.EllipseROI(
                    pos=[x_center - width/2, y_center - height/2],
                    size=[width, height],
                    pen=pg.mkPen('r', width=2)
                )
            else:  # Default to rectangle
                roi = pg.RectROI(
                    pos=[x_center - width/2, y_center - height/2],
                    size=[width, height],
                    pen=pg.mkPen('r', width=2)
                )
            
            # Add directly to the ViewBox
            view_box.addItem(roi)
            
            # Store reference in dictionary
            gate_id = str(uuid.uuid4())
            self.roi_dict[gate_id] = roi
            
            return roi
        except Exception as e:
            logger.error(f"Error creating gate: {e}")
            import traceback
            traceback.print_exc()
            return None



if __name__ == '__main__':
    # pass
    app = QApplication([])
    plot = PseudocolorPlot()
    plot.show()
    app.exec()
