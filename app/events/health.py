"""Health check endpoints router"""

import sqlite3
import platform
import psutil
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pathlib import Path

from ..schema.responses import HealthResponse
from ..schema.models import SystemInfo
from ..database.connection import get_sync_database
from ..config import settings
from ..common.utils import get_available_disk_space, format_file_size

router = APIRouter(
    tags=["health"],
    responses={503: {"description": "Service unavailable"}}
)

# Track application start time
APP_START_TIME = datetime.now()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    
    try:
        # Check database connectivity
        database_status = "healthy"
        try:
            conn = get_sync_database()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
        except Exception as e:
            database_status = f"unhealthy: {str(e)}"
        
        return HealthResponse(
            status="healthy" if database_status == "healthy" else "degraded",
            service=settings.app_name,
            version=settings.app_version,
            timestamp=datetime.now(),
            database_status=database_status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Health check failed: {str(e)}"
        )

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system information"""
    
    try:
        # Database health
        database_health = {"status": "unknown", "error": None}
        try:
            conn = get_sync_database()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tasks")
            task_count = cursor.fetchone()[0]
            conn.close()
            database_health = {
                "status": "healthy",
                "task_count": task_count
            }
        except Exception as e:
            database_health = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # System information
        uptime = (datetime.now() - APP_START_TIME).total_seconds()
        
        try:
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
            memory_available = format_file_size(memory_info.available)
        except:
            memory_usage = None
            memory_available = "unknown"
        
        # Disk space
        upload_dir = Path(settings.upload_dir)
        output_dir = Path(settings.output_dir)
        
        disk_info = {
            "upload_dir": {
                "path": str(upload_dir),
                "available": format_file_size(get_available_disk_space(upload_dir))
            },
            "output_dir": {
                "path": str(output_dir),
                "available": format_file_size(get_available_disk_space(output_dir))
            }
        }
        
        return {
            "service": {
                "name": settings.app_name,
                "version": settings.app_version,
                "status": "healthy" if database_health["status"] == "healthy" else "degraded",
                "uptime_seconds": uptime,
                "timestamp": datetime.now().isoformat()
            },
            "database": database_health,
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "memory_usage_percent": memory_usage,
                "memory_available": memory_available
            },
            "storage": disk_info,
            "configuration": {
                "max_file_size": format_file_size(settings.max_file_size),
                "allowed_extensions": settings.allowed_extensions,
                "cleanup_files": settings.cleanup_files
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Detailed health check failed: {str(e)}"
        )

@router.get("/health/database")
async def database_health_check():
    """Database-specific health check"""
    
    try:
        conn = get_sync_database()
        cursor = conn.cursor()
        
        # Test basic connectivity
        cursor.execute("SELECT 1")
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get task statistics
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM tasks 
            GROUP BY status
        """)
        status_counts = dict(cursor.fetchall())
        
        # Get recent activity
        cursor.execute("""
            SELECT COUNT(*) 
            FROM tasks 
            WHERE created_at > datetime('now', '-1 hour')
        """)
        recent_tasks = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "healthy",
            "tables": tables,
            "task_statistics": status_counts,
            "recent_activity": {
                "tasks_last_hour": recent_tasks
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health/storage")
async def storage_health_check():
    """Storage-specific health check"""
    
    try:
        upload_dir = Path(settings.upload_dir)
        output_dir = Path(settings.output_dir)
        
        # Ensure directories exist
        upload_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check disk space
        upload_space = get_available_disk_space(upload_dir)
        output_space = get_available_disk_space(output_dir)
        
        # Count files
        upload_files = len(list(upload_dir.glob("*"))) if upload_dir.exists() else 0
        output_files = len(list(output_dir.glob("*"))) if output_dir.exists() else 0
        
        # Check write permissions
        upload_writable = upload_dir.exists() and upload_dir.is_dir()
        output_writable = output_dir.exists() and output_dir.is_dir()
        
        return {
            "status": "healthy" if upload_writable and output_writable else "degraded",
            "directories": {
                "upload": {
                    "path": str(upload_dir),
                    "exists": upload_dir.exists(),
                    "writable": upload_writable,
                    "file_count": upload_files,
                    "available_space": format_file_size(upload_space)
                },
                "output": {
                    "path": str(output_dir),
                    "exists": output_dir.exists(),
                    "writable": output_writable,
                    "file_count": output_files,
                    "available_space": format_file_size(output_space)
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }