"""Validators for file and data validation"""

import json
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import UploadFile

from .exceptions import ValidationError, FileSizeError, FileTypeError
from .constants import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, SUPPORTED_MIME_TYPES

class FileValidator:
    """Validator for uploaded files"""
    
    @staticmethod
    def validate_file(file: UploadFile, max_size: int = MAX_FILE_SIZE) -> None:
        """Validate uploaded file"""
        if not file.filename:
            raise ValidationError("No file provided", "file")
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise FileTypeError(file_ext, ALLOWED_EXTENSIONS)
        
        # Check file size
        if file.size and file.size > max_size:
            raise FileSizeError(file.size, max_size)
        
        # Check MIME type if available
        if file.content_type:
            if file.content_type not in SUPPORTED_MIME_TYPES:
                # Try to guess MIME type from filename
                guessed_type, _ = mimetypes.guess_type(file.filename)
                if guessed_type not in SUPPORTED_MIME_TYPES:
                    raise ValidationError(
                        f"Unsupported MIME type: {file.content_type}",
                        "content_type"
                    )
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """Validate and sanitize filename"""
        if not filename:
            raise ValidationError("Filename cannot be empty", "filename")
        
        # Remove potentially dangerous characters
        sanitized = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
        
        if not sanitized:
            raise ValidationError("Invalid filename", "filename")
        
        return sanitized.strip()
    
    @staticmethod
    def validate_output_filename(filename: Optional[str]) -> Optional[str]:
        """Validate output filename"""
        if not filename:
            return None
        
        return FileValidator.validate_filename(filename)

class MetadataValidator:
    """Validator for metadata"""
    
    @staticmethod
    def validate_metadata(metadata_str: Optional[str]) -> Optional[Dict[str, Any]]:
        """Validate and parse metadata JSON string"""
        if not metadata_str:
            return None
        
        try:
            metadata = json.loads(metadata_str)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format in metadata: {e}", "metadata")
        
        if not isinstance(metadata, dict):
            raise ValidationError("Metadata must be a JSON object", "metadata")
        
        # Validate metadata structure
        MetadataValidator._validate_metadata_structure(metadata)
        
        return metadata
    
    @staticmethod
    def _validate_metadata_structure(metadata: Dict[str, Any]) -> None:
        """Validate metadata structure"""
        allowed_fields = {
            'author': str,
            'title': str,
            'tags': list,
            'custom_fields': dict
        }
        
        for key, value in metadata.items():
            if key in allowed_fields:
                expected_type = allowed_fields[key]
                if not isinstance(value, expected_type):
                    raise ValidationError(
                        f"Metadata field '{key}' must be of type {expected_type.__name__}",
                        f"metadata.{key}"
                    )
                
                # Additional validation for specific fields
                if key == 'tags' and value:
                    if not all(isinstance(tag, str) for tag in value):
                        raise ValidationError(
                            "All tags must be strings",
                            "metadata.tags"
                        )
                
                if key == 'custom_fields' and value:
                    if not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
                        raise ValidationError(
                            "Custom fields must be string key-value pairs",
                            "metadata.custom_fields"
                        )
            else:
                # Allow unknown fields but warn
                pass

class TaskValidator:
    """Validator for task-related data"""
    
    @staticmethod
    def validate_task_id(task_id: str) -> str:
        """Validate task ID format"""
        if not task_id:
            raise ValidationError("Task ID cannot be empty", "task_id")
        
        # Basic UUID format validation
        if len(task_id) != 36 or task_id.count('-') != 4:
            raise ValidationError("Invalid task ID format", "task_id")
        
        return task_id
    
    @staticmethod
    def validate_pagination(limit: int, offset: int) -> tuple[int, int]:
        """Validate pagination parameters"""
        if limit < 1 or limit > 1000:
            raise ValidationError("Limit must be between 1 and 1000", "limit")
        
        if offset < 0:
            raise ValidationError("Offset must be non-negative", "offset")
        
        return limit, offset