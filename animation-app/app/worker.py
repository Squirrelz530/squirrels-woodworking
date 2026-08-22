"""Worker thread for background image generation."""

from PySide6.QtCore import QObject, QThread, Signal, Slot
from typing import Optional

from .api import ImageGenerationAPI
from .models import Asset, GenerationRequest, GenerationResult
from .storage import AssetStorage


class GenerationWorker(QObject):
    """Worker that performs image generation in a background thread."""
    
    # Signals
    generation_started = Signal()
    generation_progress = Signal(int)  # Percent complete (0-100)
    generation_complete = Signal(Asset)  # Successfully generated asset
    generation_failed = Signal(str)  # Error message
    
    def __init__(self, api: ImageGenerationAPI, storage: AssetStorage):
        """Initialize the worker.
        
        Args:
            api: The image generation API client
            storage: The asset storage for saving results
        """
        super().__init__()
        self.api = api
        self.storage = storage
        self.request: Optional[GenerationRequest] = None
        self._is_cancelled = False
    
    def cancel(self) -> None:
        """Cancel the current generation."""
        self._is_cancelled = True
    
    @Slot()
    def run(self) -> None:
        """Perform the image generation in the background thread."""
        if self.request is None:
            self.generation_failed.emit("No generation request provided")
            return
        
        if self._is_cancelled:
            return
        
        # Emit started signal
        self.generation_started.emit()
        
        # Update progress
        self.generation_progress.emit(0)
        
        try:
            # Generate the image
            self.generation_progress.emit(30)
            result = self.api.generate_image(self.request)
            
            if self._is_cancelled:
                return
            
            if not result.success:
                self.generation_failed.emit(result.error_message or "Unknown error")
                return
            
            self.generation_progress.emit(60)
            
            # Save the asset
            if result.image_data:
                asset = self.storage.save_asset(
                    image_data=result.image_data,
                    prompt=self.request.prompt,
                )
                self.generation_progress.emit(90)
                
                if self._is_cancelled:
                    # Clean up the saved file if cancelled
                    try:
                        import os
                        if asset.exists:
                            os.remove(asset.file_path)
                    except OSError:
                        pass
                    return
                
                self.generation_progress.emit(100)
                self.generation_complete.emit(asset)
            else:
                self.generation_failed.emit("No image data received")
                
        except Exception as e:
            self.generation_failed.emit(f"Generation error: {str(e)}")


class WorkerManager(QObject):
    """Manages worker threads for image generation."""
    
    # Signals that forward from the worker
    generation_started = Signal()
    generation_progress = Signal(int)
    generation_complete = Signal(Asset)
    generation_failed = Signal(str)
    
    def __init__(self, api: ImageGenerationAPI, storage: AssetStorage):
        """Initialize the worker manager.
        
        Args:
            api: The image generation API client
            storage: The asset storage for saving results
        """
        super().__init__()
        self.api = api
        self.storage = storage
        self.current_worker: Optional[GenerationWorker] = None
        self.worker_thread: Optional[QThread] = None
    
    def is_generating(self) -> bool:
        """Check if a generation is currently in progress."""
        return self.current_worker is not None and self.worker_thread is not None
    
    def start_generation(self, request: GenerationRequest) -> bool:
        """Start a new image generation.
        
        Args:
            request: The generation request
            
        Returns:
            True if generation started, False if already generating
        """
        if self.is_generating():
            return False
        
        # Clean up any previous worker
        self.cancel_generation()
        
        # Create new worker and thread
        self.worker_thread = QThread()
        self.current_worker = GenerationWorker(self.api, self.storage)
        self.current_worker.request = request
        self.current_worker.moveToThread(self.worker_thread)
        
        # Connect signals
        # Forward worker signals to manager signals
        self.current_worker.generation_started.connect(self.generation_started)
        self.current_worker.generation_progress.connect(self.generation_progress)
        self.current_worker.generation_complete.connect(self.generation_complete)
        self.current_worker.generation_failed.connect(self.generation_failed)
        
        # Connect thread started to worker run
        self.worker_thread.started.connect(self.current_worker.run)
        
        # Start the thread
        self.worker_thread.start()
        
        return True
    
    def cancel_generation(self) -> None:
        """Cancel the current generation if in progress."""
        if self.current_worker:
            self.current_worker.cancel()
        
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait(1000)  # Wait up to 1 second
        
        # Clean up references
        self.current_worker = None
        self.worker_thread = None
    
    def cleanup(self) -> None:
        """Clean up all worker resources."""
        self.cancel_generation()
