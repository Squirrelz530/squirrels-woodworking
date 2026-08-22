"""Tests for the asset storage."""

import pytest
import tempfile
from pathlib import Path
from app.storage import AssetStorage
from app.models import Asset


class TestAssetStorage:
    """Tests for the AssetStorage class."""
    
    def test_init(self, tmp_path):
        """Test storage initialization."""
        storage = AssetStorage(tmp_path)
        assert storage.base_dir == tmp_path
        assert storage.assets_dir == tmp_path / "assets"
        assert storage.metadata_file == tmp_path / "assets.json"
        
        # Assets directory should be created
        assert storage.assets_dir.exists()
    
    def test_save_and_load_asset(self, tmp_path):
        """Test saving and loading an asset."""
        storage = AssetStorage(tmp_path)
        
        # Create test image data (minimal PNG)
        # This is a minimal valid PNG file
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        # Save asset
        asset = storage.save_asset(
            image_data=png_data,
            prompt="test prompt",
        )
        
        assert asset is not None
        assert asset.id is not None
        assert asset.file_path.exists()
        assert asset.prompt == "test prompt"
        
        # Load assets
        assets = storage.get_all_assets()
        assert len(assets) >= 1
        
        # Find the saved asset
        found = False
        for a in assets:
            if a.id == asset.id:
                found = True
                break
        assert found
    
    def test_cleanup_missing_assets(self, tmp_path):
        """Test cleaning up missing assets."""
        storage = AssetStorage(tmp_path)
        
        # Create a directory for testing
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Create a test file
        test_file = assets_dir / "test.png"
        test_file.write_bytes(b"test")
        
        # Save an asset
        storage.save_asset(b"test", "prompt 1")
        
        # Manually add a metadata entry for a non-existent file
        import json
        from datetime import datetime
        
        # Read existing metadata
        if storage.metadata_file.exists():
            with open(storage.metadata_file, "r") as f:
                data = json.load(f)
        else:
            data = []
        
        # Add a fake entry
        fake_asset = {
            "id": "fake-123",
            "file_path": str(assets_dir / "nonexistent.png"),
            "display_name": "Fake Asset",
            "prompt": "fake",
            "created_at": datetime.now().isoformat(),
            "width": 0,
            "height": 0,
            "file_size": 0,
        }
        data.append(fake_asset)
        
        with open(storage.metadata_file, "w") as f:
            json.dump(data, f)
        
        # Now cleanup should remove the fake entry
        removed = storage.cleanup_missing_assets()
        assert removed >= 1
        
        # Verify the fake asset is gone
        assets = storage.load_assets_metadata()
        fake_found = any(a.id == "fake-123" for a in assets)
        assert not fake_found
    
    def test_delete_asset(self, tmp_path):
        """Test deleting an asset."""
        storage = AssetStorage(tmp_path)
        
        # Save an asset
        asset = storage.save_asset(b"test data", "test prompt")
        asset_id = asset.id
        
        # Verify it exists
        assert asset.exists
        
        # Delete it
        result = storage.delete_asset(asset_id)
        assert result is True
        
        # Verify it's gone
        assert not asset.exists
        
        # Verify it's not in metadata
        assets = storage.get_all_assets()
        assert not any(a.id == asset_id for a in assets)
    
    def test_generate_filename(self, tmp_path):
        """Test filename generation."""
        storage = AssetStorage(tmp_path)
        
        # Generate two filenames with the same prompt
        name1 = storage._generate_filename("test prompt")
        name2 = storage._generate_filename("test prompt")
        
        # They should be different due to timestamp
        assert name1 != name2
        
        # Both should start with "asset_"
        assert name1.startswith("asset_")
        assert name2.startswith("asset_")
        
        # Both should end with ".png"
        assert name1.endswith(".png")
        assert name2.endswith(".png")
