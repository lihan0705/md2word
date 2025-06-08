"""Conversion endpoints router"""

import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional

from ..schema.requests import ConversionRequest
from ..schema.responses import ConversionRequestResponse, ConversionStatusResponse
from ..common.validators import FileValidator, MetadataValidator
from ..common.utils import generate_task_id, safe_delete_file
from ..common.exceptions import ValidationError, TaskNotFoundError, ConversionError
from ..services import conversion_service
from ..config import settings

router = APIRouter(
    prefix="/documents",
    tags=["conversion"],
    responses={404: {"description": "Not found"}}
)

@router.post("/convert", response_model=ConversionRequestResponse)
async def convert_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Markdown file to convert"),
    output_filename: Optional[str] = Form(None, description="Desired output filename"),
    metadata: Optional[str] = Form(None, description="JSON metadata for the document"),
    keep_bookmarks: Optional[bool] = Form(False, description="Whether to keep bookmarks")
):
    """Upload markdown file and start conversion to Word document"""
    
    try:
        # Validate file
        FileValidator.validate_file(file, settings.max_file_size)
        
        # Validate and parse metadata
        parsed_metadata = MetadataValidator.validate_metadata(metadata)
        
        # Validate output filename
        validated_output_filename = FileValidator.validate_output_filename(output_filename)
        
        # Create conversion task
        task_id = await conversion_service.create_conversion_task(
            file=file,
            output_filename=validated_output_filename,
            metadata=parsed_metadata,
            keep_bookmarks=keep_bookmarks or False
        )
        
        # Start background conversion
        background_tasks.add_task(conversion_service.convert_document, task_id)
        
        return ConversionRequestResponse(
            task_id=task_id,
            status_url=f"/api/v1/documents/convert/status/{task_id}",
            message="Document conversion started successfully"
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ConversionError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/convert/status/{task_id}", response_model=ConversionStatusResponse)
async def get_conversion_status(task_id: str):
    """Get the status of a document conversion task"""
    
    try:
        task = await conversion_service.get_task_status(task_id)
        
        return ConversionStatusResponse(
            task_id=task_id,
            status=task["status"],
            created_at=task["created_at"],
            updated_at=task["updated_at"],
            download_url=task.get("download_url"),
            error_message=task.get("error_message"),
            progress=task.get("progress")
        )
        
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/download/{task_id}")
async def download_document(task_id: str):
    """Download the converted Word document"""
    
    try:
        output_path, filename = await conversion_service.get_download_file(task_id)
        
        return FileResponse(
            path=str(output_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a conversion task and its associated files"""
    
    try:
        success = await conversion_service.delete_task(task_id)
        
        if success:
            return {"message": f"Task {task_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
            
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")