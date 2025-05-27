"""
File operations for MT Manager Linux
"""
import os
import shutil
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QMessageBox, QProgressDialog, QApplication


class FileOperationWorker(QThread):
    """Worker thread for file operations"""
    
    progress_updated = pyqtSignal(int)
    operation_finished = pyqtSignal(bool, str)
    
    def __init__(self, operation, source_paths, destination, parent=None):
        super().__init__(parent)
        self.operation = operation  # 'copy', 'move', 'delete'
        self.source_paths = source_paths
        self.destination = destination
        self.cancelled = False
    
    def run(self):
        """Execute the file operation"""
        try:
            if self.operation == 'copy':
                self._copy_files()
            elif self.operation == 'move':
                self._move_files()
            elif self.operation == 'delete':
                self._delete_files()
            
            if not self.cancelled:
                self.operation_finished.emit(True, "Operation completed successfully")
        except Exception as e:
            self.operation_finished.emit(False, str(e))
    
    def cancel(self):
        """Cancel the operation"""
        self.cancelled = True
    
    def _copy_files(self):
        """Copy files to destination"""
        total_files = len(self.source_paths)
        
        for i, source_path in enumerate(self.source_paths):
            if self.cancelled:
                break
            
            source = Path(source_path)
            dest_path = Path(self.destination) / source.name
            
            try:
                if source.is_dir():
                    shutil.copytree(str(source), str(dest_path))
                else:
                    shutil.copy2(str(source), str(dest_path))
            except Exception as e:
                raise Exception(f"Failed to copy {source.name}: {str(e)}")
            
            progress = int((i + 1) * 100 / total_files)
            self.progress_updated.emit(progress)
    
    def _move_files(self):
        """Move files to destination"""
        total_files = len(self.source_paths)
        
        for i, source_path in enumerate(self.source_paths):
            if self.cancelled:
                break
            
            source = Path(source_path)
            dest_path = Path(self.destination) / source.name
            
            try:
                shutil.move(str(source), str(dest_path))
            except Exception as e:
                raise Exception(f"Failed to move {source.name}: {str(e)}")
            
            progress = int((i + 1) * 100 / total_files)
            self.progress_updated.emit(progress)
    
    def _delete_files(self):
        """Delete files"""
        total_files = len(self.source_paths)
        
        for i, source_path in enumerate(self.source_paths):
            if self.cancelled:
                break
            
            source = Path(source_path)
            
            try:
                if source.is_dir():
                    shutil.rmtree(str(source))
                else:
                    source.unlink()
            except Exception as e:
                raise Exception(f"Failed to delete {source.name}: {str(e)}")
            
            progress = int((i + 1) * 100 / total_files)
            self.progress_updated.emit(progress)


class FileOperations(QObject):
    """File operations manager"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
    
    def copy_files(self, source_paths, destination):
        """Copy files with progress dialog"""
        self._execute_operation('copy', source_paths, destination)
    
    def move_files(self, source_paths, destination):
        """Move files with progress dialog"""
        self._execute_operation('move', source_paths, destination)
    
    def delete_files(self, source_paths):
        """Delete files with confirmation and progress dialog"""
        # Show confirmation dialog
        file_names = [Path(path).name for path in source_paths]
        if len(file_names) == 1:
            message = f"Are you sure you want to delete '{file_names[0]}'?"
        else:
            message = f"Are you sure you want to delete {len(file_names)} items?"
        
        reply = QMessageBox.question(
            self.parent_widget,
            "Confirm Delete",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._execute_operation('delete', source_paths, None)
    
    def _execute_operation(self, operation, source_paths, destination):
        """Execute file operation with progress dialog"""
        # Create progress dialog
        progress_dialog = QProgressDialog(
            f"{operation.capitalize()}ing files...",
            "Cancel",
            0, 100,
            self.parent_widget
        )
        progress_dialog.setWindowTitle(f"{operation.capitalize()} Files")
        progress_dialog.setModal(True)
        progress_dialog.show()
        
        # Create worker thread
        worker = FileOperationWorker(operation, source_paths, destination)
        
        # Connect signals
        worker.progress_updated.connect(progress_dialog.setValue)
        worker.operation_finished.connect(
            lambda success, message: self._on_operation_finished(
                success, message, progress_dialog, worker
            )
        )
        progress_dialog.canceled.connect(worker.cancel)
        
        # Start operation
        worker.start()
    
    def _on_operation_finished(self, success, message, progress_dialog, worker):
        """Handle operation completion"""
        progress_dialog.close()
        worker.quit()
        worker.wait()
        
        if success:
            # Emit signal to refresh file views
            if hasattr(self.parent_widget, 'refresh_views'):
                self.parent_widget.refresh_views()
        else:
            QMessageBox.critical(
                self.parent_widget,
                "Operation Failed",
                message
            )
    
    def rename_file(self, old_path, new_name):
        """Rename a file or directory"""
        try:
            old_path = Path(old_path)
            new_path = old_path.parent / new_name
            
            if new_path.exists():
                QMessageBox.warning(
                    self.parent_widget,
                    "Rename Failed",
                    f"A file or folder named '{new_name}' already exists."
                )
                return False
            
            old_path.rename(new_path)
            
            # Refresh file views
            if hasattr(self.parent_widget, 'refresh_views'):
                self.parent_widget.refresh_views()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self.parent_widget,
                "Rename Failed",
                f"Failed to rename: {str(e)}"
            )
            return False
    
    def create_folder(self, parent_path, folder_name):
        """Create a new folder"""
        try:
            new_folder_path = Path(parent_path) / folder_name
            
            if new_folder_path.exists():
                QMessageBox.warning(
                    self.parent_widget,
                    "Create Folder Failed",
                    f"A folder named '{folder_name}' already exists."
                )
                return False
            
            new_folder_path.mkdir(parents=True)
            
            # Refresh file views
            if hasattr(self.parent_widget, 'refresh_views'):
                self.parent_widget.refresh_views()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self.parent_widget,
                "Create Folder Failed",
                f"Failed to create folder: {str(e)}"
            )
            return False
