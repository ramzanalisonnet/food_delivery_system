import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'food_delivery.db')

def get_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=()):
    """Executes a mutation query (INSERT, UPDATE, DELETE)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor

def fetch_all(query, params=()):
    """Fetches all rows matching the query query."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def fetch_one(query, params=()):
    """Fetches a single row matching the query query."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None