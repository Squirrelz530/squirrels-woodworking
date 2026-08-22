"""Data models for the animation application."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4


@dataclass
class Asset:
    """Represents a generated image asset."""
    id: str = field(default_factory=lambda: str(uuid4()))
    file_path: Path = field(default_factory=Path)
    display_name: str = ""
    prompt: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    width: int = 0
    height: int = 0
    file_size: int = 0
    
    def __post_init__(self):
        if isinstance(self.file_path, str):
            self.file_path = Path(self.file_path)
    
    @property
    def exists(self) -> bool:
        """Check if the asset file exists on disk."""
        return self.file_path.exists() and self.file_path.is_file()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "file_path": str(self.file_path),
            "display_name": self.display_name,
            "prompt": self.prompt,
            "created_at": self.created_at.isoformat(),
            "width": self.width,
            "height": self.height,
            "file_size": self.file_size,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Asset":
        """Create an Asset from a dictionary."""
        return cls(
            id=data.get("id", str(uuid4())),
            file_path=data.get("file_path", ""),
            display_name=data.get("display_name", ""),
            prompt=data.get("prompt", ""),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            width=data.get("width", 0),
            height=data.get("height", 0),
            file_size=data.get("file_size", 0),
        )


@dataclass
class GenerationRequest:
    """Represents a request to generate an image."""
    prompt: str
    width: int = 512
    height: int = 512
    seed: Optional[int] = None
    nolog: bool = True  # Don't log the request on the server
    
    def to_pollinations_params(self) -> dict:
        """Convert to parameters for Pollinations.ai API."""
        params = {
            "prompt": self.prompt,
            "width": self.width,
            "height": self.height,
            "nolog": str(self.nolog).lower(),
        }
        if self.seed is not None:
            params["seed"] = self.seed
        return params


@dataclass
class GenerationResult:
    """Result of an image generation request."""
    success: bool
    image_data: Optional[bytes] = None
    file_path: Optional[Path] = None
    error_message: Optional[str] = None
    asset: Optional[Asset] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if the result contains valid image data."""
        return self.success and self.image_data is not None


@dataclass
class TimelineState:
    """Represents the timeline state."""
    duration_seconds: float = 0.0
    current_time_seconds: float = 0.0
    is_playing: bool = False
    fps: float = 24.0
    
    @property
    def duration_str(self) -> str:
        """Format duration as MM:SS."""
        minutes = int(self.duration_seconds // 60)
        seconds = int(self.duration_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def current_time_str(self) -> str:
        """Format current time as MM:SS."""
        minutes = int(self.current_time_seconds // 60)
        seconds = int(self.current_time_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def current_frame(self) -> int:
        """Get the current frame number."""
        return int(self.current_time_seconds * self.fps)
    
    @property
    def total_frames(self) -> int:
        """Get the total number of frames."""
        return int(self.duration_seconds * self.fps)
