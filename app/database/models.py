"""Database models"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class Task:
    """Task database model"""
    id: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    input_path: str
    output_path: str
    original_filename: str
    output_filename: str
    metadata: Optional[str] = None
    keep_bookmarks: bool = False
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    progress: float = 0.0
    
    @classmethod
    def from_row(cls, row) -> 'Task':
        """Create Task from database row"""
        return cls(
            id=row['id'],
            status=TaskStatus(row['status']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            input_path=row['input_path'],
            output_path=row['output_path'],
            original_filename=row['original_filename'],
            output_filename=row['output_filename'],
            metadata=row['metadata'],
            keep_bookmarks=bool(row['keep_bookmarks']),
            download_url=row['download_url'],
            error_message=row['error_message'],
            progress=float(row['progress']) if row['progress'] else 0.0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'input_path': self.input_path,
            'output_path': self.output_path,
            'original_filename': self.original_filename,
            'output_filename': self.output_filename,
            'metadata': self.metadata,
            'keep_bookmarks': self.keep_bookmarks,
            'download_url': self.download_url,
            'error_message': self.error_message,
            'progress': self.progress
        }