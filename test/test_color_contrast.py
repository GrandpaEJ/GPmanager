#!/usr/bin/env python3
"""
Color contrast testing utility for MT Manager Linux
Tests all UI elements for proper color contrast and visibility
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                                QComboBox, QListWidget, QTableWidget, QTableWidgetItem,
                                QCheckBox, QRadioButton, QSpinBox, QProgressBar,
                                QSlider, QGroupBox, QTabWidget, QTextEdit, QTreeWidget,
                                QTreeWidgetItem, QToolTip, QMenu, QAction)
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont, QPalette
    from src.ui.themes import ThemeManager
    
    class ColorContrastTestWindow(QMainWindow):
        """Test window for color contrast verification"""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("MT Manager Linux - Color Contrast Test")
            self.setGeometry(100, 100, 1200, 800)
            
            self.setup_ui()
            self.setup_test_data()
            
        def setup_ui(self):
            """Setup user interface"""
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout(central_widget)
            
            # Title
            title = QLabel("Color Contrast Test - All UI Elements")
            title.setFont(QFont("Arial", 16, QFont.Bold))
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)
            
            # Create tabs for different element types
            self.tab_widget = QTabWidget()
            layout.addWidget(self.tab_widget)
            
            # Basic elements tab
            self.create_basic_elements_tab()
            
            # List and table elements tab
            self.create_list_table_tab()
            
            # Form elements tab
            self.create_form_elements_tab()
            
            # Interactive elements tab
            self.create_interactive_tab()
            
            # Status bar
            self.statusBar().showMessage("Hover over elements to test tooltips and suggestions")
            
        def create_basic_elements_tab(self):
            """Create basic elements test tab"""
            widget = QWidget()
            layout = QVBoxLayout(widget)
            
            # Labels
            layout.addWidget(QLabel("Basic Text Label"))
            
            # Buttons
            button_layout = QHBoxLayout()
            
            normal_btn = QPushButton("Normal Button")
            normal_btn.setToolTip("This is a tooltip test")
            button_layout.addWidget(normal_btn)
            
            hover_btn = QPushButton("Hover Me")
            hover_btn.setToolTip("Hover tooltip with proper contrast")
            button_layout.addWidget(hover_btn)
            
            disabled_btn = QPushButton("Disabled Button")
            disabled_btn.setEnabled(False)
            button_layout.addWidget(disabled_btn)
            
            layout.addLayout(button_layout)
            
            # Line edits
            line_edit = QLineEdit()
            line_edit.setPlaceholderText("Enter text here...")
            line_edit.setToolTip("Line edit with tooltip")
            layout.addWidget(line_edit)
            
            # Text edit
            text_edit = QTextEdit()
            text_edit.setPlainText("This is a text editor with multiple lines.\nTest selection and hover colors.")
            text_edit.setMaximumHeight(100)
            layout.addWidget(text_edit)
            
            layout.addStretch()
            self.tab_widget.addTab(widget, "Basic Elements")
            
        def create_list_table_tab(self):
            """Create list and table elements test tab"""
            widget = QWidget()
            layout = QHBoxLayout(widget)
            
            # List widget
            list_group = QGroupBox("List Widget")
            list_layout = QVBoxLayout(list_group)
            
            list_widget = QListWidget()
            for i in range(10):
                list_widget.addItem(f"List Item {i+1} - Hover and select to test colors")
            list_layout.addWidget(list_widget)
            layout.addWidget(list_group)
            
            # Table widget
            table_group = QGroupBox("Table Widget")
            table_layout = QVBoxLayout(table_group)
            
            table_widget = QTableWidget(5, 3)
            table_widget.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])
            
            for row in range(5):
                for col in range(3):
                    item = QTableWidgetItem(f"Cell {row+1},{col+1}")
                    table_widget.setItem(row, col, item)
            
            table_layout.addWidget(table_widget)
            layout.addWidget(table_group)
            
            # Tree widget
            tree_group = QGroupBox("Tree Widget")
            tree_layout = QVBoxLayout(tree_group)
            
            tree_widget = QTreeWidget()
            tree_widget.setHeaderLabels(["Name", "Type"])
            
            for i in range(5):
                parent = QTreeWidgetItem([f"Parent {i+1}", "Folder"])
                tree_widget.addTopLevelItem(parent)
                
                for j in range(3):
                    child = QTreeWidgetItem([f"Child {j+1}", "File"])
                    parent.addChild(child)
            
            tree_widget.expandAll()
            tree_layout.addWidget(tree_widget)
            layout.addWidget(tree_group)
            
            self.tab_widget.addTab(widget, "Lists & Tables")
            
        def create_form_elements_tab(self):
            """Create form elements test tab"""
            widget = QWidget()
            layout = QVBoxLayout(widget)
            
            # Combo box
            combo_layout = QHBoxLayout()
            combo_layout.addWidget(QLabel("ComboBox:"))
            combo = QComboBox()
            combo.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
            combo.setToolTip("ComboBox with dropdown suggestions")
            combo_layout.addWidget(combo)
            combo_layout.addStretch()
            layout.addLayout(combo_layout)
            
            # Checkboxes
            checkbox_group = QGroupBox("Checkboxes")
            checkbox_layout = QVBoxLayout(checkbox_group)
            
            cb1 = QCheckBox("Checkbox 1 - Normal")
            cb1.setToolTip("Normal checkbox")
            checkbox_layout.addWidget(cb1)
            
            cb2 = QCheckBox("Checkbox 2 - Checked")
            cb2.setChecked(True)
            cb2.setToolTip("Checked checkbox")
            checkbox_layout.addWidget(cb2)
            
            cb3 = QCheckBox("Checkbox 3 - Disabled")
            cb3.setEnabled(False)
            checkbox_layout.addWidget(cb3)
            
            layout.addWidget(checkbox_group)
            
            # Radio buttons
            radio_group = QGroupBox("Radio Buttons")
            radio_layout = QVBoxLayout(radio_group)
            
            rb1 = QRadioButton("Radio 1 - Selected")
            rb1.setChecked(True)
            rb1.setToolTip("Selected radio button")
            radio_layout.addWidget(rb1)
            
            rb2 = QRadioButton("Radio 2 - Normal")
            rb2.setToolTip("Normal radio button")
            radio_layout.addWidget(rb2)
            
            rb3 = QRadioButton("Radio 3 - Disabled")
            rb3.setEnabled(False)
            radio_layout.addWidget(rb3)
            
            layout.addWidget(radio_group)
            
            # Spin box
            spin_layout = QHBoxLayout()
            spin_layout.addWidget(QLabel("SpinBox:"))
            spin_box = QSpinBox()
            spin_box.setRange(0, 100)
            spin_box.setValue(50)
            spin_box.setToolTip("Spin box with hover effects")
            spin_layout.addWidget(spin_box)
            spin_layout.addStretch()
            layout.addLayout(spin_layout)
            
            layout.addStretch()
            self.tab_widget.addTab(widget, "Form Elements")
            
        def create_interactive_tab(self):
            """Create interactive elements test tab"""
            widget = QWidget()
            layout = QVBoxLayout(widget)
            
            # Progress bar
            progress_layout = QHBoxLayout()
            progress_layout.addWidget(QLabel("Progress Bar:"))
            progress = QProgressBar()
            progress.setValue(65)
            progress.setToolTip("Progress bar showing completion")
            progress_layout.addWidget(progress)
            layout.addLayout(progress_layout)
            
            # Slider
            slider_layout = QHBoxLayout()
            slider_layout.addWidget(QLabel("Slider:"))
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(30)
            slider.setToolTip("Slider with hover effects")
            slider_layout.addWidget(slider)
            layout.addLayout(slider_layout)
            
            # Menu test button
            menu_btn = QPushButton("Test Context Menu")
            menu_btn.setToolTip("Right-click to test menu colors")
            menu_btn.setContextMenuPolicy(Qt.CustomContextMenu)
            menu_btn.customContextMenuRequested.connect(self.show_context_menu)
            layout.addWidget(menu_btn)
            
            # Tooltip test button
            tooltip_btn = QPushButton("Hover for Tooltip Test")
            tooltip_btn.setToolTip("This is a comprehensive tooltip test.\nMultiple lines to verify text visibility.\nBackground and text colors should have good contrast.")
            layout.addWidget(tooltip_btn)
            
            # Color information
            info_group = QGroupBox("Color Information")
            info_layout = QVBoxLayout(info_group)
            
            palette = QApplication.palette()
            
            color_info = f"""
            Current Color Scheme:
            • Window Background: {palette.color(QPalette.Window).name()}
            • Window Text: {palette.color(QPalette.WindowText).name()}
            • Tooltip Background: {palette.color(QPalette.ToolTipBase).name()}
            • Tooltip Text: {palette.color(QPalette.ToolTipText).name()}
            • Highlight Background: {palette.color(QPalette.Highlight).name()}
            • Highlighted Text: {palette.color(QPalette.HighlightedText).name()}
            • Button Background: {palette.color(QPalette.Button).name()}
            • Button Text: {palette.color(QPalette.ButtonText).name()}
            """
            
            info_label = QLabel(color_info)
            info_label.setFont(QFont("monospace", 9))
            info_layout.addWidget(info_label)
            
            layout.addWidget(info_group)
            
            layout.addStretch()
            self.tab_widget.addTab(widget, "Interactive")
            
        def show_context_menu(self, position):
            """Show context menu for testing"""
            menu = QMenu(self)
            
            action1 = QAction("Menu Item 1", self)
            action1.setToolTip("First menu item")
            menu.addAction(action1)
            
            action2 = QAction("Menu Item 2", self)
            action2.setToolTip("Second menu item")
            menu.addAction(action2)
            
            menu.addSeparator()
            
            submenu = menu.addMenu("Submenu")
            sub_action1 = QAction("Sub Item 1", self)
            sub_action2 = QAction("Sub Item 2", self)
            submenu.addAction(sub_action1)
            submenu.addAction(sub_action2)
            
            menu.exec_(self.sender().mapToGlobal(position))
            
        def setup_test_data(self):
            """Setup test data and interactions"""
            # Timer to show tooltip programmatically
            self.tooltip_timer = QTimer()
            self.tooltip_timer.timeout.connect(self.show_test_tooltip)
            self.tooltip_timer.start(5000)  # Show tooltip every 5 seconds
            
        def show_test_tooltip(self):
            """Show a test tooltip"""
            QToolTip.showText(
                self.mapToGlobal(self.rect().center()),
                "Automatic tooltip test\nVerifying color contrast\nBackground and text should be clearly visible"
            )
    
    def main():
        """Main application entry point"""
        app = QApplication(sys.argv)
        
        print("Color Contrast Test for MT Manager Linux")
        print("=" * 50)
        
        # Apply dark theme
        ThemeManager.apply_dark_theme(app)
        print("✓ Dark theme applied")
        
        # Create test window
        window = ColorContrastTestWindow()
        window.show()
        
        print("✓ Test window created")
        print("\nInstructions:")
        print("1. Hover over all elements to test tooltip visibility")
        print("2. Select items in lists and tables to test selection colors")
        print("3. Right-click the context menu button to test menu colors")
        print("4. Check that all text is clearly readable")
        print("5. Verify no elements have invisible text")
        
        return app.exec_()

except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure PyQt5 is installed and the application is properly set up")
    sys.exit(1)

if __name__ == "__main__":
    main()
