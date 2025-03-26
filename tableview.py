import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTreeView, QVBoxLayout, 
                              QWidget, QStyledItemDelegate, QHeaderView, QTabWidget)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush, QFont
from PySide6.QtCore import Qt, QSize

class StatisticsDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def paint(self, painter, option, index):
        """Custom painting for numeric values in the statistics column"""
        if index.column() == 1 and index.data() is not None:
            try:
                # Handle compact display of X/Y pairs
                if " | " in index.data():
                    x_value, y_value = index.data().split(" | ")
                    x_float = float(x_value.split(": ")[1])
                    y_float = float(y_value.split(": ")[1])
                    
                    # Format as a compact pair
                    text = f"X: {x_float:.2f} | Y: {y_float:.2f}"
                    self.initStyleOption(option, index)
                    option.text = text
                    super().paint(painter, option, index)
                    return
                else:
                    # Handle regular numeric values
                    value = float(index.data())
                    if value > 0:
                        option.palette.setBrush(option.palette.text, QBrush(QColor(0, 128, 0)))
                    elif value < 0:
                        option.palette.setBrush(option.palette.text, QBrush(QColor(192, 0, 0)))
                    
                    text = f"{value:,.2f}"
                    self.initStyleOption(option, index)
                    option.text = text
                    super().paint(painter, option, index)
                    return
            except (ValueError, TypeError, IndexError):
                pass
        
        super().paint(painter, option, index)
    
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        return QSize(size.width(), size.height() + 2)  # Reduced padding for compactness

class StatisticsTreeView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gate Statistics")
        self.resize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create a tab widget to further save space
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create the All Gates tab
        all_gates_widget = QWidget()
        all_gates_layout = QVBoxLayout(all_gates_widget)
        
        # Create tree view for all gates
        self.tree_view = QTreeView()
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        
        # Set row height to be smaller
        self.tree_view.setStyleSheet("QTreeView::item { padding: 1px; }")
        
        # Set custom delegate for better display
        self.tree_view.setItemDelegate(StatisticsDelegate())
        
        # Create model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Gate/Metric', 'Value'])
        self.tree_view.setModel(self.model)
        
        all_gates_layout.addWidget(self.tree_view)
        self.tab_widget.addTab(all_gates_widget, "All Gates")
        
        # Populate with sample data
        self.populate_compact_tree()
        
        # Set column widths
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.Stretch)
        
    def populate_compact_tree(self):
        """Populate the tree with more compact statistical data"""
        # Sample gates data
        gates = {
            'Gate 1': {
                'Position': {
                    'Mean': {'X': 42.5, 'Y': 38.7},
                    'Median': {'X': 41.2, 'Y': 37.9}
                },
                'Dispersion': {
                    'Standard Deviation': {'X': 15.3, 'Y': 12.1},
                    'Variance': {'X': 234.1, 'Y': 146.4}
                },
                'Summary': {
                    'Count': 156,
                    'Percentage': 25.3
                }
            },
            'Gate 2': {
                'Position': {
                    'Mean': {'X': 75.2, 'Y': 82.3},
                    'Median': {'X': 74.8, 'Y': 81.5}
                },
                'Dispersion': {
                    'Standard Deviation': {'X': 22.4, 'Y': 18.7},
                    'Variance': {'X': 501.8, 'Y': 349.7}
                },
                'Summary': {
                    'Count': 243,
                    'Percentage': 39.5
                }
            },
            'Gate 3': {
                'Position': {
                    'Mean': {'X': 31.7, 'Y': 45.2},
                    'Median': {'X': 30.9, 'Y': 44.7}
                },
                'Dispersion': {
                    'Standard Deviation': {'X': 12.8, 'Y': 14.5},
                    'Variance': {'X': 163.8, 'Y': 210.3}
                },
                'Summary': {
                    'Count': 217,
                    'Percentage': 35.2
                }
            }
        }
        
        # Add each gate
        for gate_name, categories in gates.items():
            # Create gate item with compact summary
            summary = categories.get('Summary', {})
            count = summary.get('Count', 0)
            percentage = summary.get('Percentage', 0)
            mean_x = categories.get('Position', {}).get('Mean', {}).get('X', 0)
            mean_y = categories.get('Position', {}).get('Mean', {}).get('Y', 0)
            
            gate_item = QStandardItem(f"{gate_name}")
            gate_item.setFont(QFont("Arial", 9, QFont.Bold))
            
            # Add summary value that's visible when collapsed
            summary_value = QStandardItem(f"Count: {count} | {percentage:.1f}% | Mean X/Y: {mean_x:.1f}/{mean_y:.1f}")
            
            self.model.appendRow([gate_item, summary_value])
            
            # Add categories
            for category_name, stats in categories.items():
                if category_name == 'Summary':
                    continue  # Skip summary as we already displayed it
                    
                category_item = QStandardItem(category_name)
                category_item.setFont(QFont("Arial", 8, QFont.Bold))
                category_value = QStandardItem("")
                gate_item.appendRow([category_item, category_value])
                
                # Add stats with compact X/Y representation
                for stat_name, values in stats.items():
                    stat_item = QStandardItem(stat_name)
                    
                    if isinstance(values, dict) and 'X' in values and 'Y' in values:
                        # Compact X/Y pair display
                        stat_value = QStandardItem(f"X: {values['X']} | Y: {values['Y']}")
                    else:
                        stat_value = QStandardItem(str(values))
                        
                    category_item.appendRow([stat_item, stat_value])
        
        # Add individual gate tabs for detailed view
        for gate_name in gates.keys():
            self.add_gate_tab(gate_name, gates[gate_name])
            
    def add_gate_tab(self, gate_name, gate_data):
        """Add a dedicated tab for a single gate with more detailed view"""
        gate_widget = QWidget()
        gate_layout = QVBoxLayout(gate_widget)
        
        gate_tree = QTreeView()
        gate_tree.setAlternatingRowColors(True)
        gate_tree.setItemDelegate(StatisticsDelegate())
        
        gate_model = QStandardItemModel()
        gate_model.setHorizontalHeaderLabels(['Metric', 'Value'])
        gate_tree.setModel(gate_model)
        
        gate_layout.addWidget(gate_tree)
        self.tab_widget.addTab(gate_widget, gate_name)
        
        # Add detailed statistics for this gate
        for category_name, stats in gate_data.items():
            category_item = QStandardItem(category_name)
            category_item.setFont(QFont("Arial", 9, QFont.Bold))
            category_value = QStandardItem("")
            gate_model.appendRow([category_item, category_value])
            
            for stat_name, values in stats.items():
                if isinstance(values, dict):
                    # Expand X/Y pairs into separate rows for more detail
                    stat_item = QStandardItem(stat_name)
                    stat_value = QStandardItem("")
                    category_item.appendRow([stat_item, stat_value])
                    
                    for axis, value in values.items():
                        axis_item = QStandardItem(f"{axis}")
                        axis_value = QStandardItem(str(value))
                        stat_item.appendRow([axis_item, axis_value])
                else:
                    stat_item = QStandardItem(stat_name)
                    stat_value = QStandardItem(str(values))
                    category_item.appendRow([stat_item, stat_value])
        
        gate_tree.expandAll()
        gate_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        gate_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = StatisticsTreeView()
    window.show()
    sys.exit(app.exec())