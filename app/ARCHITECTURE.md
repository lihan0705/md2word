# Noah System Architecture

This document provides a visual overview of the Noah document conversion system architecture using Mermaid diagrams.

## System Overview

```mermaid
graph TB
    subgraph "API Layer"
        A[FastAPI Application]
        B[Health Endpoints]
        C[Conversion Endpoints]
        D[Task Endpoints]
    end
    
    subgraph "Service Layer"
        E[ConversionService]
        F[FileService]
        G[TaskService]
        H[BaseService]
    end
    
    subgraph "Data Layer"
        I[TaskRepository]
        J[Database Models]
        K[SQLite Database]
    end
    
    subgraph "External Tools"
        L[md2docx Tool]
        M[File System]
    end
    
    A --> B
    A --> C
    A --> D
    
    C --> E
    D --> G
    
    E --> F
    E --> G
    F --> H
    G --> H
    
    G --> I
    I --> J
    J --> K
    
    E --> L
    F --> M
    
    style A fill:#e1f5fe
    style E fill:#f3e5f5
    style I fill:#e8f5e8
    style L fill:#fff3e0
```

## Service Layer Architecture

```mermaid
classDiagram
    class BaseService {
        +upload_dir: str
        +output_dir: str
        +ensure_directories()
    }
    
    class FileService {
        +save_uploaded_file(file, task_id)
        +get_download_path(task_id)
        +delete_task_files(task_id)
        +cleanup_file(file_path)
        +file_exists(file_path)
        +get_output_file_path(task_id, filename)
    }
    
    class TaskService {
        -task_repository: TaskRepository
        +create_task(task_data)
        +get_task(task_id)
        +update_task_status(task_id, status)
        +update_task_metadata(task_id, metadata)
        +delete_task(task_id)
    }
    
    class ConversionService {
        -file_service: FileService
        -task_service: TaskService
        +create_conversion_task(file, metadata)
        +get_task_status(task_id)
        +download_file(task_id)
        +delete_task(task_id)
        +convert_document_background(task_id)
    }
    
    BaseService <|-- FileService
    BaseService <|-- TaskService
    BaseService <|-- ConversionService
    
    ConversionService --> FileService
    ConversionService --> TaskService
```

## Request Flow Diagram

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant CS as ConversionService
    participant FS as FileService
    participant TS as TaskService
    participant TR as TaskRepository
    participant Tool as md2docx
    
    Client->>API: POST /convert (upload file)
    API->>CS: create_conversion_task()
    
    CS->>FS: save_uploaded_file()
    FS-->>CS: file_path
    
    CS->>TS: create_task()
    TS->>TR: create()
    TR-->>TS: task_id
    TS-->>CS: task_id
    
    CS->>CS: convert_document_background()
    CS->>Tool: md2docx conversion
    Tool-->>CS: converted file
    
    CS->>TS: update_task_status("completed")
    TS->>TR: update()
    
    CS-->>API: task_id
    API-->>Client: {"task_id": "..."}
    
    Client->>API: GET /tasks/{task_id}
    API->>TS: get_task()
    TS->>TR: get_by_id()
    TR-->>TS: task_data
    TS-->>API: task_data
    API-->>Client: task status
    
    Client->>API: GET /download/{task_id}
    API->>CS: download_file()
    CS->>FS: get_download_path()
    FS-->>CS: file_path
    CS-->>API: file_response
    API-->>Client: converted file
```

## File System Structure

```mermaid
graph TD
    A[Noah Project Root]
    A --> B[app/]
    A --> C[tools/]
    A --> D[test_data/]
    A --> E[results/]
    
    B --> F[services/]
    B --> G[events/]
    B --> H[database/]
    B --> I[schema/]
    B --> J[common/]
    
    F --> K[__init__.py]
    F --> L[base_service.py]
    F --> M[file_service.py]
    F --> N[task_service.py]
    F --> O[conversion_service.py]
    F --> P[README.md]
    
    G --> Q[conversion.py]
    G --> R[tasks.py]
    G --> S[health.py]
    
    H --> T[models.py]
    H --> U[repository.py]
    H --> V[connection.py]
    
    C --> W[md2docx.py]
    
    style F fill:#e8f5e8
    style G fill:#e1f5fe
    style H fill:#fff3e0
    style C fill:#f3e5f5
```

## Data Flow

```mermaid
flowchart LR
    A[Upload File] --> B[FileService.save_uploaded_file]
    B --> C[TaskService.create_task]
    C --> D[Background Conversion]
    D --> E[md2docx Tool]
    E --> F[Update Task Status]
    F --> G[File Ready for Download]
    
    H[Client Request] --> I[Get Task Status]
    I --> J[TaskService.get_task]
    J --> K[Return Status]
    
    L[Download Request] --> M[ConversionService.download_file]
    M --> N[FileService.get_download_path]
    N --> O[Return File]
    
    style A fill:#e8f5e8
    style E fill:#f3e5f5
    style G fill:#e1f5fe
```

## Key Design Principles

1. **Separation of Concerns**: Each service has a specific responsibility
2. **Dependency Injection**: Services depend on abstractions, not concrete implementations
3. **Single Responsibility**: Each class has one reason to change
4. **Domain-Driven Design**: Services are organized around business domains
5. **Backward Compatibility**: Legacy imports are maintained through the services package

## Benefits

- **Testability**: Each service can be tested in isolation
- **Maintainability**: Clear separation makes code easier to understand and modify
- **Scalability**: New services can be added without affecting existing ones
- **Reusability**: Services can be reused across different parts of the application