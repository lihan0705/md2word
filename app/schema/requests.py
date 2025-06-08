"""Request schemas for API endpoints"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ConversionRequest(BaseModel):
    """Request model for document conversion"""
    output_filename: Optional[str] = Field(None, description="Desired output filename (without extension)")
    metadata: Optional[str] = Field(None, description="JSON string containing document metadata")
    keep_bookmarks: Optional[bool] = Field(False, description="Whether to keep bookmarks in the document")

class HealthRequest(BaseModel):
    """Request model for health check (if needed)"""
    pass

class TaskListRequest(BaseModel):
    """Request model for listing tasks"""
    limit: Optional[int] = Field(100, description="Maximum number of tasks to return", ge=1, le=1000)
    offset: Optional[int] = Field(0, description="Number of tasks to skip", ge=0)
    status: Optional[str] = Field(None, description="Filter by task status")