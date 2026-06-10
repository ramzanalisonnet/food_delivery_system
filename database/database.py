import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'food_delivery.db')

class DatabaseConnection:
    """Context manager for database connections with proper commit/rollback."""
    def __init__(self):
        self.conn = None
    
    def __enter__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()
        return False

def get_connection():
    """Returns a DatabaseConnection context manager."""
    return DatabaseConnection()

def execute_query(query, params=()):
    """Executes a mutation query (INSERT, UPDATE, DELETE)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor

def fetch_all(query, params=()):
    """Fetches all rows matching the query."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def fetch_one(query, params=()):
    """Fetches a single row matching the query."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

def execute_many(query, params_list):
    """Executes a query with multiple parameter sets."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        return cursor