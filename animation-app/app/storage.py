"""Asset storage and persistence for the animation application."""

import hashlib
import json
import os
from pathlib import Path
from typing import List, Optional

from .models import Asset


class AssetStorage:
    """Handles asset file storage and persistence."""
    
    ASSETS_DIR = "assets"
    ASSETS_METADATA_FILE = "assets.json"
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize the asset storage.
        
        Args:
            base_dir: Base directory for assets. If None, uses the directory
                     where this module is located.
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.assets_dir = self.base_dir / self.ASSETS_DIR
        self.metadata_file = self.base_dir / self.ASSETS_METADATA_FILE
        
        # Ensure assets directory exists
        self._ensure_assets_dir()
    
    def _ensure_assets_dir(self) -> None:
        """Create the assets directory if it doesn't exist."""
        if not self.assets_dir.exists():
            self.assets_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_filename(self, prompt: str, extension: str = "png") -> str:
        """Generate a collision-resistant filename from a prompt.
        
        Args:
            prompt: The prompt text to hash
            extension: File extension (default: png)
            
        Returns:
            A unique filename based on the prompt hash and timestamp
        """
        import time
        # Create a hash of the prompt and timestamp for uniqueness
        hash_input = f"{prompt}{time.time()}"
        prompt_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        return f"asset_{prompt_hash}.{extension}"
    
    def save_asset(self, image_data: bytes, prompt: str, 
                   display_name: Optional[str] = None) -> Asset:
        """Save image data as an asset file.
        
        Args:
            image_data: Binary image data
            prompt: The prompt used to generate the image
            display_name: Optional display name for the asset
            
        Returns:
            The created Asset object
        """
        # Generate filename
        filename = self._generate_filename(prompt)
        file_path = self.assets_dir / filename
        
        # Save the image data
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        # Get file info
        file_size = len(image_data)
        
        # Try to get image dimensions (without loading the whole image)
        width, height = 0, 0
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_data))
            width, height = img.size
        except (ImportError, Exception):
            # PIL not available or image data is invalid
            # Try to parse PNG header manually
            if image_data.startswith(b'\x89PNG\r\n\x1a\n'):
                # PNG file - parse IHDR chunk for dimensions
                # Bytes 16-23 are width and height (4 bytes each, big-endian)
                if len(image_data) >= 24:
                    width = int.from_bytes(image_data[16:20], byteorder='big')
                    height = int.from_bytes(image_data[20:24], byteorder='big')
        
        # Create asset
        asset = Asset(
            file_path=file_path,
            display_name=display_name or filename,
            prompt=prompt,
            file_size=file_size,
            width=width,
            height=height,
        )
        
        # Save metadata
        self._save_metadata(asset)
        
        return asset
    
    def _save_metadata(self, asset: Asset) -> None:
        """Save asset metadata to the metadata file."""
        # Load existing metadata
        assets_list = self.load_assets_metadata()
        
        # Update or add the asset
        existing_indices = [i for i, a in enumerate(assets_list) if a.id == asset.id]
        if existing_indices:
            assets_list[existing_indices[0]] = asset
        else:
            assets_list.append(asset)
        
        # Save back
        self._write_metadata(assets_list)
    
    def _write_metadata(self, assets: List[Asset]) -> None:
        """Write metadata list to file."""
        data = [asset.to_dict() for asset in assets]
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    def load_assets_metadata(self) -> List[Asset]:
        """Load all assets from metadata file.
        
        Returns:
            List of Asset objects
        """
        if not self.metadata_file.exists():
            return []
        
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Asset.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError):
            return []
    
    def get_all_assets(self) -> List[Asset]:
        """Get all assets that exist on disk.
        
        Returns:
            List of valid Asset objects
        """
        assets = self.load_assets_metadata()
        # Filter out assets whose files no longer exist
        return [a for a in assets if a.exists]
    
    def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset by ID.
        
        Args:
            asset_id: The ID of the asset to delete
            
        Returns:
            True if the asset was deleted, False otherwise
        """
        # Load assets
        assets = self.load_assets_metadata()
        
        # Find the asset
        asset_to_delete = None
        for asset in assets:
            if asset.id == asset_id:
                asset_to_delete = asset
                break
        
        if asset_to_delete is None:
            return False
        
        # Delete the file
        try:
            if asset_to_delete.exists:
                os.remove(asset_to_delete.file_path)
        except OSError:
            return False
        
        # Remove from metadata
        assets = [a for a in assets if a.id != asset_id]
        self._write_metadata(assets)
        
        return True
    
    def cleanup_missing_assets(self) -> int:
        """Remove metadata entries for assets that no longer exist on disk.
        
        Returns:
            Number of entries removed
        """
        assets = self.load_assets_metadata()
        original_count = len(assets)
        
        # Keep only assets that exist
        assets = [a for a in assets if a.exists]
        
        self._write_metadata(assets)
        
        return original_count - len(assets)
