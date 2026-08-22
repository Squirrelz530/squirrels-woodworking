"""Tests for data models."""

import pytest
from datetime import datetime
from pathlib import Path
from app.models import Asset, GenerationRequest, GenerationResult, TimelineState


class TestAsset:
    """Tests for the Asset model."""
    
    def test_asset_creation(self):
        """Test creating an asset with default values."""
        asset = Asset()
        assert asset.id is not None
        assert asset.file_path == Path()
        assert asset.display_name == ""
        assert asset.prompt == ""
        assert asset.file_size == 0
        assert asset.width == 0
        assert asset.height == 0
    
    def test_asset_with_values(self):
        """Test creating an asset with specific values."""
        asset = Asset(
            id="test-123",
            file_path=Path("/path/to/image.png"),
            display_name="Test Image",
            prompt="A test prompt",
            width=512,
            height=512,
            file_size=1024,
        )
        assert asset.id == "test-123"
        assert asset.file_path == Path("/path/to/image.png")
        assert asset.display_name == "Test Image"
        assert asset.prompt == "A test prompt"
        assert asset.width == 512
        assert asset.height == 512
        assert asset.file_size == 1024
    
    def test_asset_exists(self, tmp_path):
        """Test the exists property."""
        # Create a test file
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"test data")
        
        # Asset with existing file
        asset = Asset(file_path=test_file)
        assert asset.exists
        
        # Asset with non-existing file
        asset2 = Asset(file_path=tmp_path / "nonexistent.png")
        assert not asset2.exists
    
    def test_asset_to_dict(self):
        """Test converting asset to dictionary."""
        asset = Asset(
            id="test-123",
            file_path=Path("/path/to/image.png"),
            display_name="Test Image",
            prompt="A test prompt",
        )
        data = asset.to_dict()
        
        assert data["id"] == "test-123"
        assert data["file_path"] == "/path/to/image.png" or data["file_path"] == "\\path\\to\\image.png"
        assert data["display_name"] == "Test Image"
        assert data["prompt"] == "A test prompt"
    
    def test_asset_from_dict(self):
        """Test creating asset from dictionary."""
        data = {
            "id": "test-456",
            "file_path": "/path/to/image.png",
            "display_name": "Test Image 2",
            "prompt": "Another prompt",
        }
        asset = Asset.from_dict(data)
        
        assert asset.id == "test-456"
        assert asset.file_path == Path("/path/to/image.png")
        assert asset.display_name == "Test Image 2"
        assert asset.prompt == "Another prompt"


class TestGenerationRequest:
    """Tests for the GenerationRequest model."""
    
    def test_default_request(self):
        """Test creating a request with default values."""
        request = GenerationRequest(prompt="test")
        assert request.prompt == "test"
        assert request.width == 512
        assert request.height == 512
        assert request.seed is None
        assert request.nolog is True
    
    def test_custom_request(self):
        """Test creating a request with custom values."""
        request = GenerationRequest(
            prompt="custom prompt",
            width=1024,
            height=768,
            seed=12345,
            nolog=False,
        )
        assert request.prompt == "custom prompt"
        assert request.width == 1024
        assert request.height == 768
        assert request.seed == 12345
        assert request.nolog is False
    
    def test_to_pollinations_params(self):
        """Test converting request to Pollinations.ai parameters."""
        request = GenerationRequest(
            prompt="test prompt",
            width=1024,
            height=768,
            seed=12345,
        )
        params = request.to_pollinations_params()
        
        assert params["prompt"] == "test prompt"
        assert params["width"] == 1024
        assert params["height"] == 768
        assert params["seed"] == 12345
        assert params["nolog"] == "true"


class TestGenerationResult:
    """Tests for the GenerationResult model."""
    
    def test_successful_result(self):
        """Test a successful generation result."""
        result = GenerationResult(
            success=True,
            image_data=b"image data",
        )
        assert result.success is True
        assert result.is_valid is True
        assert result.image_data == b"image data"
    
    def test_failed_result(self):
        """Test a failed generation result."""
        result = GenerationResult(
            success=False,
            error_message="Error occurred",
        )
        assert result.success is False
        assert result.is_valid is False
        assert result.error_message == "Error occurred"


class TestTimelineState:
    """Tests for the TimelineState model."""
    
    def test_default_state(self):
        """Test default timeline state."""
        state = TimelineState()
        assert state.duration_seconds == 0.0
        assert state.current_time_seconds == 0.0
        assert state.is_playing is False
        assert state.fps == 24.0
    
    def test_duration_str(self):
        """Test duration string formatting."""
        state = TimelineState(duration_seconds=125.5)
        assert state.duration_str == "02:05"
    
    def test_current_time_str(self):
        """Test current time string formatting."""
        state = TimelineState(current_time_seconds=45.0)
        assert state.current_time_str == "00:45"
    
    def test_frame_calculations(self):
        """Test frame calculations."""
        state = TimelineState(
            duration_seconds=2.0,
            current_time_seconds=1.0,
            fps=24.0,
        )
        assert state.current_frame == 24
        assert state.total_frames == 48
