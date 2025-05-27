"""
Detachable window system for GP Manager tools
Allows tools to be separated into independent, scalable windows
"""
import json
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QToolBar, QAction, QPushButton, QLabel, QMenuBar,
                            QMenu, QMessageBox, QApplication)
from PyQt5.QtGui import QIcon, QKeySequence
from src.utils.config import config


class DetachableWindow(QMainWindow):
    """Base class for detachable tool windows"""

    # Signals
    window_closed = pyqtSignal(str)  # tool_name
    window_attached = pyqtSignal(str)  # tool_name
    window_detached = pyqtSignal(str)  # tool_name

    def __init__(self, tool_name, tool_widget, parent=None):
        super().__init__(parent)
        self.tool_name = tool_name
        self.tool_widget = tool_widget
        self.parent_window = parent
        self.is_detached = True

        self.setup_window()
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_toolbar()
        self.load_window_state()

    def setup_window(self):
        """Setup window properties"""
        self.setWindowTitle(f"GP Manager - {self.tool_name}")
        self.setMinimumSize(400, 300)

        # Enable all window controls
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowCloseButtonHint
        )

        # Set window icon (same as main window)
        # self.setWindowIcon(QIcon('resources/icons/gpmanager.png'))

        # Enable window scaling and resizing
        self.setAttribute(Qt.WA_DeleteOnClose, False)  # Don't delete on close

    def setup_ui(self):
        """Setup user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Add the tool widget
        if self.tool_widget:
            layout.addWidget(self.tool_widget)

        # Status bar
        self.statusBar().showMessage(f"{self.tool_name} - Ready")

    def setup_menu_bar(self):
        """Setup menu bar for detached window"""
        menubar = self.menuBar()

        # Window menu
        window_menu = menubar.addMenu("Window")

        # Attach to main window
        attach_action = QAction("Attach to Main Window", self)
        attach_action.setShortcut(QKeySequence("Ctrl+Shift+A"))
        attach_action.triggered.connect(self.attach_to_main)
        window_menu.addAction(attach_action)

        window_menu.addSeparator()

        # Always on top
        self.always_on_top_action = QAction("Always on Top", self)
        self.always_on_top_action.setCheckable(True)
        self.always_on_top_action.triggered.connect(self.toggle_always_on_top)
        window_menu.addAction(self.always_on_top_action)

        # Minimize to tray (future feature)
        minimize_action = QAction("Minimize to Tray", self)
        minimize_action.setEnabled(False)  # Not implemented yet
        window_menu.addAction(minimize_action)

        window_menu.addSeparator()

        # Close window
        close_action = QAction("Close Window", self)
        close_action.setShortcut(QKeySequence.Close)
        close_action.triggered.connect(self.close)
        window_menu.addAction(close_action)

        # View menu
        view_menu = menubar.addMenu("View")

        # Fullscreen
        fullscreen_action = QAction("Full Screen", self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # Zoom controls (if applicable)
        if hasattr(self.tool_widget, 'zoom_in'):
            view_menu.addSeparator()

            zoom_in_action = QAction("Zoom In", self)
            zoom_in_action.setShortcut(QKeySequence.ZoomIn)
            zoom_in_action.triggered.connect(self.tool_widget.zoom_in)
            view_menu.addAction(zoom_in_action)

            zoom_out_action = QAction("Zoom Out", self)
            zoom_out_action.setShortcut(QKeySequence.ZoomOut)
            zoom_out_action.triggered.connect(self.tool_widget.zoom_out)
            view_menu.addAction(zoom_out_action)

            zoom_reset_action = QAction("Reset Zoom", self)
            zoom_reset_action.setShortcut(QKeySequence("Ctrl+0"))
            zoom_reset_action.triggered.connect(self.tool_widget.zoom_reset)
            view_menu.addAction(zoom_reset_action)

    def setup_toolbar(self):
        """Setup toolbar for detached window"""
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(True)

        # Attach button
        attach_btn = QPushButton("📎 Attach")
        attach_btn.setToolTip("Attach to main window")
        attach_btn.clicked.connect(self.attach_to_main)
        toolbar.addWidget(attach_btn)

        toolbar.addSeparator()

        # Tool-specific actions
        if hasattr(self.tool_widget, 'get_toolbar_actions'):
            actions = self.tool_widget.get_toolbar_actions()
            for action in actions:
                if action is None:
                    toolbar.addSeparator()
                else:
                    toolbar.addAction(action)

        # Always on top toggle
        toolbar.addSeparator()

        self.on_top_btn = QPushButton("📌")
        self.on_top_btn.setToolTip("Toggle always on top")
        self.on_top_btn.setCheckable(True)
        self.on_top_btn.clicked.connect(self.toggle_always_on_top)
        toolbar.addWidget(self.on_top_btn)

    def attach_to_main(self):
        """Attach this window back to main window"""
        self.save_window_state()
        self.window_attached.emit(self.tool_name)
        self.hide()

    def toggle_always_on_top(self):
        """Toggle always on top window flag"""
        if self.always_on_top_action.isChecked():
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.on_top_btn.setChecked(True)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.on_top_btn.setChecked(False)

        self.show()  # Need to show again after changing flags

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def closeEvent(self, event):
        """Handle window close event"""
        # Save window state
        self.save_window_state()

        # Emit signal
        self.window_closed.emit(self.tool_name)

        # Hide instead of closing (so it can be reopened)
        event.ignore()
        self.hide()

    def save_window_state(self):
        """Save window geometry and state"""
        state_key = f"detached_window_{self.tool_name.lower().replace(' ', '_')}"

        geometry = self.geometry()
        state = {
            'geometry': {
                'x': geometry.x(),
                'y': geometry.y(),
                'width': geometry.width(),
                'height': geometry.height()
            },
            'maximized': self.isMaximized(),
            'always_on_top': self.always_on_top_action.isChecked() if hasattr(self, 'always_on_top_action') else False
        }

        config.set(state_key, state)
        config.save_config()

    def load_window_state(self):
        """Load window geometry and state"""
        state_key = f"detached_window_{self.tool_name.lower().replace(' ', '_')}"
        state = config.get(state_key, {})

        if state:
            # Restore geometry
            geometry = state.get('geometry', {})
            if geometry:
                self.setGeometry(
                    geometry.get('x', 100),
                    geometry.get('y', 100),
                    geometry.get('width', 800),
                    geometry.get('height', 600)
                )

            # Restore maximized state
            if state.get('maximized', False):
                self.showMaximized()

            # Restore always on top
            if state.get('always_on_top', False):
                self.always_on_top_action.setChecked(True)
                self.toggle_always_on_top()
        else:
            # Default size and position
            self.resize(800, 600)

            # Center on screen
            screen = QApplication.desktop().screenGeometry()
            self.move(
                (screen.width() - self.width()) // 2,
                (screen.height() - self.height()) // 2
            )


class WindowManager:
    """Manages detachable windows for tools"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.detached_windows = {}  # tool_name -> DetachableWindow
        self.tool_widgets = {}      # tool_name -> widget

    def register_tool(self, tool_name, tool_widget):
        """Register a tool widget that can be detached"""
        self.tool_widgets[tool_name] = tool_widget

        # Add detach capability to tool widget if it doesn't exist
        if not hasattr(tool_widget, 'detach_requested'):
            # Add a detach button or menu item to the tool
            self.add_detach_controls(tool_widget, tool_name)

    def add_detach_controls(self, tool_widget, tool_name):
        """Add detach controls to a tool widget"""
        # This would be implemented based on the specific tool widget
        # For now, we'll add it programmatically when needed
        pass

    def detach_tool(self, tool_name):
        """Detach a tool into its own window"""
        if tool_name in self.detached_windows:
            # Window already exists, just show it
            window = self.detached_windows[tool_name]
            window.show()
            window.raise_()
            window.activateWindow()
            return window

        if tool_name not in self.tool_widgets:
            QMessageBox.warning(
                self.main_window,
                "Tool Not Found",
                f"Tool '{tool_name}' is not registered for detachment."
            )
            return None

        # Get the tool widget
        tool_widget = self.tool_widgets[tool_name]

        # Remove from main window (if it's currently there)
        if tool_widget.parent():
            tool_widget.setParent(None)

        # Create detached window
        window = DetachableWindow(tool_name, tool_widget, self.main_window)

        # Connect signals
        window.window_closed.connect(self.on_window_closed)
        window.window_attached.connect(self.on_window_attached)

        # Store reference
        self.detached_windows[tool_name] = window

        # Show window
        window.show()

        return window

    def attach_tool(self, tool_name):
        """Attach a tool back to the main window"""
        if tool_name not in self.detached_windows:
            return False

        window = self.detached_windows[tool_name]
        tool_widget = window.tool_widget

        # Remove from detached window
        tool_widget.setParent(None)

        # Add back to main window
        # This would need to be implemented based on main window structure
        self.main_window.attach_tool(tool_name, tool_widget)

        # Close and remove detached window
        window.close()
        del self.detached_windows[tool_name]

        return True

    def on_window_closed(self, tool_name):
        """Handle detached window being closed"""
        if tool_name in self.detached_windows:
            # Tool is now hidden but can be reopened
            pass

    def on_window_attached(self, tool_name):
        """Handle tool being attached back to main window"""
        self.attach_tool(tool_name)

    def get_detached_tools(self):
        """Get list of currently detached tools"""
        return list(self.detached_windows.keys())

    def is_tool_detached(self, tool_name):
        """Check if a tool is currently detached"""
        return tool_name in self.detached_windows

    def close_all_detached(self):
        """Close all detached windows"""
        for window in self.detached_windows.values():
            window.close()
        self.detached_windows.clear()

    def save_all_states(self):
        """Save state of all detached windows"""
        for window in self.detached_windows.values():
            window.save_window_state()


# Global window manager instance
window_manager = None

def get_window_manager():
    """Get the global window manager instance"""
    return window_manager

def initialize_window_manager(main_window):
    """Initialize the global window manager"""
    global window_manager
    window_manager = WindowManager(main_window)
    return window_manager
