# Service Layer Package

This package contains the business logic services organized using a domain-driven design approach. The services are separated into focused, single-responsibility classes that handle specific aspects of the application.

## Package Structure

```
services/
├── __init__.py          # Package initialization and service instances
├── base_service.py      # Base service class with common functionality
├── file_service.py      # File handling operations
├── task_service.py      # Task management operations
├── conversion_service.py # Document conversion orchestration
└── README.md           # This documentation
```

## Services Overview

### BaseService

Provides common functionality for all services:
- Directory management and validation
- Configuration access
- Shared utilities

### FileService

Handles all file-related operations:
- **save_uploaded_file()** - Save uploaded files to disk
- **get_download_file_path()** - Get file paths for downloads
- **delete_task_files()** - Clean up files associated with tasks
- **cleanup_file()** - Delete individual files
- **file_exists()** - Check file existence
- **generate_output_path()** - Generate output file paths

### TaskService

Manages task lifecycle and database operations:
- **create_task()** - Create new tasks in database
- **get_task()** - Retrieve task by ID
- **get_task_status()** - Get task status and details
- **update_task_status()** - Update task status
- **update_task_progress()** - Update task progress
- **update_task_metadata()** - Update task metadata
- **delete_task()** - Remove tasks from database
- **task_exists()** - Check task existence

### ConversionService

Orchestrates document conversion operations:
- **create_conversion_task()** - Create and initialize conversion tasks
- **get_task_status()** - Get conversion task status
- **get_download_file()** - Get converted files for download
- **delete_task()** - Delete tasks and associated files
- **convert_document()** - Perform background document conversion

## Usage

### Importing Services

```python
# Import individual services
from app.services import ConversionService, FileService, TaskService

# Import service instances (recommended)
from app.services import conversion_service, file_service, task_service
```

### Using Services

```python
# Create a conversion task
task_id = await conversion_service.create_conversion_task(
    file=uploaded_file,
    output_filename="document.docx",
    metadata={"author": "John Doe"},
    keep_bookmarks=True
)

# Check task status
status = conversion_service.get_task_status(task_id)

# Get file for download
file_path, filename = conversion_service.get_download_file(task_id)
```

## Design Principles

### Single Responsibility
Each service has a single, well-defined responsibility:
- FileService: File operations
- TaskService: Task management
- ConversionService: Conversion orchestration

### Dependency Injection
Services are injected as dependencies rather than created internally:
```python
class ConversionService(BaseService):
    def __init__(self, file_service: FileService, task_service: TaskService):
        self.file_service = file_service
        self.task_service = task_service
```

### Separation of Concerns
- **FileService**: Handles file I/O operations
- **TaskService**: Manages database operations
- **ConversionService**: Orchestrates business logic

### Error Handling
Each service handles its own domain-specific errors:
- FileService: File I/O errors, path validation
- TaskService: Database errors, task validation
- ConversionService: Conversion errors, orchestration failures

## Benefits

### Improved Testability
- Services can be tested in isolation
- Easy to mock dependencies
- Clear test boundaries

### Better Maintainability
- Focused, single-purpose classes
- Clear separation of concerns
- Easier to understand and modify

### Enhanced Scalability
- Services can be optimized independently
- Easy to add new services
- Clear extension points

### Dependency Management
- Explicit dependencies
- Easy to swap implementations
- Better control over service lifecycle

## Migration from Legacy services.py

The original `services.py` file has been converted to a compatibility layer that imports from this package. This ensures backward compatibility while allowing gradual migration to the new structure.

### Legacy Import (still works)
```python
from app.services import conversion_service
```

### New Import (recommended)
```python
from app.services import conversion_service, file_service, task_service
```

## Future Enhancements

### Potential New Services
- **NotificationService**: Handle user notifications
- **MetricsService**: Collect and report metrics
- **CacheService**: Manage caching operations
- **ValidationService**: Centralized validation logic

### Service Improvements
- Add service health checks
- Implement service metrics
- Add configuration validation
- Enhance error reporting

## Testing

Each service should have comprehensive unit tests:

```python
# Example test structure
tests/
├── test_file_service.py
├── test_task_service.py
├── test_conversion_service.py
└── test_service_integration.py
```

Run the test script to verify the package structure:
```bash
python test_services.py
```