"""Application constants"""

# File handling constants
ALLOWED_EXTENSIONS = [".md", ".markdown"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_MIME_TYPES = [
    "text/markdown",
    "text/plain",
    "application/octet-stream"  # Some browsers send this for .md files
]

# Task constants
TASK_TIMEOUT_SECONDS = 300  # 5 minutes
MAX_CONCURRENT_TASKS = 10
TASK_CLEANUP_DAYS = 7

# Database constants
DATABASE_TIMEOUT = 30  # seconds
MAX_DB_CONNECTIONS = 20

# API constants
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
MAX_PAGINATION_LIMIT = 1000
DEFAULT_PAGINATION_LIMIT = 100

# File storage constants
UPLOAD_SUBDIR = "uploads"
OUTPUT_SUBDIR = "outputs"
TEMP_SUBDIR = "temp"
LOG_SUBDIR = "logs"

# Conversion constants
DEFAULT_OUTPUT_FORMAT = "docx"
SUPPORTED_OUTPUT_FORMATS = ["docx"]

# Error codes
ERROR_CODES = {
    "VALIDATION_ERROR": "E001",
    "FILE_NOT_FOUND": "E002",
    "TASK_NOT_FOUND": "E003",
    "CONVERSION_ERROR": "E004",
    "DATABASE_ERROR": "E005",
    "SERVICE_UNAVAILABLE": "E006",
    "INSUFFICIENT_STORAGE": "E007",
    "RATE_LIMIT_EXCEEDED": "E008"
}

# HTTP status codes for specific errors
HTTP_STATUS_CODES = {
    "VALIDATION_ERROR": 400,
    "FILE_NOT_FOUND": 404,
    "TASK_NOT_FOUND": 404,
    "CONVERSION_ERROR": 500,
    "DATABASE_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503,
    "INSUFFICIENT_STORAGE": 507,
    "RATE_LIMIT_EXCEEDED": 429
}

# Logging constants
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Health check constants
HEALTH_CHECK_TIMEOUT = 5  # seconds
HEALTH_CHECK_INTERVAL = 30  # seconds

# Rate limiting constants
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# Cache constants
CACHE_TTL = 300  # 5 minutes
MAX_CACHE_SIZE = 1000

# Security constants
ALLOWED_HOSTS = ["*"]  # Configure appropriately for production
CORS_MAX_AGE = 86400  # 24 hours

# Performance constants
MAX_WORKERS = 4
WORKER_TIMEOUT = 300  # 5 minutes
KEEP_ALIVE_TIMEOUT = 5

# Monitoring constants
METRICS_RETENTION_DAYS = 30
ALERT_THRESHOLDS = {
    "error_rate": 0.05,  # 5%
    "response_time_p95": 5.0,  # 5 seconds
    "disk_usage": 0.9,  # 90%
    "memory_usage": 0.8  # 80%
}