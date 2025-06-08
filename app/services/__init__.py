"""Service Layer Package

This package contains all business logic services organized by domain:
- FileService: File handling operations
- TaskService: Task management operations  
- ConversionService: Document conversion operations
"""

from .file_service import FileService
from .task_service import TaskService
from .conversion_service import ConversionService
from .base_service import BaseService

# Global service instances
file_service = FileService()
task_service = TaskService()
conversion_service = ConversionService(file_service, task_service)

__all__ = [
    "BaseService",
    "FileService",
    "TaskService", 
    "ConversionService",
    "file_service",
    "task_service",
    "conversion_service"
]