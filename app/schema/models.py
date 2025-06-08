"""Shared models for API schemas"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class DocumentMetadata(BaseModel):
    """Document metadata model"""
    author: Optional[str] = Field(None, description="Document author")
    title: Optional[str] = Field(None, description="Document title")
    tags: Optional[List[str]] = Field(None, description="Document tags")
    custom_fields: Optional[Dict[str, str]] = Field(None, description="Custom metadata fields")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TaskRecord(BaseModel):
    """Internal task record model"""
    task_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    input_path: str
    output_path: str
    original_filename: str
    output_filename: str
    metadata: Optional[Dict[str, Any]] = None
    keep_bookmarks: bool = False
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    progress: Optional[float] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FileInfo(BaseModel):
    """File information model"""
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME content type")
    upload_time: datetime = Field(..., description="Upload timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ConversionOptions(BaseModel):
    """Conversion options model"""
    keep_bookmarks: bool = Field(False, description="Whether to keep bookmarks")
    include_toc: bool = Field(True, description="Whether to include table of contents")
    page_break_before_heading: bool = Field(False, description="Add page breaks before headings")
    custom_styles: Optional[Dict[str, str]] = Field(None, description="Custom CSS styles")
    
class SystemInfo(BaseModel):
    """System information model"""
    version: str = Field(..., description="Application version")
    python_version: str = Field(..., description="Python version")
    platform: str = Field(..., description="Operating system platform")
    uptime: float = Field(..., description="Application uptime in seconds")
    memory_usage: Optional[float] = Field(None, description="Memory usage in MB")