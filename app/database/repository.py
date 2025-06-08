"""Database repository for task operations"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from .connection import get_sync_database
from .models import Task, TaskStatus

class TaskRepository:
    """Repository for task database operations"""
    
    def create_task(self, task_data: Dict[str, Any]) -> str:
        """Create a new task in database"""
        conn = get_sync_database()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO tasks (
                    id, status, created_at, updated_at, input_path, output_path,
                    original_filename, output_filename, metadata, keep_bookmarks,
                    download_url, error_message, progress
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_data['id'],
                task_data['status'],
                task_data['created_at'].isoformat(),
                task_data['updated_at'].isoformat(),
                task_data['input_path'],
                task_data['output_path'],
                task_data['original_filename'],
                task_data['output_filename'],
                json.dumps(task_data.get('metadata')) if task_data.get('metadata') else None,
                task_data.get('keep_bookmarks', False),
                task_data.get('download_url'),
                task_data.get('error_message'),
                task_data.get('progress', 0.0)
            ))
            
            conn.commit()
            return task_data['id']
            
        finally:
            conn.close()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        conn = get_sync_database()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            
            if row:
                return Task.from_row(row)
            return None
            
        finally:
            conn.close()
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task data"""
        conn = get_sync_database()
        cursor = conn.cursor()
        
        try:
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key == 'metadata' and value is not None:
                    set_clauses.append(f"{key} = ?")
                    values.append(json.dumps(value))
                elif key in ['created_at', 'updated_at'] and isinstance(value, datetime):
                    set_clauses.append(f"{key} = ?")
                    values.append(value.isoformat())
                else:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            # Always update updated_at
            if 'updated_at' not in updates:
                set_clauses.append("updated_at = ?")
                values.append(datetime.now().isoformat())
            
            values.append(task_id)
            
            query = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            return cursor.rowcount > 0
            
        finally:
            conn.close()
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task"""
        conn = get_sync_database()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0
            
        finally:
            conn.close()
    
    def list_tasks(self, limit: int = 100, offset: int = 0) -> List[Task]:
        """List all tasks with pagination"""
        conn = get_sync_database()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = cursor.fetchall()
            
            return [Task.from_row(row) for row in rows]
            
        finally:
            conn.close()
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status"""
        conn = get_sync_database()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM tasks WHERE status = ?", (status.value,))
            rows = cursor.fetchall()
            
            return [Task.from_row(row) for row in rows]
            
        finally:
            conn.close()
    
    def cleanup_old_tasks(self, days: int = 7) -> int:
        """Clean up tasks older than specified days"""
        conn = get_sync_database()
        cursor = conn.cursor()
        
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            
            cursor.execute(
                "DELETE FROM tasks WHERE created_at < ?",
                (cutoff_date.isoformat(),)
            )
            
            conn.commit()
            return cursor.rowcount
            
        finally:
            conn.close()