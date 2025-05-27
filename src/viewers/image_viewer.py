"""
Image viewer widget for GP Manager
Supports viewing various image formats with zoom, pan, and basic editing features
"""
import os
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QScrollArea, QSlider, QToolBar,
                            QAction, QMessageBox, QFileDialog, QSizePolicy,
                            QFrame, QSpinBox, QComboBox)
from PyQt5.QtGui import QPixmap, QPainter, QTransform, QIcon, QFont


class ImageLabel(QLabel):
    """Custom label for displaying images with zoom and pan support"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(200, 200)
        self.setStyleSheet("border: 1px solid #555; background-color: #1e1e1e;")

        # Image properties
        self.original_pixmap = None
        self.scaled_pixmap = None
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.dragging = False
        self.last_pan_point = QPoint()

        # Enable mouse tracking for pan
        self.setMouseTracking(True)

    def set_image(self, pixmap):
        """Set the image to display"""
        self.original_pixmap = pixmap
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update_display()

    def update_display(self):
        """Update the displayed image based on zoom and pan"""
        if not self.original_pixmap:
            return

        # Calculate scaled size
        scaled_size = self.original_pixmap.size() * self.zoom_factor

        # Create scaled pixmap
        self.scaled_pixmap = self.original_pixmap.scaled(
            scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.setPixmap(self.scaled_pixmap)

    def zoom_in(self):
        """Zoom in by 25%"""
        self.zoom_factor = min(self.zoom_factor * 1.25, 10.0)
        self.update_display()

    def zoom_out(self):
        """Zoom out by 25%"""
        self.zoom_factor = max(self.zoom_factor * 0.8, 0.1)
        self.update_display()

    def zoom_to_fit(self):
        """Zoom to fit the widget"""
        if not self.original_pixmap:
            return

        widget_size = self.size()
        pixmap_size = self.original_pixmap.size()

        scale_x = widget_size.width() / pixmap_size.width()
        scale_y = widget_size.height() / pixmap_size.height()

        self.zoom_factor = min(scale_x, scale_y, 1.0)
        self.pan_offset = QPoint(0, 0)
        self.update_display()

    def zoom_actual_size(self):
        """Zoom to actual size (100%)"""
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update_display()

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def mousePressEvent(self, event):
        """Handle mouse press for panning"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_pan_point = event.pos()

    def mouseMoveEvent(self, event):
        """Handle mouse move for panning"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            delta = event.pos() - self.last_pan_point
            self.pan_offset += delta
            self.last_pan_point = event.pos()
            # Note: Full panning implementation would require custom painting

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.dragging = False


class ImageViewer(QWidget):
    """Image viewer widget with toolbar and controls"""

    image_changed = pyqtSignal(str)  # Emitted when image changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.image_files = []
        self.current_index = 0
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # Navigation actions
        self.prev_action = QAction("⬅️ Previous", self)
        self.prev_action.setShortcut("Left")
        self.prev_action.triggered.connect(self.previous_image)
        self.toolbar.addAction(self.prev_action)

        self.next_action = QAction("➡️ Next", self)
        self.next_action.setShortcut("Right")
        self.next_action.triggered.connect(self.next_image)
        self.toolbar.addAction(self.next_action)

        self.toolbar.addSeparator()

        # Zoom actions
        self.zoom_in_action = QAction("🔍+ Zoom In", self)
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.toolbar.addAction(self.zoom_in_action)

        self.zoom_out_action = QAction("🔍- Zoom Out", self)
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.toolbar.addAction(self.zoom_out_action)

        self.zoom_fit_action = QAction("📐 Fit", self)
        self.zoom_fit_action.setShortcut("Ctrl+0")
        self.zoom_fit_action.triggered.connect(self.zoom_to_fit)
        self.toolbar.addAction(self.zoom_fit_action)

        self.zoom_actual_action = QAction("🔍 100%", self)
        self.zoom_actual_action.setShortcut("Ctrl+1")
        self.zoom_actual_action.triggered.connect(self.zoom_actual_size)
        self.toolbar.addAction(self.zoom_actual_action)

        self.toolbar.addSeparator()

        # Rotation actions
        self.rotate_left_action = QAction("↺ Rotate Left", self)
        self.rotate_left_action.triggered.connect(self.rotate_left)
        self.toolbar.addAction(self.rotate_left_action)

        self.rotate_right_action = QAction("↻ Rotate Right", self)
        self.rotate_right_action.triggered.connect(self.rotate_right)
        self.toolbar.addAction(self.rotate_right_action)

        self.toolbar.addSeparator()

        # File actions
        self.open_action = QAction("📁 Open", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)
        self.toolbar.addAction(self.open_action)

        self.save_as_action = QAction("💾 Save As", self)
        self.save_as_action.setShortcut("Ctrl+S")
        self.save_as_action.triggered.connect(self.save_as)
        self.toolbar.addAction(self.save_as_action)

        layout.addWidget(self.toolbar)

        # Image display area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        self.image_label = ImageLabel()
        self.scroll_area.setWidget(self.image_label)

        layout.addWidget(self.scroll_area)

        # Status bar
        status_layout = QHBoxLayout()

        self.info_label = QLabel("No image loaded")
        self.info_label.setStyleSheet("color: #888; padding: 5px;")
        status_layout.addWidget(self.info_label)

        status_layout.addStretch()

        # Zoom control
        zoom_label = QLabel("Zoom:")
        status_layout.addWidget(zoom_label)

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 1000)  # 10% to 1000%
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        status_layout.addWidget(self.zoom_slider)

        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(40)
        status_layout.addWidget(self.zoom_label)

        layout.addLayout(status_layout)

    def setup_connections(self):
        """Setup signal connections"""
        pass

    def load_image(self, file_path):
        """Load an image file"""
        try:
            file_path = str(file_path)
            self.current_file = file_path

            print(f"DEBUG ImageViewer: Loading image: {file_path}")
            print(f"DEBUG ImageViewer: File exists: {Path(file_path).exists()}")

            # Load the image
            pixmap = QPixmap(file_path)
            print(f"DEBUG ImageViewer: QPixmap created, isNull: {pixmap.isNull()}")
            print(f"DEBUG ImageViewer: QPixmap size: {pixmap.size().width()}x{pixmap.size().height()}")

            if pixmap.isNull():
                print(f"DEBUG ImageViewer: QPixmap is null, raising exception")
                raise Exception("Failed to load image")

            # Set the image
            self.image_label.set_image(pixmap)
            print(f"DEBUG ImageViewer: Image set in label")

            # Update info
            file_info = Path(file_path)
            size_info = f"{pixmap.width()}×{pixmap.height()}"
            file_size = file_info.stat().st_size
            size_str = self.format_file_size(file_size)

            self.info_label.setText(
                f"{file_info.name} | {size_info} | {size_str}"
            )

            # Load directory images for navigation
            self.load_directory_images(file_path)

            # Update navigation buttons
            self.update_navigation_buttons()

            # Emit signal
            self.image_changed.emit(file_path)

            return True

        except Exception as e:
            QMessageBox.warning(self, "Image Viewer", f"Failed to load image: {str(e)}")
            return False

    def format_file_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def load_directory_images(self, file_path):
        """Load all images from the same directory"""
        try:
            directory = Path(file_path).parent
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff', '.ico'}

            self.image_files = []
            for file in directory.iterdir():
                if file.is_file() and file.suffix.lower() in image_extensions:
                    self.image_files.append(str(file))

            self.image_files.sort()

            # Find current index
            try:
                self.current_index = self.image_files.index(file_path)
            except ValueError:
                self.current_index = 0

        except Exception:
            self.image_files = [file_path]
            self.current_index = 0

    def update_navigation_buttons(self):
        """Update navigation button states"""
        has_multiple = len(self.image_files) > 1
        self.prev_action.setEnabled(has_multiple and self.current_index > 0)
        self.next_action.setEnabled(has_multiple and self.current_index < len(self.image_files) - 1)

    # Navigation methods
    def previous_image(self):
        """Go to previous image"""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image(self.image_files[self.current_index])

    def next_image(self):
        """Go to next image"""
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_image(self.image_files[self.current_index])

    # Zoom methods
    def zoom_in(self):
        """Zoom in"""
        self.image_label.zoom_in()
        self.update_zoom_display()

    def zoom_out(self):
        """Zoom out"""
        self.image_label.zoom_out()
        self.update_zoom_display()

    def zoom_to_fit(self):
        """Zoom to fit"""
        self.image_label.zoom_to_fit()
        self.update_zoom_display()

    def zoom_actual_size(self):
        """Zoom to actual size"""
        self.image_label.zoom_actual_size()
        self.update_zoom_display()

    def on_zoom_slider_changed(self, value):
        """Handle zoom slider change"""
        zoom_factor = value / 100.0
        self.image_label.zoom_factor = zoom_factor
        self.image_label.update_display()
        self.zoom_label.setText(f"{value}%")

    def update_zoom_display(self):
        """Update zoom display"""
        zoom_percent = int(self.image_label.zoom_factor * 100)
        self.zoom_slider.setValue(zoom_percent)
        self.zoom_label.setText(f"{zoom_percent}%")

    # Rotation methods
    def rotate_left(self):
        """Rotate image left (counter-clockwise)"""
        if self.image_label.original_pixmap:
            transform = QTransform().rotate(-90)
            rotated = self.image_label.original_pixmap.transformed(transform)
            self.image_label.set_image(rotated)

    def rotate_right(self):
        """Rotate image right (clockwise)"""
        if self.image_label.original_pixmap:
            transform = QTransform().rotate(90)
            rotated = self.image_label.original_pixmap.transformed(transform)
            self.image_label.set_image(rotated)

    # File operations
    def open_file(self):
        """Open file dialog to select image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp *.tiff *.ico);;All Files (*)"
        )
        if file_path:
            self.load_image(file_path)

    def save_as(self):
        """Save current image as"""
        if not self.image_label.scaled_pixmap:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image As", "",
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        if file_path:
            try:
                self.image_label.scaled_pixmap.save(file_path)
                QMessageBox.information(self, "Save Image", f"Image saved to: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Save Image", f"Failed to save image: {str(e)}")
