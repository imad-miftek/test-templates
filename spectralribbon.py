"""
@package spectralribbon
This file is the spectral ribbon plot object for the Player, it is responsible for handling all of 
the controls and data for the spectral ribbon plot. The spectral ribbon plot is a plot that shows
the intensity of a wavelength over a range of channels.

Classes:
    RotatedTickAxis: This class is a custom axis item that allows for the x-axis to be rotated.
    SpectralRibbon: This class is the spectral ribbon plot object that is used to display the spectral
"""
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog, QGraphicsTransform
import pyqtgraph as pg
from multiprocessing.pool import ThreadPool as pool
import math

import numpy as np
from ui.color_maps import colormaps
from data import attributes
from data import algorithms

class RotatedTickAxis(pg.AxisItem):
    """
    @class RotatedTickAxis
    This class is a custom axis item that allows for the x-axis to be rotated. This class is used in
    the SpectralRibbon class to allow for the x-axis to be rotated to display the wavelengths in a
    more readable format.
    """
    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        """
        @brief Draw the axis, ticks, and text
        
        @details This method is called to draw the axis, ticks, and text for the axis. This method 
                is called by the pyqtgraph library to draw the axis, ticks, and text for the axis.
        
        @param p: (QPainter) The painter object that is used to draw the axis
        @param axisSpec: (tuple) The axis specification that is used to draw the axis
        @param tickSpecs: (list) The list of tick specifications that are used to draw the ticks
        @param textSpecs: (list) The list of text specifications that are used to draw the text
        
        @return void
        """
        p.setRenderHint(p.RenderHint.Antialiasing, False)
        p.setRenderHint(p.RenderHint.TextAntialiasing, True)

        ## draw long line along axis
        pen, p1, p2 = axisSpec
        p.setPen(pen)
        p.drawLine(p1, p2)
        p.translate(0.5,0)  ## resolves some damn pixel ambiguity
        ## draw ticks
        for pen, p1, p2 in tickSpecs:
            p.setPen(pen)
            p.drawLine(p1, p2)
        ## Draw all text
        if self.style['tickFont'] is not None:
            p.setFont(self.style['tickFont'])
        p.setPen(self.textPen())
        p.setPen(self.textPen())

        for rect, flags, text in textSpecs:
            # this is the important part
            p.save()
            p.translate(rect.center())
            p.rotate(45)
            p.translate(-rect.center())
            p.drawText(rect, int(flags), text)
            # restoring the painter is *required*!!!
            p.restore()

    @property
    def nudge(self):
        """
        @brief Get the nudge value
        
        @details This method is called to get the nudge value for the axis. The nudge value is used 
                to nudge the axis to the left or right to make sure the axis label is not clipped.
                
        @return The nudge value
        """
        if not hasattr(self, "_nudge"):
            self._nudge = 5
        return self._nudge

    @nudge.setter
    def nudge(self, nudge):
        """
        @brief Set the nudge value
        
        @details This method is called to set the nudge value for the axis. The nudge value is used
                to nudge the axis to the left or right to make sure the axis label is not clipped.
                
        @param nudge: (int) The nudge value to set
        
        @return void
        """
        self._nudge = nudge
        s = self.size()
        # call resizeEvent indirectly
        self.resize(s + QtCore.QSizeF(1, 1))
        self.resize(s)

    def resizeEvent(self, ev=None):
        """
        @brief Resize the axis
        
        @details This method is called to resize the axis. This method is called by the pyqtgraph
                library to resize the axis. This method is used to set the position of the label
                based on the orientation of the axis.
                
        @param ev: (QResizeEvent) The resize event that is used to resize the axis
        
        @return void
        """
        ## Set the position of the label
        nudge = self.nudge
        br = self.label.boundingRect()
        p = QtCore.QPointF(0, 0)
        if self.orientation == "left":
            p.setY(int(self.size().height() / 2 + br.width() / 2))
            p.setX(-nudge)
        elif self.orientation == "right":
            p.setY(int(self.size().height() / 2 + br.width() / 2))
            p.setX(int(self.size().width() - br.height() + nudge))
        elif self.orientation == "top":
            p.setY(-nudge)
            p.setX(int(self.size().width() / 2.0 - br.width() / 2.0))
        elif self.orientation == "bottom":
            p.setX(int(self.size().width() / 2.0 - br.width() / 2.0))
            p.setY(int(self.size().height() - br.height() + nudge))
        self.label.setPos(p)
        self.picture = None

    def setHeight(self, h=None):
        """
        @brief Set the height of the axis
        
        @details This method is called to set the height of the axis. The height of the axis is
                reserved for ticks and tick labels. The height of the axis label is automatically
                added. If the height is None, then the value will be determined automatically based
                on the size of the tick text.
                
        @param h: (int) The height of the axis to set
        
        @return void
        """
        self.fixedHeight = h
        self._updateHeight()

    def _updateHeight(self):
        """
        @brief Update the height of the axis
        
        @details This method is called to update the height of the axis. This method is called by 
                the setHeight method to update the height of the axis. This method is used to set
                the height of the axis based on the size of the tick text.
                
        @return void
        """
        if not self.isVisible():
            h = 0
        else:
            if self.fixedHeight is None:
                if not self.style['showValues']:
                    h = 0
                elif self.style['autoExpandTextSpace']:
                    h = self.textHeight+20
                else:
                    h = self.style['tickTextHeight']
                h += self.style['tickTextOffset'][1] if self.style['showValues'] else 0
                h += max(0, self.style['tickLength'])
                if self.label.isVisible():
                    h += self.label.boundingRect().height() * 0.8
            else:
                h = self.fixedHeight

        self.setMaximumHeight(h)
        self.setMinimumHeight(h)
        self.picture = None


class SpectralRibbon(QtWidgets.QWidget):
    """
    @class SpectralRibbon
    Class for the spectral ribbon plot object that is used to display the spectral ribbon plot. The
    spectral ribbon plot is a plot that shows the intensity of a wavelength over a range of 
    channels.
    """
    
    def __init__(self, index, config, db_list_software, db_list_hardware, worksheet):
        """
        @brief Constructor for the SpectralRibbon object
        
        @details This method is the constructor for the SpectralRibbon object. This method is called
                to initialize the SpectralRibbon object. This method is used to setup the layout and
                view for the spectral ribbon plot.
                
        @param index: (int) The index of the plot
        @param config: (Config) The configuration object for the Player
        @param db_list_software: (dict) The database list for the software data
        @param db_list_hardware: (dict) The database list for the hardware data
        @param worksheet: (Worksheet) The worksheet object for the Player
        
        @var num_bins: (int) The number of bins for the spectral ribbon plot
        @var H: (list) The list of histograms for the spectral ribbon plot
        @var initialH: (list) The initial list of histograms for the spectral ribbon plot
        @var num_bins_list: (list) The list of number of bins for the spectral ribbon plot
        @var data_set: (list) The list of data for the spectral ribbon plot
        @var worksheet: (Worksheet) The worksheet object for the Player
        @var db_coll: (list) The list of database collections for the spectral ribbon plot
        @var db: (int) The database index for the spectral ribbon plot
        @var features_software: (list) The list of features for the software data
        @var features_hardware: (list) The list of features for the hardware data
        @var cur_feat: (str) The current feature for the spectral ribbon plot
        @var descrim_wavelengths: (list) The list of wavelengths to not show on the spectral ribbon plot
        @var cur_gate: (Gate) The current gate for the spectral ribbon plot
        @var eventNum: (int) The event number for the spectral ribbon plot
        @var totalEvents: (int) The total number of events for the spectral ribbon plot
        @var xmax: (int) The maximum x value for the spectral ribbon plot
        @var ylow: (int) The lower y value for the spectral ribbon plot
        @var ymax: (int) The upper y value for the spectral ribbon plot
        @var log: (bool) The log scaling flag for the spectral ribbon plot
        @var config: (Config) The configuration object for the Player
        @var num_channels: (int) The number of channels for the spectral ribbon plot
        @var uuid: (str) The UUID for the spectral ribbon plot
        @var num_roi: (int) The number of regions of interest for the spectral ribbon plot
        @var gate_applied: (Gate) The gate applied for the spectral ribbon plot
        @var events: (list) The list of events for the spectral ribbon plot
        @var pool: (ThreadPool) The thread pool for the spectral ribbon plot
        @var ribbon: (PlotWidget) The plot widget for the spectral ribbon plot
        @var draw: (bool) The draw flag for the spectral ribbon plot
        
        @return void
        """
        super().__init__()
        self.num_bins = 1024
        self.H = 0
        self.initialH = 0
        self.num_bins_list = attributes.num_bins_list
        self.data_set = []
        self.worksheet = worksheet
        self.db_coll = [db_list_software, db_list_hardware]
        self.db = 0

        self.features_software = [x for x in list(db_list_software.keys()) if 'time' not in x]
        self.features_hardware = [x for x in list(db_list_hardware.keys()) if 'time' not in x]
        self.cur_feat = self.features_software[1]
        self.descrim_wavelengths = []

        self.cur_gate = None
        self.eventNum = 0
        self.totalEvents = 0
        self.xmax = 0
        self.ylow = attributes.graph_lower_bound + 1000
        self.ymax = attributes.graph_upper_bound
        self.log = True
        self.config = config
        self.num_channels = len(config.adc_non_alpha) if "_adc_" in self.cur_feat else len(config.photon_non_alpha)
        self.uuid = None
        self.num_roi = None # This is not actually used for spectralribbon.

        self.gate_applied = None
        self.events = []

        self.pool = pool(self.num_channels)
        
        self.ribbon = None
        self.draw = False

        self.view_setup()
        self.image_setup()
        
        #-------- Right Click Menu --------#
        self.ribbon.setMenuEnabled(False)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.setup_menu)
        #-------- Right Click Menu --------#

    def config_init(self):
        """
        @brief Initialize the configuration for the spectral ribbon plot
        
        @details This method is called to initialize the configuration for the spectral ribbon plot.
                This method is used to setup the configuration for a new spectral ribbon plot.
                
        @return list of the configuration values for the spectral ribbon plot
        """
        return [None, 'spectral', self.num_bins, self.cur_feat, 0,
                0, 0, 0, 0, 0, 0, 1, 0]
        
    def load_plot_config(self, dict_values):
        """
        @brief Load the configuration for the spectral ribbon plot
        
        @details This method is called to load the configuration for the spectral ribbon plot. This
                method is used to load the configuration for a new spectral ribbon plot.
                
        @param dict_values: (dict) The dictionary of values to load for the spectral ribbon plot
        
        @return void
        """
        self.uuid = dict_values[0]
        self.num_bins = dict_values[2]
        if 'laser' not in dict_values[3]:
            dict_values[3] = 'laser1_' + dict_values[3]
        if 'hw' in dict_values[3]:
            self.cur_feat = self.features_hardware[self.features_hardware.index(dict_values[3])]
        else:
            self.cur_feat = self.features_software[self.features_software.index(dict_values[3])]
        self.log = True if dict_values[11] == 1 else False
        self.update_graph_limits()

    def remove_gate(self):
        """
        @brief Remove the gate for the spectral ribbon plot
        
        @details This method exists on the off chance something goes wrong and the remove_gate 
                method is called for the spectral ribbon plot. This will prevent an error from
                occurring.
        
        @return void
        """
        print("This should not happen to the spectral ribbon plot")

    def image_setup(self):
        """
        @brief Setup the layout for the spectral ribbon plot
        
        @details This method is called to setup the layout for the spectral ribbon plot. This method
                is used to setup the layout for the spectral ribbon plot.
                
        @return void
        """
        overalllayout = QVBoxLayout(self)
        overalllayout.addWidget(self.ribbon)
        overalllayout.setContentsMargins(20,10,10,40)
        self.setLayout(overalllayout)

    
    def view_setup(self):
        """
        @brief Setup the plot view for the spectral ribbon plot
        
        @details This method is called to setup the plot view for the spectral ribbon plot. This 
                method is used to setup the plot view for the spectral ribbon plot.
                
        @return void
        """
        rotated_tick_axis = RotatedTickAxis(orientation='bottom')

        self.ribbon = pg.PlotWidget(title="Spectral Ribbon", axisItems={'bottom':rotated_tick_axis})
        self.ribbon.showGrid(True, True)
        self.ribbon.setContentsMargins(50,50,50,50)

        color = colormaps().turbo[::-1]
        cmap = pg.ColorMap(pos=None, color=color)

        self.H = []
        for i in range(self.num_channels):
            hist, self.edges = np.histogram(self.data_set, bins=self.num_bins)
            self.H.append(hist)
        self.H = np.rot90(self.H)
        self.initialH = self.H
        
        self.ribbonplot = pg.ImageItem(self.H, levels=(0,1))
        font = QtGui.QFont("Times", 12)
        font2 = QtGui.QFont("Times", 12)
        self.ribbonplot.setColorMap(cmap)
        self.ribbonplot.setLevels((0, len(color)))
        
        self.ribbon.getAxis('bottom').setPen('black')
        self.ribbon.getAxis('bottom').setTextPen('black')
        self.ribbon.getAxis('bottom').setTickFont(font)
        self.ribbon.getAxis('bottom').label.setFont(font2)
        

        self.ribbon.getAxis('left').label.setFont(font2)
        self.ribbon.getAxis('left').setTickFont(font)
        self.ribbon.getAxis('left').setPen('black')
        self.ribbon.getAxis('left').setTextPen('black')

        self.x_axis = self.ribbon.getAxis('bottom')
        self.x_axis.setStyle(tickTextOffset=15)
        self.update_graph_labels()
        self.update_scaling(None)
        
        self.ribbon.addItem(self.ribbonplot)
        self.ribbon.setBackground('w')
        self.ribbon.setLabel('bottom', "Wavelengths")
        self.ribbon.setLabel('left', f"Intensity, {self.cur_feat}")
        
        self.ribbon.setMouseEnabled(x=True, y=True)

    def update_scaling(self, flag):
        """
        @brief Update the scaling for the spectral ribbon plot
        
        @details This method is called to update the scaling for the spectral ribbon plot. This 
                method is used to update the scaling for the spectral ribbon plot.
                
        @param flag: (int) The flag to determine if the scaling should be updated
        
        @return void
        """
        if flag:
            self.log = False if self.log == True else True
        self.ribbon.setLogMode(False, self.log)
        transform = QtGui.QTransform()
        ylow = self.ylow
        yhigh = self.ymax
        if self.log == True:
            yhigh = math.ceil(math.log10(self.ymax))
            if self.ylow > 0:
                ylow = math.floor(math.log10(self.ylow))
            self.ribbon.getAxis('left').autoSIPrefixScale = 1
            self.ribbon.getAxis('left').autoSIPrefix = False
            self.ribbon.getAxis('left').setLabel(text=f"Intensity, {self.cur_feat}")
        else:
            self.ribbon.getAxis('left').autoSIPrefix = True
        
        transform.scale(1, (yhigh-ylow)/self.num_bins)
        transform.translate(0, ylow/((yhigh-ylow)/self.num_bins))
        self.ribbonplot.setTransform(transform)
        
        self.ribbon.setLimits(xMin=0, xMax=(self.num_channels+1), yMin=ylow, yMax=yhigh)
        self.ribbon.setXRange(0,(self.num_channels+1), padding=0)
        self.ribbon.setYRange(ylow,yhigh, padding=0)
        
        self.redraw = True
        
        if flag:
            self.worksheet.updatePlotConfig.emit(self.uuid, [self.num_bins, self.cur_feat, 
                                                         0, 0, 0, 0, self.ylow, self.ymax, 0, int(self.log), 0])

    def update_graph_labels(self):
        """
        @brief Update the graph labels for the spectral ribbon plot
        
        @details This method is called to update the graph labels for the spectral ribbon plot. This
                method is used to update the graph labels for the spectral ribbon plot.
                
        @return void
        """
        new_ticks = []
        num = 0
        non_alpha = self.config.adc_non_alpha if '_adc_' in self.cur_feat else self.config.photon_non_alpha
        for n in non_alpha:
            if n not in self.descrim_wavelengths:
                num += 1
                new_ticks.append((num, f'{n}'))

        self.num_channels = num
        self.x_axis.setTicks([new_ticks])

        self.update_graph_limits()

    def remove_channels(self, checked, name):
        """
        @brief Remove channels from the spectral ribbon plot
        
        @details This method is called to remove channels from the spectral ribbon plot. This method
                is used to remove channels from the spectral ribbon plot. This method will update
                the graph labels for the spectral ribbon plot.
                
        @param checked: (bool) The flag to determine if the channel should be removed
        @param name: (str) The name of the channel to remove
        
        @return void
        """
        if checked == True:
            self.descrim_wavelengths.append(name)
        else:
            self.descrim_wavelengths.remove(name)
        
        self.update_graph_labels()
    
    def setup_menu(self):
        """
        @brief Setup the right click menu for the spectral ribbon plot
        
        @details This method is called to setup the right click menu for the spectral ribbon plot.
                The menu allows the user to remove the plot, change the scaling values, and apply
                a gate to the plot.
        
        @return void
        """
        self.menu = QtWidgets.QMenu(self)
        remove_plot = self.menu.addAction("Remove Plot")
        log_scaling = self.menu.addAction("Log Scaling")
        log_scaling.setCheckable(True)
        if self.log == True:
            log_scaling.setChecked(True)

        chg_val = self.menu.addAction("Change Scaling Values")

        apply_gate = self.menu.addMenu("Apply Gate")
        gateopt = []
        names = []
        for i in self.config.gates:
            names.append(i.name)
            gateopt.append(apply_gate.addAction(f"{i.name}"))
            gateopt[-1].setCheckable(True)
            if i.identifier == self.gate_applied:
                gateopt[-1].setChecked(True)

        for i in range(len(gateopt)):
            gateopt[i].setCheckable(True)
            gateopt[i].triggered.connect(lambda checked=gateopt[i].isChecked(), index=i: self.apply_gate(checked, names[index]))

        hideMenu = self.menu.addMenu('Hide Channel(s)')
        hiddenChannels = []
        non_alpha = self.config.adc_non_alpha if '_adc_' in self.cur_feat else self.config.photon_non_alpha
        for i in range(len(non_alpha)):
            hiddenChannels.append(hideMenu.addAction(f"{non_alpha[i]}"))
            hiddenChannels[i].setCheckable(True)
            if self.config.adc_non_alpha[i] in self.descrim_wavelengths:
                hiddenChannels[i].setChecked(True)

        for i in range(len(hiddenChannels)):
            hiddenChannels[i].triggered.connect(lambda checked=hiddenChannels[i].isChecked(), index=i: self.remove_channels(checked, self.config.photon_non_alpha[index]))

        remove_plot.triggered.connect(lambda: self.worksheet.removePlot.emit(self))
        log_scaling.triggered.connect(lambda: self.update_scaling(1))
        chg_val.triggered.connect(self.change_values_popout)

        self.menu.popup(QtGui.QCursor.pos())
    
    def change_values_popout(self):
        """
        @brief Change the scaling values for the spectral ribbon plot
        
        @details This method is called to change the scaling values for the spectral ribbon plot. 
                This method is used to change the scaling values for the spectral ribbon plot. This
                method will open a popout window to allow the user to change the scaling values for
                the spectral ribbon plot.
                
        @return void
        """
        dlg = QDialog()
        dlg.setWindowTitle("Scaling")
        
        verticalLayout1 = QVBoxLayout()
        verticalLayout2 = QVBoxLayout()
        horizontalLayout = QHBoxLayout()
        
        yrangelowLabel = QtWidgets.QLabel("y-range low")
        yrangelow = QtWidgets.QDoubleSpinBox()
        yrangelow.setKeyboardTracking(False)
        yrangelow.setDecimals(0)
        yrangelow.setRange(attributes.graph_lower_bound, attributes.graph_upper_bound - 1)
        yrangelow.setSingleStep(1)
        yrangelow.setValue(self.ylow)

        yrangeLabel = QtWidgets.QLabel("y-range upper")
        yrange = QtWidgets.QDoubleSpinBox()
        yrange.setKeyboardTracking(False)
        yrange.setDecimals(0)
        yrange.setRange(attributes.graph_lower_bound + 1, attributes.graph_upper_bound)
        yrange.setSingleStep(1)
        yrange.setValue(self.ymax)
        
        binsLabel = QtWidgets.QLabel("bins")
        numbins = QtWidgets.QComboBox()
        for i in self.num_bins_list:
            numbins.addItem(f'{i}')
        numbins.setCurrentIndex(self.num_bins_list.index(self.num_bins))

        databaseOpt = QtWidgets.QLabel("Database")
        opt = QtWidgets.QComboBox()
        opt.addItem("Software")
        opt.addItem("Hardware")
        if 'hw' in self.cur_feat:
            opt.setCurrentIndex(1)
        else:
            opt.setCurrentIndex(0)

        featureLabel = QtWidgets.QLabel('Features')
        feature = QtWidgets.QComboBox()
        for i in self.features_software:
            feature.addItem(f'{i}')
        if 'hw' in self.cur_feat:
            feature.setCurrentIndex(self.features_hardware.index(self.cur_feat))
        else:
            feature.setCurrentIndex(self.features_software.index(self.cur_feat))
        
        verticalLayout1.addWidget(yrangelowLabel)
        verticalLayout1.addWidget(yrangeLabel)
        verticalLayout1.addWidget(binsLabel)
        verticalLayout1.addWidget(databaseOpt)
        verticalLayout1.addWidget(featureLabel)

        verticalLayout2.addWidget(yrangelow)
        verticalLayout2.addWidget(yrange)
        verticalLayout2.addWidget(numbins)
        verticalLayout2.addWidget(opt)
        verticalLayout2.addWidget(feature)

        horizontalLayout.addLayout(verticalLayout1)
        horizontalLayout.addLayout(verticalLayout2)

        dlg.setLayout(horizontalLayout)
        
        yrangelow.valueChanged.connect(lambda: self.change_axis_scales("low", yrangelow.value()))
        yrange.valueChanged.connect(lambda: self.change_axis_scales("max", yrange.value()))
        numbins.currentIndexChanged.connect(lambda: self.num_bins_changed(self.num_bins_list[numbins.currentIndex()]))
        opt.currentIndexChanged.connect(lambda: self.update_feature(feature.currentIndex(), opt.currentIndex()))
        feature.currentIndexChanged.connect(lambda: self.update_feature(feature.currentIndex(), opt.currentIndex()))
        
        dlg.exec()
        self.worksheet.updatePlotConfig.emit(self.uuid, [self.num_bins, self.cur_feat, 
                                                         0, 0, 0, 0, self.ylow, self.ymax, 0, int(self.log), 0])

    def change_axis_scales(self, flag, value):
        """
        @brief Change the axis scales for the spectral ribbon plot
        
        @details This method is called to change the axis scales for the spectral ribbon plot. This 
                method will update the graph limits for the spectral ribbon plot.
                
        @param flag: (str) The flag to determine if the axis scale should be changed
        @param value: (int) The value to change the axis scale to
        
        @return void
        """
        if flag == "low":
            self.ylow = value
        elif flag == "max":
            self.ymax = value
        else:
            print("This is an error to look into. Spectral Ribbon plot")
        self.update_graph_limits()
    
    def num_bins_changed(self, binsIn):
        """
        @brief Change the number of bins for the spectral ribbon plot
        
        @details This method is called to change the number of bins for the spectral ribbon plot. 
                This method will update the transform and the levels for the ribbon plot. This
                method is called any time the user would like to change the number of bins used in
                graphing, currently set on the right click menu.
                
        @param binsIn: (int) The number of bins to change to
        
        @return void
        """
        color = colormaps().turbo[::-1]
        self.num_bins = binsIn
        self.ribbonplot.setLevels((0, len(color)))
        self.redraw = True
        
    def apply_gate(self, checked, gate_name):
        """
        @brief Apply a gate to the spectral ribbon plot
        
        @details This method is called to apply a gate to the spectral ribbon plot. This method will
                apply a gate to the spectral ribbon plot which will act as a discriminator for the
                plot.
                
        @param checked: (bool) The flag to determine if the gate should be applied
        @param gate_name: (str) The name of the gate to apply
        
        @return void
        """
        if checked:
            for i in self.config.gates:
                if i.name == gate_name:
                    self.gate_applied = i.identifier
        else:
            self.gate_applied = None
            self.events = []
        self.redraw = True
    
    def live_update_plot(self):
        """
        @brief Live update the spectral ribbon plot
        
        @details: This method is called to update the spectral ribbon plot with the most recent data 
                from the database.
                
        @return void
        """
        self.H = []

        if (self.db_coll[self.db][f'{self.cur_feat}'].count_documents({}) == 0) and not self.redraw:
            return
        
        if self.gate_applied:
            for i in self.config.gates:
                if i.identifier == self.gate_applied:
                    self.events = i.events
            
        non_alpha = self.config.adc_non_alpha if '_adc_' in self.cur_feat else self.config.photon_non_alpha
        non_alpha_values = self.config.adc_non_alpha_values if '_adc_' in self.cur_feat else self.config.photon_non_alpha_values

        indexes = [non_alpha.index(w) for w in self.descrim_wavelengths]
        x_indexes = [int(i) for i in non_alpha_values if i not in indexes]

        if self.log == True:
            yl = self.ylow
            if self.ylow > 0:
                yl = math.log10(self.ylow)
            binsLog = np.logspace(start=yl, stop=math.log10(self.ymax), num=self.num_bins, base=10.0)
            binsLog[0] = attributes.graph_lower_bound
            binsLog[self.num_bins-1] = attributes.graph_upper_bound
        else:
            binsLog = np.linspace(start=self.ylow, stop=self.ymax, num=self.num_bins)
            binsLog[0] = attributes.graph_lower_bound
            binsLog[self.num_bins-1] = attributes.graph_upper_bound

        try:
            if not self.pool.apply(self.hist_calc, args=(x_indexes, binsLog)):
                return
        except Exception as e:
            print(f"Error, Spectral Ribbon plot: {e}")
            
        self.H = np.array(self.H)

    def update_image(self):
        """
        @brief Update the spectral ribbon plot image
        
        @details This method is called to update the spectral ribbon plot image with the most recent
                drawing from live_update_plot.
                
        @return void
        """
        if self.draw == False:
            return
        try:
            if self.db_coll[self.db][f'{self.cur_feat}'].count_documents({}) > 0:
                self.ribbonplot.updateImage(self.H)
            else:
                self.ribbonplot.clear()
            self.draw = False
        except Exception as e:
            return
        
    def clear_plots(self):
        """
        @brief Clear the spectral ribbon plot
        
        @details This method is called to clear the spectral ribbon plot. This method is used to
                clear the spectral ribbon plot.
                
        @return void
        """
        self.ribbonplot.clear()
        self.H = self.initialH
        
    def hist_calc(self, x_indexes, binsLog):
        """
        @brief Calculate the histogram for the spectral ribbon plot
        
        @details This method is called to calculate the histogram for the spectral ribbon plot. This
                method is called with a thread pool to calculate the histogram for the spectral
                ribbon plot.
                
        @param ct: (list) The list of channels to calculate the histogram for
        @param binsLog: (list) The list of bins to calculate the histogram for
        
        @return bool: The flag to determine if the histogram was calculated successfully
        """
        x = []
        try:
            for idx in x_indexes:
                temp = self.db_coll[self.db][f'{self.cur_feat}'].aggregate([
                    {'$sort' : {'event' : 1}},
                    {'$group':
                        {'_id':'null', 
                            f'ch{idx}':{'$push':f"$ch {idx}"}}}
                    ])

                for q in temp:
                    if self.gate_applied:
                        if self.events:
                            temp = list(q.values())[1]
                            temp = [temp[i] for i in self.events] 
                            x.append(np.array(temp, dtype='f'))
                        else:
                            x.append([])
                    else:
                        x.append(np.array(list(q.values())[1], dtype='f'))
                
                if not x:
                    self.redraw = False
                    return False
                
                self.totalEvents = len(x[0])

            reverse_lookup = {}
            names = self.config.adc_names if '_adc_' in self.cur_feat else self.config.photon_names
            for k, v in names.items():
                if not isinstance(v, list):  # Skip 'nc' which has list value
                    reverse_lookup[v] = k

            wavelengths = [reverse_lookup[channel] for channel in x_indexes]

            # Find first alphanumeric wavelength
            transition_idx = next((idx for idx, w in enumerate(wavelengths) if w[0].isalpha()), None)

            for i in range(len(x)):
                hist, self.edges = np.histogram(x[i], bins=binsLog)

                # Insert gap at exact transition point
                if transition_idx is not None and i == transition_idx:
                    empty_hist = np.zeros_like(hist)
                    self.H.append(empty_hist)

                self.H.append(hist)
            self.draw = True
        except Exception as e:
            print(f"Spectral plot error: {e}")
            return False
        
        self.redraw = False
        return True

    def gate_update(self):
        """
        @brief Update the gate for the spectral ribbon plot
        
        @details  This method keeps the pass because there are no gates to be placed on a spectral 
                ribbon plot but it silences the error if it is removed. The error is due to cycling 
                through all plots and calling gate_update, a pass is quicker than having a 
                conditional for every plot in the  list of plots for the worksheet.
                
        @return void
        """
        pass

    def update_graph_limits(self):
        """
        @brief Update the graph limits for the spectral ribbon plot
        
        @details This method is called to update the graph limits for the spectral ribbon plot. This
                method is used to update the graph limits for the spectral ribbon plot.
                
        @return void
        """
        self.update_scaling(None)

    def update_feature(self, feat, db):
        """
        @brief Update the feature for the spectral ribbon plot
        
        @details This method is called to update the feature for the spectral ribbon plot.
        
        @param feat: (int) The feature to update to
        @param db: (int) The database to update to
        
        @return void
        """
        self.db = db
        if db == 0:
            self.cur_feat = self.features_software[feat]
        else:
            self.cur_feat = self.features_hardware[feat]

        self.update_scaling(None)
        self.worksheet.updatePlotConfig.emit(self.uuid, [self.num_bins, self.cur_feat, 
                                                         0, 0, 0, 0, self.ylow, self.ymax, 0, int(self.log), 0])