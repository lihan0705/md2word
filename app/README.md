# MD2Word API

A FastAPI-based web service for converting Markdown files to Word documents (.docx) with a modern, scalable architecture.

## Features

- **File Upload & Conversion**: Upload Markdown files and convert them to Word documents
- **Asynchronous Processing**: Background task processing for file conversion
- **Status Tracking**: Real-time status updates for conversion tasks
- **File Download**: Download converted Word documents
- **Metadata Support**: Optional document metadata handling
- **Health Monitoring**: Health check endpoints for service monitoring

## Architecture

The backend follows a modular microservice architecture:

- **FastAPI Application** (`main.py`): API endpoints and request handling
- **Configuration Management** (`config.py`): Centralized settings and environment variables
- **Data Models** (`models.py`): Pydantic models for request/response validation
- **Business Logic** (`services.py`): Core conversion and task management services
- **Integration Layer**: Uses existing `md2docx` tool from `/tools/` directory

## API Endpoints

### 1. Health Check
```
GET /health
```
Returns service health status and version information.

### 2. Document Conversion
```
POST /api/v1/documents/convert
```
Upload a Markdown file and start conversion process.

**Request:**
- `file`: Markdown file (.md)
- `output_filename` (optional): Desired output filename
- `metadata` (optional): JSON string with document metadata
- `keep_bookmarks` (optional): Whether to preserve bookmarks

**Response:**
```json
{
  "task_id": "uuid-string",
  "status_url": "/api/v1/documents/convert/status/{task_id}",
  "message": "Document conversion started successfully"
}
```

### 3. Conversion Status
```
GET /api/v1/documents/convert/status/{task_id}
```
Check the status of a conversion task.

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "PENDING|PROCESSING|COMPLETED|FAILED",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "download_url": "/api/v1/documents/download/{task_id}",
  "error_message": null,
  "progress": 100.0
}
```

### 4. Document Download
```
GET /api/v1/documents/download/{task_id}
```
Download the converted Word document.

## Installation & Setup

### Prerequisites

1. Python 3.8+
2. All dependencies from `requirements.txt`
3. Pandoc (for document conversion)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create storage directories (auto-created on startup):
```bash
mkdir -p app/storage/uploads
mkdir -p app/storage/outputs
```

### Configuration

The application uses environment variables for configuration. Create a `.env` file in the app directory:

```env
# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=false

# File Settings
MAX_FILE_SIZE=10485760  # 10MB
CLEANUP_FILES=true

# Storage Settings
UPLOAD_DIR=app/storage/uploads
OUTPUT_DIR=app/storage/outputs
```

## Running the Server

### Method 1: Using the run script
```bash
python -m app.run
```

### Method 2: Using uvicorn directly
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Method 3: Development mode with auto-reload
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Usage Examples

### Upload and Convert a Markdown File

```bash
curl -X POST "http://localhost:8000/api/v1/documents/convert" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@example.md" \
  -F "output_filename=my-document" \
  -F "keep_bookmarks=false"
```

### Check Conversion Status

```bash
curl -X GET "http://localhost:8000/api/v1/documents/convert/status/{task_id}" \
  -H "accept: application/json"
```

### Download Converted Document

```bash
curl -X GET "http://localhost:8000/api/v1/documents/download/{task_id}" \
  -H "accept: application/octet-stream" \
  -o converted-document.docx
```

## API Documentation

Once the server is running, you can access:

- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## File Storage

- **Uploads**: Temporary storage for uploaded Markdown files
- **Outputs**: Storage for converted Word documents
- **Cleanup**: Input files are automatically cleaned up after conversion (configurable)

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid file format, malformed requests
- **404 Not Found**: Task ID not found, file not found
- **413 Payload Too Large**: File size exceeds limit
- **500 Internal Server Error**: Conversion failures, system errors

## Security Considerations

- File size limits to prevent abuse
- File type validation (only .md files accepted)
- CORS configuration for cross-origin requests
- Automatic cleanup of temporary files

## Monitoring

- Health check endpoint for service monitoring
- Structured logging for debugging
- Task status tracking for conversion monitoring

## Key Improvements

### Service Layer Package
- **Domain-Driven Design**: Services organized by business domain
- **Single Responsibility**: Each service handles one specific concern
- **Dependency Injection**: Clean separation and testable architecture
- **FileService**: File operations (upload, download, cleanup)
- **TaskService**: Task lifecycle and database operations
- **ConversionService**: Document conversion orchestration

### FastAPI Routers
- **Conversion Router** (`/api/v1/documents`): Document upload, conversion, and download
- **Health Router** (`/api/v1/health`): System health monitoring and diagnostics
- **Tasks Router** (`/api/v1/tasks`): Task management and statistics

### Database Integration
- **SQLite Database**: Lightweight, file-based database with async support
- **Repository Pattern**: Clean separation between business logic and data access
- **Task Management**: Persistent task storage with status tracking

### Enhanced API Structure
- **Pydantic Schemas**: Strong typing and validation for requests/responses
- **Custom Exceptions**: Proper error handling with meaningful messages
- **Input Validation**: Comprehensive validation for files, metadata, and parameters

## Integration with Existing Tools

The backend seamlessly integrates with the existing `md2docx` tool located in `/tools/md2docx.py`, providing:

- Mermaid diagram support
- Vega/Vega-Lite chart rendering
- Unicode color icon handling
- Advanced table formatting
- Bookmark preservation options

## Development

### Project Structure
```
app/
├── events/                 # FastAPI routers and endpoints
│   ├── __init__.py        # Router exports
│   ├── conversion.py      # Document conversion endpoints
│   ├── health.py          # Health check endpoints
│   └── tasks.py           # Task management endpoints
├── services/              # Service Layer Package (Business Logic)
│   ├── __init__.py        # Service exports and instances
│   ├── base_service.py    # Base service class
│   ├── file_service.py    # File handling operations
│   ├── task_service.py    # Task management operations
│   ├── conversion_service.py # Document conversion orchestration
│   └── README.md          # Service layer documentation
├── schema/                # Pydantic models and schemas
│   ├── __init__.py        # Schema exports
│   ├── models.py          # Data models
│   ├── requests.py        # Request schemas
│   └── responses.py       # Response schemas
├── database/              # Database layer
│   ├── __init__.py        # Database exports
│   ├── models.py          # SQLAlchemy models
│   └── repository.py      # Data access layer
├── common/                # Shared utilities
│   ├── __init__.py        # Common exports
│   ├── exceptions.py      # Custom exceptions
│   ├── utils.py           # Utility functions
│   └── validators.py      # Input validation
├── main.py                # FastAPI application
├── config.py              # Configuration settings
├── services.py            # Legacy compatibility layer
├── requirements.txt       # Python dependencies
├── test_api.py           # API tests
├── test_services.py      # Service layer tests
└── README.md             # This file
```

### Adding New Features

1. **New API Endpoints**: Add routes in `main.py`
2. **Data Models**: Define new Pydantic models in `models.py`
3. **Business Logic**: Implement services in `services.py`
4. **Configuration**: Add settings in `config.py`

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the project root directory
2. **File Permission Errors**: Check write permissions for storage directories
3. **Pandoc Not Found**: Install Pandoc system-wide or use pypandoc-binary
4. **Port Already in Use**: Change the port in configuration or stop conflicting services

### Logs

Check server logs for detailed error information:
```bash
uvicorn app.main:app --log-level debug
```