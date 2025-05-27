"""
DEX (Dalvik Executable) Editor for GP Manager
Provides comprehensive DEX file editing capabilities similar to MT Manager
"""
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, List
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QTreeWidget, QTreeWidgetItem, QTextEdit, QLabel,
                            QPushButton, QSplitter, QGroupBox, QListWidget,
                            QListWidgetItem, QMessageBox, QFileDialog,
                            QProgressBar, QComboBox, QLineEdit, QCheckBox,
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtGui import QFont, QIcon, QPixmap


class DexStructureViewer(QWidget):
    """Widget for viewing DEX file structure"""
    
    item_selected = pyqtSignal(str, dict)  # item_type, item_data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dex_parser = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the structure viewer UI"""
        layout = QVBoxLayout(self)
        
        # Header info
        self.header_group = QGroupBox("DEX Header")
        header_layout = QVBoxLayout(self.header_group)
        
        self.header_table = QTableWidget(0, 2)
        self.header_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.header_table.horizontalHeader().setStretchLastSection(True)
        header_layout.addWidget(self.header_table)
        
        layout.addWidget(self.header_group)
        
        # Structure tree
        self.structure_tree = QTreeWidget()
        self.structure_tree.setHeaderLabel("DEX Structure")
        self.structure_tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.structure_tree)
    
    def load_dex_file(self, file_path: str) -> bool:
        """Load and parse DEX file"""
        try:
            from src.parsers.dex_parser import DexParser
            
            self.dex_parser = DexParser(file_path)
            if not self.dex_parser.parse():
                return False
            
            self.populate_header_info()
            self.populate_structure_tree()
            return True
            
        except ImportError:
            QMessageBox.warning(self, "Error", "DEX parser not available")
            return False
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load DEX file: {str(e)}")
            return False
    
    def populate_header_info(self):
        """Populate header information table"""
        if not self.dex_parser or not self.dex_parser.header:
            return
        
        header = self.dex_parser.header
        header_info = [
            ("Magic", header.magic.decode('ascii', errors='replace')),
            ("Version", header.version),
            ("File Size", f"{header.file_size:,} bytes"),
            ("Checksum", f"0x{header.checksum:08X}"),
            ("Header Size", f"{header.header_size} bytes"),
            ("Endian Tag", f"0x{header.endian_tag:08X}"),
            ("Strings", f"{header.string_ids_size:,}"),
            ("Types", f"{header.type_ids_size:,}"),
            ("Prototypes", f"{header.proto_ids_size:,}"),
            ("Fields", f"{header.field_ids_size:,}"),
            ("Methods", f"{header.method_ids_size:,}"),
            ("Classes", f"{header.class_defs_size:,}")
        ]
        
        self.header_table.setRowCount(len(header_info))
        for i, (prop, value) in enumerate(header_info):
            self.header_table.setItem(i, 0, QTableWidgetItem(prop))
            self.header_table.setItem(i, 1, QTableWidgetItem(str(value)))
    
    def populate_structure_tree(self):
        """Populate the structure tree"""
        if not self.dex_parser:
            return
        
        self.structure_tree.clear()
        
        # String pool
        strings_item = QTreeWidgetItem(["String Pool"])
        strings_item.setData(0, Qt.UserRole, {"type": "string_pool"})
        for i, string in enumerate(self.dex_parser.strings[:100]):  # Limit display
            string_item = QTreeWidgetItem([f"[{i}] {string[:50]}..."])
            string_item.setData(0, Qt.UserRole, {"type": "string", "index": i, "value": string})
            strings_item.addChild(string_item)
        self.structure_tree.addTopLevelItem(strings_item)
        
        # Type definitions
        types_item = QTreeWidgetItem(["Type Definitions"])
        types_item.setData(0, Qt.UserRole, {"type": "type_pool"})
        for i, type_id in enumerate(self.dex_parser.type_ids[:100]):
            type_item = QTreeWidgetItem([f"[{i}] {type_id.descriptor}"])
            type_item.setData(0, Qt.UserRole, {"type": "type", "index": i, "descriptor": type_id.descriptor})
            types_item.addChild(type_item)
        self.structure_tree.addTopLevelItem(types_item)
        
        # Method definitions
        methods_item = QTreeWidgetItem(["Method Definitions"])
        methods_item.setData(0, Qt.UserRole, {"type": "method_pool"})
        for i, method_id in enumerate(self.dex_parser.method_ids[:100]):
            method_name = f"{method_id.class_name}.{method_id.method_name}"
            method_item = QTreeWidgetItem([f"[{i}] {method_name}"])
            method_item.setData(0, Qt.UserRole, {
                "type": "method", 
                "index": i, 
                "class_name": method_id.class_name,
                "method_name": method_id.method_name,
                "prototype": method_id.prototype
            })
            methods_item.addChild(method_item)
        self.structure_tree.addTopLevelItem(methods_item)
        
        # Class definitions
        classes_item = QTreeWidgetItem(["Class Definitions"])
        classes_item.setData(0, Qt.UserRole, {"type": "class_pool"})
        for i, class_def in enumerate(self.dex_parser.class_defs):
            class_item = QTreeWidgetItem([f"[{i}] {class_def.class_name}"])
            class_item.setData(0, Qt.UserRole, {
                "type": "class",
                "index": i,
                "class_name": class_def.class_name,
                "superclass": class_def.superclass_name,
                "access_flags": class_def.access_flags
            })
            classes_item.addChild(class_item)
        self.structure_tree.addTopLevelItem(classes_item)
    
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item click"""
        data = item.data(0, Qt.UserRole)
        if data:
            self.item_selected.emit(data.get("type", ""), data)


class DexBytecodeViewer(QWidget):
    """Widget for viewing and editing DEX bytecode"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the bytecode viewer UI"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.disassemble_btn = QPushButton("Disassemble")
        self.disassemble_btn.clicked.connect(self.disassemble_method)
        toolbar_layout.addWidget(self.disassemble_btn)
        
        self.assemble_btn = QPushButton("Assemble")
        self.assemble_btn.clicked.connect(self.assemble_method)
        toolbar_layout.addWidget(self.assemble_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Bytecode display
        self.bytecode_edit = QTextEdit()
        self.bytecode_edit.setFont(QFont("monospace", 10))
        layout.addWidget(self.bytecode_edit)
    
    def disassemble_method(self):
        """Disassemble selected method"""
        # Placeholder for bytecode disassembly
        self.bytecode_edit.setPlainText("// Bytecode disassembly not yet implemented\n// This would show Dalvik bytecode instructions")
    
    def assemble_method(self):
        """Assemble bytecode back to DEX"""
        # Placeholder for bytecode assembly
        QMessageBox.information(self, "Info", "Bytecode assembly not yet implemented")


class DexSmaliViewer(QWidget):
    """Widget for viewing and editing Smali code"""
    
    conversion_finished = pyqtSignal(bool, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_dex_path = None
        self.current_smali_dir = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the Smali viewer UI"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.dex_to_smali_btn = QPushButton("DEX → Smali")
        self.dex_to_smali_btn.clicked.connect(self.convert_dex_to_smali)
        toolbar_layout.addWidget(self.dex_to_smali_btn)
        
        self.smali_to_dex_btn = QPushButton("Smali → DEX")
        self.smali_to_dex_btn.clicked.connect(self.convert_smali_to_dex)
        toolbar_layout.addWidget(self.smali_to_dex_btn)
        
        self.open_smali_btn = QPushButton("Open Smali Dir")
        self.open_smali_btn.clicked.connect(self.open_smali_directory)
        toolbar_layout.addWidget(self.open_smali_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Smali file browser and editor
        splitter = QSplitter(Qt.Horizontal)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.open_smali_file)
        splitter.addWidget(self.file_list)
        
        # Smali editor
        self.smali_edit = QTextEdit()
        self.smali_edit.setFont(QFont("monospace", 10))
        splitter.addWidget(self.smali_edit)
        
        splitter.setSizes([200, 600])
        layout.addWidget(splitter)
    
    def set_dex_file(self, dex_path: str):
        """Set the current DEX file"""
        self.current_dex_path = dex_path
    
    def convert_dex_to_smali(self):
        """Convert DEX to Smali"""
        if not self.current_dex_path:
            QMessageBox.warning(self, "Warning", "No DEX file selected")
            return
        
        # Choose output directory
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select Output Directory for Smali Files"
        )
        if not output_dir:
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Converting DEX to Smali...")
        
        # Start conversion in worker thread
        from src.tools.dex_tools import SmaliWorker
        
        self.worker = SmaliWorker('dex2smali', self.current_dex_path, output_dir)
        self.worker.operation_finished.connect(self.on_conversion_finished)
        self.worker.progress_updated.connect(self.status_label.setText)
        self.worker.start()
    
    def convert_smali_to_dex(self):
        """Convert Smali to DEX"""
        if not self.current_smali_dir:
            QMessageBox.warning(self, "Warning", "No Smali directory selected")
            return
        
        # Choose output file
        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save DEX File", "", "DEX Files (*.dex)"
        )
        if not output_file:
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Converting Smali to DEX...")
        
        # Start conversion in worker thread
        from src.tools.dex_tools import SmaliWorker
        
        self.worker = SmaliWorker('smali2dex', self.current_smali_dir, output_file)
        self.worker.operation_finished.connect(self.on_conversion_finished)
        self.worker.progress_updated.connect(self.status_label.setText)
        self.worker.start()
    
    def on_conversion_finished(self, success: bool, message: str):
        """Handle conversion completion"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.conversion_finished.emit(True, message)
        else:
            QMessageBox.warning(self, "Error", message)
            self.conversion_finished.emit(False, message)
    
    def open_smali_directory(self):
        """Open Smali directory"""
        smali_dir = QFileDialog.getExistingDirectory(
            self, "Select Smali Directory"
        )
        if smali_dir:
            self.current_smali_dir = smali_dir
            self.load_smali_files(smali_dir)
    
    def load_smali_files(self, smali_dir: str):
        """Load Smali files from directory"""
        self.file_list.clear()
        smali_path = Path(smali_dir)
        
        for smali_file in smali_path.rglob("*.smali"):
            relative_path = smali_file.relative_to(smali_path)
            item = QListWidgetItem(str(relative_path))
            item.setData(Qt.UserRole, str(smali_file))
            self.file_list.addItem(item)
    
    def open_smali_file(self, item: QListWidgetItem):
        """Open Smali file in editor"""
        file_path = item.data(Qt.UserRole)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.smali_edit.setPlainText(content)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open file: {str(e)}")


class DexEditor(QWidget):
    """Main DEX editor widget"""
    
    file_opened = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main DEX editor UI"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.open_btn = QPushButton("Open DEX")
        self.open_btn.clicked.connect(self.open_dex_file)
        toolbar_layout.addWidget(self.open_btn)
        
        self.validate_btn = QPushButton("Validate")
        self.validate_btn.clicked.connect(self.validate_dex)
        toolbar_layout.addWidget(self.validate_btn)
        
        self.info_btn = QPushButton("File Info")
        self.info_btn.clicked.connect(self.show_file_info)
        toolbar_layout.addWidget(self.info_btn)
        
        toolbar_layout.addStretch()
        
        self.file_label = QLabel("No file loaded")
        toolbar_layout.addWidget(self.file_label)
        
        layout.addLayout(toolbar_layout)
        
        # Main content tabs
        self.tab_widget = QTabWidget()
        
        # Structure viewer tab
        self.structure_viewer = DexStructureViewer()
        self.tab_widget.addTab(self.structure_viewer, "Structure")
        
        # Bytecode viewer tab
        self.bytecode_viewer = DexBytecodeViewer()
        self.tab_widget.addTab(self.bytecode_viewer, "Bytecode")
        
        # Smali viewer tab
        self.smali_viewer = DexSmaliViewer()
        self.tab_widget.addTab(self.smali_viewer, "Smali")
        
        layout.addWidget(self.tab_widget)
        
        # Connect signals
        self.structure_viewer.item_selected.connect(self.on_structure_item_selected)
    
    def open_dex_file(self):
        """Open DEX file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open DEX File", "", "DEX Files (*.dex);;All Files (*)"
        )
        if file_path:
            self.load_dex_file(file_path)
    
    def load_dex_file(self, file_path: str):
        """Load DEX file"""
        try:
            # Validate DEX file
            from src.tools.dex_tools import DexTools
            
            is_valid, message = DexTools.validate_dex_file(file_path)
            if not is_valid:
                QMessageBox.warning(self, "Invalid DEX File", message)
                return
            
            self.current_file = file_path
            self.file_label.setText(f"File: {Path(file_path).name}")
            
            # Load in structure viewer
            if self.structure_viewer.load_dex_file(file_path):
                # Set file for Smali viewer
                self.smali_viewer.set_dex_file(file_path)
                
                self.file_opened.emit(file_path)
                QMessageBox.information(self, "Success", "DEX file loaded successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to parse DEX file")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load DEX file: {str(e)}")
    
    def validate_dex(self):
        """Validate current DEX file"""
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "No DEX file loaded")
            return
        
        from src.tools.dex_tools import DexTools
        
        is_valid, message = DexTools.validate_dex_file(self.current_file)
        if is_valid:
            QMessageBox.information(self, "Validation", message)
        else:
            QMessageBox.warning(self, "Validation Failed", message)
    
    def show_file_info(self):
        """Show DEX file information"""
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "No DEX file loaded")
            return
        
        from src.tools.dex_tools import DexTools
        
        info = DexTools.get_dex_info(self.current_file)
        
        info_text = "DEX File Information:\n\n"
        for key, value in info.items():
            info_text += f"{key}: {value}\n"
        
        QMessageBox.information(self, "DEX File Info", info_text)
    
    def on_structure_item_selected(self, item_type: str, item_data: dict):
        """Handle structure item selection"""
        # This could be used to show detailed information about selected items
        # or to navigate to specific bytecode sections
        pass
