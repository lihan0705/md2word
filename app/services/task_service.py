"""Task service for handling task operations"""

from datetime import datetime
from typing import Dict, Any, Optional

from .base_service import BaseService
from ..database.models import Task, TaskStatus
from ..database.repository import TaskRepository
from ..common.utils import generate_task_id
from ..common.exceptions import TaskNotFoundError


class TaskService(BaseService):
    """Service for handling task operations"""
    
    def __init__(self):
        super().__init__()
        self.task_repo = TaskRepository()
    
    def create_task(
        self,
        input_filename: str,
        output_filename: str,
        input_file_path: str,
        output_file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        keep_bookmarks: bool = False
    ) -> str:
        """Create a new task in database"""
        task_id = generate_task_id()
        
        # Prepare conversion options
        conversion_options = {
            "keep_bookmarks": keep_bookmarks,
            "output_format": "docx"
        }
        
        # Create task
        task = Task(
            id=task_id,
            status=TaskStatus.PENDING,
            input_filename=input_filename,
            output_filename=output_filename,
            input_file_path=input_file_path,
            output_file_path=output_file_path,
            metadata=metadata or {},
            conversion_options=conversion_options,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.task_repo.create_task(task)
        return task_id
    
    def get_task(self, task_id: str) -> Task:
        """Get task by ID"""
        task = self.task_repo.get_task(task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return task
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status and details"""
        task = self.get_task(task_id)
        
        result = {
            "task_id": task.id,
            "status": task.status.value.lower(),
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "progress": task.metadata.get("progress", 0)
        }
        
        # Add download URL if conversion is completed
        if task.status == TaskStatus.COMPLETED:
            result["download_url"] = f"/api/v1/documents/download/{task_id}"
        
        # Add error message if failed
        if task.status == TaskStatus.FAILED:
            result["error_message"] = task.metadata.get("error_message")
        
        return result
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """Update task status"""
        self.task_repo.update_task_status(task_id, status)
    
    def update_task_progress(self, task_id: str, progress: int) -> None:
        """Update task progress"""
        self.update_task_metadata(task_id, {"progress": progress})
    
    def update_task_metadata(self, task_id: str, metadata_updates: Dict[str, Any]) -> None:
        """Update task metadata"""
        task = self.task_repo.get_task(task_id)
        if task:
            updated_metadata = {**(task.metadata or {}), **metadata_updates}
            self.task_repo.update_task_metadata(task_id, updated_metadata)
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task from database"""
        return self.task_repo.delete_task(task_id)
    
    def task_exists(self, task_id: str) -> bool:
        """Check if task exists"""
        try:
            self.get_task(task_id)
            return True
        except TaskNotFoundError:
            return False