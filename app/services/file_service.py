"""File service for handling file operations"""

import asyncio
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile

from .base_service import BaseService
from ..common.utils import safe_delete_file
from ..common.exceptions import ConversionError, FileNotFoundError


class FileService(BaseService):
    """Service for handling file operations"""
    
    async def save_uploaded_file(self, file: UploadFile, task_id: str) -> Path:
        """Save uploaded file to disk"""
        file_path = self.upload_dir / f"{task_id}_{file.filename}"
        
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            return file_path
        except Exception as e:
            raise ConversionError(f"Failed to save uploaded file: {str(e)}")
    
    def get_download_file_path(self, output_file_path: str, output_filename: str) -> Tuple[Path, str]:
        """Get file path and filename for download"""
        output_path = Path(output_file_path)
        if not output_path.exists():
            raise FileNotFoundError("Converted file not found")
        
        return output_path, output_filename
    
    def delete_task_files(self, input_file_path: str = None, output_file_path: str = None) -> None:
        """Delete files associated with a task"""
        if input_file_path:
            safe_delete_file(Path(input_file_path))
        if output_file_path:
            safe_delete_file(Path(output_file_path))
    
    def cleanup_file(self, file_path: Path) -> None:
        """Clean up a single file"""
        safe_delete_file(file_path)
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return Path(file_path).exists()
    
    def generate_output_path(self, task_id: str, output_filename: str) -> str:
        """Generate output file path for a task"""
        return str(self.output_dir / f"{task_id}_{output_filename}")