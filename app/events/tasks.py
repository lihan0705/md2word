"""Task management endpoints router"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime

from ..schema.requests import TaskListRequest
from ..schema.responses import TaskListResponse, TaskStatsResponse
from ..schema.models import TaskRecord
from ..database.repository import TaskRepository
from ..database.models import TaskStatus
from ..common.validators import TaskValidator
from ..common.exceptions import TaskNotFoundError, ValidationError
from ..services import conversion_service

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}}
)

# Dependency to get task repository
def get_task_repository() -> TaskRepository:
    return TaskRepository()

@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by task status"),
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """List conversion tasks with pagination and filtering"""
    
    try:
        # Validate pagination parameters
        TaskValidator.validate_pagination(page, limit)
        
        # Validate status filter
        status_filter = None
        if status:
            try:
                status_filter = TaskStatus(status.upper())
            except ValueError:
                raise ValidationError(f"Invalid status: {status}")
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get tasks
        if status_filter:
            tasks = task_repo.get_tasks_by_status(status_filter, limit, offset)
            total_count = task_repo.count_tasks_by_status(status_filter)
        else:
            tasks = task_repo.list_tasks(limit, offset)
            total_count = task_repo.count_all_tasks()
        
        # Convert to response format
        task_records = [
            TaskRecord(
                task_id=task.id,
                status=task.status.value.lower(),
                created_at=task.created_at,
                updated_at=task.updated_at,
                input_filename=task.input_filename,
                output_filename=task.output_filename,
                file_size=task.metadata.get("file_size") if task.metadata else None,
                progress=task.metadata.get("progress") if task.metadata else None
            )
            for task in tasks
        ]
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return TaskListResponse(
            tasks=task_records,
            pagination={
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/stats", response_model=TaskStatsResponse)
async def get_task_statistics(
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Get task statistics and metrics"""
    
    try:
        # Get status counts
        status_counts = {}
        for status in TaskStatus:
            count = task_repo.count_tasks_by_status(status)
            status_counts[status.value.lower()] = count
        
        # Get recent activity (last 24 hours)
        recent_tasks = task_repo.get_recent_tasks(hours=24)
        recent_count = len(recent_tasks)
        
        # Calculate success rate
        total_completed = status_counts.get("completed", 0) + status_counts.get("failed", 0)
        success_rate = (
            (status_counts.get("completed", 0) / total_completed * 100)
            if total_completed > 0 else 0
        )
        
        # Get average processing time for completed tasks
        completed_tasks = task_repo.get_tasks_by_status(TaskStatus.COMPLETED, limit=100)
        avg_processing_time = None
        if completed_tasks:
            processing_times = []
            for task in completed_tasks:
                if task.created_at and task.updated_at:
                    delta = task.updated_at - task.created_at
                    processing_times.append(delta.total_seconds())
            
            if processing_times:
                avg_processing_time = sum(processing_times) / len(processing_times)
        
        return TaskStatsResponse(
            total_tasks=sum(status_counts.values()),
            status_counts=status_counts,
            recent_activity={
                "last_24_hours": recent_count
            },
            performance_metrics={
                "success_rate_percent": round(success_rate, 2),
                "average_processing_time_seconds": round(avg_processing_time, 2) if avg_processing_time else None
            },
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{task_id}", response_model=TaskRecord)
async def get_task_details(
    task_id: str,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Get detailed information about a specific task"""
    
    try:
        # Validate task ID
        TaskValidator.validate_task_id(task_id)
        
        # Get task
        task = task_repo.get_task(task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        return TaskRecord(
            task_id=task.id,
            status=task.status.value.lower(),
            created_at=task.created_at,
            updated_at=task.updated_at,
            input_filename=task.input_filename,
            output_filename=task.output_filename,
            input_file_path=task.input_file_path,
            output_file_path=task.output_file_path,
            file_size=task.metadata.get("file_size") if task.metadata else None,
            progress=task.metadata.get("progress") if task.metadata else None,
            error_message=task.metadata.get("error_message") if task.metadata else None,
            conversion_options=task.conversion_options
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Delete a specific task and its associated files"""
    
    try:
        # Validate task ID
        TaskValidator.validate_task_id(task_id)
        
        # Use conversion service to delete task (handles file cleanup)
        success = await conversion_service.delete_task(task_id)
        
        if success:
            return {"message": f"Task {task_id} deleted successfully"}
        else:
            raise TaskNotFoundError(f"Task {task_id} not found")
            
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/cleanup")
async def cleanup_old_tasks(
    days: int = Query(7, ge=1, le=365, description="Delete tasks older than this many days"),
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Clean up old completed and failed tasks"""
    
    try:
        # Clean up old tasks
        deleted_count = task_repo.cleanup_old_tasks(days)
        
        return {
            "message": f"Cleaned up {deleted_count} old tasks",
            "deleted_count": deleted_count,
            "cutoff_days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@router.post("/{task_id}/retry")
async def retry_task(
    task_id: str,
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Retry a failed conversion task"""
    
    try:
        # Validate task ID
        TaskValidator.validate_task_id(task_id)
        
        # Get task
        task = task_repo.get_task(task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        # Check if task can be retried
        if task.status not in [TaskStatus.FAILED, TaskStatus.COMPLETED]:
            raise ValidationError(f"Task {task_id} cannot be retried (current status: {task.status.value})")
        
        # Reset task status to pending
        task_repo.update_task_status(task_id, TaskStatus.PENDING)
        
        # Start conversion again
        await conversion_service.convert_document(task_id)
        
        return {
            "message": f"Task {task_id} retry initiated",
            "task_id": task_id,
            "status": "pending"
        }
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retry failed: {str(e)}")