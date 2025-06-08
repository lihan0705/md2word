"""Conversion service for handling document conversion operations"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from fastapi import UploadFile

from .base_service import BaseService
from .file_service import FileService
from .task_service import TaskService
from ..database.models import TaskStatus
from ..common.exceptions import ConversionError, TaskNotFoundError, FileNotFoundError
from ..common.utils import md2docx_tool


class ConversionService(BaseService):
    """Service for handling document conversion operations"""
    
    def __init__(self, file_service: FileService, task_service: TaskService):
        super().__init__()
        self.file_service = file_service
        self.task_service = task_service
    
    async def create_conversion_task(
        self,
        file: UploadFile,
        output_filename: str,
        metadata: Optional[Dict[str, Any]] = None,
        keep_bookmarks: bool = False
    ) -> str:
        """Create a new conversion task"""
        from ..common.utils import generate_task_id
        
        # Generate task ID first
        temp_task_id = generate_task_id()
        
        # Save uploaded file with temporary name
        input_file_path = await self.file_service.save_uploaded_file(file, temp_task_id)
        
        # Generate output file path
        output_file_path = self.file_service.generate_output_path(temp_task_id, output_filename)
        
        # Create task in database
        task_id = self.task_service.create_task(
            input_filename=file.filename,
            output_filename=output_filename,
            input_file_path=str(input_file_path),
            output_file_path=output_file_path,
            metadata=metadata,
            keep_bookmarks=keep_bookmarks
        )
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        return self.task_service.get_task_status(task_id)
    
    def get_download_file(self, task_id: str) -> Tuple[Path, str]:
        """Get file for download"""
        task = self.task_service.get_task(task_id)
        
        if task.status != TaskStatus.COMPLETED:
            raise ConversionError("Task is not completed yet")
        
        return self.file_service.get_download_file_path(
            task.output_file_path,
            task.output_filename
        )
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task and associated files"""
        try:
            task = self.task_service.get_task(task_id)
            
            # Delete associated files
            self.file_service.delete_task_files(
                task.input_file_path,
                task.output_file_path
            )
            
            # Delete task from database
            return self.task_service.delete_task(task_id)
        except TaskNotFoundError:
            return False
    
    async def convert_document(self, task_id: str) -> None:
        """Convert document in background"""
        try:
            task = self.task_service.get_task(task_id)
            
            # Update status to processing
            self.task_service.update_task_status(task_id, TaskStatus.PROCESSING)
            self.task_service.update_task_progress(task_id, 10)
            
            # Get conversion options
            keep_bookmarks = task.conversion_options.get("keep_bookmarks", False)
            
            # Update progress
            self.task_service.update_task_progress(task_id, 30)
            
            # Perform conversion
            success = await asyncio.to_thread(
                md2docx_tool,
                task.input_file_path,
                task.output_file_path,
                keep_bookmarks
            )
            
            if success:
                self.task_service.update_task_progress(task_id, 90)
                
                # Verify output file exists
                if self.file_service.file_exists(task.output_file_path):
                    self.task_service.update_task_status(task_id, TaskStatus.COMPLETED)
                    self.task_service.update_task_progress(task_id, 100)
                else:
                    raise ConversionError("Output file was not created")
            else:
                raise ConversionError("Conversion tool failed")
                
        except Exception as e:
            # Update task status to failed
            self.task_service.update_task_status(task_id, TaskStatus.FAILED)
            self.task_service.update_task_metadata(task_id, {
                "error_message": str(e),
                "progress": 0
            })
            
            # Clean up input file on failure
            try:
                task = self.task_service.get_task(task_id)
                self.file_service.cleanup_file(Path(task.input_file_path))
            except:
                pass  # Ignore cleanup errors