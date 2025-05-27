"""
Theme management for GP Manager
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor


class ThemeManager:
    """Manages application themes"""

    @staticmethod
    def get_dark_theme():
        """Get dark theme stylesheet"""
        return """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }

        QMenuBar {
            background-color: #3c3c3c;
            color: #ffffff;
            border: none;
        }

        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }

        QMenuBar::item:selected {
            background-color: #4a4a4a;
        }

        QMenu {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
        }

        QMenu::item:selected {
            background-color: #4a4a4a;
        }

        QToolBar {
            background-color: #3c3c3c;
            border: none;
            spacing: 2px;
        }

        QToolButton {
            background-color: transparent;
            border: none;
            padding: 4px;
            margin: 1px;
        }

        QToolButton:hover {
            background-color: #4a4a4a;
            border-radius: 3px;
        }

        QToolButton:pressed {
            background-color: #555555;
        }

        QSplitter::handle {
            background-color: #555555;
        }

        QSplitter::handle:horizontal {
            width: 3px;
        }

        QSplitter::handle:vertical {
            height: 3px;
        }

        QTreeView {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
            selection-background-color: #4a4a4a;
            alternate-background-color: #323232;
        }

        QTreeView::item {
            padding: 2px;
            border: none;
        }

        QTreeView::item:selected {
            background-color: #4a4a4a;
        }

        QTreeView::item:hover {
            background-color: #3a3a3a;
        }

        QHeaderView::section {
            background-color: #3c3c3c;
            color: #ffffff;
            border: none;
            padding: 4px;
            border-right: 1px solid #555555;
        }

        QScrollBar:vertical {
            background-color: #3c3c3c;
            width: 12px;
            border: none;
        }

        QScrollBar::handle:vertical {
            background-color: #555555;
            border-radius: 6px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #666666;
        }

        QScrollBar:horizontal {
            background-color: #3c3c3c;
            height: 12px;
            border: none;
        }

        QScrollBar::handle:horizontal {
            background-color: #555555;
            border-radius: 6px;
            min-width: 20px;
        }

        QScrollBar::add-line, QScrollBar::sub-line {
            border: none;
            background: none;
        }

        QTextEdit {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
            selection-background-color: #4a4a4a;
        }

        QLineEdit {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 4px;
            border-radius: 3px;
        }

        QLineEdit:focus {
            border-color: #0078d4;
        }

        QPushButton {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 6px 12px;
            border-radius: 3px;
        }

        QPushButton:hover {
            background-color: #4a4a4a;
        }

        QPushButton:pressed {
            background-color: #555555;
        }

        QStatusBar {
            background-color: #3c3c3c;
            color: #ffffff;
            border-top: 1px solid #555555;
        }

        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #2b2b2b;
        }

        QTabBar::tab {
            background-color: #3c3c3c;
            color: #ffffff;
            padding: 6px 12px;
            border: 1px solid #555555;
            border-bottom: none;
        }

        QTabBar::tab:selected {
            background-color: #2b2b2b;
        }

        QTabBar::tab:hover {
            background-color: #4a4a4a;
        }

        /* Tooltip and suggestion styling */
        QToolTip {
            background-color: #4a4a4a;
            color: #ffffff;
            border: 1px solid #666666;
            padding: 4px;
            border-radius: 3px;
        }

        /* Completer and suggestion styling */
        QAbstractItemView {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
            selection-background-color: #0078d4;
            selection-color: #ffffff;
        }

        QAbstractItemView::item {
            padding: 4px;
            border: none;
            color: #ffffff;
        }

        QAbstractItemView::item:hover {
            background-color: #4a4a4a;
            color: #ffffff;
        }

        QAbstractItemView::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }

        /* ComboBox dropdown styling */
        QComboBox {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 4px;
            border-radius: 3px;
        }

        QComboBox:hover {
            background-color: #4a4a4a;
        }

        QComboBox::drop-down {
            border: none;
            background-color: transparent;
        }

        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #ffffff;
            margin-right: 4px;
        }

        QComboBox QAbstractItemView {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
            selection-background-color: #0078d4;
        }

        /* List widget styling */
        QListWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
            selection-background-color: #0078d4;
        }

        QListWidget::item {
            padding: 4px;
            border: none;
            color: #ffffff;
        }

        QListWidget::item:hover {
            background-color: #4a4a4a;
            color: #ffffff;
        }

        QListWidget::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }

        /* Table widget styling */
        QTableWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
            gridline-color: #555555;
            selection-background-color: #0078d4;
        }

        QTableWidget::item {
            padding: 4px;
            border: none;
            color: #ffffff;
        }

        QTableWidget::item:hover {
            background-color: #4a4a4a;
            color: #ffffff;
        }

        QTableWidget::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }

        /* Dialog styling */
        QDialog {
            background-color: #2b2b2b;
            color: #ffffff;
        }

        /* Group box styling */
        QGroupBox {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 3px;
            margin-top: 10px;
            padding-top: 10px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #ffffff;
        }

        /* Checkbox and radio button styling */
        QCheckBox {
            color: #ffffff;
            spacing: 5px;
        }

        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            background-color: #3c3c3c;
            border: 1px solid #555555;
            border-radius: 2px;
        }

        QCheckBox::indicator:hover {
            background-color: #4a4a4a;
        }

        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border-color: #0078d4;
        }

        QRadioButton {
            color: #ffffff;
            spacing: 5px;
        }

        QRadioButton::indicator {
            width: 16px;
            height: 16px;
            background-color: #3c3c3c;
            border: 1px solid #555555;
            border-radius: 8px;
        }

        QRadioButton::indicator:hover {
            background-color: #4a4a4a;
        }

        QRadioButton::indicator:checked {
            background-color: #0078d4;
            border-color: #0078d4;
        }

        /* Spin box styling */
        QSpinBox {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 4px;
            border-radius: 3px;
        }

        QSpinBox:hover {
            background-color: #4a4a4a;
        }

        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #555555;
            border: none;
            width: 16px;
        }

        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #666666;
        }

        /* Progress bar styling */
        QProgressBar {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 3px;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 2px;
        }

        /* Slider styling */
        QSlider::groove:horizontal {
            background-color: #3c3c3c;
            height: 6px;
            border-radius: 3px;
        }

        QSlider::handle:horizontal {
            background-color: #0078d4;
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -5px 0;
        }

        QSlider::handle:horizontal:hover {
            background-color: #1084d8;
        }
        """

    @staticmethod
    def apply_dark_theme(app):
        """Apply dark theme to application"""
        app.setStyleSheet(ThemeManager.get_dark_theme())

        # Set dark palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(43, 43, 43))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(43, 43, 43))
        palette.setColor(QPalette.AlternateBase, QColor(60, 60, 60))
        palette.setColor(QPalette.ToolTipBase, QColor(74, 74, 74))  # Fixed: Dark background for tooltips
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))  # Fixed: White text for tooltips
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(60, 60, 60))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 212))  # Fixed: Better contrast for selections
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))  # Fixed: White text on blue background

        app.setPalette(palette)
