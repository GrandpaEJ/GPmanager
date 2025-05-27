"""
Custom title bar with window controls for GP Manager
"""
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
                            QSizePolicy, QFrame)
from PyQt5.QtGui import QFont, QPalette


class WindowControlButton(QPushButton):
    """Custom window control button"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(30, 30)
        self.setFlat(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QPushButton:pressed {
                background-color: #505050;
            }
        """)


class CloseButton(WindowControlButton):
    """Close button with red hover effect"""

    def __init__(self, parent=None):
        super().__init__("×", parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #ffffff;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)


class CustomTitleBar(QWidget):
    """Custom title bar widget with window controls"""

    # Signals
    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    close_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.dragging = False
        self.drag_position = QPoint()
        self.setup_ui()

    def setup_ui(self):
        """Setup the title bar UI"""
        self.setFixedHeight(35)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border-bottom: 1px solid #555555;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

        # Application icon (placeholder)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setStyleSheet("background-color: #0078d4; border-radius: 3px;")
        layout.addWidget(self.icon_label)

        # Title label
        self.title_label = QLabel("GP Manager")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                margin-left: 10px;
                background-color: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.title_label)

        # Spacer
        layout.addStretch()

        # Window control buttons
        self.minimize_btn = WindowControlButton("−")
        self.minimize_btn.clicked.connect(self.minimize_clicked.emit)
        layout.addWidget(self.minimize_btn)

        self.maximize_btn = WindowControlButton("□")
        self.maximize_btn.clicked.connect(self.maximize_clicked.emit)
        layout.addWidget(self.maximize_btn)

        self.close_btn = CloseButton()
        self.close_btn.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self.close_btn)

    def set_title(self, title):
        """Set the window title"""
        self.title_label.setText(title)

    def update_maximize_button(self, is_maximized):
        """Update maximize button appearance based on window state"""
        if is_maximized:
            self.maximize_btn.setText("❐")
            self.maximize_btn.setToolTip("Restore")
        else:
            self.maximize_btn.setText("□")
            self.maximize_btn.setToolTip("Maximize")

    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.LeftButton and self.dragging:
            if self.parent_window.isMaximized():
                # If maximized, restore to normal size when dragging
                self.parent_window.showNormal()
                # Adjust drag position for restored window
                self.drag_position = QPoint(
                    int(self.parent_window.width() / 2),
                    int(self.height() / 2)
                )

            self.parent_window.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """Handle double click to maximize/restore"""
        if event.button() == Qt.LeftButton:
            self.maximize_clicked.emit()
            event.accept()


class FramelessWindow(QWidget):
    """Frameless window with custom title bar"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_frameless_window()

    def setup_frameless_window(self):
        """Setup frameless window properties"""
        # Remove window frame
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        # Enable window controls
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # Set minimum size
        self.setMinimumSize(800, 600)

        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(1, 1, 1, 1)  # Border
        self.main_layout.setSpacing(0)

        # Add custom title bar
        self.title_bar = CustomTitleBar(self)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self.toggle_maximize)
        self.title_bar.close_clicked.connect(self.close)

        self.main_layout.addWidget(self.title_bar)

        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.addWidget(self.content_widget)

        # Add border styling
        self.setStyleSheet("""
            FramelessWindow {
                border: 1px solid #555555;
                background-color: #2b2b2b;
            }
        """)

    def toggle_maximize(self):
        """Toggle between maximized and normal state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

        # Update title bar button
        self.title_bar.update_maximize_button(self.isMaximized())

    def set_title(self, title):
        """Set window title"""
        self.title_bar.set_title(title)
        self.setWindowTitle(title)

    def set_content_widget(self, widget):
        """Set the main content widget"""
        # Clear existing content
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)

        # Add new content
        self.content_layout.addWidget(widget)

    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)
        # Update maximize button state
        self.title_bar.update_maximize_button(self.isMaximized())

    def changeEvent(self, event):
        """Handle window state changes"""
        super().changeEvent(event)
        if event.type() == event.WindowStateChange:
            self.title_bar.update_maximize_button(self.isMaximized())
