"""
Tool dock system for MT Manager Linux
Provides flexible tool arrangement and detachment capabilities
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                            QPushButton, QLabel, QMenu, QAction, QSplitter,
                            QDockWidget, QMainWindow, QToolBar, QFrame)
from PyQt5.QtGui import QIcon
from src.ui.detachable_window import get_window_manager


class DetachableTab(QWidget):
    """A tab widget that can be detached"""
    
    detach_requested = pyqtSignal(str)  # tool_name
    
    def __init__(self, tool_name, tool_widget, parent=None):
        super().__init__(parent)
        self.tool_name = tool_name
        self.tool_widget = tool_widget
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tab header with detach button
        header = QFrame()
        header.setFrameStyle(QFrame.StyledPanel)
        header.setMaximumHeight(30)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(5, 2, 5, 2)
        
        # Tool name label
        self.title_label = QLabel(self.tool_name)
        self.title_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Detach button
        self.detach_btn = QPushButton("⧉")
        self.detach_btn.setToolTip(f"Detach {self.tool_name} to separate window")
        self.detach_btn.setMaximumSize(20, 20)
        self.detach_btn.clicked.connect(self.request_detach)
        header_layout.addWidget(self.detach_btn)
        
        layout.addWidget(header)
        
        # Tool widget
        if self.tool_widget:
            layout.addWidget(self.tool_widget)
    
    def request_detach(self):
        """Request detachment of this tool"""
        self.detach_requested.emit(self.tool_name)


class ToolDock(QDockWidget):
    """Dockable widget for tools"""
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.tools = {}  # tool_name -> tool_widget
        
        self.setup_ui()
        
        # Make dockable
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetClosable
        )
    
    def setup_ui(self):
        """Setup user interface"""
        # Main widget
        main_widget = QWidget()
        self.setWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Tab widget for tools
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.South)
        self.tab_widget.setTabsClosable(False)  # We handle this ourselves
        layout.addWidget(self.tab_widget)
    
    def add_tool(self, tool_name, tool_widget):
        """Add a tool to this dock"""
        # Create detachable tab
        tab = DetachableTab(tool_name, tool_widget)
        tab.detach_requested.connect(self.detach_tool)
        
        # Add to tab widget
        index = self.tab_widget.addTab(tab, tool_name)
        self.tab_widget.setCurrentIndex(index)
        
        # Store reference
        self.tools[tool_name] = tool_widget
        
        return tab
    
    def remove_tool(self, tool_name):
        """Remove a tool from this dock"""
        if tool_name not in self.tools:
            return None
        
        # Find and remove tab
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if isinstance(tab, DetachableTab) and tab.tool_name == tool_name:
                self.tab_widget.removeTab(i)
                break
        
        # Remove from tools dict
        tool_widget = self.tools.pop(tool_name, None)
        return tool_widget
    
    def detach_tool(self, tool_name):
        """Detach a tool to separate window"""
        window_manager = get_window_manager()
        if window_manager:
            # Remove from dock
            tool_widget = self.remove_tool(tool_name)
            if tool_widget:
                # Detach to separate window
                window_manager.detach_tool(tool_name)
    
    def get_tool_count(self):
        """Get number of tools in this dock"""
        return len(self.tools)


class FlexibleToolManager(QWidget):
    """Manages flexible tool arrangement"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.docks = {}  # dock_name -> ToolDock
        self.tools = {}  # tool_name -> tool_widget
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar for dock management
        self.toolbar = QToolBar("Tool Management")
        self.toolbar.setMovable(False)
        
        # Add dock button
        add_dock_btn = QPushButton("+ Add Dock")
        add_dock_btn.setToolTip("Add new tool dock")
        add_dock_btn.clicked.connect(self.add_dock)
        self.toolbar.addWidget(add_dock_btn)
        
        self.toolbar.addSeparator()
        
        # Layout buttons
        layout_menu = QMenu("Layout")
        
        horizontal_action = QAction("Horizontal Layout", self)
        horizontal_action.triggered.connect(self.set_horizontal_layout)
        layout_menu.addAction(horizontal_action)
        
        vertical_action = QAction("Vertical Layout", self)
        vertical_action.triggered.connect(self.set_vertical_layout)
        layout_menu.addAction(vertical_action)
        
        grid_action = QAction("Grid Layout", self)
        grid_action.triggered.connect(self.set_grid_layout)
        layout_menu.addAction(grid_action)
        
        layout_btn = QPushButton("Layout")
        layout_btn.setMenu(layout_menu)
        self.toolbar.addWidget(layout_btn)
        
        layout.addWidget(self.toolbar)
        
        # Main area for docks
        self.dock_area = QSplitter(Qt.Horizontal)
        layout.addWidget(self.dock_area)
        
        # Create default dock
        self.add_dock("Tools")
    
    def add_dock(self, dock_name=None):
        """Add a new tool dock"""
        if not dock_name:
            dock_name = f"Dock {len(self.docks) + 1}"
        
        # Create dock
        dock = ToolDock(dock_name)
        
        # Add to main window as dock widget if main window supports it
        if isinstance(self.main_window, QMainWindow):
            self.main_window.addDockWidget(Qt.RightDockWidgetArea, dock)
        else:
            # Add to splitter
            self.dock_area.addWidget(dock)
        
        # Store reference
        self.docks[dock_name] = dock
        
        return dock
    
    def remove_dock(self, dock_name):
        """Remove a tool dock"""
        if dock_name not in self.docks:
            return
        
        dock = self.docks[dock_name]
        
        # Move tools to other docks or detach them
        tools_to_move = list(dock.tools.keys())
        for tool_name in tools_to_move:
            tool_widget = dock.remove_tool(tool_name)
            if tool_widget:
                # Try to add to another dock
                other_docks = [d for name, d in self.docks.items() if name != dock_name]
                if other_docks:
                    other_docks[0].add_tool(tool_name, tool_widget)
                else:
                    # Detach to separate window
                    window_manager = get_window_manager()
                    if window_manager:
                        window_manager.detach_tool(tool_name)
        
        # Remove dock
        if isinstance(self.main_window, QMainWindow):
            self.main_window.removeDockWidget(dock)
        else:
            dock.setParent(None)
        
        del self.docks[dock_name]
    
    def add_tool(self, tool_name, tool_widget, dock_name=None):
        """Add a tool to a dock"""
        # Store tool reference
        self.tools[tool_name] = tool_widget
        
        # Find target dock
        if dock_name and dock_name in self.docks:
            target_dock = self.docks[dock_name]
        else:
            # Use first available dock or create new one
            if self.docks:
                target_dock = list(self.docks.values())[0]
            else:
                target_dock = self.add_dock("Tools")
        
        # Add to dock
        return target_dock.add_tool(tool_name, tool_widget)
    
    def remove_tool(self, tool_name):
        """Remove a tool from all docks"""
        if tool_name not in self.tools:
            return None
        
        # Find and remove from dock
        for dock in self.docks.values():
            tool_widget = dock.remove_tool(tool_name)
            if tool_widget:
                # Remove from tools dict
                del self.tools[tool_name]
                return tool_widget
        
        return None
    
    def get_tool(self, tool_name):
        """Get a tool widget by name"""
        return self.tools.get(tool_name)
    
    def set_horizontal_layout(self):
        """Set horizontal layout for docks"""
        self.dock_area.setOrientation(Qt.Horizontal)
    
    def set_vertical_layout(self):
        """Set vertical layout for docks"""
        self.dock_area.setOrientation(Qt.Vertical)
    
    def set_grid_layout(self):
        """Set grid layout for docks (simplified)"""
        # For now, just alternate between horizontal and vertical
        # A true grid layout would require more complex implementation
        self.set_horizontal_layout()
    
    def save_layout(self):
        """Save current dock layout"""
        # Implementation would save dock positions and tool assignments
        pass
    
    def load_layout(self):
        """Load saved dock layout"""
        # Implementation would restore dock positions and tool assignments
        pass


class ToolTabWidget(QTabWidget):
    """Enhanced tab widget with detach capabilities"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(False)  # We handle this ourselves
        self.setMovable(True)
        self.setTabPosition(QTabWidget.South)
        
        # Custom tab bar for detach functionality
        self.setup_custom_tabs()
    
    def setup_custom_tabs(self):
        """Setup custom tab functionality"""
        # Add context menu to tabs
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_tab_context_menu)
    
    def show_tab_context_menu(self, position):
        """Show context menu for tab"""
        tab_index = self.tabBar().tabAt(position)
        if tab_index < 0:
            return
        
        menu = QMenu(self)
        
        # Detach action
        detach_action = QAction("Detach to Window", self)
        detach_action.triggered.connect(lambda: self.detach_tab(tab_index))
        menu.addAction(detach_action)
        
        # Close action
        close_action = QAction("Close Tab", self)
        close_action.triggered.connect(lambda: self.close_tab(tab_index))
        menu.addAction(close_action)
        
        menu.exec_(self.mapToGlobal(position))
    
    def detach_tab(self, index):
        """Detach tab to separate window"""
        if 0 <= index < self.count():
            widget = self.widget(index)
            tool_name = self.tabText(index)
            
            # Remove from tab widget
            self.removeTab(index)
            
            # Detach to window
            window_manager = get_window_manager()
            if window_manager:
                window_manager.detach_tool(tool_name)
    
    def close_tab(self, index):
        """Close tab"""
        if 0 <= index < self.count():
            self.removeTab(index)
    
    def add_detachable_tab(self, widget, title):
        """Add a tab with detach capability"""
        # Wrap widget in detachable container
        container = DetachableTab(title, widget)
        container.detach_requested.connect(lambda name: self.detach_tab_by_name(name))
        
        return self.addTab(container, title)
    
    def detach_tab_by_name(self, tool_name):
        """Detach tab by tool name"""
        for i in range(self.count()):
            if self.tabText(i) == tool_name:
                self.detach_tab(i)
                break
