"""
Text editor with syntax highlighting for MT Manager Linux
"""
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                            QLabel, QPushButton, QFileDialog, QMessageBox,
                            QTabWidget, QSplitter, QLineEdit, QCheckBox)
from PyQt5.QtGui import QFont, QTextCursor, QTextDocument
from src.editors.json_highlighter import highlighter_manager
from src.utils.config import config


class CodeEditor(QTextEdit):
    """Enhanced text editor with line numbers and syntax highlighting"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = None
        self.is_modified = False
        self.highlighter = None

        # Enable drag and drop
        self.setAcceptDrops(True)

        # Setup editor
        self.setup_editor()

        # Connect signals
        self.textChanged.connect(self.on_text_changed)

    def setup_editor(self):
        """Setup editor properties"""
        # Set font
        font = QFont(config.get('font_family', 'Consolas'))
        font.setPointSize(config.get('font_size', 10))
        self.setFont(font)

        # Enable line wrap
        self.setLineWrapMode(QTextEdit.WidgetWidth)

        # Set tab width
        self.setTabStopWidth(40)

    def load_file(self, file_path):
        """Load file into editor"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            self.setPlainText(content)
            self.file_path = file_path
            self.is_modified = False

            # Apply syntax highlighting based on file extension
            self.apply_syntax_highlighting(file_path)

            # Move cursor to beginning
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.setTextCursor(cursor)

            return True

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load file: {str(e)}"
            )
            return False

    def save_file(self, file_path=None):
        """Save file"""
        if file_path is None:
            file_path = self.file_path

        if file_path is None:
            return False

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())

            self.file_path = file_path
            self.is_modified = False
            return True

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to save file: {str(e)}"
            )
            return False

    def apply_syntax_highlighting(self, file_path):
        """Apply syntax highlighting based on file extension"""
        if self.highlighter:
            self.highlighter.setParent(None)
            self.highlighter = None

        # Use JSON-based highlighter system
        self.highlighter = highlighter_manager.get_highlighter_for_file(
            file_path, self.document()
        )

    def on_text_changed(self):
        """Handle text changes"""
        self.is_modified = True

    def get_file_name(self):
        """Get file name for display"""
        if self.file_path:
            name = Path(self.file_path).name
            if self.is_modified:
                name += " *"
            return name
        return "Untitled"

    def find_text(self, text, case_sensitive=False, whole_words=False):
        """Find text in editor"""
        flags = QTextDocument.FindFlags()

        if case_sensitive:
            flags |= QTextDocument.FindCaseSensitively
        if whole_words:
            flags |= QTextDocument.FindWholeWords

        return self.find(text, flags)

    def replace_text(self, find_text, replace_text, case_sensitive=False, whole_words=False):
        """Replace text in editor"""
        # Suppress unused parameter warnings
        _ = find_text, case_sensitive, whole_words

        cursor = self.textCursor()
        if cursor.hasSelection():
            cursor.insertText(replace_text)
            return True
        return False

    def goto_line(self, line_number):
        """Go to specific line number"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        for _ in range(line_number - 1):
            cursor.movePosition(QTextCursor.Down)
        self.setTextCursor(cursor)
        self.centerCursor()

    # Drag and Drop Support
    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            # Check if any of the URLs are files
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop event"""
        if event.mimeData().hasUrls():
            files = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    files.append(file_path)

            if files:
                # Handle the first file (open it in this editor)
                first_file = files[0]
                if Path(first_file).is_file():
                    self.load_file(first_file)

                # If there are more files, signal to parent to open them
                if len(files) > 1:
                    parent_widget = self.parent()
                    while parent_widget:
                        if hasattr(parent_widget, 'handle_dropped_files'):
                            parent_widget.handle_dropped_files(files[1:])
                            break
                        parent_widget = parent_widget.parent()

                event.acceptProposedAction()
        else:
            event.ignore()


class TextEditorWidget(QWidget):
    """Text editor widget with tabs and find/replace functionality"""

    file_modified = pyqtSignal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Create splitter for editor and find panel
        self.splitter = QSplitter(Qt.Vertical)

        # Tab widget for multiple files
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)

        self.splitter.addWidget(self.tab_widget)

        # Find/Replace panel (initially hidden)
        self.find_widget = self.create_find_widget()
        self.find_widget.hide()
        self.splitter.addWidget(self.find_widget)

        layout.addWidget(self.splitter)

        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.cursor_label = QLabel("Line 1, Col 1")

        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.cursor_label)

        layout.addLayout(status_layout)

    def create_find_widget(self):
        """Create find/replace widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Find row
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))

        self.find_edit = QLineEdit()
        find_layout.addWidget(self.find_edit)

        self.find_next_btn = QPushButton("Find Next")
        self.find_prev_btn = QPushButton("Find Previous")
        find_layout.addWidget(self.find_next_btn)
        find_layout.addWidget(self.find_prev_btn)

        self.case_sensitive_cb = QCheckBox("Case Sensitive")
        self.whole_words_cb = QCheckBox("Whole Words")
        find_layout.addWidget(self.case_sensitive_cb)
        find_layout.addWidget(self.whole_words_cb)

        close_btn = QPushButton("×")
        close_btn.setMaximumWidth(30)
        close_btn.clicked.connect(self.hide_find_widget)
        find_layout.addWidget(close_btn)

        layout.addLayout(find_layout)

        # Replace row
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace:"))

        self.replace_edit = QLineEdit()
        replace_layout.addWidget(self.replace_edit)

        self.replace_btn = QPushButton("Replace")
        self.replace_all_btn = QPushButton("Replace All")
        replace_layout.addWidget(self.replace_btn)
        replace_layout.addWidget(self.replace_all_btn)

        replace_layout.addStretch()

        layout.addLayout(replace_layout)

        return widget

    def setup_connections(self):
        """Setup signal connections"""
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # Find/Replace connections
        self.find_edit.returnPressed.connect(self.find_next)
        self.find_next_btn.clicked.connect(self.find_next)
        self.find_prev_btn.clicked.connect(self.find_previous)
        self.replace_btn.clicked.connect(self.replace_current)
        self.replace_all_btn.clicked.connect(self.replace_all)

    def open_file(self, file_path):
        """Open file in new tab"""
        # Check if file is already open
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if editor.file_path == file_path:
                self.tab_widget.setCurrentIndex(i)
                return

        # Create new editor
        editor = CodeEditor()
        if editor.load_file(file_path):
            # Add tab
            tab_index = self.tab_widget.addTab(editor, editor.get_file_name())
            self.tab_widget.setCurrentIndex(tab_index)

            # Connect editor signals
            editor.textChanged.connect(
                lambda: self.on_editor_modified(editor)
            )
            editor.cursorPositionChanged.connect(
                lambda: self.update_cursor_position(editor)
            )

    def close_tab(self, index):
        """Close tab at index with save confirmation"""
        editor = self.tab_widget.widget(index)
        if editor and editor.is_modified:
            # Switch to the tab being closed for context
            self.tab_widget.setCurrentIndex(index)

            file_name = editor.get_file_name()
            reply = QMessageBox.question(
                self, "Save Changes",
                f"Save changes to {file_name}?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )

            if reply == QMessageBox.Save:
                # Save the file
                if editor.file_path and not editor.file_path.startswith("Untitled"):
                    if not editor.save_file():
                        return  # Save failed, don't close
                else:
                    # Need to save as new file
                    file_path, _ = QFileDialog.getSaveFileName(
                        self, f"Save {file_name}", "", "All Files (*)"
                    )
                    if file_path:
                        if not editor.save_file(file_path):
                            return  # Save failed, don't close
                    else:
                        return  # User cancelled save dialog
            elif reply == QMessageBox.Cancel:
                return  # User cancelled close
            # If Discard, continue to close without saving

        # Remove the tab
        self.tab_widget.removeTab(index)

        # Update window title if this was the active tab
        if hasattr(self.parent(), 'update_window_title'):
            self.parent().update_window_title()

    def save_current_file(self):
        """Save current file"""
        editor = self.get_current_editor()
        if editor:
            if editor.file_path:
                return editor.save_file()
            else:
                # Save as
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Save File", "", "All Files (*)"
                )
                if file_path:
                    return editor.save_file(file_path)
        return False

    def get_current_editor(self):
        """Get current editor"""
        return self.tab_widget.currentWidget()

    def on_tab_changed(self, index):
        """Handle tab change"""
        editor = self.tab_widget.widget(index)
        if editor:
            self.update_cursor_position(editor)

    def on_editor_modified(self, editor):
        """Handle editor modification"""
        # Update tab title
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i) == editor:
                self.tab_widget.setTabText(i, editor.get_file_name())
                break

        self.file_modified.emit(editor.file_path or "Untitled", editor.is_modified)

    def update_cursor_position(self, editor):
        """Update cursor position display"""
        cursor = editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_label.setText(f"Line {line}, Col {col}")

    def show_find_widget(self):
        """Show find/replace widget"""
        self.find_widget.show()
        self.find_edit.setFocus()
        self.find_edit.selectAll()

    def hide_find_widget(self):
        """Hide find/replace widget"""
        self.find_widget.hide()
        editor = self.get_current_editor()
        if editor:
            editor.setFocus()

    def find_next(self):
        """Find next occurrence"""
        editor = self.get_current_editor()
        if editor:
            text = self.find_edit.text()
            if text:
                found = editor.find_text(
                    text,
                    self.case_sensitive_cb.isChecked(),
                    self.whole_words_cb.isChecked()
                )
                if not found:
                    self.status_label.setText("Text not found")

    def find_previous(self):
        """Find previous occurrence"""
        editor = self.get_current_editor()
        if editor:
            text = self.find_edit.text()
            if text:
                # Move cursor to start of current selection to find previous
                cursor = editor.textCursor()
                cursor.setPosition(cursor.selectionStart())
                editor.setTextCursor(cursor)

                # Find backwards
                flags = QTextDocument.FindBackward
                if self.case_sensitive_cb.isChecked():
                    flags |= QTextDocument.FindCaseSensitively
                if self.whole_words_cb.isChecked():
                    flags |= QTextDocument.FindWholeWords

                found = editor.find(text, flags)
                if not found:
                    self.status_label.setText("Text not found")

    def replace_current(self):
        """Replace current selection"""
        editor = self.get_current_editor()
        if editor:
            find_text = self.find_edit.text()
            replace_text = self.replace_edit.text()
            if editor.replace_text(find_text, replace_text):
                self.find_next()

    def replace_all(self):
        """Replace all occurrences"""
        editor = self.get_current_editor()
        if editor:
            find_text = self.find_edit.text()
            replace_text = self.replace_edit.text()

            if not find_text:
                return

            # Move to beginning
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            editor.setTextCursor(cursor)

            count = 0
            while editor.find_text(
                find_text,
                self.case_sensitive_cb.isChecked(),
                self.whole_words_cb.isChecked()
            ):
                editor.replace_text(find_text, replace_text)
                count += 1

            self.status_label.setText(f"Replaced {count} occurrences")

    def open_archive_file(self, archive_path, file_path, content):
        """Open file from archive with content"""
        # Create new editor
        editor = CodeEditor()
        editor.setPlainText(content)
        editor.file_path = f"{archive_path}:{file_path}"  # Special path format
        editor.is_modified = False

        # Apply syntax highlighting
        editor.apply_syntax_highlighting(file_path)

        # Add tab
        tab_name = f"{Path(file_path).name} (archive)"
        tab_index = self.tab_widget.addTab(editor, tab_name)
        self.tab_widget.setCurrentIndex(tab_index)

        # Connect editor signals
        editor.textChanged.connect(
            lambda: self.on_editor_modified(editor)
        )
        editor.cursorPositionChanged.connect(
            lambda: self.update_cursor_position(editor)
        )

    def handle_dropped_files(self, files):
        """Handle multiple dropped files"""
        for file_path in files:
            if Path(file_path).is_file():
                self.open_file(file_path)
