import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'smart_education.db'))

def get_db_connection():
    """Create and return a database connection with dict-like row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def get_db():
    """Context manager for safe database transactions."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db(schema_file=None):
    """Initialize database tables using schema.sql."""
    if schema_file is None:
        schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        
    with get_db() as conn:
        conn.executescript(schema_sql)
    print("Database schema initialized successfully.")

def query_db(query, args=(), one=False):
    """Execute a read query and return row dictionary or list of dicts."""
    with get_db() as conn:
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        cur.close()
        if one:
            return dict(rv[0]) if rv else None
        return [dict(row) for row in rv]

def execute_db(query, args=()):
    """Execute an INSERT/UPDATE/DELETE query and return the last row id."""
    with get_db() as conn:
        cur = conn.execute(query, args)
        last_id = cur.lastrowid
        cur.close()
        return last_id
