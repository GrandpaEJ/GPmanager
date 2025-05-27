"""
Advanced Hex Editor for MT Manager Linux
Features: hex/ascii view, search, replace, bookmarks, data inspector, etc.
"""
import os
import struct
from pathlib import Path
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRect
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QLabel, QLineEdit, QPushButton, QSplitter, QGroupBox,
                            QSpinBox, QComboBox, QCheckBox, QScrollArea, QFrame,
                            QMessageBox, QFileDialog, QProgressBar, QTabWidget,
                            QTableWidget, QTableWidgetItem, QHeaderView, QMenu,
                            QAction, QToolBar, QStatusBar, QDialog, QGridLayout)
from PyQt5.QtGui import (QFont, QFontMetrics, QPainter, QColor, QPen, QBrush,
                        QTextCursor, QTextCharFormat, QKeySequence, QIcon)


class HexData:
    """Manages hex data and operations"""
    
    def __init__(self, data=b''):
        self.data = bytearray(data)
        self.modified = False
        self.bookmarks = {}  # offset -> name
        self.selections = []  # list of (start, end) tuples
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
        self.modified = True
    
    def insert(self, offset, data):
        """Insert data at offset"""
        if isinstance(data, int):
            data = bytes([data])
        elif isinstance(data, str):
            data = data.encode('utf-8')
        
        self.data[offset:offset] = data
        self.modified = True
    
    def delete(self, start, end):
        """Delete data from start to end"""
        del self.data[start:end]
        self.modified = True
    
    def replace(self, start, end, data):
        """Replace data from start to end"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        self.data[start:end] = data
        self.modified = True
    
    def find(self, pattern, start=0, case_sensitive=True):
        """Find pattern in data"""
        if isinstance(pattern, str):
            if case_sensitive:
                pattern = pattern.encode('utf-8')
            else:
                pattern = pattern.lower().encode('utf-8')
                data = bytes(self.data).lower()
        else:
            data = bytes(self.data)
        
        if not case_sensitive and isinstance(pattern, str):
            return data.find(pattern, start)
        else:
            return bytes(self.data).find(pattern, start)
    
    def add_bookmark(self, offset, name):
        """Add bookmark at offset"""
        self.bookmarks[offset] = name
    
    def remove_bookmark(self, offset):
        """Remove bookmark at offset"""
        if offset in self.bookmarks:
            del self.bookmarks[offset]
    
    def get_bookmark_name(self, offset):
        """Get bookmark name at offset"""
        return self.bookmarks.get(offset, None)


class HexView(QWidget):
    """Hex view widget with hex and ASCII display"""
    
    position_changed = pyqtSignal(int)
    selection_changed = pyqtSignal(int, int)
    data_modified = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hex_data = HexData()
        self.bytes_per_line = 16
        self.current_position = 0
        self.selection_start = -1
        self.selection_end = -1
        self.font = QFont("monospace", 10)
        self.font_metrics = QFontMetrics(self.font)
        self.char_width = self.font_metrics.width('0')
        self.char_height = self.font_metrics.height()
        self.editing_mode = 'hex'  # 'hex' or 'ascii'
        self.read_only = False
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.calculate_layout()
    
    def calculate_layout(self):
        """Calculate layout dimensions"""
        # Address area: 8 hex digits + ': '
        self.address_width = self.char_width * 10
        
        # Hex area: 16 bytes * 3 chars (2 hex + space) - 1 space
        self.hex_width = self.char_width * (self.bytes_per_line * 3 - 1)
        
        # ASCII area: 16 chars
        self.ascii_width = self.char_width * self.bytes_per_line
        
        # Separators
        self.separator_width = self.char_width * 2
        
        # Total width
        total_width = (self.address_width + self.separator_width + 
                      self.hex_width + self.separator_width + self.ascii_width)
        
        self.setMinimumWidth(total_width + 20)
        
        # Calculate areas
        x = 10
        self.address_rect = QRect(x, 0, self.address_width, 0)
        x += self.address_width + self.separator_width
        
        self.hex_rect = QRect(x, 0, self.hex_width, 0)
        x += self.hex_width + self.separator_width
        
        self.ascii_rect = QRect(x, 0, self.ascii_width, 0)
    
    def set_data(self, data):
        """Set hex data"""
        if isinstance(data, (bytes, bytearray)):
            self.hex_data = HexData(data)
        else:
            self.hex_data = data
        
        self.current_position = 0
        self.selection_start = -1
        self.selection_end = -1
        self.update()
    
    def get_data(self):
        """Get hex data"""
        return bytes(self.hex_data.data)
    
    def load_file(self, file_path):
        """Load file into hex editor"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            self.set_data(data)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {e}")
            return False
    
    def save_file(self, file_path):
        """Save hex data to file"""
        try:
            with open(file_path, 'wb') as f:
                f.write(self.get_data())
            self.hex_data.modified = False
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
            return False
    
    def paintEvent(self, event):
        """Paint the hex view"""
        painter = QPainter(self)
        painter.setFont(self.font)
        
        # Clear background
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        if not self.hex_data:
            return
        
        # Calculate visible range
        first_line = max(0, event.rect().top() // self.char_height)
        last_line = min(
            (len(self.hex_data) + self.bytes_per_line - 1) // self.bytes_per_line,
            (event.rect().bottom() // self.char_height) + 1
        )
        
        y = first_line * self.char_height + self.font_metrics.ascent()
        
        for line in range(first_line, last_line):
            offset = line * self.bytes_per_line
            if offset >= len(self.hex_data):
                break
            
            # Draw address
            address_text = f"{offset:08X}:"
            painter.setPen(QColor(128, 128, 128))
            painter.drawText(self.address_rect.x(), y, address_text)
            
            # Draw hex bytes
            hex_x = self.hex_rect.x()
            ascii_x = self.ascii_rect.x()
            
            for i in range(self.bytes_per_line):
                byte_offset = offset + i
                if byte_offset >= len(self.hex_data):
                    break
                
                byte_value = self.hex_data[byte_offset]
                
                # Determine colors
                if self.is_selected(byte_offset):
                    bg_color = QColor(0, 120, 215)
                    text_color = QColor(255, 255, 255)
                elif byte_offset == self.current_position:
                    bg_color = QColor(255, 255, 0)
                    text_color = QColor(0, 0, 0)
                elif byte_offset in self.hex_data.bookmarks:
                    bg_color = QColor(255, 200, 200)
                    text_color = QColor(0, 0, 0)
                else:
                    bg_color = None
                    text_color = QColor(0, 0, 0)
                
                # Draw hex byte
                hex_text = f"{byte_value:02X}"
                hex_rect = QRect(hex_x, y - self.font_metrics.ascent(), 
                               self.char_width * 2, self.char_height)
                
                if bg_color:
                    painter.fillRect(hex_rect, bg_color)
                
                painter.setPen(text_color)
                painter.drawText(hex_x, y, hex_text)
                
                # Draw ASCII character
                if 32 <= byte_value <= 126:
                    ascii_char = chr(byte_value)
                else:
                    ascii_char = '.'
                
                ascii_rect = QRect(ascii_x + i * self.char_width, 
                                 y - self.font_metrics.ascent(),
                                 self.char_width, self.char_height)
                
                if bg_color:
                    painter.fillRect(ascii_rect, bg_color)
                
                painter.setPen(text_color)
                painter.drawText(ascii_x + i * self.char_width, y, ascii_char)
                
                hex_x += self.char_width * 3
            
            y += self.char_height
    
    def is_selected(self, offset):
        """Check if offset is in selection"""
        if self.selection_start == -1 or self.selection_end == -1:
            return False
        
        start = min(self.selection_start, self.selection_end)
        end = max(self.selection_start, self.selection_end)
        return start <= offset <= end
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            offset = self.offset_from_point(event.pos())
            if offset >= 0:
                self.current_position = offset
                self.selection_start = offset
                self.selection_end = offset
                self.position_changed.emit(offset)
                self.update()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if event.buttons() & Qt.LeftButton:
            offset = self.offset_from_point(event.pos())
            if offset >= 0:
                self.selection_end = offset
                self.selection_changed.emit(
                    min(self.selection_start, self.selection_end),
                    max(self.selection_start, self.selection_end)
                )
                self.update()
    
    def offset_from_point(self, point):
        """Get byte offset from point"""
        line = point.y() // self.char_height
        offset = line * self.bytes_per_line
        
        if self.hex_rect.contains(point):
            # Click in hex area
            rel_x = point.x() - self.hex_rect.x()
            byte_index = rel_x // (self.char_width * 3)
            offset += min(byte_index, self.bytes_per_line - 1)
        elif self.ascii_rect.contains(point):
            # Click in ASCII area
            rel_x = point.x() - self.ascii_rect.x()
            byte_index = rel_x // self.char_width
            offset += min(byte_index, self.bytes_per_line - 1)
        else:
            return -1
        
        return min(offset, len(self.hex_data) - 1) if self.hex_data else -1
    
    def keyPressEvent(self, event):
        """Handle key press"""
        if self.read_only:
            return
        
        key = event.key()
        
        # Navigation keys
        if key == Qt.Key_Left:
            self.move_cursor(-1)
        elif key == Qt.Key_Right:
            self.move_cursor(1)
        elif key == Qt.Key_Up:
            self.move_cursor(-self.bytes_per_line)
        elif key == Qt.Key_Down:
            self.move_cursor(self.bytes_per_line)
        elif key == Qt.Key_Home:
            self.current_position = 0
            self.position_changed.emit(self.current_position)
            self.update()
        elif key == Qt.Key_End:
            self.current_position = len(self.hex_data) - 1
            self.position_changed.emit(self.current_position)
            self.update()
        
        # Editing keys
        elif event.text() and not event.modifiers():
            self.insert_character(event.text())
    
    def move_cursor(self, delta):
        """Move cursor by delta"""
        new_pos = max(0, min(len(self.hex_data) - 1, self.current_position + delta))
        if new_pos != self.current_position:
            self.current_position = new_pos
            self.position_changed.emit(self.current_position)
            self.update()
    
    def insert_character(self, char):
        """Insert character at current position"""
        if self.current_position >= len(self.hex_data):
            return
        
        if self.editing_mode == 'hex':
            # Hex editing
            if char in '0123456789ABCDEFabcdef':
                # TODO: Implement hex editing
                pass
        else:
            # ASCII editing
            if len(char) == 1:
                self.hex_data[self.current_position] = ord(char)
                self.data_modified.emit()
                self.move_cursor(1)
    
    def sizeHint(self):
        """Return size hint"""
        lines = (len(self.hex_data) + self.bytes_per_line - 1) // self.bytes_per_line
        height = max(200, lines * self.char_height + 20)
        return self.size().expandedTo(self.minimumSize()).boundedTo(
            self.size().expandedTo(self.size().expandedTo(self.minimumSize()))
        )


class DataInspector(QWidget):
    """Data inspector showing different interpretations of selected bytes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.data = b''
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        layout.addWidget(QLabel("Data Inspector"))
        
        # Create table for data interpretations
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Type", "Value"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
    
    def set_data(self, data, offset=0):
        """Set data to inspect"""
        self.data = data
        self.update_interpretations(offset)
    
    def update_interpretations(self, offset=0):
        """Update data interpretations"""
        self.table.setRowCount(0)
        
        if not self.data or offset >= len(self.data):
            return
        
        interpretations = []
        
        # Single byte
        if offset < len(self.data):
            byte_val = self.data[offset]
            interpretations.extend([
                ("Byte (unsigned)", str(byte_val)),
                ("Byte (signed)", str(struct.unpack('b', bytes([byte_val]))[0])),
                ("Hex", f"0x{byte_val:02X}"),
                ("Binary", f"0b{byte_val:08b}"),
                ("ASCII", chr(byte_val) if 32 <= byte_val <= 126 else '.')
            ])
        
        # Multi-byte interpretations
        remaining = len(self.data) - offset
        
        if remaining >= 2:
            val = struct.unpack('<H', self.data[offset:offset+2])[0]
            interpretations.append(("UInt16 (LE)", str(val)))
            val = struct.unpack('>H', self.data[offset:offset+2])[0]
            interpretations.append(("UInt16 (BE)", str(val)))
        
        if remaining >= 4:
            val = struct.unpack('<I', self.data[offset:offset+4])[0]
            interpretations.append(("UInt32 (LE)", str(val)))
            val = struct.unpack('>I', self.data[offset:offset+4])[0]
            interpretations.append(("UInt32 (BE)", str(val)))
            
            val = struct.unpack('<f', self.data[offset:offset+4])[0]
            interpretations.append(("Float (LE)", f"{val:.6f}"))
        
        if remaining >= 8:
            val = struct.unpack('<Q', self.data[offset:offset+8])[0]
            interpretations.append(("UInt64 (LE)", str(val)))
            
            val = struct.unpack('<d', self.data[offset:offset+8])[0]
            interpretations.append(("Double (LE)", f"{val:.6f}"))
        
        # Add interpretations to table
        self.table.setRowCount(len(interpretations))
        for i, (type_name, value) in enumerate(interpretations):
            self.table.setItem(i, 0, QTableWidgetItem(type_name))
            self.table.setItem(i, 1, QTableWidgetItem(value))


class HexEditor(QWidget):
    """Main hex editor widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = None
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        self.toolbar = QToolBar()
        layout.addWidget(self.toolbar)
        
        # Add toolbar actions
        self.setup_toolbar()
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Hex view
        self.hex_view = HexView()
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.hex_view)
        scroll_area.setWidgetResizable(True)
        splitter.addWidget(scroll_area)
        
        # Right panel
        right_panel = QTabWidget()
        
        # Data inspector
        self.data_inspector = DataInspector()
        right_panel.addTab(self.data_inspector, "Inspector")
        
        # Bookmarks
        self.bookmarks_widget = QWidget()
        right_panel.addTab(self.bookmarks_widget, "Bookmarks")
        
        # Search
        self.search_widget = self.create_search_widget()
        right_panel.addTab(self.search_widget, "Search")
        
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 300])
        
        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        
        # Position label
        self.position_label = QLabel("Position: 0x00000000")
        self.status_bar.addWidget(self.position_label)
        
        # Selection label
        self.selection_label = QLabel("")
        self.status_bar.addWidget(self.selection_label)
        
        # File size label
        self.size_label = QLabel("Size: 0 bytes")
        self.status_bar.addPermanentWidget(self.size_label)
    
    def setup_toolbar(self):
        """Setup toolbar actions"""
        # File operations
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        self.toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        self.toolbar.addAction(save_action)
        
        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        self.toolbar.addAction(save_as_action)
        
        self.toolbar.addSeparator()
        
        # Edit operations
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy_selection)
        self.toolbar.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste_data)
        self.toolbar.addAction(paste_action)
        
        self.toolbar.addSeparator()
        
        # View options
        self.toolbar.addWidget(QLabel("Bytes per line:"))
        self.bytes_per_line_combo = QComboBox()
        self.bytes_per_line_combo.addItems(["8", "16", "32"])
        self.bytes_per_line_combo.setCurrentText("16")
        self.bytes_per_line_combo.currentTextChanged.connect(self.change_bytes_per_line)
        self.toolbar.addWidget(self.bytes_per_line_combo)
    
    def create_search_widget(self):
        """Create search widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search input
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout(search_group)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Enter search term...")
        search_layout.addWidget(self.search_edit)
        
        search_options_layout = QHBoxLayout()
        
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["Text", "Hex"])
        search_options_layout.addWidget(self.search_type_combo)
        
        self.case_sensitive_cb = QCheckBox("Case sensitive")
        search_options_layout.addWidget(self.case_sensitive_cb)
        
        search_layout.addLayout(search_options_layout)
        
        search_buttons_layout = QHBoxLayout()
        
        find_next_btn = QPushButton("Find Next")
        find_next_btn.clicked.connect(self.find_next)
        search_buttons_layout.addWidget(find_next_btn)
        
        find_prev_btn = QPushButton("Find Previous")
        find_prev_btn.clicked.connect(self.find_previous)
        search_buttons_layout.addWidget(find_prev_btn)
        
        search_layout.addLayout(search_buttons_layout)
        
        layout.addWidget(search_group)
        
        # Replace
        replace_group = QGroupBox("Replace")
        replace_layout = QVBoxLayout(replace_group)
        
        self.replace_edit = QLineEdit()
        self.replace_edit.setPlaceholderText("Replace with...")
        replace_layout.addWidget(self.replace_edit)
        
        replace_buttons_layout = QHBoxLayout()
        
        replace_btn = QPushButton("Replace")
        replace_btn.clicked.connect(self.replace_current)
        replace_buttons_layout.addWidget(replace_btn)
        
        replace_all_btn = QPushButton("Replace All")
        replace_all_btn.clicked.connect(self.replace_all)
        replace_buttons_layout.addWidget(replace_all_btn)
        
        replace_layout.addLayout(replace_buttons_layout)
        
        layout.addWidget(replace_group)
        layout.addStretch()
        
        return widget
    
    def setup_connections(self):
        """Setup signal connections"""
        self.hex_view.position_changed.connect(self.on_position_changed)
        self.hex_view.selection_changed.connect(self.on_selection_changed)
        self.hex_view.data_modified.connect(self.on_data_modified)
    
    def open_file(self, file_path=None):
        """Open file in hex editor"""
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open File", "", "All Files (*)"
            )
        
        if file_path:
            if self.hex_view.load_file(file_path):
                self.file_path = file_path
                self.update_status()
                return True
        return False
    
    def save_file(self):
        """Save current file"""
        if self.file_path:
            return self.hex_view.save_file(self.file_path)
        else:
            return self.save_file_as()
    
    def save_file_as(self):
        """Save file as"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "", "All Files (*)"
        )
        
        if file_path:
            if self.hex_view.save_file(file_path):
                self.file_path = file_path
                return True
        return False
    
    def copy_selection(self):
        """Copy selection to clipboard"""
        # TODO: Implement clipboard operations
        pass
    
    def paste_data(self):
        """Paste data from clipboard"""
        # TODO: Implement clipboard operations
        pass
    
    def change_bytes_per_line(self, value):
        """Change bytes per line"""
        try:
            self.hex_view.bytes_per_line = int(value)
            self.hex_view.calculate_layout()
            self.hex_view.update()
        except ValueError:
            pass
    
    def find_next(self):
        """Find next occurrence"""
        # TODO: Implement search functionality
        pass
    
    def find_previous(self):
        """Find previous occurrence"""
        # TODO: Implement search functionality
        pass
    
    def replace_current(self):
        """Replace current selection"""
        # TODO: Implement replace functionality
        pass
    
    def replace_all(self):
        """Replace all occurrences"""
        # TODO: Implement replace all functionality
        pass
    
    def on_position_changed(self, position):
        """Handle position change"""
        self.position_label.setText(f"Position: 0x{position:08X} ({position})")
        
        # Update data inspector
        if self.hex_view.hex_data:
            data = bytes(self.hex_view.hex_data.data)
            self.data_inspector.set_data(data, position)
    
    def on_selection_changed(self, start, end):
        """Handle selection change"""
        length = end - start + 1
        self.selection_label.setText(f"Selection: {length} bytes")
    
    def on_data_modified(self):
        """Handle data modification"""
        self.update_status()
    
    def update_status(self):
        """Update status information"""
        if self.hex_view.hex_data:
            size = len(self.hex_view.hex_data)
            modified = " (Modified)" if self.hex_view.hex_data.modified else ""
            self.size_label.setText(f"Size: {size} bytes{modified}")
    
    def load_file(self, file_path):
        """Load file (external interface)"""
        return self.open_file(file_path)
