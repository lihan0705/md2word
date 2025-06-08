"""Custom exceptions for MD2Word API"""

class MD2WordException(Exception):
    """Base exception for MD2Word API"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(MD2WordException):
    """Raised when validation fails"""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")

class ConversionError(MD2WordException):
    """Raised when document conversion fails"""
    def __init__(self, message: str, task_id: str = None):
        self.task_id = task_id
        super().__init__(message, "CONVERSION_ERROR")

class FileNotFoundError(MD2WordException):
    """Raised when a file is not found"""
    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(f"File not found: {file_path}", "FILE_NOT_FOUND")

class TaskNotFoundError(MD2WordException):
    """Raised when a task is not found"""
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}", "TASK_NOT_FOUND")

class FileSizeError(ValidationError):
    """Raised when file size exceeds limit"""
    def __init__(self, size: int, max_size: int):
        self.size = size
        self.max_size = max_size
        super().__init__(
            f"File size {size} bytes exceeds maximum allowed size {max_size} bytes",
            "file_size"
        )

class FileTypeError(ValidationError):
    """Raised when file type is not supported"""
    def __init__(self, file_type: str, allowed_types: list):
        self.file_type = file_type
        self.allowed_types = allowed_types
        super().__init__(
            f"File type '{file_type}' not supported. Allowed types: {', '.join(allowed_types)}",
            "file_type"
        )

class DatabaseError(MD2WordException):
    """Raised when database operations fail"""
    def __init__(self, message: str, operation: str = None):
        self.operation = operation
        super().__init__(message, "DATABASE_ERROR")

class ServiceUnavailableError(MD2WordException):
    """Raised when a service is unavailable"""
    def __init__(self, service_name: str):
        self.service_name = service_name
        super().__init__(f"Service unavailable: {service_name}", "SERVICE_UNAVAILABLE")