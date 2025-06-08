"""Configuration settings for the MD2Word API"""

import os
from pathlib import Path
from typing import List

class Settings:
    """Application settings"""
    
    # Application
    app_name: str = "MD2Word API"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # API
    api_prefix: str = "/api/v1"
    
    # File handling
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    allowed_extensions: List[str] = [".md", ".markdown"]
    
    # Storage
    base_dir: Path = Path(__file__).parent.parent
    upload_dir: str = os.getenv("UPLOAD_DIR", str(base_dir / "uploads"))
    output_dir: str = os.getenv("OUTPUT_DIR", str(base_dir / "outputs"))
    
    # Database
    database_path: str = os.getenv("DATABASE_PATH", str(base_dir / "data" / "tasks.db"))
    
    # Cleanup
    cleanup_files: bool = os.getenv("CLEANUP_FILES", "true").lower() == "true"
    
    # CORS
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: List[str] = ["*"]

settings = Settings()