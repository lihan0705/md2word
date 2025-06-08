"""Utility functions for common operations"""

import uuid
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List

def generate_task_id() -> str:
    """Generate a unique task ID"""
    return str(uuid.uuid4())

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()

def get_file_stem(filename: str) -> str:
    """Get file stem (name without extension) from filename"""
    return Path(filename).stem

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if it doesn't"""
    path.mkdir(parents=True, exist_ok=True)

def cleanup_old_files(directory: Path, max_age_days: int = 7) -> int:
    """Clean up files older than specified days"""
    if not directory.exists():
        return 0
    
    cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
    cleaned_count = 0
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            try:
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
            except (OSError, IOError):
                # Ignore errors when deleting files
                pass
    
    return cleaned_count

def safe_copy_file(src: Path, dst: Path) -> bool:
    """Safely copy file with error handling"""
    try:
        ensure_directory(dst.parent)
        shutil.copy2(src, dst)
        return True
    except (OSError, IOError, shutil.Error):
        return False

def safe_move_file(src: Path, dst: Path) -> bool:
    """Safely move file with error handling"""
    try:
        ensure_directory(dst.parent)
        shutil.move(str(src), str(dst))
        return True
    except (OSError, IOError, shutil.Error):
        return False

def safe_delete_file(file_path: Path) -> bool:
    """Safely delete file with error handling"""
    try:
        if file_path.exists():
            file_path.unlink()
        return True
    except (OSError, IOError):
        return False

def get_file_info(file_path: Path) -> Optional[dict]:
    """Get file information"""
    try:
        if not file_path.exists():
            return None
        
        stat = file_path.stat()
        return {
            'name': file_path.name,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'extension': file_path.suffix.lower()
        }
    except (OSError, IOError):
        return None

def calculate_progress(current: int, total: int) -> float:
    """Calculate progress percentage"""
    if total <= 0:
        return 0.0
    return min(100.0, (current / total) * 100.0)

def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse ISO timestamp string"""
    try:
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        return None

def is_recent(timestamp: datetime, minutes: int = 5) -> bool:
    """Check if timestamp is within recent minutes"""
    cutoff = datetime.now() - timedelta(minutes=minutes)
    return timestamp > cutoff

def sanitize_path(path_str: str) -> str:
    """Sanitize path string for safe file operations"""
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
    sanitized = path_str
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    
    return sanitized

def get_available_disk_space(path: Path) -> int:
    """Get available disk space in bytes"""
    try:
        stat = shutil.disk_usage(path)
        return stat.free
    except (OSError, IOError):
        return 0

def check_disk_space(path: Path, required_bytes: int) -> bool:
    """Check if there's enough disk space"""
    available = get_available_disk_space(path)
    return available >= required_bytes