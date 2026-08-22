"""Main application window for the animation app."""

import os
from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QPixmap, QImageReader, QPalette
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem,
    QSlider, QGroupBox, QFrame, QMessageBox, QProgressBar,
    QSizePolicy, QFileDialog
)
from typing import Optional, List

from .api import ImageGenerationAPI
from .models import Asset, GenerationRequest, TimelineState
from .storage import AssetStorage
from .worker import WorkerManager


class MainWindow(QMainWindow):
    """Main application window with sidebar, preview, and timeline."""
    
    # Custom signals
    asset_selected = Signal(Asset)
    generation_started = Signal()
    generation_complete = Signal(Asset)
    
    def __init__(self, api: ImageGenerationAPI, storage: AssetStorage):
        """Initialize the main window.
        
        Args:
            api: The image generation API client
            storage: The asset storage
        """
        super().__init__()
        self.api = api
        self.storage = storage
        
        # Initialize state before UI setup
        self.worker_manager = WorkerManager(api, storage)
        self.timeline_state = TimelineState()
        self.playback_timer: Optional[QTimer] = None
        self.current_asset: Optional[Asset] = None
        
        # Initialize UI
        self._setup_ui()
        self._setup_menu()
        self._setup_connections()
        
        # Load assets
        self._load_assets()
        
        # Window settings
        self.setWindowTitle("AI Animation Studio")
        self.resize(1024, 768)
    
    def _setup_ui(self) -> None:
        """Set up the main UI layout."""
        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for sidebar and main content
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # Sidebar width
        self.splitter.setStretchFactor(0, 0)  # Sidebar doesn't stretch
        self.splitter.setStretchFactor(1, 1)   # Main content stretches
        
        # Create sidebar
        self.sidebar = self._create_sidebar()
        self.splitter.addWidget(self.sidebar)
        
        # Create main content area
        self.main_content = self._create_main_content()
        self.splitter.addWidget(self.main_content)
        
        # Set initial splitter sizes
        self.splitter.setSizes([250, 700])
    
    def _create_sidebar(self) -> QWidget:
        """Create the sidebar widget with prompt input and asset list."""
        sidebar = QWidget()
        sidebar.setMinimumWidth(200)
        sidebar.setMaximumWidth(350)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # --- Prompt Section ---
        prompt_group = QGroupBox("Generate Image")
        prompt_layout = QVBoxLayout(prompt_group)
        
        # Prompt input
        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Enter your prompt... (e.g., 'a beautiful sunset over mountains')")
        prompt_layout.addWidget(self.prompt_input)
        
        # Generate button
        self.generate_button = QPushButton("Generate")
        self.generate_button.setIcon(self._create_icon("🎨"))
        self.generate_button.setEnabled(True)
        prompt_layout.addWidget(self.generate_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        prompt_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #666;")
        prompt_layout.addWidget(self.status_label)
        
        layout.addWidget(prompt_group, stretch=0)
        
        # --- Assets Section ---
        assets_group = QGroupBox("Assets")
        assets_layout = QVBoxLayout(assets_group)
        
        # Asset list
        self.asset_list = QListWidget()
        self.asset_list.setIconSize(QSize(48, 48))
        self.asset_list.setSpacing(5)
        self.asset_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        assets_layout.addWidget(self.asset_list)
        
        # Asset actions
        actions_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setIcon(self._create_icon("🔄"))
        actions_layout.addWidget(self.refresh_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.setIcon(self._create_icon("🗑️"))
        self.delete_button.setEnabled(False)
        actions_layout.addWidget(self.delete_button)
        
        actions_layout.addStretch()
        assets_layout.addLayout(actions_layout)
        
        layout.addWidget(assets_group, stretch=1)
        
        return sidebar
    
    def _create_main_content(self) -> QWidget:
        """Create the main content area with preview and timeline."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # --- Preview Section ---
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Preview label
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 400)
        self.preview_label.setStyleSheet("background-color: #222; border: 1px dashed #666;")
        self.preview_label.setText("No image selected\nGenerate or select an asset to preview")
        preview_layout.addWidget(self.preview_label, stretch=1)
        
        # Asset info
        self.asset_info_label = QLabel()
        self.asset_info_label.setStyleSheet("color: #888;")
        self.asset_info_label.setWordWrap(True)
        preview_layout.addWidget(self.asset_info_label)
        
        layout.addWidget(preview_group, stretch=1)
        
        # --- Timeline Section ---
        timeline_group = QGroupBox("Timeline")
        timeline_layout = QVBoxLayout(timeline_group)
        
        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 100)
        self.timeline_slider.setValue(0)
        self.timeline_slider.setTickPosition(QSlider.TicksBelow)
        timeline_layout.addWidget(self.timeline_slider)
        
        # Timeline controls
        controls_layout = QHBoxLayout()
        
        # Time display
        self.time_display = QLabel("00:00 / 00:00")
        self.time_display.setStyleSheet("font-family: monospace; font-size: 14px;")
        controls_layout.addWidget(self.time_display)
        
        controls_layout.addStretch()
        
        # Play/pause button
        self.play_button = QPushButton("Play")
        self.play_button.setIcon(self._create_icon("▶️"))
        self.play_button.setCheckable(True)
        controls_layout.addWidget(self.play_button)
        
        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setIcon(self._create_icon("⏹️"))
        controls_layout.addWidget(self.stop_button)
        
        # Frame display
        self.frame_display = QLabel("Frame: 0/0")
        self.frame_display.setStyleSheet("font-family: monospace;")
        controls_layout.addWidget(self.frame_display)
        
        timeline_layout.addLayout(controls_layout)
        
        layout.addWidget(timeline_group, stretch=0)
        
        return content
    
    def _setup_menu(self) -> None:
        """Set up the application menu."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_act = QAction("Open Asset...", self)
        open_act.triggered.connect(self._open_asset)
        file_menu.addAction(open_act)
        
        file_menu.addSeparator()
        
        exit_act = QAction("Exit", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        refresh_act = QAction("Refresh Assets", self)
        refresh_act.triggered.connect(self._refresh_assets)
        view_menu.addAction(refresh_act)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_act = QAction("About", self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)
    
    def _setup_connections(self) -> None:
        """Set up signal connections."""
        # Generate button
        self.generate_button.clicked.connect(self._handle_generate)
        
        # Asset list
        self.asset_list.itemSelectionChanged.connect(self._handle_asset_selected)
        self.asset_list.itemDoubleClicked.connect(self._handle_asset_double_clicked)
        
        # Asset actions
        self.refresh_button.clicked.connect(self._refresh_assets)
        self.delete_button.clicked.connect(self._handle_delete_asset)
        
        # Timeline
        self.timeline_slider.valueChanged.connect(self._handle_timeline_changed)
        self.play_button.toggled.connect(self._handle_play_toggled)
        self.stop_button.clicked.connect(self._handle_stop_clicked)
        
        # Worker connections
        self.worker_manager.generation_started.connect(
            self._handle_worker_started
        )
        self.worker_manager.generation_progress.connect(
            self._handle_worker_progress
        )
        self.worker_manager.generation_complete.connect(
            self._handle_worker_complete
        )
        self.worker_manager.generation_failed.connect(
            self._handle_worker_failed
        )
    
    def _create_icon(self, text: str) -> QIcon:
        """Create an icon from text (fallback when no actual icon available)."""
        # For simplicity, we'll just return an empty icon
        # In a real app, you'd use proper icons
        return QIcon()
    
    def _load_assets(self) -> None:
        """Load assets from storage and populate the list."""
        self.asset_list.clear()
        assets = self.storage.get_all_assets()
        
        for asset in assets:
            self._add_asset_to_list(asset)
        
        if assets:
            self.asset_list.setCurrentRow(0)
            self._show_asset_preview(assets[0])
        else:
            self._clear_preview()
    
    def _add_asset_to_list(self, asset: Asset) -> None:
        """Add an asset to the list widget."""
        item = QListWidgetItem()
        item.setText(asset.display_name)
        item.setData(Qt.UserRole, asset.id)
        item.setToolTip(f"Prompt: {asset.prompt}\nSize: {asset.width}x{asset.height}\nCreated: {asset.created_at}")
        
        # Try to load a thumbnail
        if asset.exists:
            try:
                pixmap = QPixmap(str(asset.file_path))
                if not pixmap.isNull():
                    # Scale to 48x48
                    pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    item.setIcon(QIcon(pixmap))
            except Exception:
                pass
        
        self.asset_list.addItem(item)
    
    def _handle_generate(self) -> None:
        """Handle the generate button click."""
        prompt = self.prompt_input.text().strip()
        
        if not prompt:
            QMessageBox.warning(self, "Empty Prompt", "Please enter a prompt to generate an image.")
            return
        
        # Validate prompt
        is_valid, error_msg = self.api.validate_prompt(prompt)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Prompt", error_msg)
            return
        
        # Check if already generating
        if self.worker_manager.is_generating():
            QMessageBox.information(self, "Busy", "Please wait for the current generation to complete.")
            return
        
        # Disable controls
        self._set_generating_state(True)
        
        # Create request
        request = GenerationRequest(
            prompt=prompt,
            width=512,
            height=512,
        )
        
        # Start generation
        self.status_label.setText(f"Generating: {prompt[:50]}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.worker_manager.start_generation(request)
    
    def _set_generating_state(self, generating: bool) -> None:
        """Enable or disable controls based on generation state."""
        self.generate_button.setEnabled(not generating)
        self.prompt_input.setEnabled(not generating)
        self.refresh_button.setEnabled(not generating)
        self.delete_button.setEnabled(not generating and self.asset_list.currentItem() is not None)
    
    def _handle_worker_started(self) -> None:
        """Handle worker started signal."""
        self.generation_started.emit()
    
    def _handle_worker_progress(self, percent: int) -> None:
        """Handle worker progress signal."""
        self.progress_bar.setValue(percent)
    
    def _handle_worker_complete(self, asset: Asset) -> None:
        """Handle worker complete signal."""
        # Add to list
        self._add_asset_to_list(asset)
        
        # Select and show the new asset
        for i in range(self.asset_list.count()):
            item = self.asset_list.item(i)
            if item.data(Qt.UserRole) == asset.id:
                self.asset_list.setCurrentRow(i)
                self._show_asset_preview(asset)
                break
        
        # Clean up
        self._handle_generation_finished()
        
        # Emit signal
        self.generation_complete.emit(asset)
    
    def _handle_worker_failed(self, error: str) -> None:
        """Handle worker failed signal."""
        self.status_label.setText(f"Error: {error}")
        QMessageBox.critical(self, "Generation Failed", error)
        self._handle_generation_finished()
    
    def _handle_generation_finished(self) -> None:
        """Clean up after generation finishes."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("")
        self._set_generating_state(False)
        
        # Clean up worker
        self.worker_manager.cleanup()
    
    def _handle_asset_selected(self) -> None:
        """Handle asset selection changed."""
        item = self.asset_list.currentItem()
        if item is None:
            self._clear_preview()
            self.delete_button.setEnabled(False)
            return
        
        asset_id = item.data(Qt.UserRole)
        assets = self.storage.get_all_assets()
        
        for asset in assets:
            if asset.id == asset_id:
                self._show_asset_preview(asset)
                self.current_asset = asset
                self.delete_button.setEnabled(True)
                break
    
    def _handle_asset_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle asset double click (open in external viewer)."""
        asset_id = item.data(Qt.UserRole)
        assets = self.storage.get_all_assets()
        
        for asset in assets:
            if asset.id == asset_id and asset.exists:
                # Open with default viewer
                import subprocess
                import sys
                if sys.platform == "win32":
                    os.startfile(str(asset.file_path))
                elif sys.platform == "darwin":
                    subprocess.run(["open", str(asset.file_path)])
                else:
                    subprocess.run(["xdg-open", str(asset.file_path)])
                break
    
    def _show_asset_preview(self, asset: Asset) -> None:
        """Display an asset in the preview area."""
        self.current_asset = asset
        
        if asset.exists:
            try:
                pixmap = QPixmap(str(asset.file_path))
                if not pixmap.isNull():
                    # Scale to fit the preview area
                    scaled_pixmap = pixmap.scaled(
                        self.preview_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.preview_label.setPixmap(scaled_pixmap)
                    self.asset_info_label.setText(
                        f"<b>{asset.display_name}</b><br/>"
                        f"Prompt: {asset.prompt[:100]}<br/>"
                        f"Size: {asset.width}x{asset.height} | {asset.file_size / 1024:.1f} KB"
                    )
                else:
                    self._clear_preview()
            except Exception as e:
                self._clear_preview()
                self.asset_info_label.setText(f"Error loading image: {str(e)}")
        else:
            self._clear_preview()
            self.asset_info_label.setText(f"Asset file not found: {asset.display_name}")
    
    def _clear_preview(self) -> None:
        """Clear the preview area."""
        self.preview_label.clear()
        self.preview_label.setText("No image selected\nGenerate or select an asset to preview")
        self.asset_info_label.clear()
        self.current_asset = None
    
    def _refresh_assets(self) -> None:
        """Refresh the asset list."""
        # Clean up any missing assets
        removed = self.storage.cleanup_missing_assets()
        
        if removed > 0:
            self.status_label.setText(f"Removed {removed} missing asset(s)")
        
        self._load_assets()
    
    def _handle_delete_asset(self) -> None:
        """Handle delete button click."""
        item = self.asset_list.currentItem()
        if item is None:
            return
        
        asset_id = item.data(Qt.UserRole)
        
        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Delete Asset",
            "Are you sure you want to delete this asset?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            # Delete the asset
            if self.storage.delete_asset(asset_id):
                self._refresh_assets()
                self.status_label.setText("Asset deleted")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete asset")
    
    def _open_asset(self) -> None:
        """Open an asset file from disk."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            str(self.storage.assets_dir),
            "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            import shutil
            from pathlib import Path
            
            # Copy to assets directory
            dest_path = self.storage.assets_dir / Path(file_path).name
            shutil.copy2(file_path, str(dest_path))
            
            # Create asset
            with open(file_path, "rb") as f:
                image_data = f.read()
            
            prompt = Path(file_path).stem.replace("_", " ")
            asset = self.storage.save_asset(
                image_data=image_data,
                prompt=prompt,
                display_name=Path(file_path).name
            )
            
            self._refresh_assets()
            
            # Select the new asset
            for i in range(self.asset_list.count()):
                item = self.asset_list.item(i)
                if item.data(Qt.UserRole) == asset.id:
                    self.asset_list.setCurrentRow(i)
                    break
    
    def _handle_timeline_changed(self, value: int) -> None:
        """Handle timeline slider value changed."""
        # For now, just update the display
        # In a full animation app, this would update the current frame
        total_seconds = self.timeline_state.duration_seconds
        current_seconds = (value / 100) * total_seconds
        
        self.timeline_state.current_time_seconds = current_seconds
        self.time_display.setText(f"{self.timeline_state.current_time_str} / {self.timeline_state.duration_str}")
        self.frame_display.setText(f"Frame: {self.timeline_state.current_frame}/{self.timeline_state.total_frames}")
    
    def _handle_play_toggled(self, checked: bool) -> None:
        """Handle play/pause button toggled."""
        if checked:
            self._start_playback()
        else:
            self._stop_playback()
    
    def _handle_stop_clicked(self) -> None:
        """Handle stop button clicked."""
        self._stop_playback()
        self.timeline_slider.setValue(0)
        self.timeline_state.current_time_seconds = 0
        self.time_display.setText(f"{self.timeline_state.current_time_str} / {self.timeline_state.duration_str}")
        self.frame_display.setText(f"Frame: {self.timeline_state.current_frame}/{self.timeline_state.total_frames}")
    
    def _start_playback(self) -> None:
        """Start timeline playback."""
        if self.playback_timer is None:
            self.playback_timer = QTimer()
            self.playback_timer.timeout.connect(self._update_playback)
        
        # Calculate interval based on FPS
        interval_ms = int(1000 / self.timeline_state.fps)
        self.playback_timer.start(interval_ms)
        self.timeline_state.is_playing = True
    
    def _stop_playback(self) -> None:
        """Stop timeline playback."""
        if self.playback_timer and self.playback_timer.isActive():
            self.playback_timer.stop()
        self.timeline_state.is_playing = False
        self.play_button.setChecked(False)
    
    def _update_playback(self) -> None:
        """Update playback position."""
        current_frame = self.timeline_state.current_frame
        total_frames = self.timeline_state.total_frames
        
        if total_frames > 0:
            current_frame = (current_frame + 1) % total_frames
            self.timeline_state.current_time_seconds = current_frame / self.timeline_state.fps
            
            # Update slider
            percent = int((current_frame / total_frames) * 100)
            self.timeline_slider.setValue(percent)
            
            # Update display
            self.time_display.setText(
                f"{self.timeline_state.current_time_str} / {self.timeline_state.duration_str}"
            )
            self.frame_display.setText(
                f"Frame: {self.timeline_state.current_frame}/{self.timeline_state.total_frames}"
            )
    
    def _show_about(self) -> None:
        """Show the about dialog."""
        about_text = """
        <h2>AI Animation Studio</h2>
        <p>Version 0.1.0</p>
        <p>A desktop application for generating animation frames using cloud AI image generation.</p>
        <p><b>Provider:</b> Pollinations.ai (free, no authentication required)</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Generate images from text prompts</li>
            <li>Asset management with previews</li>
            <li>Timeline controls</li>
            <li>Threaded generation (keeps UI responsive)</li>
        </ul>
        """
        QMessageBox.about(self, "About AI Animation Studio", about_text)
    
    def closeEvent(self, event) -> None:
        """Handle close event."""
        # Clean up worker
        self.worker_manager.cleanup()
        
        # Stop playback if active
        self._stop_playback()
        
        event.accept()
