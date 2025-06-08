"""Response schemas for API endpoints"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ConversionStatus(str, Enum):
    """Conversion task status enumeration"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ConversionRequestResponse(BaseModel):
    """Response model for conversion request"""
    task_id: str = Field(..., description="Unique task identifier")
    status_url: str = Field(..., description="URL to check conversion status")
    message: str = Field(..., description="Response message")

class ConversionStatusResponse(BaseModel):
    """Response model for conversion status"""
    task_id: str = Field(..., description="Task identifier")
    status: ConversionStatus = Field(..., description="Current conversion status")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    download_url: Optional[str] = Field(None, description="Download URL for completed conversion")
    error_message: Optional[str] = Field(None, description="Error message if conversion failed")
    progress: Optional[float] = Field(None, description="Conversion progress percentage (0-100)")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Response timestamp")
    database_status: Optional[str] = Field(None, description="Database connection status")

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error detail message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(..., description="Error timestamp")

class TaskListResponse(BaseModel):
    """Response model for task listing"""
    tasks: List[ConversionStatusResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
    limit: int = Field(..., description="Limit used for pagination")
    offset: int = Field(..., description="Offset used for pagination")

class TaskStatsResponse(BaseModel):
    """Response model for task statistics"""
    total_tasks: int = Field(..., description="Total number of tasks")
    pending_tasks: int = Field(..., description="Number of pending tasks")
    processing_tasks: int = Field(..., description="Number of processing tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    failed_tasks: int = Field(..., description="Number of failed tasks")