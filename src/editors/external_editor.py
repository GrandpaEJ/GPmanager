"""
External editor manager for MT Manager Linux
Supports opening files in external editors like VSCode, Vim, etc.
"""
import os
import subprocess
import shutil
from pathlib import Path
from PyQt5.QtCore import QObject, QProcess, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLineEdit, QLabel, QComboBox
from src.utils.config import config


class ExternalEditor:
    """Represents an external editor configuration"""
    
    def __init__(self, name, command, args=None, extensions=None, description=""):
        self.name = name
        self.command = command
        self.args = args or []
        self.extensions = extensions or []
        self.description = description
    
    def can_open(self, file_path):
        """Check if this editor can open the given file"""
        if not self.extensions:
            return True  # Can open any file
        
        ext = Path(file_path).suffix.lower()
        return ext in self.extensions
    
    def is_available(self):
        """Check if the editor is available on the system"""
        return shutil.which(self.command) is not None
    
    def to_dict(self):
        """Convert to dictionary for storage"""
        return {
            'name': self.name,
            'command': self.command,
            'args': self.args,
            'extensions': self.extensions,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(
            name=data.get('name', ''),
            command=data.get('command', ''),
            args=data.get('args', []),
            extensions=data.get('extensions', []),
            description=data.get('description', '')
        )


class ExternalEditorManager(QObject):
    """Manages external editors and their configurations"""
    
    editor_opened = pyqtSignal(str, str)  # file_path, editor_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editors = {}
        self.load_default_editors()
        self.load_custom_editors()
    
    def load_default_editors(self):
        """Load default editor configurations"""
        default_editors = [
            ExternalEditor(
                name="Visual Studio Code",
                command="code",
                args=["{file}"],
                extensions=[".py", ".js", ".html", ".css", ".json", ".xml", ".md", ".txt", ".java", ".cpp", ".c", ".h"],
                description="Microsoft Visual Studio Code"
            ),
            ExternalEditor(
                name="VSCode (Insiders)",
                command="code-insiders",
                args=["{file}"],
                extensions=[".py", ".js", ".html", ".css", ".json", ".xml", ".md", ".txt", ".java", ".cpp", ".c", ".h"],
                description="Visual Studio Code Insiders"
            ),
            ExternalEditor(
                name="Vim",
                command="vim",
                args=["{file}"],
                description="Vi IMproved text editor"
            ),
            ExternalEditor(
                name="Neovim",
                command="nvim",
                args=["{file}"],
                description="Neovim text editor"
            ),
            ExternalEditor(
                name="Emacs",
                command="emacs",
                args=["{file}"],
                description="GNU Emacs text editor"
            ),
            ExternalEditor(
                name="Nano",
                command="nano",
                args=["{file}"],
                description="GNU Nano text editor"
            ),
            ExternalEditor(
                name="Gedit",
                command="gedit",
                args=["{file}"],
                extensions=[".txt", ".py", ".js", ".html", ".css", ".json", ".xml", ".md"],
                description="GNOME Text Editor"
            ),
            ExternalEditor(
                name="Kate",
                command="kate",
                args=["{file}"],
                description="KDE Advanced Text Editor"
            ),
            ExternalEditor(
                name="Sublime Text",
                command="subl",
                args=["{file}"],
                description="Sublime Text editor"
            ),
            ExternalEditor(
                name="Atom",
                command="atom",
                args=["{file}"],
                description="GitHub Atom editor"
            ),
            ExternalEditor(
                name="IntelliJ IDEA",
                command="idea",
                args=["{file}"],
                extensions=[".java", ".kt", ".scala", ".groovy"],
                description="JetBrains IntelliJ IDEA"
            ),
            ExternalEditor(
                name="PyCharm",
                command="pycharm",
                args=["{file}"],
                extensions=[".py", ".pyw", ".pyi"],
                description="JetBrains PyCharm"
            ),
            ExternalEditor(
                name="Android Studio",
                command="studio",
                args=["{file}"],
                extensions=[".java", ".kt", ".xml", ".gradle"],
                description="Android Studio IDE"
            ),
            ExternalEditor(
                name="Hex Editor (GHex)",
                command="ghex",
                args=["{file}"],
                description="GNOME Hex Editor"
            ),
            ExternalEditor(
                name="Hex Editor (Bless)",
                command="bless",
                args=["{file}"],
                description="Bless Hex Editor"
            ),
            ExternalEditor(
                name="GIMP",
                command="gimp",
                args=["{file}"],
                extensions=[".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".psd"],
                description="GNU Image Manipulation Program"
            ),
            ExternalEditor(
                name="Blender",
                command="blender",
                args=["{file}"],
                extensions=[".blend", ".obj", ".fbx", ".dae"],
                description="Blender 3D Creation Suite"
            )
        ]
        
        for editor in default_editors:
            if editor.is_available():
                self.editors[editor.name] = editor
    
    def load_custom_editors(self):
        """Load custom editor configurations from config"""
        custom_editors = config.get('external_editors', [])
        for editor_data in custom_editors:
            try:
                editor = ExternalEditor.from_dict(editor_data)
                if editor.is_available():
                    self.editors[editor.name] = editor
            except Exception as e:
                print(f"Error loading custom editor: {e}")
    
    def save_custom_editors(self):
        """Save custom editors to config"""
        custom_editors = []
        for editor in self.editors.values():
            # Only save non-default editors
            if not self._is_default_editor(editor):
                custom_editors.append(editor.to_dict())
        
        config.set('external_editors', custom_editors)
        config.save_config()
    
    def _is_default_editor(self, editor):
        """Check if editor is a default editor"""
        default_commands = [
            "code", "code-insiders", "vim", "nvim", "emacs", "nano",
            "gedit", "kate", "subl", "atom", "idea", "pycharm", "studio",
            "ghex", "bless", "gimp", "blender"
        ]
        return editor.command in default_commands
    
    def get_available_editors(self):
        """Get list of available editors"""
        return list(self.editors.values())
    
    def get_editors_for_file(self, file_path):
        """Get editors that can open the given file"""
        suitable_editors = []
        for editor in self.editors.values():
            if editor.can_open(file_path):
                suitable_editors.append(editor)
        return suitable_editors
    
    def open_file(self, file_path, editor_name=None):
        """Open file in external editor"""
        if editor_name and editor_name in self.editors:
            editor = self.editors[editor_name]
        else:
            # Find best editor for file
            suitable_editors = self.get_editors_for_file(file_path)
            if not suitable_editors:
                return False, "No suitable editor found"
            editor = suitable_editors[0]
        
        try:
            # Prepare command arguments
            args = []
            for arg in editor.args:
                if "{file}" in arg:
                    args.append(arg.replace("{file}", file_path))
                else:
                    args.append(arg)
            
            # Launch editor
            process = QProcess()
            process.startDetached(editor.command, args)
            
            self.editor_opened.emit(file_path, editor.name)
            return True, f"Opened in {editor.name}"
            
        except Exception as e:
            return False, f"Failed to open in {editor.name}: {str(e)}"
    
    def add_custom_editor(self, editor):
        """Add a custom editor"""
        self.editors[editor.name] = editor
        self.save_custom_editors()
    
    def remove_editor(self, editor_name):
        """Remove an editor"""
        if editor_name in self.editors:
            editor = self.editors[editor_name]
            if not self._is_default_editor(editor):
                del self.editors[editor_name]
                self.save_custom_editors()
                return True
        return False


class ExternalEditorDialog(QDialog):
    """Dialog for managing external editors"""
    
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("External Editors")
        self.setModal(True)
        self.resize(600, 400)
        self.setup_ui()
        self.load_editors()
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Editor list
        self.editor_list = QListWidget()
        layout.addWidget(QLabel("Available Editors:"))
        layout.addWidget(self.editor_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Editor")
        add_btn.clicked.connect(self.add_editor)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_editor)
        button_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_editor)
        button_layout.addWidget(remove_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_editors(self):
        """Load editors into list"""
        self.editor_list.clear()
        for editor in self.manager.get_available_editors():
            status = "✓" if editor.is_available() else "✗"
            item_text = f"{status} {editor.name} - {editor.description}"
            self.editor_list.addItem(item_text)
    
    def add_editor(self):
        """Add new custom editor"""
        dialog = EditorConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            editor = dialog.get_editor()
            self.manager.add_custom_editor(editor)
            self.load_editors()
    
    def edit_editor(self):
        """Edit selected editor"""
        current_row = self.editor_list.currentRow()
        if current_row >= 0:
            editors = self.manager.get_available_editors()
            if current_row < len(editors):
                editor = editors[current_row]
                dialog = EditorConfigDialog(self, editor)
                if dialog.exec_() == QDialog.Accepted:
                    updated_editor = dialog.get_editor()
                    self.manager.add_custom_editor(updated_editor)
                    self.load_editors()
    
    def remove_editor(self):
        """Remove selected editor"""
        current_row = self.editor_list.currentRow()
        if current_row >= 0:
            editors = self.manager.get_available_editors()
            if current_row < len(editors):
                editor = editors[current_row]
                if self.manager.remove_editor(editor.name):
                    self.load_editors()
                else:
                    QMessageBox.information(self, "Cannot Remove", "Cannot remove default editors")


class EditorConfigDialog(QDialog):
    """Dialog for configuring an external editor"""
    
    def __init__(self, parent=None, editor=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Configure Editor")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui()
        if editor:
            self.load_editor_data()
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Name
        layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        # Command
        layout.addWidget(QLabel("Command:"))
        self.command_edit = QLineEdit()
        layout.addWidget(self.command_edit)
        
        # Arguments
        layout.addWidget(QLabel("Arguments (use {file} for file path):"))
        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText("e.g., {file} --new-window")
        layout.addWidget(self.args_edit)
        
        # Extensions
        layout.addWidget(QLabel("File Extensions (comma-separated):"))
        self.extensions_edit = QLineEdit()
        self.extensions_edit.setPlaceholderText("e.g., .py,.js,.html")
        layout.addWidget(self.extensions_edit)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.description_edit = QLineEdit()
        layout.addWidget(self.description_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_editor_data(self):
        """Load editor data into form"""
        self.name_edit.setText(self.editor.name)
        self.command_edit.setText(self.editor.command)
        self.args_edit.setText(" ".join(self.editor.args))
        self.extensions_edit.setText(",".join(self.editor.extensions))
        self.description_edit.setText(self.editor.description)
    
    def get_editor(self):
        """Get editor from form data"""
        name = self.name_edit.text().strip()
        command = self.command_edit.text().strip()
        args = [arg.strip() for arg in self.args_edit.text().split() if arg.strip()]
        extensions = [ext.strip() for ext in self.extensions_edit.text().split(",") if ext.strip()]
        description = self.description_edit.text().strip()
        
        return ExternalEditor(name, command, args, extensions, description)


# Global external editor manager
external_editor_manager = ExternalEditorManager()
