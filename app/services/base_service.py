"""Base service class for common functionality"""

from abc import ABC
from pathlib import Path
from ..config import settings
from ..common.utils import ensure_directory_exists


class BaseService(ABC):
    """Base service class with common functionality"""
    
    def __init__(self):
        """Initialize base service"""
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        upload_dir = Path(settings.upload_dir)
        output_dir = Path(settings.output_dir)
        
        ensure_directory_exists(upload_dir)
        ensure_directory_exists(output_dir)
    
    @property
    def upload_dir(self) -> Path:
        """Get upload directory path"""
        return Path(settings.upload_dir)
    
    @property
    def output_dir(self) -> Path:
        """Get output directory path"""
        return Path(settings.output_dir)