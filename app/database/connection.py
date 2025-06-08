"""Database connection and initialization"""

import sqlite3
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from ..config import settings

# Database file path
DB_PATH = Path(settings.upload_dir).parent / "database" / "md2word.db"

def init_database() -> None:
    """Initialize the database and create tables"""
    # Ensure database directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            input_path TEXT NOT NULL,
            output_path TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            output_filename TEXT NOT NULL,
            metadata TEXT,
            keep_bookmarks BOOLEAN DEFAULT FALSE,
            download_url TEXT,
            error_message TEXT,
            progress REAL DEFAULT 0.0
        )
    """)
    
    conn.commit()
    conn.close()

@asynccontextmanager
async def get_database() -> AsyncGenerator[sqlite3.Connection, None]:
    """Get database connection context manager"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    try:
        yield conn
    finally:
        conn.close()

def get_sync_database() -> sqlite3.Connection:
    """Get synchronous database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn